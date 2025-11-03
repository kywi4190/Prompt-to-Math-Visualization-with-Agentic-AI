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

class VectorAdditionExplainer(Scene):
    def construct(self):
        # 1) Number line analogy: 2 + 3 = 5
        axes = Axes(
            x_range=[0, 6, 1],
            y_range=[0, 1, 1],
            tips=False,
        )
        axes.set_stroke(width=2)
        axes.move_to([0, 2.6, 0])  # 3D-safe placement

        eqn = MathTex(r"2", "+", "3", "=", "5").scale(0.9)
        eqn.next_to(axes, UP, buff=0.3)

        # Arrows for steps 2 and 3; second is offset up proportionally to axis scale
        offset = np.array([0, 0.35 * axes.y_axis.get_unit_size(), 0])
        step_2 = Arrow(
            axes.c2p(0, 0), axes.c2p(2, 0), color=BLUE, buff=0
        )
        step_3 = Arrow(
            axes.c2p(2, 0) + offset, axes.c2p(5, 0) + offset, color=GREEN, buff=0
        )
        dot_5 = Dot(color=YELLOW).move_to(axes.c2p(5, 0))
        dot_5.set_z_index(3)

        self.play(Create(axes), run_time=1.5)
        self.play(Write(eqn), run_time=0.9)
        self.play(Create(step_2), run_time=1.2)
        self.play(Create(step_3), FadeIn(dot_5, scale=0.75), run_time=1.2)
        self.wait(0.6)
        self.play(
            FadeOut(VGroup(eqn, step_2, step_3, dot_5), shift=UP * 0.3),
            FadeOut(axes),
            run_time=1.0,
        )

        # 2) Vector addition on the plane
        plane = NumberPlane(
            x_range=[-4, 4, 1], y_range=[-3, 3, 1],
            background_line_style={"stroke_opacity": 0.3, "stroke_width": 1},
        )
        self.play(Create(plane), run_time=1.2)

        # Define vectors a, b, c in coordinate space
        a = np.array([2.5, 1.0])
        b = np.array([1.2, 1.8])
        c = np.array([-1.2, 1.0])

        # Helper to build arrows in plane coordinates (buff=0 for mathematical vectors)
        def vec_arrow(start_xy, end_xy, color=WHITE):
            return Arrow(plane.c2p(*start_xy), plane.c2p(*end_xy), buff=0, color=color)

        O = np.array([0.0, 0.0])

        arrow_a = vec_arrow(O, a, color=BLUE_C)
        arrow_b = vec_arrow(O, b, color=GREEN_C)

        self.play(Create(arrow_a), Create(arrow_b), run_time=1.5)

        # Head-to-tail: shift b to the head of a
        arrow_b_shifted = vec_arrow(a, a + b, color=GREEN_C)
        self.play(ReplacementTransform(arrow_b.copy(), arrow_b_shifted), run_time=1.2)

        # Sum arrow a + b from the origin
        sum_ab = vec_arrow(O, a + b, color=YELLOW)
        sum_ab.set_stroke(width=6)
        self.play(Create(sum_ab), run_time=1.2)

        # Moving dot: trace "do a, then do b"
        t = ValueTracker(0.0)  # 0 -> 1 along a, 1 -> 2 along b from head of a
        def path_pos():
            val = t.get_value()
            if val <= 1.0:
                pos_xy = val * a
            else:
                s = val - 1.0
                pos_xy = a + s * b
            return plane.c2p(*pos_xy)

        tracer = always_redraw(
            lambda: Dot(radius=0.06, color=YELLOW).move_to(path_pos()).set_z_index(4)
        )
        self.play(FadeIn(tracer, scale=0.75), run_time=0.6)
        self.play(t.animate.set_value(2.0), run_time=6.0, rate_func=rate_functions.smooth)

        # Commutativity: place a at the head of b as well
        arrow_a_shifted = vec_arrow(b, a + b, color=BLUE_C)
        self.play(ReplacementTransform(arrow_a.copy(), arrow_a_shifted), run_time=1.2)

        # Labels (MathTex for portability)
        label_a = MathTex(r"a").scale(0.8).move_to(arrow_a.get_end() + 0.25 * RIGHT + 0.15 * UP)
        label_b = MathTex(r"b").scale(0.8).move_to(arrow_b.get_end() + 0.25 * RIGHT + 0.15 * UP)
        label_ab = MathTex(r"a{+}b").scale(0.8).move_to(sum_ab.get_end() + 0.3 * RIGHT)
        label_a.set_z_index(3)
        label_b.set_z_index(3)
        label_ab.set_z_index(3)
        self.play(Write(label_a), Write(label_b), Write(label_ab), run_time=0.9)

        # Add a third vector c
        arrow_c = vec_arrow(O, c, color=MAROON_C)
        self.play(Create(arrow_c), run_time=1.0)

        # Place c at the head of (a+b)
        arrow_c_from_ab = vec_arrow(a + b, a + b + c, color=MAROON_C)
        self.play(ReplacementTransform(arrow_c.copy(), arrow_c_from_ab), run_time=1.0)

        # Final sum arrow a + b + c
        sum_total = vec_arrow(O, a + b + c, color=ORANGE)
        sum_total.set_stroke(width=6)
        label_total = MathTex(r"a{+}b{+}c").scale(0.8).move_to(sum_total.get_end() + 0.3 * RIGHT)
        label_total.set_z_index(3)
        self.play(Create(sum_total), Write(label_total), run_time=1.2)

        # Clean up the tracer safely (clear updaters before fading out)
        tracer.clear_updaters()
        self.play(FadeOut(tracer), run_time=0.8)
        self.wait(1.2)
