from manim import *


class MultiplicationScene(Scene):
    def construct(self):
        # Title
        title = Text("3 × 4").scale(0.9)
        title.to_corner(UL)

        # Build three colored groups of four squares (the "groups of four")
        s = 0.5
        buff = 0.06

        def make_group(color):
            squares = VGroup(*[
                Square(side_length=s, stroke_width=2).set_fill(color, opacity=0.85)
                for _ in range(4)
            ])
            squares.arrange(RIGHT, buff=buff)
            return squares

        g1 = make_group(BLUE)
        g2 = make_group(GREEN)
        g3 = make_group(ORANGE)

        row_groups = VGroup(g1, g2, g3)
        row_groups.arrange(RIGHT, buff=buff)
        row_groups.move_to([0, 1.0, 0])

        # Intro: show title and the three groups laid end-to-end
        self.play(
            FadeIn(title, shift=UP),
            FadeIn(row_groups, shift=UP, lag_ratio=0.1),
            run_time=1.5,
        )
        self.wait(0.5)

        # Sweep arrow to suggest 4 + 4 + 4 accumulating to 12
        left_x = row_groups.get_left()[0]
        right_x = row_groups.get_right()[0]
        top_y = row_groups.get_top()[1]
        sweep = Arrow(
            [left_x, top_y + 0.5, 0],
            [right_x, top_y + 0.5, 0],
            buff=0.2,
            stroke_width=6,
        )
        self.play(GrowArrow(sweep), run_time=1.3)
        self.wait(1.2)

        # Rearrange the same 12 squares into a 3×4 array (area view)
        self.play(FadeOut(sweep), run_time=0.4)

        spacing = s + buff
        x_vals = [(c - 1.5) * spacing for c in range(4)]
        y_vals = [(1 - r) * spacing - 0.4 for r in range(3)]  # rows: 0 (top),1,2 (bottom)

        anims = []
        for i in range(4):
            anims.append(g1[i].animate.move_to([x_vals[i], y_vals[0], 0]))
        for i in range(4):
            anims.append(g2[i].animate.move_to([x_vals[i], y_vals[1], 0]))
        for i in range(4):
            anims.append(g3[i].animate.move_to([x_vals[i], y_vals[2], 0]))

        self.play(AnimationGroup(*anims, lag_ratio=0.05), run_time=2.5)
        self.wait(0.5)

        # Collect all squares for bounds and labeling
        all_squares = VGroup(*[sq for grp in (g1, g2, g3) for sq in grp])
        left = all_squares.get_left()[0]
        right = all_squares.get_right()[0]
        top = all_squares.get_top()[1]
        bottom = all_squares.get_bottom()[1]

        # Axes-like arrows to name rows and columns
        h_arrow = Arrow([left, bottom - 0.35, 0], [right, bottom - 0.35, 0], buff=0.1, stroke_width=4)
        v_arrow = Arrow([left - 0.35, bottom, 0], [left - 0.35, top, 0], buff=0.1, stroke_width=4)
        lab_cols = Text("4 columns").scale(0.5).move_to([(left + right) / 2, bottom - 0.65, 0])
        lab_rows = Text("3 rows").scale(0.5).move_to([left - 1.0, (bottom + top) / 2, 0])

        self.play(Create(h_arrow), Create(v_arrow), run_time=1.1)
        self.play(FadeIn(lab_cols, shift=[0, -0.2, 0]), FadeIn(lab_rows, shift=[-0.2, 0, 0]), run_time=0.6)
        self.wait(0.4)

        # Outline the full area (3 by 4)
        rect = Rectangle(
            width=(right - left) + 0.2,
            height=(top - bottom) + 0.2,
            stroke_color=YELLOW,
            stroke_width=4,
        ).move_to([ (left + right) / 2, (bottom + top) / 2, 0 ])
        self.play(Create(rect), run_time=0.6)

        # State the result next to the array
        result_text = Text("3 × 4 = 12").scale(0.9).next_to(all_squares, RIGHT, buff=0.8).shift([0, 0.1, 0])
        self.play(Transform(title, result_text), run_time=1.2)

        # Gentle pulse to reinforce the area idea
        self.play(
            all_squares.animate.scale(1.05),
            rect.animate.scale(1.05),
            rate_func=there_and_back,
            run_time=1.5,
        )
        self.wait(2.0)
        self.wait(2.0)
