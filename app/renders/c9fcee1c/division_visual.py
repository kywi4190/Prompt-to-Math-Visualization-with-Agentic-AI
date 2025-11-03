# === Prelude: helpers for stable MVP ===
        from manim import *
        import numpy as np
        def P(x,y): return [float(x), float(y), 0.0]

        # Duration budget helpers (keeps scene brisk and consistent)
        BASE = 0.8
        def dur(x): return max(0.1, BASE * float(x))
        
from manim import *

class DivisionScene(Scene):
    def construct(self):
        # Scene parameters
        unit = 0.5  # screen units per 1 number-unit
        y_bar = -1.0
        left = -6.0  # x-position representing 0 on our bar
        bar_h = 0.6
        baseline_y = y_bar - 0.6

        # Axis-like baseline and ticks for 0..12
        baseline = Line([left, baseline_y, 0], [left + 12*unit, baseline_y, 0])
        ticks = VGroup()
        for i in range(13):
            x = left + i * unit
            ticks.add(Line([x, baseline_y - 0.08, 0], [x, baseline_y + 0.08, 0], stroke_width=2))
        lbl0 = Text("0").scale(0.4).move_to([left - 0.2, baseline_y - 0.25, 0])
        lbl12 = Text("12").scale(0.4).move_to([left + 12*unit + 0.2, baseline_y - 0.25, 0])
        axis_group = VGroup(baseline, ticks, lbl0, lbl12)

        # The 12-unit bar
        bar12 = Rectangle(width=12*unit, height=bar_h, stroke_width=2)
        bar12.set_fill(color=BLUE_D, opacity=0.6)
        bar12.move_to([left + (12*unit)/2, y_bar, 0])

        title = Text("12 ÷ 3").scale(0.9).to_edge(UP)

        self.play(FadeIn(axis_group, shift=UP), FadeIn(bar12, shift=UP), FadeIn(title), run_time=1.6)
        self.wait(0.4)

        # Visualize 12 ÷ 3 as packing chunks of width 3
        chunk_w3 = 3 * unit
        chunks3 = VGroup()
        nums3 = VGroup()
        for k in range(4):
            cx = left + (k + 0.5) * chunk_w3
            rect = Rectangle(width=chunk_w3, height=bar_h)
            rect.set_stroke(width=0)
            rect.set_fill(color=YELLOW if k % 2 == 0 else ORANGE, opacity=0.55)
            rect.move_to([cx, y_bar - 0.9, 0])  # start below
            num = Text(str(k+1)).scale(0.45).move_to([cx, y_bar + bar_h/2 + 0.22, 0]).set_opacity(0)
            chunks3.add(rect)
            nums3.add(num)
        # Animate chunks sliding into place and counting
        for k in range(4):
            target = [left + (k + 0.5) * chunk_w3, y_bar, 0]
            self.play(
                chunks3[k].animate.move_to(target),
                FadeIn(nums3[k], shift=UP*0.15),
                run_time=0.5
            )
        eq4 = Text("= 4").scale(0.9).next_to(title, RIGHT)
        self.play(FadeIn(eq4, shift=RIGHT), run_time=0.6)
        self.wait(0.3)

        # Transition to 7 ÷ 2
        self.play(FadeOut(eq4, shift=UP), run_time=0.3)
        new_title = Text("7 ÷ 2").scale(0.9).move_to(title.get_center())
        self.play(Transform(title, new_title), run_time=0.6)

        # Shrink bar to represent 7 (keep same left edge)
        bar7 = Rectangle(width=7*unit, height=bar_h, stroke_width=2)
        bar7.set_fill(color=BLUE_D, opacity=0.6)
        bar7.move_to([left + (7*unit)/2, y_bar, 0])
        self.play(Transform(bar12, bar7), run_time=0.6)
        self.play(FadeOut(chunks3), FadeOut(nums3), run_time=0.3)

        # Pack chunks of width 2 into 7: 3 full chunks and a half
        chunk_w2 = 2 * unit
        full_chunks = VGroup()
        for k in range(3):
            cx = left + (k + 0.5) * chunk_w2
            rect = Rectangle(width=chunk_w2, height=bar_h)
            rect.set_stroke(width=0)
            rect.set_fill(color=GREEN, opacity=0.55)
            rect.move_to([cx, y_bar - 0.9, 0])
            full_chunks.add(rect)
        half_chunk = Rectangle(width=1*unit, height=bar_h)
        half_chunk.set_stroke(width=0)
        half_chunk.set_fill(color=TEAL, opacity=0.55)
        half_chunk.move_to([left + 3*chunk_w2 + (1*unit)/2, y_bar - 0.9, 0])

        for k in range(3):
            target = [left + (k + 0.5) * chunk_w2, y_bar, 0]
            self.play(full_chunks[k].animate.move_to(target), run_time=0.4)
        self.play(half_chunk.animate.move_to([left + 3*chunk_w2 + (1*unit)/2, y_bar, 0]), run_time=0.4)

        res = Text("3.5").scale(1.0).move_to([left + (7*unit)/2, y_bar + 0.9, 0])
        self.play(FadeIn(res, shift=UP*0.2), run_time=0.5)
        self.wait(0.2)

        # Zoom-out view: division as scaling (divide by 2)
        arrow = Arrow([0, 2.0, 0], [4, 2.0, 0], buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.1)
        scale_lbl = Text("divide by 2 = scale by 1/2").scale(0.55).next_to(arrow, UP)
        self.play(FadeIn(arrow, shift=RIGHT), FadeIn(scale_lbl, shift=UP*0.2), run_time=0.8)
        self.play(arrow.animate.apply_matrix([[0.5, 0.0], [0.0, 1.0]]), run_time=0.8)
        self.wait(0.4)

        # Hold a moment to settle
        self.wait(0.2)
