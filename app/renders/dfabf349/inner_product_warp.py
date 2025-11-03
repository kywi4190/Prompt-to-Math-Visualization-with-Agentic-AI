from manim import *

class InnerProductWarp(Scene):
    def construct(self):
        # Create a grid to represent the standard basis
        plane = NumberPlane()
        self.play(Create(plane))
        self.wait(1)

        # Show the warping effect with an SPD matrix
        warp_matrix = [[2, 0], [0, 0.5]]
        warp = Matrix(warp_matrix)
        self.play(Transform(plane, warp), run_time=2)
        self.wait(1)

        # Introduce the map T
        T = Tex(r'T: \, 	ext{Unwarp to Standard}')
        T.to_edge(UP)
        self.play(Write(T), run_time=1)
        self.wait(1)

        # Show the unwarping process
        self.play(Transform(plane, NumberPlane()), run_time=2)
        self.wait(1)

        # Final reveal of orthogonality
        self.play(FadeOut(T), run_time=1)
        self.wait(1)
        self.play(FadeOut(plane), run_time=1)
        self.wait(1)