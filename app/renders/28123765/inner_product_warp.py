from manim import *
import numpy as np

class InnerProductWarpScene(Scene):
    def construct(self):
        # Create a number plane to represent R^n
        plane = NumberPlane(x_range=[-3, 3], y_range=[-3, 3], background_line_style={'stroke_color': BLUE})
        self.add(plane)

        # Create initial vectors
        v1 = Arrow(start=[0, 0, 0], end=[1, 2, 0], color=YELLOW)
        v2 = Arrow(start=[0, 0, 0], end=[2, 1, 0], color=GREEN)
        self.play(Create(v1), Create(v2))
        self.wait(1)

        # Warp effect using a SPD matrix
        self.play(v1.animate.apply_matrix([[1, 0.5], [0.5, 1]]), v2.animate.apply_matrix([[1, 0.5], [0.5, 1]]))
        self.wait(1)

        # Show the warped vectors
        self.play(FadeOut(v1), FadeOut(v2))
        warped_v1 = Arrow(start=[0, 0, 0], end=[1.5, 2.5, 0], color=YELLOW)
        warped_v2 = Arrow(start=[0, 0, 0], end=[2.5, 1.5, 0], color=GREEN)
        self.play(Create(warped_v1), Create(warped_v2))
        self.wait(1)

        # Unwarp back to standard orthogonality
        self.play(warped_v1.animate.apply_matrix([[1, -0.5], [-0.5, 1]]), warped_v2.animate.apply_matrix([[1, -0.5], [-0.5, 1]]))
        self.wait(1)

        # Show the final orthogonal vectors
        final_v1 = Arrow(start=[0, 0, 0], end=[1, 0, 0], color=YELLOW)
        final_v2 = Arrow(start=[0, 0, 0], end=[0, 1, 0], color=GREEN)
        self.play(FadeOut(warped_v1), FadeOut(warped_v2), Create(final_v1), Create(final_v2))
        self.wait(2)