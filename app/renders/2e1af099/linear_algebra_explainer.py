from manim import *
import math

class LinearAlgebraMinute(Scene):
    def construct(self):
        # Matrices and helpers
        A = [[1.2, 0.6], [0.0, 0.9]]  # shear+scale (upper triangular)
        detA = A[0][0]*A[1][1] - A[0][1]*A[1][0]
        Shx = [[1.0, 0.5], [0.0, 1.0]]  # shear in x
        D = [[1.2, 0.0], [0.0, 0.9]]    # anisotropic stretch

        # Basic scene objects
        plane = NumberPlane(
            x_range=[-5, 5, 1], y_range=[-3, 3, 1],
            background_line_style={"stroke_opacity": 0.5, "stroke_width": 1}
        )
        origin = Dot().move_to([0, 0, 0])
        e1 = Arrow([0, 0, 0], [1.4, 0, 0], buff=0, color=RED)
        e2 = Arrow([0, 0, 0], [0, 1.4, 0], buff=0, color=BLUE)

        title = Text("Linear algebra: warping space", font_size=36).to_corner(UL)

        # Intro (0-6s)
        self.play(FadeIn(plane), FadeIn(origin), run_time=1.5)
        self.play(Create(e1), Create(e2), run_time=1.5)
        self.play(FadeIn(title), run_time=2.0)
        self.play(FadeOut(title), run_time=0.5)

        # Show matrix warp (6-16s)
        A_text = Text("A = [[1.2, 0.6], [0.0, 0.9]]", font_size=32).to_corner(UL)
        self.play(FadeIn(A_text), run_time=1.0)

        # Keep a faint reference grid
        plane.set_stroke(opacity=0.25)
        e1_ref = e1.copy().set_opacity(0.25)
        e2_ref = e2.copy().set_opacity(0.25)
        self.add(e1_ref, e2_ref)

        planeA = plane.copy().set_stroke(opacity=0.9)
        e1A = e1.copy()
        e2A = e2.copy()
        warp_group = VGroup(planeA, e1A, e2A)
        self.add(planeA, e1A, e2A)
        self.play(
            planeA.animate.apply_matrix(A),
            e1A.animate.apply_matrix(A),
            e2A.animate.apply_matrix(A),
            run_time=7.0
        )
        self.wait(1.0)
        self.play(FadeOut(A_text), run_time=1.0)

        # Determinant via unit square (16-26s)
        unit_sq = Polygon(
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
            color=YELLOW
        ).set_fill(YELLOW, opacity=0.2)
        unit_sq.move_to([2.2, 1.1, 0])  # shift slightly for clarity
        sq_img = unit_sq.copy().set_fill(GREEN, opacity=0.2).set_stroke(GREEN)
        det_label = Text(f"det(A) = {detA:.2f}", font_size=32).next_to(unit_sq, UP)

        self.play(FadeIn(unit_sq), run_time=1.0)
        self.play(sq_img.animate.apply_matrix(A), run_time=4.0)
        self.add(sq_img)
        self.play(FadeIn(det_label), run_time=1.0)
        self.wait(3.0)
        self.play(FadeOut(unit_sq), FadeOut(sq_img), FadeOut(det_label), run_time=1.0)

        # Decomposition: shear then stretch (26-38s)
        self.play(FadeOut(warp_group), run_time=1.0)
        plane_dec = NumberPlane(
            x_range=[-5, 5, 1], y_range=[-3, 3, 1],
            background_line_style={"stroke_opacity": 0.5, "stroke_width": 1}
        )
        e1d = Arrow([0, 0, 0], [1.4, 0, 0], buff=0, color=RED)
        e2d = Arrow([0, 0, 0], [0, 1.4, 0], buff=0, color=BLUE)
        self.play(FadeIn(plane_dec), FadeIn(e1d), FadeIn(e2d), run_time=1.0)

        shear_text = Text("shear", font_size=36).to_corner(UR)
        self.play(FadeIn(shear_text), run_time=0.5)
        self.play(
            plane_dec.animate.apply_matrix(Shx),
            e1d.animate.apply_matrix(Shx),
            e2d.animate.apply_matrix(Shx),
            run_time=4.0
        )
        self.play(FadeOut(shear_text), run_time=0.5)

        stretch_text = Text("stretch", font_size=36).to_corner(UR)
        self.play(FadeIn(stretch_text), run_time=0.5)
        self.play(
            plane_dec.animate.apply_matrix(D),
            e1d.animate.apply_matrix(D),
            e2d.animate.apply_matrix(D),
            run_time=4.0
        )
        self.play(FadeOut(stretch_text), run_time=0.5)

        # Eigenvectors (38-48s)
        self.play(FadeOut(plane_dec), FadeOut(e1d), FadeOut(e2d), run_time=1.0)
        # Faint base grid remains
        # Eigen directions for A: v1 = [1,0], v2 = [-2,1]
        L = 5.0
        v1_base = Line([-L, 0, 0], [L, 0, 0], color=YELLOW).set_stroke(opacity=0.3)
        v1_line = v1_base.copy().set_stroke(opacity=1.0)

        v2 = [-2.0, 1.0]
        nrm = math.sqrt(v2[0]**2 + v2[1]**2)
        u2 = [v2[0]/nrm, v2[1]/nrm]
        start2 = [-L*u2[0], -L*u2[1], 0]
        end2 = [L*u2[0], L*u2[1], 0]
        v2_base = Line(start2, end2, color=TEAL).set_stroke(opacity=0.3)
        v2_line = v2_base.copy().set_stroke(opacity=1.0)

        v1_arrow = Arrow([0, 0, 0], [2.5, 0, 0], buff=0, color=YELLOW)
        v2_arrow = Arrow([0, 0, 0], [-4, 2, 0], buff=0, color=TEAL)

        self.play(
            FadeIn(v1_base), FadeIn(v2_base),
            Create(v1_line), Create(v2_line),
            Create(v1_arrow), Create(v2_arrow),
            run_time=2.0
        )
        self.play(
            v1_line.animate.apply_matrix(A),
            v2_line.animate.apply_matrix(A),
            v1_arrow.animate.apply_matrix(A),
            v2_arrow.animate.apply_matrix(A),
            run_time=5.0
        )
        self.wait(1.0)
        self.play(
            FadeOut(v1_base), FadeOut(v2_base),
            FadeOut(v1_line), FadeOut(v2_line),
            FadeOut(v1_arrow), FadeOut(v2_arrow),
            run_time=2.0
        )

        # Solving Ax = b (48-58s)
        # Choose b and compute x = A^{-1} b
        b_vec = [2.5, 1.5]
        # Inverse of upper triangular A = [[a,b],[0,d]] is [[1/a, -b/(a d)],[0, 1/d]]
        a, b_off, d = A[0][0], A[0][1], A[1][1]
        Ainv = [[1.0/a, -b_off/(a*d)], [0.0, 1.0/d]]
        x_vec = [Ainv[0][0]*b_vec[0] + Ainv[0][1]*b_vec[1], Ainv[1][0]*b_vec[0] + Ainv[1][1]*b_vec[1]]

        b_arrow = Arrow([0, 0, 0], [b_vec[0], b_vec[1], 0], buff=0, color=ORANGE)
        x_arrow = Arrow([0, 0, 0], [x_vec[0], x_vec[1], 0], buff=0, color=GREEN)
        solve_text = Text("Ax = b", font_size=36).to_corner(UR)

        self.play(FadeIn(b_arrow), FadeIn(x_arrow), FadeIn(solve_text), run_time=2.0)
        self.play(
            x_arrow.animate.apply_matrix(A),
            run_time=5.0
        )
        self.play(Indicate(b_arrow, scale_factor=1.1, color=ORANGE), run_time=1.0)
        self.play(FadeOut(b_arrow), FadeOut(x_arrow), FadeOut(solve_text), run_time=2.0)

        # Wrap-up (58-60s)
        wrap = Text("warp • area • eigenvectors • solving", font_size=34).to_edge(DOWN)
        self.play(FadeIn(wrap), run_time=2.5)
        # End of 60 seconds
