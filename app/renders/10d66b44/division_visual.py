from manim import *
import numpy as np

class DivisionScene(Scene):
    def construct(self):
        # -------- Hook: 12 tiles to be shared --------
        tiles = VGroup()
        side = 0.4
        for i in range(12):
            r = i // 4
            c = i % 4
            sq = Square(side_length=side, stroke_width=2).set_fill(BLUE, opacity=0.7)
            pos = [(c - 1.5) * 0.48, (1 - r) * 0.48, 0]
            sq.move_to(pos)
            tiles.add(sq)
        self.play(LaggedStart(*[FadeIn(s, scale=0.5) for s in tiles], lag_ratio=0.05), run_time=1.2)
        self.wait(0.3)

        # -------- Sharing view: 3 equal groups --------
        box_centers = [np.array([-4.0, -1.0, 0.0]), np.array([0.0, -1.0, 0.0]), np.array([4.0, -1.0, 0.0])]
        boxes = VGroup(*[
            RoundedRectangle(width=3.2, height=2.4, corner_radius=0.1, stroke_color=GRAY).move_to(box_centers[j])
            for j in range(3)
        ])
        self.play(FadeIn(boxes), run_time=0.5)

        # Compute target positions: 4 tiles per box in a 2x2 inside each box
        offsets = [np.array([-0.6,  0.6, 0.0]),
                   np.array([ 0.6,  0.6, 0.0]),
                   np.array([-0.6, -0.6, 0.0]),
                   np.array([ 0.6, -0.6, 0.0])]
        targets = []
        for i, sq in enumerate(tiles):
            j = i % 3              # which box
            q = i // 3             # index within that box (0..3)
            targets.append(box_centers[j] + offsets[q])
        self.play(LaggedStart(*[tiles[k].animate.move_to(targets[k]) for k in range(12)], lag_ratio=0.06), run_time=2.0)

        label_share = Text("4 each", font_size=36).move_to([0, -2.7, 0])
        self.play(FadeIn(label_share), run_time=0.5)
        self.wait(0.3)

        self.play(FadeOut(VGroup(tiles, boxes, label_share)), run_time=0.6)

        # -------- Measurement view: how many 3s fit into 12? --------
        nl = NumberLine(x_range=[0, 12, 1], length=8.0, include_tip=False)
        nl.move_to([0, 0.5, 0])
        tick_labels = VGroup()
        for n in [0, 3, 6, 9, 12]:
            t = Text(str(n), font_size=28)
            t.move_to(nl.n2p(n) + np.array([0, -0.4, 0]))
            tick_labels.add(t)
        self.play(Create(nl), FadeIn(tick_labels), run_time=1.0)

        dot = Dot(color=YELLOW).move_to(nl.n2p(0))
        self.play(FadeIn(dot, scale=0.8), run_time=0.3)

        step_arrows = VGroup()
        for k in range(4):
            start = dot.get_center()
            end = nl.n2p((k + 1) * 3)
            step = Arrow(start, end, buff=0, color=YELLOW, stroke_width=6, max_tip_length_to_length_ratio=0.15)
            self.play(Create(step), run_time=0.3)
            self.play(dot.animate.move_to(end), run_time=0.4)
            step_arrows.add(step)
        # Highlight the 12 mark
        twelve_label = [t for t in tick_labels if t.text == "12"][0]
        self.play(Indicate(twelve_label, color=YELLOW), run_time=0.6)

        # -------- Scaling view: divide by 3 = scale by 1/3 --------
        bar = Line(nl.n2p(0), nl.n2p(12), color=TEAL).set_stroke(width=8)
        shift_up = np.array([0, 0.7, 0])
        bar.shift(shift_up)
        self.play(Create(bar), run_time=0.4)

        info = Text("divide by 3 = scale by 1/3", font_size=34)
        info.next_to(bar, UP, buff=0.3)
        self.play(FadeIn(info), run_time=0.4)

        self.play(bar.animate.scale(1/3, about_point=nl.n2p(0) + shift_up), run_time=0.8)
        self.wait(0.2)

        # -------- Summary --------
        summary = Text("12 ÷ 3 = 4", font_size=54, color=WHITE)
        summary_bg = RoundedRectangle(width=summary.width + 0.6, height=summary.height + 0.4, corner_radius=0.15)
        summary_bg.set_fill(color=BLACK, opacity=0.7).set_stroke(width=0)
        summary_group = VGroup(summary_bg, summary).move_to([0, -2.2, 0])
        self.play(FadeIn(summary_group, shift=UP), run_time=0.7)
        self.wait(0.6)
