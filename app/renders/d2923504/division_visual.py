from manim import *

class DivisionScene(Scene):
    def construct(self):
        # Axes to act like a number line
        axes = Axes(
            x_range=[0, 12, 1],
            y_range=[-1, 1, 1],
            x_length=9,
            y_length=2,
            tips=False,
        )
        axes.to_edge(DOWN, buff=1.0)
        x_axis = axes.get_x_axis()
        x_axis.set_stroke(color=GRAY_B, width=2)

        # The full length we will divide: 12
        base_line = Line(axes.c2p(0, 0), axes.c2p(12, 0))
        base_line.set_stroke(color=BLUE_E, width=10, opacity=0.7)

        # Intro: bring in the axis and the 12-unit segment
        self.play(Create(axes), run_time=0.8)
        self.play(Create(base_line), run_time=0.8)

        # Show the "chunk" of size 3 moving along: repeated fitting
        step_arrow = Arrow(
            axes.c2p(0, 0.5),
            axes.c2p(3, 0.5),
            buff=0,
            stroke_width=6,
            color=RED_E,
        )
        label3 = Text("3").scale(0.5).set_color(RED_E)
        label3.next_to(step_arrow, UP, buff=0.1)
        label3.add_updater(lambda m: m.next_to(step_arrow, UP, buff=0.1))

        self.play(FadeIn(step_arrow), FadeIn(label3), run_time=0.7)

        # Vector for shifting the step by exactly 3 units along the axis
        dx = axes.c2p(3, 0) - axes.c2p(0, 0)

        ghosts = VGroup()
        # Four steps of length 3 fill 12
        for i in range(4):
            # Leave a translucent trace on the base line for each 3-unit fit
            ghost = Line(axes.c2p(3 * i, 0), axes.c2p(3 * (i + 1), 0))
            ghost.set_stroke(color=RED_E, width=12, opacity=0.3)
            self.play(Create(ghost), run_time=0.7)
            ghosts.add(ghost)
            if i < 3:
                self.play(step_arrow.animate.shift(dx), run_time=0.55)

        # Result text
        result = Text("12 / 3 = 4").scale(0.9).to_edge(UP)
        self.play(FadeIn(result), run_time=0.9)
        self.wait(0.5)

        # Transition to the "splitting" view: cut 12 into 3 equal parts
        self.play(FadeOut(step_arrow), FadeOut(label3), run_time=0.4)

        cut1 = Line(axes.c2p(4, -0.4), axes.c2p(4, 0.6)).set_stroke(YELLOW, width=4)
        cut2 = Line(axes.c2p(8, -0.4), axes.c2p(8, 0.6)).set_stroke(YELLOW, width=4)
        self.play(Create(cut1), Create(cut2), run_time=1.0)

        # Highlight each 4-unit piece and label it
        pieces = VGroup()
        labels = VGroup()
        for j in range(3):
            piece = Line(axes.c2p(4 * j, 0), axes.c2p(4 * (j + 1), 0))
            piece.set_stroke(color=GREEN_E, width=14, opacity=0.55)
            lbl = Text("4").scale(0.6).set_color(GREEN_E)
            lbl.move_to(axes.c2p(4 * j + 2, 0.6))
            pieces.add(piece)
            labels.add(lbl)
            self.play(Create(piece), FadeIn(lbl), run_time=0.9)

        self.wait(1.2)
