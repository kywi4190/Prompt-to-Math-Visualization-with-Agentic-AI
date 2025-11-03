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

# Determinant = signed area of the parallelogram spanned by u and v
class DeterminantAreaScene(Scene):
    def construct(self):
        # Grid
        plane = NumberPlane(
            x_range=[-6, 6, 1],
            y_range=[-3.5, 3.5, 1],
            background_line_style={
                "stroke_color": GREY_B,
                "stroke_opacity": 0.35,
                "stroke_width": 1,
            },
        )
        self.play(FadeIn(plane, shift=UP, run_time=0.8))

        # Base vector u (fixed)
        u_vec = np.array([2.4, 1.0, 0.0])

        # v will move through a path that crosses colinearity twice (sign flips)
        vA = np.array([0.4, 2.6, 0.0])                       # positive area
        vB = 1.20 * u_vec                                     # colinear, det ~ 0 (positive direction)
        vC = np.array([-1.8, 2.1, 0.0])                      # positive area again
        vD = -1.00 * u_vec                                    # colinear, det ~ 0 (opposite direction)

        s = ValueTracker(0.0)

        def smooth01(t):
            # Smoothstep easing in [0,1]
            t = np.clip(t, 0.0, 1.0)
            return t * t * (3 - 2 * t)

        def v_of_s(val):
            # Piecewise linear with per-segment easing
            if val <= 0:
                return vA.copy()
            if val >= 3:
                return vD.copy()
            i = int(np.floor(val))
            t = smooth01(val - i)
            pts = [vA, vB, vC, vD]
            a = pts[i]
            b = pts[i + 1]
            return (1 - t) * a + t * b

        def get_v_vec():
            return v_of_s(s.get_value())

        # Determinant helper
        def det_uv(u, v):
            return float(u[0] * v[1] - u[1] * v[0])

        # Map determinant sign smoothly to color blend (RED_E for negative to BLUE_E for positive)
        def sign_blend_alpha(det, eps=0.06):
            # Produces alpha in [0,1] with soft transition around zero
            return 0.5 * (np.tanh(det / eps) + 1.0)

        # Arrows for u and v
        def make_u_arrow():
            arr = Arrow([0, 0, 0], u_vec, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.14)
            arr.set_color(TEAL_C)
            arr.set_z_index(2)
            return arr

        def make_v_arrow():
            v = get_v_vec()
            arr = Arrow([0, 0, 0], v, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.14)
            arr.set_color(YELLOW_E)
            arr.set_z_index(2)
            return arr

        u_arrow = always_redraw(make_u_arrow)
        v_arrow = always_redraw(make_v_arrow)

        # Tip labels: single Text objects with position-only updaters (avoid re-creating per frame)
        u_label = Text("u", font_size=34).set_color(TEAL_C)
        u_label.set_z_index(3)
        u_label.add_updater(lambda m: m.move_to(u_vec + np.array([0.25, 0.25, 0])))

        v_label = Text("v", font_size=34).set_color(YELLOW_E)
        v_label.set_z_index(3)
        v_label.add_updater(lambda m: m.move_to(get_v_vec() + np.array([0.25, 0.25, 0])))

        # Parallelogram polygon with dynamic color by signed area
        def make_para():
            u = u_vec
            v = get_v_vec()
            poly = Polygon(
                np.array([0, 0, 0]),
                u,
                u + v,
                v,
            )
            d = det_uv(u, v)
            alpha = sign_blend_alpha(d)
            color = interpolate_color(Color(Color(RED_E)), Color(Color(BLUE_E)), alpha)
            poly.set_fill(color, opacity=0.45)
            poly.set_stroke(GREY_E, width=2, opacity=0.9)
            poly.set_z_index(1)
            return poly

        para = always_redraw(make_para)

        # Show vectors and parallelogram
        self.play(Create(u_arrow, run_time=1.0))
        self.play(Create(v_arrow, run_time=1.0))
        self.add(u_label, v_label)
        self.play(FadeIn(para, run_time=0.8))

        # Determinant readout in the corner
        det_title = Text("det =", font_size=36)
        det_title.to_corner(UR)

        plus_tex = Text("+", font_size=36).next_to(det_title, RIGHT, buff=0.2)
        plus_tex.set_color(BLUE_C)
        minus_tex = Text("−", font_size=36).next_to(det_title, RIGHT, buff=0.2)
        minus_tex.set_color(RED_C)

        # Start signs invisible; an updater will control opacity
        plus_tex.set_opacity(0.0)
        minus_tex.set_opacity(0.0)

        # Numeric magnitude of determinant; placed next to whichever sign is active
        det_value = DecimalNumber(0.00, num_decimal_places=2, include_sign=False, font_size=36)
        det_value.set_color(WHITE)
        det_value.next_to(plus_tex, RIGHT, buff=0.15)

        # Updaters for signs and value
        def update_signs(m, which):
            # which: +1 for plus_tex, -1 for minus_tex
            u = u_vec
            v = get_v_vec()
            d = det_uv(u, v)
            a = sign_blend_alpha(d)  # in [0,1]
            if which == +1:
                m.set_opacity(a)
            else:
                m.set_opacity(1 - a)

        plus_tex.add_updater(lambda m: update_signs(m, +1))
        minus_tex.add_updater(lambda m: update_signs(m, -1))

        def update_det_value(m):
            u = u_vec
            v = get_v_vec()
            d = det_uv(u, v)
            m.set_value(abs(d))
            a = sign_blend_alpha(d)
            # Color consistent with fill blend
            m.set_color(interpolate_color(Color(Color(RED_E)), Color(Color(BLUE_E)), a))
            # Position next to the currently visible sign (threshold at 0.5)
            target = plus_tex if a >= 0.5 else minus_tex
            m.next_to(target, RIGHT, buff=0.15)

        det_value.add_updater(update_det_value)

        # Bring in the readout (avoid fading signs individually to prevent updater conflicts)
        self.play(Write(det_title, run_time=0.8))
        self.add(plus_tex, minus_tex)
        self.play(FadeIn(det_value, shift=DOWN, run_time=0.6))

        # Animate v across segments to show det > 0, ~0, > 0, ~0 and < 0
        self.play(s.animate.set_value(1.0), run_time=7.0, rate_func=smooth)
        self.play(s.animate.set_value(2.0), run_time=7.0, rate_func=smooth)
        self.play(s.animate.set_value(3.0), run_time=7.0, rate_func=smooth)

        self.wait(0.8)

        # Clean up updaters (optional for neatness in longer scripts)
        for mob in [u_label, v_label, plus_tex, minus_tex, det_value]:
            mob.clear_updaters()
