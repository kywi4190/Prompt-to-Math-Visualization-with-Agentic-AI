from manim import *
import numpy as np
import math
# Optional utilities (guarded against missing)
try:
    from manim.utils.color import Color
except Exception:
    def Color(x): return x  # accept hex strings or color names
try:
    from manim.utils.space_ops import rotate_vector
except Exception:
    pass
try:
    from manim.utils.bezier import bezier
except Exception:
    pass
try:
    from manim.utils.rate_functions import smooth
except Exception:
    pass
# ParametricSurface fallback for compatibility
try:
    ParametricSurface
except NameError:
    ParametricSurface = Surface

class EigenDirectionsScene(Scene):
    def construct(self):
        # Symmetric matrix A (use eigh for robustness)
        A = np.array([[2.0, 1.0],
                      [1.0, 3.0]])
        vals, vecs = np.linalg.eigh(A)
        # Sort by descending eigenvalue for consistent display
        order = np.argsort(vals)[::-1]
        vals = vals[order]
        vecs = vecs[:, order]
        u1 = vecs[:, 0]  # eigenvector for largest eigenvalue
        u2 = vecs[:, 1]

        # Helpers
        def v3(xy):
            return np.array([xy[0], xy[1], 0.0])

        def make_plane():
            plane = NumberPlane(
                x_range=[-5, 5, 1],
                y_range=[-3, 3, 1],
                background_line_style={"stroke_color": GREY_C, "stroke_width": 1, "stroke_opacity": 0.8},
                axis_config={"stroke_color": GREY_B}
            )
            plane.z_index = 0
            return plane

        def make_circle():
            circ = Circle(radius=1.0, color=YELLOW, stroke_width=3)
            circ.z_index = 2
            return circ

        # Initial objects
        plane = make_plane()
        circle = make_circle()

        # Hook: show grid and unit circle
        self.play(Create(plane), run_time=1.4)
        self.play(Create(circle), run_time=0.8)
        self.wait(0.2)

        # Deform to ellipse under A
        group1 = VGroup(plane, circle)
        self.play(group1.animate.apply_matrix(A), run_time=2.4)
        self.wait(0.4)

        # Reset without numerical drift: swap to a fresh copy instead of applying inv(A)
        fresh_plane = make_plane()
        fresh_circle = make_circle()
        fresh_group = VGroup(fresh_plane, fresh_circle)
        self.play(ReplacementTransform(group1, fresh_group), run_time=1.4)
        self.wait(0.2)

        # Keep references to the reset plane
        plane = fresh_plane

        # Eigen-lines (through the origin)
        L = 5.0
        line1 = Line(v3(-L * u1), v3(L * u1), color=BLUE, stroke_width=3)
        line2 = Line(v3(-L * u2), v3(L * u2), color=RED, stroke_width=3)
        line1.z_index = 1
        line2.z_index = 1
        self.play(Create(line1), Create(line2), run_time=1.6)
        self.wait(0.2)

        # Eigen-arrows from the origin
        arrow_len = 2.2
        arr1 = Arrow(v3([0, 0]), v3(u1 * arrow_len), color=BLUE, buff=0, stroke_width=5)
        arr2 = Arrow(v3([0, 0]), v3(u2 * arrow_len), color=RED, buff=0, stroke_width=5)
        arr1.z_index = 2
        arr2.z_index = 2
        self.play(GrowArrow(arr1), GrowArrow(arr2), run_time=1.2)

        # Labels that stay nicely offset using current arrow direction (post-transform safe)
        lab1 = MathTex(r"\lambda_1", color=BLUE)
        lab2 = MathTex(r"\lambda_2", color=RED)
        lab1.z_index = 3
        lab2.z_index = 3

        def attach_label(label, arrow, shift_mag=0.25):
            def upd(mob):
                s = arrow.get_start()
                e = arrow.get_end()
                v = e - s
                v2 = np.array([v[0], v[1], 0.0])
                nrm = np.linalg.norm(v2[:2])
                if nrm < 1e-6:
                    dir_vec = np.array([1.0, 0.0, 0.0])
                else:
                    dir_vec = v2 / nrm
                # Screen-space perpendicular
                perp = np.array([-dir_vec[1], dir_vec[0], 0.0])
                mob.move_to(e + 0.15 * dir_vec + shift_mag * perp)
            return upd

        lab1.add_updater(attach_label(lab1, arr1))
        lab2.add_updater(attach_label(lab2, arr2))
        self.play(Write(lab1), Write(lab2), run_time=0.8)
        self.wait(0.4)

        # A generic vector v (not an eigenvector)
        v = np.array([1.8, 1.0])
        arrv = Arrow(v3([0, 0]), v3(v), color=WHITE, buff=0, stroke_width=5)
        arrv.z_index = 2
        labv = MathTex(r"v", color=WHITE)
        labv.z_index = 3
        labv.add_updater(attach_label(labv, arrv, shift_mag=0.2))
        self.play(GrowArrow(arrv), Write(labv), run_time=1.0)
        self.wait(0.4)

        # Apply A to everything: plane, eigen-lines, eigen-arrows, and v
        all_objs = VGroup(plane, line1, line2, arr1, arr2, arrv, lab1, lab2, labv)
        self.play(all_objs.animate.apply_matrix(A), run_time=3.6)
        self.wait(0.6)

        # Summary formula
        summary = MathTex(r"Av = \lambda v", color=YELLOW).to_corner(UR).shift(LEFT * 0.4 + DOWN * 0.2)
        summary.z_index = 4
        self.play(Write(summary), run_time=1.2)
        self.wait(1.6)

        # Clean up updaters to avoid lingering updates after the scene ends
        for mob in [lab1, lab2, labv]:
            mob.clear_updaters()
        self.play(FadeOut(VGroup(summary, lab1, lab2, labv, arr1, arr2, arrv, line1, line2, plane)), run_time=1.0)
        self.wait(0.2)
