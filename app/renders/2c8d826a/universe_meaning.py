from manim import *
import numpy as np
import math

class UniverseMeaningScene(Scene):
    def construct(self):
        # Fabric: a simple plane
        plane = NumberPlane(
            x_range=[-4, 4, 1],
            y_range=[-3, 3, 1],
            background_line_style={"stroke_opacity": 0.3, "stroke_width": 1},
        )
        self.play(FadeIn(plane), run_time=0.8)

        # Symmetry and invariants: a triangle with det=1 transforms
        tri = Polygon(
            [0.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
            [0.0, 1.2, 0.0],
            color=YELLOW,
            fill_opacity=0.5,
            stroke_width=2,
        )
        tri_label = Text("Symmetry → invariants (area)", font_size=32).next_to(tri, UP)
        det_label = Text("det = 1", font_size=28, color=GREEN).next_to(tri, RIGHT)
        self.play(Create(tri), FadeIn(tri_label), FadeIn(det_label), run_time=1.2)

        # Rotation: preserves area
        self.play(Rotate(tri, angle=PI/4), run_time=2.0)
        # Shear: also preserves area (det=1)
        shear_matrix_1 = [[1.0, 0.8], [0.0, 1.0]]
        self.play(ApplyMatrix(shear_matrix_1, tri), run_time=2.0)

        self.play(FadeOut(tri), FadeOut(tri_label), FadeOut(det_label), run_time=0.5)

        # Expansion: galaxies on a ring + spokes from origin
        n = 14
        r = 1.5
        galaxies = VGroup()
        for i in range(n):
            theta = 2 * math.pi * i / n
            pos = [r * math.cos(theta), r * math.sin(theta), 0.0]
            galaxies.add(Dot(radius=0.05, color=WHITE).move_to(pos))
        spokes = VGroup()
        for i in [0, 3, 6, 9]:
            theta = 2 * math.pi * i / n
            pos = [r * math.cos(theta), r * math.sin(theta), 0.0]
            spokes.add(Line([0.0, 0.0, 0.0], pos, color=BLUE, stroke_width=2))
        galaxy_group = VGroup(galaxies, spokes)
        expansion_label = Text("Expansion: scale factor a(t)", font_size=32, color=BLUE).to_corner(UR).shift([-0.5, -0.5, 0.0])
        self.play(FadeIn(galaxy_group), FadeIn(expansion_label), run_time=0.8)
        self.play(galaxy_group.animate.scale(1.6, about_point=[0.0, 0.0, 0.0]), run_time=3.0)
        self.play(FadeOut(galaxy_group), FadeOut(expansion_label), run_time=0.6)

        # Entropy and mixing: cluster of states, area-preserving scrambling
        cluster = VGroup()
        grid_size = 6
        spacing = 0.18
        for i in range(grid_size):
            for j in range(grid_size):
                x = (i - (grid_size - 1) / 2) * spacing
                y = (j - (grid_size - 1) / 2) * spacing
                cluster.add(Dot(radius=0.045, color=PURE_RED).move_to([x, y, 0.0]))
        ent_label = Text("Mixing: entropy increases (area preserved)", font_size=32, color=RED).to_corner(UL).shift([0.4, -0.6, 0.0])
        self.play(FadeIn(cluster), FadeIn(ent_label), run_time=0.8)

        # Apply alternating shears (det=1) to stretch+fold
        shearA = [[1.0, 1.0], [0.0, 1.0]]
        shearB = [[1.0, 0.0], [1.0, 1.0]]
        self.play(ApplyMatrix(shearA, cluster), run_time=3.0)
        self.play(ApplyMatrix(shearB, cluster), run_time=3.0)

        # Conclusion
        conclusion = Text(
            "Meaning via math: invariants + dynamics → patterns",
            font_size=36,
            color=YELLOW,
        ).to_edge(DOWN)
        self.play(FadeIn(conclusion), run_time=1.0)
        self.wait(1.0)
