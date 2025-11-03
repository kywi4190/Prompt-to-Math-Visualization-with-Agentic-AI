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

class VectorAdditionFixScene(Scene):
    def construct(self):
        # NUMBER LINE SECTION -------------------------------------------------
        axes = Axes(
            x_range=[-4, 6, 1],
            y_range=[-1, 1, 1],  # widened so small vertical offsets remain inside range
            x_length=9,
            y_length=1.2,
            tips=False,
        )
        # Hide y-axis; keep x-axis ticks and numbers
        axes.get_y_axis().set_stroke(width=0)
        axes.get_x_axis().add_numbers(
            [-4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]
        )
        axes.to_edge(UP, buff=0.8)

        self.play(Create(axes), run_time=1.2)

        a_val = 2.0
        b_tracker = ValueTracker(0.01)  # start slightly away from zero to avoid zero-length arrow

        # Fixed a arrow and label
        a_start = axes.c2p(0, 0)
        a_end = axes.c2p(a_val, 0)
        arrow_a = Arrow(a_start, a_end, buff=0, color=BLUE, max_tip_length_to_length_ratio=0.15)
        label_a = Text("a", font_size=32, color=BLUE)
        label_a.move_to((a_start + a_end) / 2 + 0.3 * UP)

        self.play(Create(arrow_a), FadeIn(label_a, shift=0.1 * UP), run_time=0.8)

        # Moving b arrow, dot, and sum arrow using always_redraw
        def make_arrow_b():
            return Arrow(
                axes.c2p(a_val, 0),
                axes.c2p(a_val + b_tracker.get_value(), 0),
                buff=0,
                color=GREEN,
                max_tip_length_to_length_ratio=0.15,
            )

        def make_dot_move():
            d = Dot(color=YELLOW, radius=0.06)
            d.set_z_index(10)
            return d.move_to(axes.c2p(a_val + b_tracker.get_value(), 0))

        def make_arrow_sum():
            return Arrow(
                axes.c2p(0, 0),
                axes.c2p(a_val + b_tracker.get_value(), 0),
                buff=0,
                color=Color("#ffaa00"),
                stroke_opacity=0.6,
                max_tip_length_to_length_ratio=0.15,
            )

        def make_b_label():
            center = axes.c2p(a_val + 0.5 * b_tracker.get_value(), 0)
            return Text("b", font_size=32, color=GREEN).move_to(center + 0.3 * UP)

        def make_sum_label():
            center = axes.c2p(0.5 * (a_val + b_tracker.get_value()), 0)
            return Text("a+b", font_size=30, color=Color("#ffaa00")).move_to(center + 0.45 * UP)

        arrow_b = always_redraw(make_arrow_b)
        dot_move = always_redraw(make_dot_move)
        arrow_sum = always_redraw(make_arrow_sum)
        b_label = always_redraw(make_b_label)
        sum_label = always_redraw(make_sum_label)

        self.play(
            FadeIn(arrow_b),
            FadeIn(dot_move),
            FadeIn(arrow_sum),
            FadeIn(b_label),
            FadeIn(sum_label),
            run_time=0.8,
        )

        # Animate b growing; the dot and sum arrow track a + b
        self.play(b_tracker.animate.set_value(3.0), run_time=8.0, rate_func=smooth)
        self.wait(0.4)

        # Group for coordinated fade (avoid double-parenting of axis numbers)
        nline_group = VGroup(
            axes,
            arrow_a,
            label_a,
            arrow_b,
            b_label,
            dot_move,
            arrow_sum,
            sum_label,
        )
        self.play(FadeOut(nline_group), run_time=1.0)
        # Explicitly clear updaters/remove always_redraw objects to avoid lingering
        for m in (arrow_b, b_label, dot_move, arrow_sum, sum_label):
            m.clear_updaters()
            self.remove(m)

        # PLANE SECTION -------------------------------------------------------
        plane = NumberPlane(
            x_range=[-4, 6, 1], y_range=[-3, 3, 1],
            background_line_style={"stroke_opacity": 0.4, "stroke_width": 1}
        )
        plane.shift(DOWN * 0.3)
        self.play(Create(plane), run_time=1.2)

        # Define vectors u and v (in coordinate space), then use plane.c2p consistently
        ux, uy = 2.0, 1.0
        vx, vy = 1.5, -0.5
        origin = plane.c2p(0, 0)
        u_tip = plane.c2p(ux, uy)
        v_tip = plane.c2p(vx, vy)
        u_vec = u_tip - origin
        v_vec = v_tip - origin

        u_arrow = Arrow(origin, u_tip, buff=0, color=BLUE, max_tip_length_to_length_ratio=0.15)
        v_arrow = Arrow(origin, v_tip, buff=0, color=GREEN, max_tip_length_to_length_ratio=0.15)

        u_label = Text("u", font_size=30, color=BLUE).move_to(u_tip + 0.25 * UP)
        v_label = Text("v", font_size=30, color=GREEN).move_to(v_tip + 0.25 * UP)

        self.play(Create(u_arrow), Create(v_arrow), FadeIn(u_label), FadeIn(v_label), run_time=1.0)

        # Tip-to-tail clones: initialize in place before adding to avoid pop-in at origin
        v_clone = v_arrow.copy().shift(u_vec)
        u_clone = u_arrow.copy().shift(v_vec)
        self.add(v_clone, u_clone)  # Add then reveal
        self.play(
            FadeIn(v_clone),
            FadeIn(u_clone),
            run_time=0.8,
        )

        # Parallelogram edges
        uv_tip = plane.c2p(ux + vx, uy + vy)
        edge1 = Line(u_tip, uv_tip, color=GREY_B, stroke_opacity=0.7)
        edge2 = Line(v_tip, uv_tip, color=GREY_B, stroke_opacity=0.7)
        self.play(Create(edge1), Create(edge2), run_time=1.2)

        # Resultant u + v as the diagonal from origin
        sum_arrow2 = Arrow(origin, uv_tip, buff=0, color=YELLOW, max_tip_length_to_length_ratio=0.15)
        sum_label2 = Text("u+v", font_size=32, color=YELLOW).move_to(uv_tip + 0.3 * UP)
        self.play(Create(sum_arrow2), run_time=1.0)
        self.play(FadeIn(sum_label2, shift=0.1 * UP), run_time=0.4)

        # Gentle emphasis
        self.play(sum_arrow2.animate.set_stroke(width=6), run_time=0.4)
        self.play(sum_arrow2.animate.set_stroke(width=4), run_time=0.4)
        self.wait(1.0)
