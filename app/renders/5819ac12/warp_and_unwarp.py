from manim import *
import math

# Single Scene class as required
class WarpAndUnwarp(Scene):
    def construct(self):
        # --- Helper linear algebra for 2x2 matrices (no external libs) ---
        def mat_mult(A, B):
            return [
                [A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
                [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]],
            ]
        def mat_vec(A, v):
            return [A[0][0]*v[0] + A[0][1]*v[1], A[1][0]*v[0] + A[1][1]*v[1], 0]
        def transpose(A):
            return [[A[0][0], A[1][0]],[A[0][1], A[1][1]]]
        def rotation(theta):
            c = math.cos(theta); s = math.sin(theta)
            return [[c, -s],[s, c]]
        def diag(a,b):
            return [[a,0],[0,b]]

        # --- A concrete SPD matrix: eigenvalues and a rotation ---
        theta = math.pi/6  # rotate eigenbasis
        lam1, lam2 = 2.0, 0.5
        R = rotation(theta)
        Rt = transpose(R)
        D = diag(lam1, lam2)
        sqrtD = diag(math.sqrt(lam1), math.sqrt(lam2))
        invSqrtD = diag(1/math.sqrt(lam1), 1/math.sqrt(lam2))

        # A = R D R^T  , sqrtA = R sqrtD R^T, inv_sqrtA = R invSqrtD R^T
        A = mat_mult(mat_mult(R, D), Rt)
        sqrtA = mat_mult(mat_mult(R, sqrtD), Rt)
        inv_sqrtA = mat_mult(mat_mult(R, invSqrtD), Rt)

        # --- Visual elements ---
        plane = NumberPlane(x_range=[-4,4,1], y_range=[-3.5,3.5,1], background_line_style={"stroke_opacity": 0.2})
        plane.add_coordinate_labels(font_size=20)

        title = MathTex("\langle x,y\rangle_A = x^T A y", font_size=36).to_edge(UP)

        # Parametric ellipse for unit A-ball: x such that x^T A x = 1
        # Points obtained by x = inv_sqrtA * [cos t, sin t]^T
        def ellipse_point(t):
            c = math.cos(t); s = math.sin(t)
            p = mat_vec(inv_sqrtA, (c, s))
            return p

        ellipse = ParametricFunction(lambda t: ellipse_point(t), t_min=0, t_max=TAU, color=YELLOW, stroke_width=3)
        ellipse_label = MathTex("\{x: x^T A x = 1\}", font_size=24).next_to(ellipse, UR, buff=0.2)

        # Two vectors that are A-orthogonal: u = inv_sqrtA * e1, v = inv_sqrtA * e2
        u_tip = mat_vec(inv_sqrtA, (1,0))[:2]
        v_tip = mat_vec(inv_sqrtA, (0,1))[:2]
        u_arrow = Arrow(ORIGIN, u_tip, buff=0, stroke_width=6, color=BLUE)
        v_arrow = Arrow(ORIGIN, v_tip, buff=0, stroke_width=6, color=GREEN)
        u_label = MathTex("u", font_size=24).next_to(u_tip[0]*RIGHT + u_tip[1]*UP, UR, buff=0.1)
        v_label = MathTex("v", font_size=24).next_to(v_tip[0]*RIGHT + v_tip[1]*UP, UR, buff=0.1)

        # Display the A-orthogonality equation
        eq = MathTex("u^T A v = 0", font_size=28).to_edge(DOWN)

        # Group the warped scene
        warped_group = VGroup(plane, ellipse, u_arrow, v_arrow, u_label, v_label, ellipse_label)

        # --- Build scene: show the warp and the ellipse ---
        self.play(FadeIn(title), Write(ellipse_label), run_time=1.0)
        self.play(Create(plane, run_time=1.0), Create(ellipse, run_time=1.2))
        self.play(GrowArrow(u_arrow), GrowArrow(v_arrow), Write(u_label), Write(v_label), run_time=1.0)
        self.wait(0.4)

        # Show A-orthogonality (algebraic) while visually not perpendicular
        eq_box = SurroundingRectangle(eq, buff=0.15, color=WHITE)
        self.play(Write(eq), Create(eq_box), run_time=0.8)
        self.wait(0.6)

        # Emphasize that u and v look non-perpendicular in Euclidean picture
        cross_mark = VGroup(
            Line(u_arrow.get_end(), u_arrow.get_end()+0.3*(u_arrow.get_end()-ORIGIN)/np.linalg.norm(u_arrow.get_end()-ORIGIN), color=RED),
        )
        # subtle pulse on arrows to draw attention
        self.play(u_arrow.animate.set_opacity(1).scale(1.02), v_arrow.animate.set_opacity(1).scale(1.02), run_time=0.6)
        self.wait(0.4)

        # --- Introduce the unwarping map T = sqrt(A) ---
        T_label = MathTex("T = A^{1/2}", font_size=36).to_edge(UP).shift(DOWN*0.4)
        self.play(Transform(title, T_label), run_time=0.6)
        self.wait(0.2)

        # Apply T = sqrtA to the entire warped_group to unwarp it.
        # Convert sqrtA nested lists into matrix suitable for apply_matrix
        # apply_matrix expects array-like; we provide 2x2 nested lists.
        M = sqrtA  # a 2x2 nested list

        # Prepare a copy for the circle and Euclidean axes to show result for comparison
        circle = Circle(radius=1, color=YELLOW, stroke_width=3)
        circle.move_to(ORIGIN)
        unit1 = Arrow(ORIGIN, RIGHT, buff=0, color=BLUE)
        unit2 = Arrow(ORIGIN, UP, buff=0, color=GREEN)
        euclid_group = VGroup(circle, unit1, unit2)
        euclid_group.set_opacity(0)
        self.add(euclid_group)

        # Animate the unwarp: apply_matrix on the visual objects
        # The group.animate.apply_matrix method maps points by the linear map.
        self.play(warped_group.animate.apply_matrix(M), run_time=3.0)

        # After transform, the ellipse should align with the unit circle and arrows to axis directions
        # Fade-in the explicit Euclidean objects for reinforcement
        self.play(FadeIn(euclid_group, shift=0.1*UP), euclid_group.animate.set_opacity(1.0), run_time=0.8)

        # Replace labels: show that transformed u and v are standard basis
        u_label2 = MathTex("T(u)=e_1", font_size=24).next_to(unit1.get_end(), UR, buff=0.1)
        v_label2 = MathTex("T(v)=e_2", font_size=24).next_to(unit2.get_end(), UR, buff=0.1)
        self.play(Write(u_label2), Write(v_label2), run_time=0.6)

        # Show the unit circle equation to confirm unwarping
        circ_eq = MathTex("\{z: z^T z = 1\}", font_size=24).next_to(circle, UR, buff=0.2)
        self.play(Write(circ_eq), run_time=0.5)

        # Final note: keep everything for a moment and then fade out
        self.wait(1.0)
        finale = MathTex("T\;\text{straightens the A-geometry}", font_size=28).to_edge(DOWN)
        self.play(Write(finale), run_time=0.6)
        self.wait(1.2)

        # Gentle fade out to end.
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
