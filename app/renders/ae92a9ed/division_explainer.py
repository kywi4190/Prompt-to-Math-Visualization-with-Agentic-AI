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

class DivisionExplainer(Scene):
    def construct(self):
        # Section 1: 12 dots grouped into 3 equal groups
        dots = VGroup()
        for _ in range(12):
            dots.add(Dot(radius=0.07, color=BLUE))
        dots.arrange(RIGHT, buff=0.25)
        dots.to_edge(UP).shift(DOWN*0.6)
        self.play(FadeIn(dots), run_time=1.2)

        # Create three rectangles around groups of 4 dots each (no SurroundingRectangle to keep primitives minimal)
        groups = [VGroup(*dots[i:i+4]) for i in range(0, 12, 4)]
        rects = VGroup()
        for g in groups:
            pad_w = 0.3
            pad_h = 0.3
            r = Rectangle(
                width=g.width + pad_w,
                height=g.height + pad_h,
                stroke_color=GREY,
                stroke_width=2
            )
            r.move_to(g.get_center())
            rects.add(r)
        self.play(*[Create(r) for r in rects], run_time=1.3)

        # Highlight each group sequentially
        self.play(groups[0].animate.set_color(YELLOW), run_time=0.7)
        self.play(groups[1].animate.set_color(ORANGE), run_time=0.7)
        self.play(groups[2].animate.set_color(GREEN), run_time=0.7)

        eq_div = MathTex(r"12", "\\div", "3", "=", "4").scale(1.0)
        eq_div.next_to(dots, DOWN, buff=0.6)
        self.play(Write(eq_div), run_time=1.0)
        self.wait(0.3)

        # Section 2: Number line from 0 to 12, robust mapping to frame
        fw = config.frame_width
        fh = config.frame_height
        left_x = -fw/2 + 1.0
        right_x = fw/2 - 1.0
        y_line = -fh/2 + 1.2
        def x_to_point(x, y=y_line):
            alpha = np.clip(x/12.0, 0.0, 1.0)
            return np.array([left_x + (right_x - left_x) * alpha, y, 0.0])

        base_line = Line(x_to_point(0), x_to_point(12), stroke_width=4)
        ticks = VGroup()
        labels = VGroup()
        for k in range(0, 13, 3):
            p = x_to_point(k)
            t = Line(p + np.array([0, -0.12, 0]), p + np.array([0, 0.12, 0]), stroke_color=GREY)
            ticks.add(t)
            lab = Text(str(k), font_size=28).move_to(p + np.array([0, -0.4, 0]))
            labels.add(lab)
        numberline_group = VGroup(base_line, ticks, labels)
        self.play(Create(base_line), run_time=0.6)
        self.play(*[Create(t) for t in ticks], *[FadeIn(l) for l in labels], run_time=0.8)

        t_tracker = ValueTracker(0.0)
        dyn_arrow = always_redraw(
            lambda: Arrow(
                start=x_to_point(t_tracker.get_value()) + np.array([0, -0.5, 0]),
                end=x_to_point(t_tracker.get_value()) + np.array([0, 0.1, 0]),
                color=GREY,
                buff=0,
                max_tip_length_to_length_ratio=0.2
            )
        )
        self.add(dyn_arrow)

        # Animate 4 equal jumps of 3 up to 12
        segs = VGroup()
        prev = 0
        count_labels = VGroup()
        for step_i, nxt in enumerate([3, 6, 9, 12], start=1):
            self.play(t_tracker.animate.set_value(nxt), run_time=1.0)
            seg = Line(x_to_point(prev), x_to_point(nxt), color=GREEN, stroke_width=6)
            segs.add(seg)
            mid = (x_to_point(prev) + x_to_point(nxt)) / 2
            count_lbl = Text(str(step_i), font_size=28, color=GREEN).move_to(mid + np.array([0, 0.35, 0]))
            count_labels.add(count_lbl)
            self.play(Create(seg), FadeIn(count_lbl, shift=UP*0.2), run_time=0.5)
            prev = nxt
        groups_text = Text("4 equal groups", font_size=34, color=GREEN).next_to(base_line, UP, buff=0.6)
        self.play(FadeIn(groups_text, shift=UP*0.2), run_time=0.7)
        self.wait(0.3)

        # Clean dynamic updaters before fading out the number line section
        dyn_arrow.clear_updaters()
        self.play(
            FadeOut(VGroup(dyn_arrow, segs, count_labels, groups_text, numberline_group)),
            FadeOut(VGroup(dots, rects)),
            run_time=1.0
        )

        # Section 3: Axes and scaling line y = 4x from (0,0) to (3,12)
        axes = Axes(
            x_range=[0, 3, 1], y_range=[0, 12, 3],
            x_length=5, y_length=3.5,
            tips=False,
            axis_config={"stroke_color": GREY}
        ).to_edge(LEFT, buff=1.0).shift(DOWN*0.3)
        x_label = Text("x", font_size=28).next_to(axes.x_axis, RIGHT, buff=0.2)
        y_label = Text("y", font_size=28).next_to(axes.y_axis, UP, buff=0.2)
        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label), run_time=1.2)

        line = Line(axes.c2p(0, 0), axes.c2p(3, 12), color=YELLOW)
        mover = Dot(color=YELLOW).move_to(axes.c2p(0, 0))
        self.play(Create(line), FadeIn(mover), run_time=1.0)

        self.play(mover.animate.move_to(axes.c2p(3, 12)), run_time=1.5)
        times4 = Text("×4", font_size=36, color=YELLOW).next_to(line, UP, buff=0.2)
        self.play(FadeIn(times4, shift=UP*0.2), run_time=0.6)
        self.wait(0.2)

        # Equation transformation: 12 ÷ 3 = 4  ->  3x = 12  ->  x = 4
        eq_div_center = MathTex(r"12", "\\div", "3", "=", "4").scale(1.0).to_edge(UP)
        self.play(Transform(eq_div, eq_div_center), run_time=0.7)

        eq_mul = MathTex(r"3", "x", "=", "12").scale(1.0).to_edge(UP)
        self.play(
            TransformMatchingTex(eq_div, eq_mul, key_map={"12": "12", "=": "="}),
            run_time=1.1
        )
        eq_sol = MathTex(r"x", "=", "4").scale(1.0).to_edge(UP)
        self.play(
            TransformMatchingTex(eq_mul, eq_sol, key_map={"=": "="}),
            run_time=1.0
        )

        self.wait(0.5)
