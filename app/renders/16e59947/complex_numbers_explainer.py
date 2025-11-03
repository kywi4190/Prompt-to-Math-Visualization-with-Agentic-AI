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

class ComplexNumbersExplainer(ThreeDScene):
    def construct(self):
        # Plane and unit circle hook
        plane = NumberPlane(
            x_range=[-5, 5, 1], y_range=[-3, 3, 1],
            background_line_style={"stroke_opacity": 0.3, "stroke_width": 1}
        )
        unit_circle = Circle(radius=2.0, color=GREY_B, stroke_opacity=0.6)
        self.play(Create(plane), Create(unit_circle), run_time=1.2)

        # Hook: a small triangle rotating by 90 degrees (multiply by i)
        tri = Polygon(
            np.array([1.4, 0.2, 0.0]),
            np.array([2.1, 0.2, 0.0]),
            np.array([1.4, 0.9, 0.0]),
            color=BLUE_D,
            stroke_width=2,
            fill_color=BLUE_E,
            fill_opacity=0.6,
        )
        xi_label = Text("× i", color=WHITE).scale(0.6)
        xi_label.add_background_rectangle(buff=0.08, opacity=0.8)
        xi_label.move_to(np.array([3.6, 1.8, 0]))
        self.add(tri)
        self.play(FadeIn(xi_label, shift=UP*0.2), run_time=0.6)
        self.play(Rotate(tri, angle=PI/2, about_point=ORIGIN), run_time=2.2)
        self.wait(0.4)

        # i^2 = -1 with a rotating arrow
        one_arrow = Arrow(np.array([0, 0, 0]), np.array([2.0, 0, 0]), buff=0.0, color=YELLOW, tip_length=0.15)
        self.play(Create(one_arrow), run_time=0.8)
        self.play(Rotate(one_arrow, angle=PI/2, about_point=ORIGIN), run_time=1.6)
        self.play(Rotate(one_arrow, angle=PI/2, about_point=ORIGIN), run_time=1.6)
        i2_text = MathTex(r"i^2 = -1").scale(0.9)
        i2_text.add_background_rectangle(buff=0.08, opacity=0.85)
        i2_text.move_to(np.array([3.8, -0.4, 0]))
        self.play(Write(i2_text), run_time=0.8)
        self.wait(0.4)

        # Clean hook artifacts
        self.play(FadeOut(tri), FadeOut(one_arrow), FadeOut(xi_label), run_time=0.8)

        # Trackers for z and w
        r1 = ValueTracker(1.5)
        th1 = ValueTracker(20 * DEGREES)
        r2 = ValueTracker(1.2)
        th2 = ValueTracker(60 * DEGREES)

        def z_tip():
            return np.array([
                r1.get_value() * math.cos(th1.get_value()),
                r1.get_value() * math.sin(th1.get_value()),
                0.0,
            ])

        def w_tip():
            return np.array([
                r2.get_value() * math.cos(th2.get_value()),
                r2.get_value() * math.sin(th2.get_value()),
                0.0,
            ])

        def p_tip():
            rp = r1.get_value() * r2.get_value()
            ang = th1.get_value() + th2.get_value()
            return np.array([
                rp * math.cos(ang),
                rp * math.sin(ang),
                0.0,
            ])

        # Dynamic arrows for z, w, and product p = z*w
        z_arrow = always_redraw(lambda: Arrow(np.array([0, 0, 0]), z_tip(), buff=0.0, color=BLUE, tip_length=0.15))
        w_arrow = always_redraw(lambda: Arrow(np.array([0, 0, 0]), w_tip(), buff=0.0, color=GREEN, tip_length=0.15))
        p_arrow = always_redraw(lambda: Arrow(np.array([0, 0, 0]), p_tip(), buff=0.0, color=YELLOW, tip_length=0.15))

        z_label = always_redraw(lambda: MathTex(r"z").scale(0.8).next_to(z_arrow.get_end(), UR, buff=0.1))
        w_label = always_redraw(lambda: MathTex(r"w").scale(0.8).next_to(w_arrow.get_end(), UR, buff=0.1))
        p_label = always_redraw(lambda: MathTex(r"zw").scale(0.8).next_to(p_arrow.get_end(), UR, buff=0.1))

        self.play(Create(z_arrow), Create(w_arrow), run_time=1.2)
        self.play(Create(p_arrow), FadeIn(z_label), FadeIn(w_label), FadeIn(p_label), run_time=1.0)

        # Overlay formula (fixed in frame) — corrected LaTeX string (raw, single backslashes)
        w_formula = MathTex(r"(re^{i\theta})(se^{i\phi})=rs\,e^{i(\theta+\phi)}").scale(0.8)
        w_formula.add_background_rectangle(buff=0.08, opacity=0.85)
        w_formula.to_corner(UL)
        w_formula.set_z_index(10)

        mag_eq = MathTex(r"|zw|=|z|\,|w|").scale(0.9)
        mag_eq.add_background_rectangle(buff=0.08, opacity=0.85)
        mag_eq.to_corner(DL)
        mag_eq.set_z_index(10)

        self.add_fixed_in_frame_mobjects(w_formula)
        self.play(FadeIn(w_formula), run_time=0.6)

        # Angle addition: rotate z, then w
        self.play(th1.animate.set_value(th1.get_value() + 60 * DEGREES), run_time=3.0)
        self.play(th2.animate.set_value(th2.get_value() - 40 * DEGREES), run_time=3.0)

        # Magnitude product: scale r1 and r2
        self.add_fixed_in_frame_mobjects(mag_eq)
        self.play(FadeIn(mag_eq), run_time=0.6)
        self.play(r1.animate.set_value(2.0), run_time=2.4)
        self.play(r2.animate.set_value(1.6), run_time=2.4)
        self.wait(0.4)

        # Transition to 3D view and cone visualization
        cone_title = Text("Magnitude as height").scale(0.7)
        cone_title.add_background_rectangle(buff=0.08, opacity=0.85)
        cone_title.to_corner(UR)
        cone_title.set_z_index(10)
        self.add_fixed_in_frame_mobjects(cone_title)

        self.play(FadeOut(i2_text), run_time=0.4)
        self.play(self.move_camera, {"phi": 70 * DEGREES, "theta": 45 * DEGREES, "zoom": 1.0}, run_time=2.0)
        self.play(FadeIn(cone_title), run_time=0.6)

        cone_surface = ParametricSurface(
            lambda u, v: np.array([u * math.cos(v), u * math.sin(v), 0.5 * u]),
            u_range=[0.0, 3.2], v_range=[0, TAU],
            checkerboard_colors=[PURPLE_E, PURPLE_C],
            fill_opacity=0.35, stroke_color=PURPLE, stroke_opacity=0.25
        )
        self.play(Create(cone_surface), run_time=1.2)

        # Lift the product tip up to the cone height
        def p_lift_top():
            tip = p_tip()
            rp = r1.get_value() * r2.get_value()
            return np.array([tip[0], tip[1], 0.5 * rp])

        p_lift = always_redraw(lambda: Line(p_tip(), p_lift_top(), color=YELLOW, stroke_width=3))
        p_top_dot = always_redraw(lambda: Dot(p_lift_top(), color=YELLOW).scale(0.8))

        self.play(Create(p_lift), FadeIn(p_top_dot), run_time=0.8)

        # Vary |w| to show height follows |zw|
        self.play(r2.animate.set_value(2.2), run_time=2.6)
        self.play(r2.animate.set_value(1.0), run_time=2.6)
        self.play(r2.animate.set_value(1.6), run_time=2.0)

        # Small camera motion for parallax
        self.play(self.move_camera, {"phi": 65 * DEGREES, "theta": 60 * DEGREES}, run_time=1.6)
        self.play(self.move_camera, {"phi": 72 * DEGREES, "theta": 35 * DEGREES}, run_time=1.6)

        # Summary overlay
        summary = Text("Multiply magnitudes, add angles").scale(0.8)
        summary.add_background_rectangle(buff=0.08, opacity=0.9)
        summary.move_to(np.array([0, 3.2, 0]))
        summary.set_z_index(10)
        self.add_fixed_in_frame_mobjects(summary)
        self.play(FadeIn(summary, shift=UP*0.2), run_time=0.8)
        self.wait(1.2)

        # Cleanup/fade out
        self.play(*[FadeOut(m) for m in [p_lift, p_top_dot, cone_surface, z_arrow, w_arrow, p_arrow, z_label, w_label, p_label, unit_circle]], run_time=1.4)
        self.play(FadeOut(plane), FadeOut(w_formula), FadeOut(mag_eq), FadeOut(cone_title), FadeOut(summary), run_time=1.0)
        self.wait(0.2)
