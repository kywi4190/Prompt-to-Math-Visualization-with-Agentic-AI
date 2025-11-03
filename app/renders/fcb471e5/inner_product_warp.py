import numpy as np
from manim import *

class InnerProductWarp(Scene):
    def construct(self):
        # Create a grid to represent the standard plane
        grid = NumberPlane()
        self.play(Create(grid))
        self.wait(1)

        # Warp the space using an SPD matrix
        warp_matrix = np.array([[2, 0], [0, 0.5]])
        warped_points = [warp_matrix @ np.array([x, y]) for x in range(-3, 4) for y in range(-3, 4)]
        warped_dots = [Dot(point=point, color=BLUE) for point in warped_points]
        self.play(*[Create(dot) for dot in warped_dots])
        self.wait(1)

        # Show the inner product
        inner_product_text = Text('Inner Product', font_size=24).shift(UP * 3)
        self.play(Write(inner_product_text))
        self.wait(1)

        # Unwarp the space
        unwarp_matrix = np.linalg.inv(warp_matrix)
        unwarped_points = [unwarp_matrix @ point for point in warped_points]
        unwarped_dots = [Dot(point=point, color=GREEN) for point in unwarped_points]
        self.play(*[FadeOut(dot) for dot in warped_dots])
        self.play(*[Create(dot) for dot in unwarped_dots])
        self.wait(1)

        # Show the map T
        map_T_text = Text('Map T', font_size=24).shift(UP * 3)
        self.play(Write(map_T_text))
        self.wait(1)

        # Restore orthogonality
        orthogonality_text = Text('Orthogonality Restored', font_size=24).shift(UP * 3)
        self.play(Transform(map_T_text, orthogonality_text))
        self.wait(1)

        # End scene
        self.play(FadeOut(grid), FadeOut(map_T_text))
        self.wait(1)