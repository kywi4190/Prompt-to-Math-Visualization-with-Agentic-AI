from manim import *


class DivisionScene(Scene):
    def construct(self):
        # Helper to build step arrows of length b filling up to a on the x-axis
        def make_step_arrows(a_len, b_step, ax, color=BLUE, y=0.0):
            arrows = VGroup()
            x = 0.0
            # Build arrows from 0 up to the greatest multiple not exceeding a_len
            while x + b_step <= a_len + 1e-6:
                start = ax.c2p(x, y)
                end = ax.c2p(x + b_step, y)
                arr = Arrow(start, end, buff=0.0, stroke_width=6, max_tip_length_to_length_ratio=0.08)
                arr.set_color(color)
                arrows.add(arr)
                x += b_step
            return arrows

        # Axis as a measuring tape along the bottom
        axes = Axes(
            x_range=[0, 13, 1],
            y_range=[0, 1, 1],
            x_length=10,
            y_length=1.8,
            tips=False,
        )
        axes.to_edge(DOWN)
        self.play(FadeIn(axes), run_time=0.6)

        # Measuring 12 with steps of 3
        seg12 = Line(axes.c2p(0, 0), axes.c2p(12, 0)).set_stroke(YELLOW, width=8)
        self.play(Create(seg12), run_time=0.4)

        arrows_12_3 = make_step_arrows(12, 3, axes, color=BLUE)
        self.play(LaggedStart(*[Create(a) for a in arrows_12_3], lag_ratio=0.2), run_time=5.0)

        label_12_3 = Text("12 ÷ 3 = 4").scale(0.7).to_edge(UP)
        self.play(FadeIn(label_12_3, shift=UP * 0.2), run_time=0.5)
        self.wait(0.5)  # reaches ~7.0s total so far

        # Equal sharing: 12 dots
        start_x = -5.5
        step_x = 1.0
        y_row = 2.2
        dots = VGroup(*[
            Dot(point=[start_x + i * step_x, y_row, 0], radius=0.07, color=WHITE)
            for i in range(12)
        ])
        self.play(LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.05), run_time=1.2)

        # Group into 4 baskets of 3
        rects3 = VGroup()
        for k in range(4):
            subgroup = VGroup(*dots[k * 3:(k + 1) * 3])
            r = SurroundingRectangle(subgroup, buff=0.15, corner_radius=0.1)
            r.set_stroke(GREEN, width=2).set_fill(GREEN, opacity=0.15)
            rects3.add(r)
        self.play(LaggedStart(*[Create(r) for r in rects3], lag_ratio=0.1), run_time=1.0)

        label_12_3_groups = Text("12 ÷ 3 = 4 groups").scale(0.6).to_edge(UP)
        self.play(Transform(label_12_3, label_12_3_groups), run_time=0.6)
        self.wait(0.2)

        # Now regroup into 6 baskets of 2
        rects2 = VGroup()
        for k in range(6):
            subgroup = VGroup(*dots[k * 2:(k * 2) + 2])
            r = SurroundingRectangle(subgroup, buff=0.15, corner_radius=0.1)
            r.set_stroke(BLUE, width=2).set_fill(BLUE, opacity=0.12)
            rects2.add(r)
        self.play(FadeOut(rects3, shift=UP * 0.1), run_time=1.0)
        label_12_2_groups = Text("12 ÷ 2 = 6 groups").scale(0.6).to_edge(UP)
        self.play(
            LaggedStart(*[Create(r) for r in rects2], lag_ratio=0.07),
            Transform(label_12_3, label_12_2_groups),
            run_time=1.0,
        )
        self.wait(1.0)  # up to ~13.0s

        # Clean the sharing view
        self.play(FadeOut(rects2), FadeOut(dots), run_time=0.8)
        # Clear the first measurement
        self.play(FadeOut(arrows_12_3), FadeOut(seg12), FadeOut(label_12_3), run_time=0.5)

        # Remainder example: 7 ÷ 3
        seg7 = Line(axes.c2p(0, 0), axes.c2p(7, 0)).set_stroke(YELLOW, width=8)
        self.play(Create(seg7), run_time=0.3)

        arrows_7_3 = make_step_arrows(6, 3, axes, color=BLUE)
        self.play(LaggedStart(*[Create(a) for a in arrows_7_3], lag_ratio=0.15), run_time=1.2)

        rem = Line(axes.c2p(6, 0), axes.c2p(7, 0)).set_stroke(RED, width=8)
        self.play(Create(rem), run_time=0.6)
        rem_label = Text("remainder 1").scale(0.5)
        rem_label.next_to(rem, UP)
        self.play(FadeIn(rem_label), run_time=0.4)
        self.wait(0.2)
        self.play(FadeOut(seg7), FadeOut(arrows_7_3), FadeOut(rem), FadeOut(rem_label), run_time=0.5)

        # Inverse-of-multiplication view
        eq_q = Text("3 × ? = 12").scale(0.9).move_to([0, 1.5, 0])
        self.play(FadeIn(eq_q), run_time=0.6)
        eq_a = Text("3 × 4 = 12").scale(0.9).move_to([0, 1.5, 0])
        self.play(Transform(eq_q, eq_a), run_time=1.0)
        self.wait(1.3)

        # Wrap up
        self.play(FadeOut(eq_q), FadeOut(axes), run_time=0.6)
        self.wait(1.0)
