from manim import *
import numpy as np
import math
# Optional utilities (guarded; some versions may not expose them)
try:
    from manim.utils.color import Color as _Color
except Exception:
    try:
        from manim.utils.color import ManimColor as _Color  # older naming
    except Exception:
        # Last-resort parser: parse_color returns a ManimColor
        from manim.utils.color import parse_color as _parse_color
        class _Color:
            def __new__(cls, x):
                return _parse_color(x)
Color = _Color

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

# Helper geometry builders

def make_cylinder(radius=0.3, height=1.0, color=GRAY, v_range=None, fill_opacity=1.0, stroke_opacity=0.2):
    if v_range is None:
        v_range = [0.0, height]
    surf = ParametricSurface(
        lambda u, v: np.array([
            radius * np.cos(u),
            radius * np.sin(u),
            v,
        ]),
        u_range=[0, TAU],
        v_range=v_range,
        resolution=(32, 12),
    )
    surf.set_style(
        fill_color=color,
        fill_opacity=fill_opacity,
        stroke_color=BLACK,
        stroke_opacity=stroke_opacity,
        stroke_width=0.5,
    )
    return surf


def make_cylinder_x(length=1.0, radius=0.1, color=GRAY, fill_opacity=1.0, stroke_opacity=0.2):
    # Build around center along the x-axis by using v_range symmetric and rotating
    cyl = make_cylinder(radius=radius, height=length, color=color, v_range=[-length / 2.0, length / 2.0], fill_opacity=fill_opacity, stroke_opacity=stroke_opacity)
    cyl.rotate(PI / 2, axis=UP)  # rotate around y to align height with x
    return cyl


def make_sphere(radius=0.5, color=YELLOW, fill_opacity=0.25, stroke_opacity=0.5):
    sph = ParametricSurface(
        lambda u, v: np.array([
            radius * np.sin(u) * np.cos(v),
            radius * np.sin(u) * np.sin(v),
            radius * np.cos(u),
        ]),
        u_range=[0, PI],
        v_range=[0, TAU],
        resolution=(24, 18),
    )
    sph.set_style(
        fill_color=color,
        fill_opacity=fill_opacity,
        stroke_color=color,
        stroke_opacity=stroke_opacity,
        stroke_width=0.5,
    )
    return sph


def build_cowboy(x=0.0, main_color="#8B5A2B", hat_color="#5C4033", arm_bias_deg=0):
    # Body stack along z
    pieces = []
    # Legs/boots
    legs = make_cylinder(radius=0.18, height=0.60, color=main_color)
    pieces.append(legs)
    # Torso
    torso = make_cylinder(radius=0.26, height=0.95, color=main_color)
    torso.shift([0, 0, 0.60])
    pieces.append(torso)
    # Head (cylindrical)
    head = make_cylinder(radius=0.18, height=0.35, color=main_color)
    head.shift([0, 0, 1.55])
    pieces.append(head)
    # Hat: brim + crown (both cylinders)
    hat_brim = make_cylinder(radius=0.38, height=0.05, color=hat_color, fill_opacity=0.95)
    hat_brim.shift([0, 0, 1.90])
    pieces.append(hat_brim)
    hat_crown = make_cylinder(radius=0.22, height=0.35, color=hat_color)
    hat_crown.shift([0, 0, 1.95])
    pieces.append(hat_crown)
    # Arms (simple forward-pointing cylinders along x)
    arm_z = 1.05
    arm_span = 0.60
    arm_radius = 0.06
    armL = make_cylinder_x(length=arm_span, radius=arm_radius, color=main_color)
    armR = make_cylinder_x(length=arm_span, radius=arm_radius, color=main_color)
    # Position arms to left/right of torso
    armL.shift([-0.45, 0, arm_z])
    armR.shift([+0.45, 0, arm_z])
    # Give initial bias (hands slightly back or forward)
    if arm_bias_deg != 0:
        bias = arm_bias_deg * DEGREES
        armL.rotate(bias, axis=UP, about_point=np.array([-0.45, 0, arm_z]))
        armR.rotate(bias, axis=UP, about_point=np.array([+0.45, 0, arm_z]))
    pieces.extend([armL, armR])

    group = VGroup(*pieces)
    group.shift([x, 0, 0])
    return group, {"armL": armL, "armR": armR, "x": x, "arm_z": arm_z}


class StandoffScene(ThreeDScene):
    def construct(self):
        # Palette
        SAND = Color("#E3D7A4")
        BROWN = Color("#8B5A2B")
        DARK_BROWN = Color("#5C4033")
        WEED = Color("#C8A165")
        DUST = Color("#D0C28A")

        # Camera setup
        self.set_camera_orientation(phi=70 * DEGREES, theta=45 * DEGREES, zoom=1.05)

        # Ground plane as a parametric surface (desert)
        ground = ParametricSurface(
            lambda u, v: np.array([u, v, 0]),
            u_range=[-7, 7],
            v_range=[-4, 4],
            resolution=(2, 2),
        )
        ground.set_style(
            fill_color=SAND,
            fill_opacity=1.0,
            stroke_color=SAND,
            stroke_opacity=0.0,
        )

        # Very faint ground guider lines (wind-made creases) using Lines
        creases = VGroup(
            Line([-6.5, -1.2, 0], [6.5, -1.1, 0], color=DUST, stroke_opacity=0.25, stroke_width=2),
            Line([-6.5, 0.4, 0], [6.5, 0.5, 0], color=DUST, stroke_opacity=0.25, stroke_width=2),
        )

        self.play(FadeIn(ground), run_time=2)
        self.add(creases)

        # Build cowboys out of cylinders
        left_x, right_x = -3.5, 3.5
        left_cowboy, left_meta = build_cowboy(x=left_x, main_color=str(BROWN), hat_color=str(DARK_BROWN), arm_bias_deg=-35)
        right_cowboy, right_meta = build_cowboy(x=right_x, main_color=str(BROWN), hat_color=str(DARK_BROWN), arm_bias_deg=+35)

        # Reveal left cowboy piece by piece
        for piece in left_cowboy:
            piece.set_opacity(0)
        self.play(*[FadeIn(piece) for piece in left_cowboy[:3]], run_time=1.5)
        self.play(*[FadeIn(p) for p in left_cowboy[3:]], run_time=1.5)

        # Reveal right cowboy
        for piece in right_cowboy:
            piece.set_opacity(0)
        self.play(*[FadeIn(piece) for piece in right_cowboy[:3]], run_time=1.8)
        self.play(*[FadeIn(p) for p in right_cowboy[3:]], run_time=1.6)

        # Slow framing pan
        self.move_camera(theta=20 * DEGREES, phi=72 * DEGREES, run_time=6)

        # Tumbleweed (sphere)
        r_weed = 0.35
        weed = make_sphere(radius=r_weed, color=WEED, fill_opacity=0.25, stroke_opacity=0.6)
        weed.move_to(np.array([-6.0, 0.0, r_weed]))
        self.play(FadeIn(weed), run_time=1.2)

        # Wind lines drifting with the tumbleweed
        wind = VGroup(
            Line([-6.5, -0.3, 0], [-5.0, -0.3, 0], color=DUST, stroke_opacity=0.6, stroke_width=3),
            Line([-6.5, 0.1, 0], [-5.2, 0.1, 0], color=DUST, stroke_opacity=0.5, stroke_width=3),
            Line([-6.5, 0.5, 0], [-5.4, 0.5, 0], color=DUST, stroke_opacity=0.4, stroke_width=3),
        )
        self.add(wind)

        # Roll the sphere across with correct spin (angle = distance / radius)
        distance = 12.0
        total_angle = distance / r_weed
        self.play(
            weed.animate.shift(RIGHT * distance),
            Rotate(weed, angle=total_angle, axis=UP),
            *[w.animate.shift(RIGHT * distance) for w in wind],
            run_time=16,
            rate_func=linear,
        )

        # Low ground shot
        self.move_camera(phi=88 * DEGREES, zoom=1.3, run_time=6)

        # Draw moment: rotate arms toward center about shoulder pivots
        lpivL = np.array([left_meta["x"] - 0.45, 0, left_meta["arm_z"]])
        lpivR = np.array([left_meta["x"] + 0.45, 0, left_meta["arm_z"]])
        rpivL = np.array([right_meta["x"] - 0.45, 0, right_meta["arm_z"]])
        rpivR = np.array([right_meta["x"] + 0.45, 0, right_meta["arm_z"]])

        self.play(
            Rotate(left_meta["armL"], angle=+35 * DEGREES, axis=UP, about_point=lpivL),
            Rotate(left_meta["armR"], angle=+35 * DEGREES, axis=UP, about_point=lpivR),
            Rotate(right_meta["armL"], angle=-35 * DEGREES, axis=UP, about_point=rpivL),
            Rotate(right_meta["armR"], angle=-35 * DEGREES, axis=UP, about_point=rpivR),
            run_time=4,
        )

        # Tension: slow ambient orbit
        self.begin_ambient_camera_rotation(rate=0.05)
        self.wait(11)
        self.stop_ambient_camera_rotation()

        # Final wide pullback
        self.move_camera(phi=70 * DEGREES, theta=45 * DEGREES, zoom=1.0, run_time=6)

        # Fade out
        all_objs = VGroup(ground, creases, left_cowboy, right_cowboy, weed, wind)
        self.play(FadeOut(all_objs), run_time=3)
