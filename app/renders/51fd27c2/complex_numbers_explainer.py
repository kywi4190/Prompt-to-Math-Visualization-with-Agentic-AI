from manim import *
import numpy as np
import math
# Optional utilities (guarded; some versions may not expose them)
try:
    from manim.utils.color import Color
except Exception:
    def Color(x): return x  # accept hex strings or named colors

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

class ComplexNumbersScene(ThreeDScene):
    def construct(self):
        # Camera: start top-down for clean 2D feel
        self.set_camera_orientation(phi=90*DEGREES, theta=0*DEGREES, zoom=1.1)

        # Helper: color by argument (angle)
        def angle_color(theta):
            # Map [-pi, pi] -> [0, 1]
            t = (theta + math.pi) / (2 * math.pi)
            return interpolate_color(Color(Color(BLUE)), Color(Color(YELLOW)), t)

        # --- Hook: real line and missing solution ---
        eq = MathTex(r"x^2 + 1 = 0").to_edge(UP)
        real_axis = Line([-5, 0, 0], [5, 0, 0], color=GRAY)
        self.play(Write(eq), Create(real_axis), run_time=3.0)

        dot_neg1 = Dot([-1, 0, 0], color=YELLOW)
        lab_neg1 = MathTex(r"-1").scale(0.6).next_to([-1, 0, 0], DOWN)
        self.play(FadeIn(dot_neg1, scale=0.5), Write(lab_neg1), run_time=0.8)

        imag_axis = Line([0, -3.2, 0], [0, 3.2, 0], color=GRAY)
        self.play(Create(imag_axis), run_time=1.2)

        dot_pos_i = Dot([0, 1, 0], color=GREEN)
        dot_neg_i = Dot([0, -1, 0], color=GREEN)
        lab_i = MathTex(r"i").scale(0.6).next_to([0, 1, 0], LEFT)
        lab_mi = MathTex(r"-i").scale(0.6).next_to([0, -1, 0], LEFT)
        self.play(FadeIn(dot_pos_i), FadeIn(dot_neg_i), FadeIn(lab_i), FadeIn(lab_mi), run_time=0.8)

        # --- Setup: complex plane and polar view ---
        plane = NumberPlane(x_range=[-4, 4, 1], y_range=[-3, 3, 1],
                            background_line_style={"stroke_opacity": 0.35, "stroke_color": BLUE_E, "stroke_width": 1})
        re_label = Tex("Re").scale(0.6).move_to([4.4, -0.3, 0])
        im_label = Tex("Im").scale(0.6).move_to([-0.4, 3.2, 0])
        self.play(FadeOut(VGroup(real_axis, dot_neg1, lab_neg1), shift=DOWN*0.2), FadeTransform(imag_axis, plane),
                  FadeIn(re_label), FadeIn(im_label), run_time=1.8)

        # A sample complex number z
        z_point = np.array([2.0, 1.0, 0.0])
        z_arrow = Arrow(ORIGIN, z_point, buff=0, color=YELLOW)
        theta = math.atan2(z_point[1], z_point[0])
        r = math.sqrt(z_point[0]**2 + z_point[1]**2)
        theta_arc = Arc(arc_center=ORIGIN, start_angle=0, angle=theta, radius=0.8, color=ORANGE)
        z_dot = Dot(z_point, color=YELLOW)
        polar_text = MathTex(r"z = r e^{i\\theta}").scale(0.7).next_to([2.6, 1.4, 0], UR)
        self.play(Create(z_arrow), Create(theta_arc), FadeIn(z_dot), run_time=1.8)
        self.play(Write(polar_text), run_time=1.2)

        # --- Multiplication by i: 90-degree rotation ---
        def make_sample_arrows(n=6, radius=1.4):
            arrows = []
            for k in range(n):
                ang = 2 * math.pi * k / n
                end = np.array([radius * math.cos(ang), radius * math.sin(ang), 0])
                arr = Arrow(ORIGIN, end, buff=0, stroke_width=3, color=angle_color(ang))
                arrows.append(arr)
            return VGroup(*arrows)

        samples = make_sample_arrows(n=8, radius=1.6)
        mul_i_text = Tex("\u00D7 i: rotate 90$^\circ$", tex_template=TexFontTemplates.comic_sans).scale(0.5)
        mul_i_text.next_to([-2.6, 2.2, 0], UL)
        self.play(Create(samples), run_time=1.0)
        self.play(FadeIn(mul_i_text, shift=UP*0.1), run_time=0.6)
        self.play(samples.animate.rotate(90*DEGREES, about_point=ORIGIN), run_time=2.5)
        i2_text = MathTex(r"i^2 = -1").scale(0.7).next_to([-2.4, 1.6, 0], UL)
        self.play(samples.animate.rotate(90*DEGREES, about_point=ORIGIN), run_time=2.5)
        self.play(FadeIn(i2_text), run_time=0.8)

        # --- Multiply by a+bi: rotate + scale (linear map) ---
        ab_text = Tex("Multiply by $a+bi$ = rotate + scale").scale(0.6).to_edge(LEFT).shift(UP*2.6)
        self.play(Write(ab_text), run_time=0.8)

        a, b = 1.2, 0.5
        M = np.array([[a, -b], [b, a]])

        # little right-angle marker to suggest conformality
        p = np.array([1.0, 1.0, 0.0])
        L_shape = VGroup(
            Line(p, p + np.array([0.35, 0, 0]), color=RED),
            Line(p, p + np.array([0, 0.35, 0]), color=RED)
        )
        self.add(L_shape)

        # Prepare transformed copies
        plane_t = plane.copy(); plane_t.apply_matrix(M)
        samples_t = samples.copy(); samples_t.apply_matrix(M)
        z_arrow_t = z_arrow.copy(); z_arrow_t.apply_matrix(M)
        z_dot_t = z_dot.copy(); z_dot_t.apply_matrix(M)
        L_t = L_shape.copy(); L_t.apply_matrix(M)

        self.play(
            Transform(plane, plane_t),
            Transform(samples, samples_t),
            Transform(z_arrow, z_arrow_t),
            Transform(z_dot, z_dot_t),
            Transform(L_shape, L_t),
            run_time=3.5
        )
        conf_text = Tex("angles preserved (conformal)").scale(0.5).next_to([2.6, -2.2, 0], DR)
        self.play(FadeIn(conf_text), run_time=1.0)

        # --- Reset to plain plane; z^2 mapping on unit circle ---
        self.play(FadeOut(VGroup(samples, z_arrow, z_dot, L_shape, ab_text, mul_i_text, i2_text, conf_text, polar_text)), run_time=1.0)
        plane2 = NumberPlane(x_range=[-4, 4, 1], y_range=[-3, 3, 1],
                             background_line_style={"stroke_opacity": 0.35, "stroke_color": BLUE_E, "stroke_width": 1})
        self.play(Transform(plane, plane2), run_time=1.0)

        unit_circle = Circle(radius=1.4, color=WHITE, stroke_opacity=0.7)
        self.play(Create(unit_circle), run_time=0.8)

        N = 10
        angles = [2*math.pi*k/N for k in range(N)]
        dots = VGroup(*[Dot([1.4*math.cos(t), 1.4*math.sin(t), 0], color=angle_color(t)) for t in angles])
        self.play(FadeIn(dots), run_time=1.0)

        sq_text = Tex("$z\mapsto z^2$: doubles angles").scale(0.6).next_to([-2.6, 2.2, 0], UL)
        self.play(FadeIn(sq_text), run_time=0.8)

        # Target positions: radius squared (1.4^2) on doubled angles
        R2 = 1.4**2
        dots_target = VGroup(*[Dot([R2*math.cos(2*t), R2*math.sin(2*t), 0], color=angle_color(2*t)) for t in angles])
        self.play(Transform(dots, dots_target), run_time=3.0)
        self.wait(1.0)

        # --- 3D view: |z| as height (cone) ---
        self.play(FadeOut(VGroup(dots, unit_circle, re_label, im_label, sq_text, lab_i, lab_mi, dot_pos_i, dot_neg_i)), run_time=1.0)

        axes3d = ThreeDAxes(x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[0, 3.5, 1])
        self.play(FadeIn(axes3d), run_time=1.0)

        def cone(u, v):
            return np.array([u, v, math.sqrt(u*u + v*v)])
        surface = ParametricSurface(
            cone,
            u_range=[-2.2, 2.2], v_range=[-2.2, 2.2],
            resolution=(24, 24),
            fill_color=BLUE_E, fill_opacity=0.6, stroke_color=BLUE_E, stroke_opacity=0.2
        )
        self.play(Create(surface), run_time=2.0)

        # Move camera to 3D view
        self.move_camera(phi=70*DEGREES, theta=45*DEGREES, run_time=2.0)

        # Show |z| as height for our earlier z
        z0 = np.array([2.0, 1.0, 0.0])
        r0 = math.sqrt(z0[0]**2 + z0[1]**2)
        z_base = Dot(z0, color=YELLOW)
        z_up = Line(z0, np.array([z0[0], z0[1], r0]), color=YELLOW)
        mod_label = MathTex(r"|z|").scale(0.7).move_to([z0[0], z0[1], r0+0.25])
        self.play(FadeIn(z_base), Create(z_up), FadeIn(mod_label), run_time=1.5)

        # Concluding message with slow camera motion
        conclude = Text("Complex numbers: rotation + scaling made algebraic", font_size=36)
        conclude.move_to([0, -2.4, 0])
        self.play(FadeIn(conclude), run_time=1.2)
        self.begin_ambient_camera_rotation(rate=0.05)
        self.wait(20)
        self.stop_ambient_camera_rotation()
