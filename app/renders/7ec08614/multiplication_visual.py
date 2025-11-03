# === Prelude: helpers for stable MVP ===
from manim import *
import numpy as np

def P(x, y): 
    return [float(x), float(y), 0.0]

# Duration budget helpers (keeps scene brisk and consistent)
BASE = 0.8
def dur(x): 
    return max(0.1, BASE * float(x))

from manim import *


class MultiplicationScene(Scene):
    def construct(self):
        # Parameters for the dot grid
        spacing = 0.6
        cols = 4
        rows = 3
        center = [-3.5, 1.5, 0]

        def make_row(y):
            dots = []
            for j in range(cols):
                x = center[0] + (j - (cols - 1) / 2) * spacing
                dots.append(Dot(radius=0.08, color=BLUE).move_to([x, y, 0]))
            return VGroup(*dots)

        # First row of 4 dots
        y1 = center[1]
        row1 = make_row(y1)
        self.play(
            LaggedStart(*[FadeIn(dot, shift=[0, 0.15, 0]) for dot in row1], lag_ratio=0.15),
            run_time=1.8,
        )
        self.wait(0.4)

        # Build 3 rows total (repeated addition picture)
        row2 = row1.copy().shift([0, -spacing, 0])
        row3 = row1.copy().shift([0, -2 * spacing, 0])
        self.play(FadeIn(row2, shift=[0, 0.15, 0]), run_time=0.7)
        self.play(FadeIn(row3, shift=[0, 0.15, 0]), run_time=0.7)
        self.wait(1.6)

        sum_text = Text("4 + 4 + 4", font_size=36).move_to([-1.0, 1.2, 0])
        self.play(FadeIn(sum_text), run_time=0.8)
        self.wait(1.5)

        # Area model: surround with a rectangle and label 3 x 4
        grid_group = VGroup(row1, row2, row3)
        rect = SurroundingRectangle(grid_group, color=YELLOW, buff=0.25)
        rect.set_fill(YELLOW, opacity=0.15)
        prod_text = Text("3 × 4", font_size=42, color=YELLOW).next_to(rect, UP, buff=0.2)
        self.play(FadeIn(rect), run_time=0.8)
        self.play(FadeIn(prod_text), run_time=0.5)
        self.wait(1.2)

        # Number line: scaling view
        numline = NumberLine(x_range=[0, 13, 1], length=6.4, include_numbers=False)
        numline.move_to([2.7, -1.4, 0])
        labels = VGroup()
        for val in [0, 4, 12]:
            lbl = Text(str(val), font_size=28)
            lbl.move_to(numline.n2p(val) + [0, -0.35, 0])
            labels.add(lbl)
        self.play(Create(numline), run_time=0.8)
        self.play(
            LaggedStart(*[FadeIn(lbl, shift=[0, -0.2, 0]) for lbl in labels], lag_ratio=0.2),
            run_time=0.5,
        )
        # Arrow for 4, then scale by 3
        arr4 = Arrow(numline.n2p(0), numline.n2p(4), buff=0, color=GREEN)
        arr4.set_stroke(width=6)
        self.play(Create(arr4), run_time=0.7)
        times3 = Text("×3", font_size=36, color=GREEN).next_to(arr4, UP, buff=0.2)
        self.play(FadeIn(times3), run_time=0.3)
        self.wait(1.2)

        arr12 = Arrow(numline.n2p(0), numline.n2p(12), buff=0, color=GREEN)
        arr12.set_stroke(width=6)
        self.play(Transform(arr4, arr12), run_time=2.0)
        self.wait(1.0)

        # Wrap-up message
        conclusion = Text("Groups = Area = Scaling", font_size=36).move_to([0, 3.0, 0])
        self.play(FadeIn(conclusion, shift=[0, 0.3, 0]), run_time=0.8)
        self.play(Indicate(rect, color=YELLOW), run_time=0.4)
        self.play(Indicate(arr4, color=GREEN), run_time=0.4)
        self.wait(1.4)
