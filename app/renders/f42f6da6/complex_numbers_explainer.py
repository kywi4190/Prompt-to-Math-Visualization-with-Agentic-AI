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

class ComplexNumbersScene(Scene):
    def construct(self):
        # Number plane
        plane = NumberPlane(
            x_range=[-4, 4, 1],
            y_range=[-3, 3, 1],
            background_line_style={
                "stroke_opacity": 0.3,
                "stroke_width": 1,
            },
        )
        plane.set_z_index(0)
        self.play(Create(plane), run_time=1.2)

        # Unit circle and phasor e^{it}
        unit_circle = Circle(radius=1.0, color=BLUE).set_stroke(width=3, opacity=0.5)
        self.play(Create(unit_circle), run_time=1.0)

        t = ValueTracker(0.0)

        def tip():
            return np.array([math.cos(t.get_value()), math.sin(t.get_value()), 0.0])

        phasor_arrow = always_redraw(
            lambda: Arrow(start=np.array([0.0, 0.0, 0.0]), end=tip(), buff=0, color=YELLOW, stroke_width=6)
        )
        phasor_dot = always_redraw(lambda: Dot(radius=0.06, color=YELLOW).move_to(tip()))
        eit = always_redraw(lambda: MathTex(r"e^{it}").scale(0.7).next_to(phasor_dot, UR, buff=0.1))

        # Projections and labels that truly track the phasor tip
        x_drop = always_redraw(
            lambda: Line(
                np.array([tip()[0], 0.0, 0.0]),
                np.array([tip()[0], tip()[1], 0.0]),
                color=GREEN,
            ).set_stroke(width=3, opacity=0.7)
        )
        y_drop = always_redraw(
            lambda: Line(
                np.array([0.0, tip()[1], 0.0]),
                np.array([tip()[0], tip()[1], 0.0]),
                color=RED,
            ).set_stroke(width=3, opacity=0.7)
        )
        cos_lbl = always_redraw(
            lambda: MathTex(r"\cos t").scale(0.6).next_to(
                np.array([tip()[0], 0.0, 0.0]), DOWN, buff=0.1
            )
        )
        sin_lbl = always_redraw(
            lambda: MathTex(r"\sin t").scale(0.6).next_to(
                np.array([0.0, tip()[1], 0.0]), LEFT, buff=0.1
            )
        )

        self.add(phasor_arrow, phasor_dot)
        self.play(Write(eit), FadeIn(x_drop), FadeIn(y_drop), Write(cos_lbl), Write(sin_lbl), run_time=2.8)
        self.play(t.animate.set_value(2 * math.pi), run_time=9.0, rate_func=linear)
        self.play(FadeOut(eit, cos_lbl, sin_lbl, x_drop, y_drop, unit_circle), run_time=1.0)

        # Multiply by i: 90-degree rotation
        w = np.array([1.2, 0.6, 0.0])
        w_arrow = Arrow(np.array([0.0, 0.0, 0.0]), w, buff=0, color=WHITE, stroke_width=6)
        line_before = Line(np.array([0.0, 0.0, 0.0]), w, color=WHITE, stroke_width=6)
        self.play(Create(w_arrow), Create(line_before), run_time=1.6)

        # Target after rotation by i (matrix for 90-degree rotation)
        R = np.array([[0.0, -1.0], [1.0, 0.0]])
        def apply_R(v3):
            v2 = np.array([v3[0], v3[1]])
            r2 = R @ v2
            return np.array([r2[0], r2[1], 0.0])
        line_after_rot = line_before.copy()
        line_after_rot.set_color(YELLOW)
        line_after_rot.set_stroke(width=6)
        # Precompute rotated target geometry for TransformFromCopy
        line_after_rot_target = Line(
            np.array([0.0, 0.0, 0.0]), apply_R(w), color=YELLOW, stroke_width=6
        )
        self.play(
            TransformFromCopy(line_before, line_after_rot_target),
            w_arrow.animate.apply_matrix(R),
            run_time=3.5,
        )
        # Replace temp with the on-screen rotated copy for angle measurement consistency
        self.remove(line_after_rot)
        self.add(line_after_rot_target)
        ang_i = Angle(line_before, line_after_rot_target, radius=0.55, color=MAROON)
        self.play(Create(ang_i), run_time=1.4)
        self.wait(1.0)
        self.play(FadeOut(ang_i), run_time=0.7)

        # Conformal mapping near a point for f(z) = z^2
        # Fix a nonzero point p and two small rays from p
        p = np.array([1.2, 0.6, 0.0])
        dot_p = Dot(p, color=WHITE)
        phi1 = np.deg2rad(20.0)
        delta = ValueTracker(np.deg2rad(60.0))
        eps = 0.8

        def d1_vec():
            return np.array([math.cos(phi1), math.sin(phi1), 0.0])
        def d2_vec():
            ang = phi1 + delta.get_value()
            return np.array([math.cos(ang), math.sin(ang), 0.0])

        ray1 = always_redraw(
            lambda: Line(p, p + eps * d1_vec(), color=ORANGE, stroke_width=5)
        )
        ray2 = always_redraw(
            lambda: Line(p, p + eps * d2_vec(), color=PURPLE, stroke_width=5)
        )
        ang0 = always_redraw(
            lambda: Angle(ray1, ray2, radius=0.35, color=YELLOW)
        )

        self.play(FadeOut(phasor_arrow, phasor_dot, w_arrow, line_before, line_after_rot_target), run_time=0.7)
        self.play(FadeIn(dot_p), Create(ray1), Create(ray2), run_time=2.5)
        self.play(Create(ang0), run_time=1.2)

        # Mapping under f(z)=z^2: exact curve images, and tangent-based angle at q=f(p)
        tex_f = MathTex(r"f(z)=z^2").scale(0.8).move_to(np.array([3.3, 2.3, 0.0]))
        self.play(Write(tex_f), run_time=1.2)

        def z2_map(x, y):
            return np.array([x * x - y * y, 2 * x * y, 0.0])

        q = z2_map(p[0], p[1])
        dot_q = Dot(q, color=WHITE)

        def curve_from(p_xy, d_xy, color):
            px, py = p_xy[0], p_xy[1]
            dx, dy = d_xy[0], d_xy[1]
            return ParametricFunction(
                lambda tt: np.array([
                    (px + tt * dx) ** 2 - (py + tt * dy) ** 2,
                    2 * (px + tt * dx) * (py + tt * dy),
                    0.0,
                ]),
                t_range=[0.0, eps, eps / 40.0],
                color=color,
                stroke_width=5,
            )

        curve1 = always_redraw(lambda: curve_from(p, d1_vec(), ORANGE))
        curve2 = always_redraw(lambda: curve_from(p, d2_vec(), PURPLE))

        def J_z2(x, y):
            # Jacobian of z^2 at (x,y): [[2x, -2y], [2y, 2x]]
            return np.array([[2 * x, -2 * y], [2 * y, 2 * x]])

        def tangent_line_at_q(dir_vec3, color):
            J = J_z2(p[0], p[1])
            v2 = np.array([dir_vec3[0], dir_vec3[1]])
            tp = J @ v2
            n = np.linalg.norm(tp)
            if n < 1e-8:
                tp_u = np.array([1.0, 0.0])
            else:
                tp_u = tp / n
            s = 0.55
            end = np.array([q[0] + s * tp_u[0], q[1] + s * tp_u[1], 0.0])
            return Line(q, end, color=color, stroke_width=5)

        tan1 = always_redraw(lambda: tangent_line_at_q(d1_vec(), ORANGE))
        tan2 = always_redraw(lambda: tangent_line_at_q(d2_vec(), PURPLE))
        ang1 = always_redraw(lambda: Angle(tan1, tan2, radius=0.45, color=TEAL))

        self.play(Create(curve1), Create(curve2), FadeIn(dot_q), run_time=3.5)
        self.play(Create(tan1), Create(tan2), run_time=1.5)
        self.play(Create(ang1), run_time=1.2)

        # Vary the second ray to show angle preservation dynamically
        self.play(delta.animate.set_value(np.deg2rad(100.0)), run_time=14.0, rate_func=linear)
        self.wait(2.0)

        # Clean end
        everything = VGroup(
            plane, dot_p, ray1, ray2, ang0, tex_f, curve1, curve2, dot_q, tan1, tan2, ang1
        )
        self.play(FadeOut(everything), run_time=2.0)
        self.wait(1.0)
