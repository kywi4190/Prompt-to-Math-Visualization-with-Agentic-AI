# === Prelude: helpers for stable MVP ===
        from manim import *
        import numpy as np
        def P(x,y): return [float(x), float(y), 0.0]

        # Duration budget helpers (keeps scene brisk and consistent)
        BASE = 0.8
        def dur(x): return max(0.1, BASE * float(x))
        
from manim import *
import numpy as np

class MultiplicationVisualScene(Scene):
    def construct(self):
        # Phase 1: Number line hops (groups)
        number_line = NumberLine(x_range=[-1, 13, 1], length=10)
        number_line.to_edge(DOWN)
        dot = Dot(radius=0.07, color=YELLOW).move_to(number_line.n2p(0))

        title = Text("3 × 4", font_size=36).to_edge(UP)
        self.play(FadeIn(number_line), FadeIn(dot), FadeIn(title), run_time=0.5)

        def hop_path(i):
            start = number_line.n2p(4 * i)
            end = number_line.n2p(4 * (i + 1))
            ctrl = (start + end) / 2 + np.array([0, 1.0, 0])
            path = QuadraticBezier(start, ctrl, end)
            path.set_stroke(YELLOW, width=4)
            return path

        for i in range(3):
            path = hop_path(i)
            self.play(Create(path), run_time=0.25)
            self.play(MoveAlongPath(dot, path), run_time=1.15, rate_func=smooth)
            self.play(FadeOut(path), run_time=0.05)

        groups_label = Text("3 groups of 4 = 12", font_size=36)
        groups_label.next_to(title, DOWN, buff=0.2)
        self.play(FadeIn(groups_label), run_time=0.6)

        # Transition to area model
        self.play(
            FadeOut(VGroup(number_line, dot, title, groups_label)),
            run_time=0.4
        )

        # Phase 2: Rectangle (area)
        s = 0.6
        squares = VGroup()
        for r in range(3):
            for c in range(4):
                sq = Square(side_length=s)
                sq.set_stroke(WHITE, width=2)
                sq.set_fill(BLUE, opacity=0.0)
                x = (c - 1.5) * s
                y = (1 - r) * s
                sq.move_to([x, y, 0])
                squares.add(sq)
        squares.move_to([0, 0, 0])

        self.play(LaggedStart(*[FadeIn(sq) for sq in squares], lag_ratio=0.07), run_time=1.0)
        self.play(LaggedStart(*[sq.animate.set_fill(BLUE, opacity=0.6) for sq in squares], lag_ratio=0.05), run_time=1.2)

        brace_w = Brace(squares, DOWN, buff=0.1)
        brace_h = Brace(squares, LEFT, buff=0.1)
        label_w = Text("4", font_size=32).next_to(brace_w, DOWN, buff=0.1)
        label_h = Text("3", font_size=32).next_to(brace_h, LEFT, buff=0.1)
        area_text = Text("Area = 12", font_size=36).next_to(squares, UP, buff=0.2)

        self.play(GrowFromCenter(brace_w), GrowFromCenter(brace_h), FadeIn(label_w), FadeIn(label_h), FadeIn(area_text), run_time=1.0)

        # Transition to scaling view
        self.play(FadeOut(VGroup(squares, brace_w, brace_h, label_w, label_h, area_text)), run_time=0.5)

        # Phase 3: Scaling interpretation
        seg = Line([-3.0, -1.8, 0], [-1.0, -1.8, 0], stroke_width=8, color=YELLOW)
        pin = Dot(radius=0.06, color=WHITE).move_to(seg.get_start())
        label_len_before = Text("4", font_size=36).next_to(seg, UP, buff=0.12)
        x3_text = Text("× 3", font_size=32).next_to(seg, DOWN, buff=0.12)

        self.play(Create(seg), FadeIn(pin), FadeIn(label_len_before), FadeIn(x3_text), run_time=0.8)

        label_len_after = Text("12", font_size=36).move_to(label_len_before.get_center())
        self.play(
            seg.animate.stretch(3, dim=0, about_point=seg.get_start()),
            Transform(label_len_before, label_len_after),
            run_time=1.4
        )

        summary = Text("Groups = Area = Scaling", font_size=36).to_edge(UP)
        self.play(FadeIn(summary), run_time=0.7)
        self.wait(0.4)
