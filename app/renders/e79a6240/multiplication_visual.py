# === Prelude: helpers for stable MVP ===
        from manim import *
        import numpy as np
        def P(x,y): return [float(x), float(y), 0.0]

        # Duration budget helpers (keeps scene brisk and consistent)
        BASE = 0.8
        def dur(x): return max(0.1, BASE * float(x))
        
from manim import *
import math

class MultiplicationScene(Scene):
    def construct(self):
        # PART 1: Repeated addition on a number line
        nline = NumberLine(x_range=[0, 7, 1], unit_size=1, length=8, include_numbers=True)
        nline.shift([0, 2, 0])
        self.play(Create(nline), run_time=0.8)

        segments = VGroup()
        for i in range(3):
            seg = Line([2 * i, 2, 0], [2 * (i + 1), 2, 0], color=YELLOW, stroke_width=8)
            segments.add(seg)
        self.play(LaggedStart(*[Create(seg) for seg in segments], lag_ratio=0.25, run_time=1.5))

        label_groups = Text("3 groups of 2").scale(0.6).move_to([3, 2.6, 0])
        self.play(FadeIn(label_groups, shift=[0, 0.3, 0]), run_time=0.6)

        total_arrow = Arrow([0, 2, 0], [6, 2, 0], buff=0, color=WHITE)
        eq_text = Text("3 x 2 = 6").scale(0.6).next_to(total_arrow, DOWN, buff=0.2)
        self.play(GrowArrow(total_arrow), FadeIn(eq_text, shift=[0, -0.3, 0]), run_time=0.8)
        self.wait(0.4)

        self.play(FadeOut(VGroup(label_groups, segments, total_arrow, eq_text, nline)), run_time=0.7)

        # PART 2: Scaling view
        unit_arrow = Arrow([0, 0, 0], [1, 0, 0], buff=0, color=BLUE)
        unit_label = Text("1").scale(0.5).next_to(unit_arrow, DOWN, buff=0.1)
        self.play(GrowArrow(unit_arrow), FadeIn(unit_label, shift=[0, -0.2, 0]), run_time=0.6)

        dot = Dot().move_to([2, 0, 0]).set_color(RED)
        x_label = Text("2").scale(0.5).next_to(dot, DOWN, buff=0.1)
        self.play(FadeIn(dot), FadeIn(x_label), run_time=0.4)

        times3 = Text("x3").scale(0.6).move_to([0.5, 0.6, 0])
        self.play(FadeIn(times3, shift=[0, 0.2, 0]), run_time=0.3)

        scaled_arrow = Arrow([0, 0, 0], [3, 0, 0], buff=0, color=BLUE)
        self.play(Transform(unit_arrow, scaled_arrow), run_time=0.8)
        self.play(dot.animate.move_to([6, 0, 0]), x_label.animate.next_to(dot, DOWN, buff=0.1), run_time=0.8)
        scale_text = Text("Multiplying scales distance").scale(0.5).move_to([3, -0.7, 0])
        self.play(FadeIn(scale_text), run_time=0.4)
        self.wait(0.2)
        self.play(FadeOut(VGroup(unit_arrow, unit_label, dot, x_label, times3, scale_text)), run_time=0.6)

        # PART 3: Area model
        plane = NumberPlane(
            x_range=[-1, 4, 1],
            y_range=[-1, 3, 1],
            background_line_style={"stroke_opacity": 0.2, "stroke_width": 1},
        )
        plane.shift([0, -0.2, 0])
        self.play(FadeIn(plane), run_time=0.5)

        rect_outline = Polygon([0, 0, 0], [3, 0, 0], [3, 2, 0], [0, 2, 0])
        rect_outline.set_stroke(color=WHITE, width=2)
        rect_fill = Polygon([0, 0, 0], [3, 0, 0], [3, 2, 0], [0, 2, 0])
        rect_fill.set_fill(color=GREEN, opacity=0.25).set_stroke(width=0)
        rect = VGroup(rect_fill, rect_outline)
        self.play(FadeIn(rect, shift=[0, 0.2, 0]), run_time=0.6)

        centers = [
            [0.5, 0.5, 0], [1.5, 0.5, 0], [2.5, 0.5, 0],
            [0.5, 1.5, 0], [1.5, 1.5, 0], [2.5, 1.5, 0],
        ]
        tiles = VGroup(*[Square(1).move_to(c).set_stroke(width=1).set_fill(YELLOW, opacity=0.6) for c in centers])
        self.play(LaggedStart(*[FadeIn(sq, scale=0.8) for sq in tiles], lag_ratio=0.1, run_time=1.2))

        label_area = Text("3 x 2 = 6 squares").scale(0.6).next_to(rect, DOWN, buff=0.2)
        self.play(FadeIn(label_area, shift=[0, -0.2, 0]), run_time=0.4)

        area_group = VGroup(tiles, rect)
        new_label = Text("2 x 3 = 6 squares").scale(0.6).move_to(label_area.get_center())
        self.play(area_group.animate.rotate(math.pi / 2), Transform(label_area, new_label), run_time=0.9)

        self.wait(1.5)
