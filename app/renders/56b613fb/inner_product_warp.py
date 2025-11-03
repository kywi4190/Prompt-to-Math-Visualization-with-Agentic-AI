from manim import *
import numpy as np

class InnerProductWarpScene(Scene):
    def construct(self):
        # Create the plane
        plane = NumberPlane(x_range=[-3, 3], y_range=[-3, 3], background_line_style={'stroke_color': BLUE, 'stroke_width': 1})
        self.play(Create(plane))

        # Define original vectors
        v1 = Arrow([0, 0, 0], [2, 1, 0], color=YELLOW)
        v2 = Arrow([0, 0, 0], [1, 2, 0], color=RED)
        self.play(Create(v1), Create(v2))

        # Warp matrix (SPD)
        warp_matrix = [[2, 0.5], [0.5, 2]]

        # Apply the warp to the vectors
        warped_v1 = v1.copy().apply_matrix(warp_matrix)
        warped_v2 = v2.copy().apply_matrix(warp_matrix)

        self.play(Transform(v1, warped_v1), Transform(v2, warped_v2))

        # Show the warped vectors
        self.wait(1)

        # Define the transformation T (unwarp)
        unwarp_matrix = np.linalg.inv(warp_matrix)

        # Unwarp the vectors
        unwarped_v1 = warped_v1.copy().apply_matrix(unwarp_matrix)
        unwarped_v2 = warped_v2.copy().apply_matrix(unwarp_matrix)

        self.play(Transform(warped_v1, unwarped_v1), Transform(warped_v2, unwarped_v2))

        # Final state
        self.wait(2)
        self.play(FadeOut(v1), FadeOut(v2), FadeOut(plane))