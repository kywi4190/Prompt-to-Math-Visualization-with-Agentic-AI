import os, json, textwrap, subprocess, uuid, pathlib, traceback, logging
from typing import List

from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape

from pydantic import BaseModel, Field, ValidationError
from shutil import which

# --- OpenAI ---
from openai import OpenAI

# ---------- LOGGING ----------
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("app")

# ---------- CONFIG ----------
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")  # default model for JSON output
BASE_DIR = pathlib.Path(__file__).parent
RENDERS_DIR = BASE_DIR / "renders"
RENDERS_DIR.mkdir(exist_ok=True)

client = OpenAI()  # uses OPENAI_API_KEY from env

# Voice TTS model and voice name for narration (you can adjust via env vars)
OPENAI_VOICE_MODEL = os.getenv("OPENAI_VOICE_MODEL", "tts-1")
OPENAI_VOICE = os.getenv("OPENAI_VOICE", "alloy")

# ---------- TEMPLATES ----------
env = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates")),
    autoescape=select_autoescape()
)

# ---------- APP ----------
app = FastAPI()
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/renders", StaticFiles(directory=str(RENDERS_DIR)), name="renders")

# ---------- GLOBAL EXCEPTION HANDLER ----------
@app.exception_handler(Exception)
async def unhandled_exc_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    log.error("UNHANDLED EXCEPTION at %s\n%s", request.url.path, tb)
    return JSONResponse(
        {"error": f"Unhandled server error: {type(exc).__name__}", "traceback": tb[:8000]},
        status_code=500
    )

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    template = env.get_template("index.html")
    return HTMLResponse(template.render())

# ---------- Schemas for strict validation ----------
class SubtitleCue(BaseModel):
    start: float = Field(ge=0)
    end: float = Field(ge=0)
    text: str

class ManimPayload(BaseModel):
    file_name: str
    scene_name: str
    code: str
    subtitle_cues: List[SubtitleCue]

# ---------- Helpers ----------
import re

def sanitize_and_fix_code(src: str) -> str:
    """
    Minimal guardrails + standard Manim prelude.
    - Blocks dangerous imports.
    - Injects common Manim/numpy/math imports.
    - Provides ParametricSurface fallback for compatibility.
    - Strips duplicate imports.
    - Makes MathTex/Tex strings raw to avoid escape issues.
    - Fixes common LaTeX syntax issues (unmatched braces, missing braces around exponents, double backslashes, etc.).
    """
    s = (src or "").replace("\r\n", "\n")
    low = s.lower()

    # 1) Block dangerous imports
    forbidden = (
        "import os", "from os",
        "import subprocess", "from subprocess",
        "import sys", "from sys",
        "import pathlib", "from pathlib",
        "import requests", "from requests",
        "import pickle", "from pickle",
        "import shutil", "from shutil"
    )
    if any(tok in low for tok in forbidden):
        raise ValueError("Generated code contains forbidden imports or IO modules.")

    # 2) Prelude (standard imports and fallbacks)
    prelude = textwrap.dedent("""\
        from manim import *
        import numpy as np
        import math
        # Optional utilities (guarded against missing)
        try:
            from manim.utils.color import Color
        except Exception:
            def Color(x): return x  # accept hex strings or color names
        try:
            from manim.utils.space_ops import rotate_vector
        except Exception:
            pass
        try:
            from manim.utils.bezier import bezier
        except Exception:
            pass
        try:
            from manim.utils.rate_functions import smooth
        except Exception:
            pass
        # ParametricSurface fallback for compatibility
        try:
            ParametricSurface
        except NameError:
            ParametricSurface = Surface
    """)

    # 3) Remove duplicate top-level imports (to avoid conflicts)
    dup_import_patterns = [
        r'^\s*from\s+manim\s+import\s+\*\s*$',
        r'^\s*import\s+numpy\s+as\s+np\s*$',
        r'^\s*import\s+math\s*$',
        r'^\s*from\s+manim\.utils\.color\s+import\s+Color\s*$',
        r'^\s*from\s+manim\.utils\.space_ops\s+import\s+rotate_vector\s*$',
        r'^\s*from\s+manim\.utils\.bezier\s+import\s+bezier\s*$',
        r'^\s*from\s+manim\.utils\.rate_functions\s+import\s+smooth\s*$',
    ]
    for pat in dup_import_patterns:
        s = re.sub(pat, "", s, flags=re.MULTILINE)

    # 4) Make MathTex and Tex string arguments raw (to avoid escape issues)
    s = s.replace('MathTex("', 'MathTex(r"').replace("MathTex('", "MathTex(r'")
    s = s.replace('Tex("', 'Tex(r"').replace("Tex('", "Tex(r'")

    # 5) Fix interpolate_color usage (wrap args in Color())
    s = re.sub(
        r"interpolate_color\(\s*([^,]+)\s*,\s*([^,]+)\s*,",
        r"interpolate_color(Color(\1), Color(\2),",
        s
    )

    # 6) Fix common LaTeX syntax issues in Tex/MathTex strings
    def fix_latex_expr(expr: str) -> str:
        # Automatically correct common LaTeX syntax errors
        result_chars = []
        brace_stack = 0
        i = 0
        while i < len(expr):
            c = expr[i]
            if c == '\\':
                if i + 1 < len(expr) and expr[i+1] in '{}':
                    # Preserve escaped braces
                    result_chars.append(c)
                    result_chars.append(expr[i+1])
                    i += 2
                    continue
                elif i + 1 < len(expr) and expr[i+1] == '\\':
                    # Normalize double backslashes (e.g., \\theta -> \\theta)
                    if i + 2 >= len(expr) or expr[i+2].isspace():
                        result_chars.append('\\')
                        result_chars.append('\\')
                        i += 2
                        continue
                    else:
                        result_chars.append(c)
                        i += 1
                        continue
                else:
                    result_chars.append(c)
                    i += 1
                    continue
            elif c == '{':
                brace_stack += 1
                result_chars.append(c)
            elif c == '}':
                if brace_stack > 0:
                    brace_stack -= 1
                    result_chars.append(c)
                # Skip unmatched closing brace
            else:
                result_chars.append(c)
            i += 1
        # Append missing braces if any remain open
        result = "".join(result_chars)
        if brace_stack > 0:
            result += '}' * brace_stack
        # Add braces around multi-character exponents after e^
        result = re.sub(r'e\^((?:[A-Za-z0-9]|\\[A-Za-z]+)+)', r'e^{\1}', result)

        # Handle exponents written as e^(...) without braces
        while "e^(" in result:
            idx = result.find("e^(")
            start = idx + 2
            paren_depth = 1
            match_idx = -1
            for j in range(start+1, len(result)):
                if result[j] == '(':
                    paren_depth += 1
                elif result[j] == ')':
                    paren_depth -= 1
                    if paren_depth == 0:
                        match_idx = j
                        break
            if match_idx != -1:
                result = result[:idx+2] + "{" + result[idx+2:match_idx+1] + "}" + result[match_idx+1:]
            else:
                break
        return result

    # Apply LaTeX fixes to all Tex/MathTex string literals
    s = re.sub(r'(?:MathTex|Tex)\(r?"([^"]*?)"', lambda m:
               m.group(0)[:len(m.group(0)) - len(m.group(1)) - 1] +
               fix_latex_expr(m.group(1)) + '"', s)
    s = re.sub(r"(?:MathTex|Tex)\(r?'([^']*?)'", lambda m:
               m.group(0)[:len(m.group(0)) - len(m.group(1)) - 1] +
               fix_latex_expr(m.group(1)) + "'", s)

    # 7) Final assembled code
    return prelude + "\n" + s.strip() + "\n"

def to_vtt_time(t: float) -> str:
    t = float(t)
    ms = int((t - int(t)) * 1000)
    s = int(t) % 60
    m = (int(t) // 60) % 60
    h = int(t) // 3600
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

@app.post("/generate")
async def generate(prompt: str = Form(...)):
    log.info("POST /generate received")
    # --- Preflight checks: fail early with a clear message ---
    if not os.getenv("OPENAI_API_KEY"):
        log.error("OPENAI_API_KEY missing")
        return JSONResponse({"error": "OPENAI_API_KEY is not set in this shell."}, status_code=500)
    if not which("manim"):
        log.error("manim not found on PATH")
        return JSONResponse({"error": "Manim not found on PATH. Activate your venv or install manim."}, status_code=500)
    if not which("ffmpeg"):
        log.error("ffmpeg not found on PATH")
        return JSONResponse({"error": "ffmpeg not found on PATH. Install ffmpeg and open a new terminal."}, status_code=500)

    job_id = str(uuid.uuid4())[:8]
    workdir = RENDERS_DIR / job_id
    workdir.mkdir(parents=True, exist_ok=True)
    log.info("Job %s workdir: %s", job_id, workdir)

    system = textwrap.dedent(f"""
    ===================== SYSTEM PROMPT =====================
    You are a senior math educator + Manim engineer. 
    Given a user’s math prompt, you must return a SINGLE JSON object (strict schema) that contains:
    - file_name: Python filename to write (e.g., "explainer.py")
    - scene_name: Name of ONE Scene or ThreeDScene subclass to render (e.g., "ExplainerScene")
    - subtitle_cues: array of {{start: number, end: number, text: string}}
    - code: complete Manim code that runs without modification

    ===================== PRIMARY GOAL =====================
    Produce a clear, creative, and mathematically accurate visual explanation.
    Favor geometric/spatial intuition, unusual analogies, and smooth, readable motion.
    Support advanced Manim: parametric curves/surfaces, 3D camera motion, vector fields, field lines,
    level sets, projections, color/opacity encoding, etc.
    Target total runtime: 20–45 seconds.

    ===================== ALLOWED IMPORTS =====================
    from manim import *
    import numpy as np
    import math
    from sympy import *       (optional, for symbolic math)

    DO NOT import:
    os, subprocess, sys, pathlib, json, requests, PIL, skimage, or any network/IO modules.
    DO NOT perform file IO or network requests.

    ===================== LATEX =====================
    You MAY use LaTeX mobjects (Tex, MathTex) if helpful,
    but keep it minimal and stable (short expressions, simple layout).

    ===================== GEOMETRY & COORDINATES =====================
    All 2D objects should use 3D-safe coordinates: [x, y, 0].
    Use Line([x1,y1,0],[x2,y2,0]), Arrow([x1,y1,0],[x2,y2,0]), Dot().move_to([x,y,0]), etc.
    Use mobject.apply_matrix([[a,b],[c,d]]) for linear transforms.
    For 3D scenes:
    - subclass ThreeDScene
    - set camera orientation with self.set_camera_orientation(...)
    - allowed: Surface, ParametricSurface, ThreeDAxes, StreamLines, VectorField, etc.

    ===================== PERFORMANCE =====================
    Keep complexity moderate.
    No massive point clouds or extreme loops.
    Use always_redraw and trackers efficiently.
    Avoid OpenGL-only features and custom shaders.

    ===================== DETERMINISM =====================
    If randomness is used:
    import random; random.seed(7)
    np.random.seed(7)

    ===================== SCENE CONTRACT =====================
    Exactly ONE Scene or ThreeDScene class with the name equal to scene_name.
    No undefined names or external assets.
    Allowed primitives:
    NumberPlane, Axes, ThreeDAxes, VGroup, Text, Tex, MathTex, Dot, Line, Arrow, Surface,
    ParametricFunction, ParametricSurface, VectorField, StreamLines, ValueTracker,
    always_redraw, Create, Write, Fade, Transform, Rotate, Scale.

    ===================== SUBTITLES =====================
    Provide narration aligned with beats (1–4s each). Total coverage: full 20–45s runtime.
    Strict JSON format:
    "subtitle_cues": [
        {{"start": 0.0, "end": 3.0, "text": "Hook the viewer with the core idea."}},
        {{"start": 3.0, "end": 7.0, "text": "Introduce the structure and camera motion."}}
    ]


    ===================== PEDAGOGY & STYLE =====================
    Start with an immediate visual hook.
    Use motion and transformation to convey concepts.
    Use 3D analogies for abstract concepts (e.g., surfaces, projections, slicing, color maps).
    Favor minimal labels, smooth animation, and cause→effect structure.

    ===================== VALIDATION CHECKLIST =====================
    [ ] Exactly one Scene/ThreeDScene class named scene_name
    [ ] Only allowed imports used (+ sympy if needed)
    [ ] All 2D coords in [x,y,0]; proper use of 3D constructs
    [ ] LaTeX only if minimal and stable
    [ ] Duration ≈ 20–35 seconds
    [ ] Subtitle cues strictly increasing, required fields only
    [ ] Renders with: manim -ql -o out.mp4 <file_name> <scene_name>
    [ ] When calling interpolate_color, wrap both color arguments with Color(...), e.g., interpolate_color(Color("#ffaa00"), Color(BLUE), alpha).
    [ ] Do NOT use self.camera.frame. For 3D camera movement use only:
    self.set_camera_orientation(phi=..., theta=..., zoom=...), 
    self.move_camera(phi=..., theta=..., gamma=..., zoom=..., run_time=...), 
    self.begin_ambient_camera_rotation(rate=...), self.stop_ambient_camera_rotation().
    [ ] Never use run_time=0. The minimum run_time for any animation or move_camera is 0.2s.
    """).strip()

    user_prompt = textwrap.dedent(f"""
    USER PROMPT:
    {prompt}

    ===================== USER PROMPT =====================
    The user has described a mathematical concept, process, theorem, structure, or object.

    Your task:
    Design an advanced Manim visual explanation (20-35 seconds) showing geometric intuition.
    Include engaging narration (subtitles) throughout, matching the scene transitions.
    """).strip()

    # --- OpenAI: Chat Completions with JSON MODE (stable) ---
    log.info("Calling OpenAI model=%s", OPENAI_MODEL)
    try:
        chat = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt + "\n\nReturn ONLY valid JSON. No prose."}
            ],
            response_format={"type": "json_object"},
            temperature=1,
        )
    except Exception as e:
        tb = traceback.format_exc()
        log.error("OpenAI request failed: %s\n%s", repr(e), tb)
        return JSONResponse({"error": f"OpenAI request failed: {repr(e)}", "traceback": tb[:8000]}, status_code=500)

    raw_text = (chat.choices[0].message.content or "").strip()
    log.info("LLM returned %d chars of JSON", len(raw_text))

    # ---- Extract, normalize, then validate ----
    try:
        data = json.loads(raw_text)
    except Exception as e:
        log.error("Failed to parse JSON: %s", e)
        return JSONResponse({"error": f"Failed to parse JSON: {e}", "raw": raw_text[:4000]}, status_code=500)

    # Normalize subtitle_cues: accept either {time, text} or {start, end, text}
    cues = data.get("subtitle_cues", []) or []
    for i, cue in enumerate(cues):
        # If only "time" exists, map to start/end
        if "start" not in cue and "time" in cue:
            try:
                t = float(cue["time"])
            except Exception:
                t = 0.0
            if i + 1 < len(cues) and "time" in cues[i + 1]:
                try:
                    next_t = float(cues[i + 1]["time"])
                    cue["end"] = max(t + 0.2, next_t - 0.2)
                except Exception:
                    cue["end"] = t + 2.0
            else:
                cue["end"] = t + 2.0
            cue["start"] = t
            cue.pop("time", None)
        # If start exists but no end, default to +2.0s
        if "start" in cue and "end" not in cue:
            try:
                st = float(cue["start"])
            except Exception:
                st = 0.0
            cue["end"] = st + 2.0
        # Ensure numeric types
        if "start" in cue:
            cue["start"] = float(cue["start"])
        if "end" in cue:
            cue["end"] = float(cue["end"])
    # Write back normalized cues
    data["subtitle_cues"] = cues

    # Now validate against the strict schema
    try:
        manim_payload = ManimPayload.model_validate(data)
    except ValidationError as ve:
        log.error("LLM JSON validation failed after normalization: %s", ve)
        return JSONResponse({
            "error": "LLM JSON validation failed after normalization",
            "details": ve.errors(),
            "raw": json.dumps(data)[:4000]
        }, status_code=500)

    file_name = (manim_payload.file_name or "explainer.py").strip()
    scene_name = manim_payload.scene_name.strip()
    code_str = manim_payload.code
    subtitle_cues = manim_payload.subtitle_cues
    # Unescape newline characters from JSON if present
    code_str = code_str.replace("\\n", "\n")

    # --- Critique and regenerate loop ---
    log.info("Critiquing generated code with OpenAI")
    critique_text = ""
    try:
        critique_prompt = (
            "Please critique the following Manim code for any syntax or design issues, focusing on Manim compatibility. "
            "Provide constructive feedback and do NOT simplify the content:\n"
            f"```python\n{code_str}\n```"
        )
        critique_chat = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": critique_prompt}],
            temperature=1,
        )
    except Exception as e:
        tb = traceback.format_exc()
        log.error("OpenAI critique request failed: %s\n%s", repr(e), tb)
        # If critique fails, skip regeneration
    else:
        critique_text = (critique_chat.choices[0].message.content or "").strip()
        log.info("Critique text: %s", critique_text[:200].replace("\n", " "))

    if critique_text:
        try:
            regen_prompt = (
                f"The assistant provided the following critique of the Manim code:\n{critique_text}\n\n"
                "Please incorporate these suggestions and improvements into the code, without changing the scene's purpose or length. "
                "Return an improved JSON with file_name, scene_name, subtitle_cues, code."
            )
            regen_chat = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": regen_prompt}],
                response_format={"type": "json_object"},
                temperature=1,
            )
        except Exception as e:
            tb = traceback.format_exc()
            log.error("OpenAI regeneration request failed: %s\n%s", repr(e), tb)
        else:
            new_raw = (regen_chat.choices[0].message.content or "").strip()
            log.info("LLM improved JSON %d chars", len(new_raw))
            if new_raw:
                try:
                    new_data = json.loads(new_raw)
                except Exception as e_json:
                    log.error("Failed to parse improved JSON: %s", e_json)
                else:
                    try:
                        new_payload = ManimPayload.model_validate(new_data)
                    except ValidationError as ve:
                        log.error("Improved JSON validation failed: %s", ve)
                    else:
                        file_name = (new_payload.file_name or file_name).strip()
                        scene_name = new_payload.scene_name.strip()
                        code_str = new_payload.code
                        subtitle_cues = new_payload.subtitle_cues
                        code_str = code_str.replace("\\n", "\n")

    py_path = workdir / file_name
    vtt_path = workdir / "captions.vtt"
    mp4_path = workdir / "out.mp4"
    log.info("Writing code to %s", py_path)

    # --- Sanitize / auto-fix and write code file ---
    try:
        code_str_fixed = sanitize_and_fix_code(code_str)
    except ValueError as ve:
        log.error("Code sanitize failed: %s", ve)
        return JSONResponse({"error": str(ve)}, status_code=500)
    # --- Syntax check the sanitized code ---
    try:
        compile(code_str_fixed, str(py_path), 'exec')
    except SyntaxError as se:
        # Write syntax error details to log and attempt automatic fix
        error_lines = traceback.format_exception_only(type(se), se)
        first_out = "Traceback (most recent call last):\n" + "".join(error_lines)
        (workdir / "render.log").write_text(first_out, encoding="utf-8")
        log.error("Generated code has a syntax error:\n%s", first_out)
        # Attempt to fix syntax errors via GPT-5
        try:
            tb_index = first_out.find("Traceback")
            error_snippet = first_out[tb_index:] if tb_index != -1 else first_out
            repair_prompt = (
                f"The Manim code failed to compile with the following syntax error:\n```text\n{error_snippet}\n```\n"
                f"The original code was:\n```python\n{code_str}\n```\n"
                "Please fix any syntax errors in the code while preserving the code's purpose and complexity. "
                "Do not remove features or simplify the content to avoid errors. "
                "Keep the same file_name and scene_name unless a change is required to fix the issue. "
                "Return a JSON object with keys file_name, scene_name, subtitle_cues, code."
            ).strip()
            repair_chat = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": repair_prompt}],
                response_format={"type": "json_object"},
                temperature=1,
            )
        except Exception as e_fix:
            tb = traceback.format_exc()
            log.error("OpenAI repair request failed: %s\n%s", repr(e_fix), tb)
            return JSONResponse({"error": "Manim render failed", "details": first_out[-8000:]}, status_code=500)
        fix_raw = (repair_chat.choices[0].message.content or "").strip()
        log.info("LLM repair returned %d chars of JSON", len(fix_raw))
        if not fix_raw:
            return JSONResponse({"error": "Manim render failed", "details": first_out[-8000:]}, status_code=500)
        try:
            fix_data = json.loads(fix_raw)
        except Exception as e_json:
            log.error("Failed to parse repair JSON: %s", e_json)
            return JSONResponse({"error": "Manim render failed", "details": first_out[-8000:]}, status_code=500)
        try:
            fix_payload = ManimPayload.model_validate(fix_data)
        except ValidationError as ve:
            log.error("Repaired JSON validation failed: %s", ve)
            return JSONResponse({"error": "Manim render failed", "details": first_out[-8000:]}, status_code=500)
        # Overwrite code with repaired payload
        file_name = (fix_payload.file_name or file_name).strip()
        scene_name = fix_payload.scene_name.strip()
        code_str = fix_payload.code
        subtitle_cues = fix_payload.subtitle_cues
        log.info("Writing repaired code to %s", workdir / file_name)
        try:
            code_str_fixed2 = sanitize_and_fix_code(code_str)
        except ValueError as ve:
            log.error("Code sanitize failed for repaired code: %s", ve)
            return JSONResponse({"error": str(ve)}, status_code=500)
        (workdir / file_name).write_text(code_str_fixed2, encoding="utf-8")
        # Rewrite subtitles with updated cues
        vtt_lines = ["WEBVTT", ""]
        for i, cue in enumerate(subtitle_cues, start=1):
            start = max(0.0, float(cue.start))
            end = max(start + 0.01, float(cue.end))
            text = (cue.text or "").replace("\n", " ")
            vtt_lines += [f"{i}", f"{to_vtt_time(start)} --> {to_vtt_time(end)}", text, ""]
        (workdir / "captions.vtt").write_text("\n".join(vtt_lines), encoding="utf-8")
        # Prepare to run Manim with repaired code (after syntax fix)
        cmd = [
            "manim",
            "-ql",
            "--disable_caching",
            "--media_dir", ".",
            "--output_file", "out",
            str(pathlib.Path(file_name).name),
            scene_name,
        ]
        log.info("Running Manim (repair attempt): %s", " ".join(cmd))
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(workdir),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=900,
                text=True
            )
            second_out = proc.stdout or ""
            with open(workdir / "render.log", "a", encoding="utf-8") as f:
                f.write("\n[Repair Attempt Output]\n")
                f.write(second_out)
            log.info("Manim completed OK after syntax repair (%d chars of log)", len(second_out))
            # Locate rendered mp4 (after repair)
            module_name = pathlib.Path(file_name).stem
            candidates = list((workdir / "media" / "videos" / module_name).rglob("out.mp4"))
            if not candidates:
                candidates = list(workdir.rglob("out.mp4"))
            if not candidates:
                log.error("Render finished but out.mp4 was not found under %s (after syntax repair)", workdir)
                return JSONResponse({"error": "Render finished but out.mp4 was not found", "details": (workdir / "render.log").read_text(encoding="utf-8", errors="ignore")[-4000:]}, status_code=500)
            mp4_src = max(candidates, key=lambda p: p.stat().st_mtime)
            import shutil
            shutil.copy2(mp4_src, mp4_path)
            log.info("Copied rendered video from %s to %s", mp4_src, mp4_path)
        except subprocess.CalledProcessError as e2:
            second_out = e2.stdout or ""
            with open(workdir / "render.log", "a", encoding="utf-8") as f:
                f.write("\n[Repair Attempt Error]\n")
                f.write(second_out)
            log.error("Manim render failed after syntax repair:\n%s", second_out)
            error_log_content = (workdir / "render.log").read_text(encoding="utf-8", errors="ignore")
            (workdir / "error.txt").write_text(error_log_content, encoding="utf-8")
            return JSONResponse({"error": "Manim render failed", "details": second_out[-8000:]}, status_code=500)

    # If initial compile succeeded, run Manim normally
    (workdir / file_name).write_text(code_str_fixed, encoding="utf-8")
    # Write initial subtitles to VTT
    vtt_lines = ["WEBVTT", ""]
    for i, cue in enumerate(subtitle_cues, start=1):
        start = max(0.0, float(cue.start))
        end = max(start + 0.01, float(cue.end))
        text = (cue.text or "").replace("\n", " ")
        vtt_lines += [f"{i}", f"{to_vtt_time(start)} --> {to_vtt_time(end)}", text, ""]
    (workdir / "captions.vtt").write_text("\n".join(vtt_lines), encoding="utf-8")

    # --- Run Manim (no caching) ---
    cmd = [
        "manim",
        "-ql",
        "--disable_caching",
        "--media_dir", ".",
        "--output_file", "out",
        str(py_path.name),
        scene_name,
    ]
    log.info("Running Manim: %s", " ".join(cmd))
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(workdir),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=480,
            text=True
        )
        manim_log = proc.stdout
        (workdir / "render.log").write_text(manim_log or "", encoding="utf-8")
        log.info("Manim completed OK (%d chars of log)", len(manim_log or ""))

        # --- Locate the rendered mp4 and copy to out.mp4 (success path) ---
        from pathlib import Path
        import shutil
        module_name = Path(py_path.name).stem
        candidates = list((workdir / "media" / "videos" / module_name).rglob("out.mp4"))
        if not candidates:
            candidates = list(workdir.rglob("out.mp4"))
        if not candidates:
            log.error("Render finished but out.mp4 was not found under %s", workdir)
            return JSONResponse({"error": "Render finished but out.mp4 was not found", "details": (workdir / "render.log").read_text(encoding="utf-8", errors="ignore")[-4000:]}, status_code=500)
        mp4_src = max(candidates, key=lambda p: p.stat().st_mtime)
        shutil.copy2(mp4_src, mp4_path)
        log.info("Copied rendered video from %s to %s", mp4_src, mp4_path)

    except subprocess.CalledProcessError as e:
        first_out = e.stdout or ""
        (workdir / "render.log").write_text(first_out, encoding="utf-8")
        log.error("Manim render failed on first attempt:\n%s", first_out)
        # --- Error-repair loop: attempt to fix code via GPT (runtime errors) ---
        try:
            error_snippet = first_out
            tb_index = first_out.rfind("Traceback")
            if tb_index != -1:
                error_snippet = first_out[tb_index:]
            elif len(first_out) > 2000:
                error_snippet = first_out[-2000:]
            latex_issue = False
            if ("latex error" in first_out.lower() or "latex compilation error" in first_out
                or "missing }" in first_out.lower() or "missing {" in first_out.lower()
                or "undefined control" in first_out.lower() or "missing $" in first_out.lower()
                or "extra }" in first_out.lower()):
                latex_issue = True
            if latex_issue:
                repair_prompt = (
                    f"The Manim code failed to render due to a LaTeX syntax error. The error was:\n```text\n{error_snippet}\n```\n"
                    f"The original code was:\n```python\n{code_str}\n```\n"
                    "Identify and fix any LaTeX syntax issues in the code (e.g., unmatched braces, missing braces around exponents, incorrect backslashes) that caused this error. "
                    "Do not simplify or change other parts of the code; preserve the code's purpose and complexity. "
                    "Keep the same file_name and scene_name unless absolutely necessary. "
                    "Return a JSON object with keys file_name, scene_name, subtitle_cues, code."
                ).strip()
            else:
                repair_prompt = (
                    f"The Manim code failed to render with the following error:\n```text\n{error_snippet}\n```\n"
                    f"The original code was:\n```python\n{code_str}\n```\n"
                    "Please fix the code to resolve the error while preserving the code's purpose and complexity. "
                    "Do not remove features or simplify the content to avoid errors. "
                    "Keep the same file_name and scene_name unless a change is required to fix the issue. "
                    "Return a JSON object with keys file_name, scene_name, subtitle_cues, code."
                ).strip()
            repair_chat = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": repair_prompt}],
                response_format={"type": "json_object"},
                temperature=1,
            )
        except Exception as e_fix:
            tb = traceback.format_exc()
            log.error("OpenAI repair request failed: %s\n%s", repr(e_fix), tb)
            return JSONResponse({"error": "Manim render failed", "details": first_out[-8000:]}, status_code=500)
        fix_raw = (repair_chat.choices[0].message.content or "").strip()
        log.info("LLM repair returned %d chars of JSON", len(fix_raw))
        if not fix_raw:
            return JSONResponse({"error": "Manim render failed", "details": first_out[-8000:]}, status_code=500)
        try:
            fix_data = json.loads(fix_raw)
        except Exception as e_json:
            log.error("Failed to parse repair JSON: %s", e_json)
            return JSONResponse({"error": "Manim render failed", "details": first_out[-8000:]}, status_code=500)
        try:
            fix_payload = ManimPayload.model_validate(fix_data)
        except ValidationError as ve:
            log.error("Repaired JSON validation failed: %s", ve)
            return JSONResponse({"error": "Manim render failed", "details": first_out[-8000:]}, status_code=500)
        # Overwrite code with repaired payload
        file_name = (fix_payload.file_name or file_name).strip()
        scene_name = fix_payload.scene_name.strip()
        code_str = fix_payload.code
        subtitle_cues = fix_payload.subtitle_cues
        log.info("Writing repaired code to %s", workdir / file_name)
        try:
            code_str_fixed2 = sanitize_and_fix_code(code_str)
        except ValueError as ve:
            log.error("Code sanitize failed for repaired code: %s", ve)
            return JSONResponse({"error": str(ve)}, status_code=500)
        (workdir / file_name).write_text(code_str_fixed2, encoding="utf-8")
        # Rewrite subtitles with updated cues
        vtt_lines = ["WEBVTT", ""]
        for i, cue in enumerate(subtitle_cues, start=1):
            start = max(0.0, float(cue.start))
            end = max(start + 0.01, float(cue.end))
            text = (cue.text or "").replace("\n", " ")
            vtt_lines += [f"{i}", f"{to_vtt_time(start)} --> {to_vtt_time(end)}", text, ""]
        (workdir / "captions.vtt").write_text("\n".join(vtt_lines), encoding="utf-8")
        # Prepare second attempt run
        cmd[6] = str(pathlib.Path(file_name).name)
        cmd[7] = scene_name
        log.info("Running Manim (repair attempt): %s", " ".join(cmd))
    except subprocess.TimeoutExpired as e:
        msg = str(e)
        log.error("Manim render timed out: %s", msg)
        return JSONResponse({"error": "Manim render timed out", "details": msg}, status_code=500)

    # If we reach here, an output video should be at out.mp4 (silent)
    # --- Automatic Speech Generation and Audio Muxing ---
    log.info("Generating narration audio via OpenAI TTS (model=%s, voice=%s)", OPENAI_VOICE_MODEL, OPENAI_VOICE)
    try:
        from pydub import AudioSegment
    except ImportError:
        log.error("pydub is not installed. Please install pydub for audio generation.")
        return JSONResponse({"error": "Audio generation failed", "details": "pydub not installed"}, status_code=500)

    audio_segments = []
    prev_end = 0.0
    try:
        # Iterate through subtitle cues and generate each segment
        for idx, cue in enumerate(subtitle_cues):
            text = (cue.text or "").strip()
            start_time = float(cue.start)
            end_time = float(cue.end)
            # Add silence for any gap between previous end and this cue's start
            if start_time > prev_end:
                gap_ms = int((start_time - prev_end) * 1000)
                if gap_ms > 0:
                    audio_segments.append(AudioSegment.silent(duration=gap_ms))
            # Generate speech for this subtitle text
            log.info("TTS for subtitle %d: \"%s\"", idx+1, text)
            response = client.audio.speech.create(
                model=OPENAI_VOICE_MODEL,
                voice=OPENAI_VOICE,
                input=text,
                response_format="mp3"
            )
            # Save audio chunk to file and load with pydub
            chunk_path = workdir / f"speech_chunk_{idx+1}.mp3"
            response.stream_to_file(str(chunk_path))
            segment_audio = AudioSegment.from_file(str(chunk_path), format="mp3")
            audio_segments.append(segment_audio)
            prev_end = end_time
    except Exception as e:
        log.error("OpenAI TTS generation failed: %s", e)
        return JSONResponse({"error": "OpenAI TTS generation failed", "details": str(e)}, status_code=500)

    # If video is longer than last subtitle, add trailing silence
    video_duration = prev_end
    try:
        # Get actual video duration via ffprobe
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "csv=p=0", str(mp4_path)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        duration_str = (probe.stdout or "").strip()
        if duration_str:
            vid_len = float(duration_str)
            video_duration = max(video_duration, vid_len)
    except Exception as e:
        log.warning("Failed to probe video duration for audio padding: %s", e)
    if video_duration > prev_end:
        gap_ms = int((video_duration - prev_end) * 1000)
        if gap_ms > 0:
            audio_segments.append(AudioSegment.silent(duration=gap_ms))
            log.info("Added %.2f seconds of trailing silence to match video length", gap_ms/1000.0)

    # Combine all audio segments into one track
    if audio_segments:
        full_audio = audio_segments[0]
        for seg in audio_segments[1:]:
            full_audio += seg
    else:
        full_audio = AudioSegment.silent(duration=int(video_duration * 1000))
    audio_path = workdir / "narration.mp3"
    full_audio.export(str(audio_path), format="mp3")
    log.info("Narration audio saved to %s (%.2f seconds)", audio_path, len(full_audio) / 1000.0)

    # Use ffmpeg to mux the narration audio with the video (copy video stream)
    merged_path = workdir / "merged.mp4"
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", str(mp4_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        str(merged_path)
    ]
    log.info("Muxing audio and video with ffmpeg")
    try:
        proc = subprocess.run(ffmpeg_cmd, cwd=str(workdir), check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        ffmpeg_output = proc.stdout or ""
        log.info("FFmpeg output: %s", ffmpeg_output[-200:] if ffmpeg_output else "(none)")
    except subprocess.CalledProcessError as e:
        ff_out = e.stdout or ""
        log.error("FFmpeg mux failed:\n%s", ff_out)
        return JSONResponse({"error": "Audio-video muxing failed", "details": ff_out[-8000:]}, status_code=500)
    except Exception as e:
        log.error("FFmpeg execution error: %s", e)
        return JSONResponse({"error": "Audio-video muxing exception", "details": str(e)}, status_code=500)

    # Replace original out.mp4 with merged video (with audio)
    try:
        os.remove(mp4_path)  # remove silent video
    except Exception:
        pass
    merged_path.rename(mp4_path)
    log.info("Merged video with audio saved to %s", mp4_path)

    # Return URLs for video with audio and subtitles
    return {
        "videoUrl": f"/renders/{workdir.name}/out.mp4",
        "subsUrl":  f"/renders/{workdir.name}/captions.vtt"
    }

# Optional quick diagnostics endpoint
@app.get("/diag")
def diag():
    try:
        import openai
        has_openai = True
    except ImportError:
        has_openai = False
    try:
        import pydub
        has_pydub = True
    except ImportError:
        has_pydub = False
    return {
        "python": os.sys.version.split()[0],
        "openai_model": OPENAI_MODEL,
        "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "has_openai": has_openai,
        "has_manim": bool(which("manim")),
        "has_ffmpeg": bool(which("ffmpeg")),
        "has_pydub": has_pydub
    }
