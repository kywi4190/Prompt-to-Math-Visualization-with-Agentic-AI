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
        # Helper for z^2 mapping on the plane
        def square_point(p):
            x, y = p[0], p[1]
            return np.array([x * x - y * y, 2 * x * y, 0.0])

        # 2D Argand plane (drawn in 3D-safe coordinates)
        plane = NumberPlane(
            x_range=[-5, 5, 1],
            y_range=[-3, 3, 1],
            background_line_style={
                "stroke_color": GREY_B,
                "stroke_opacity": 0.4,
                "stroke_width": 1,
            },
        ).set_stroke(color=GREY_B, width=1, opacity=0.5)

        self.play(Create(plane), run_time=1.2)

        # A sample complex number z = a + bi
        a, b = 2.0, 1.2
        z_vec = Arrow([0, 0, 0], [a, b, 0], buff=0.0, color=WHITE,
                      max_stroke_width_to_length_ratio=6, stroke_width=4)
        z_dot = Dot(radius=0.06, color=WHITE).move_to([a, b, 0])
        z_label = MathTex(r"z = a + bi", font_size=36).next_to(z_dot, UR, buff=0.2)

        self.play(GrowArrow(z_vec), run_time=1.2)
        self.play(FadeIn(z_dot, scale=1.2), Write(z_label), run_time=0.8)

        # Angle annotation between x-axis and current z (robust with always_redraw)
        x_axis_line = Line([0, 0, 0], [2.5, 0, 0])
        vec_line = always_redraw(lambda: Line([0, 0, 0], z_dot.get_center()))
        angle_arc = always_redraw(lambda: Angle(x_axis_line, vec_line, radius=0.8, color=YELLOW))
        self.add(angle_arc)

        # Multiplication by i: rotate 90 degrees CCW, then back
        z_group = VGroup(z_vec, z_dot)
        self.play(Rotate(z_group, angle=90 * DEGREES, about_point=ORIGIN), run_time=2.0)
        self.wait(0.4)
        self.play(Rotate(z_group, angle=-90 * DEGREES, about_point=ORIGIN), run_time=1.0)
        self.play(FadeOut(angle_arc), run_time=0.6)
        self.remove(angle_arc, vec_line)

        # Compare z and z^2 simultaneously
        w_tip_dot = always_redraw(
            lambda: Dot(radius=0.06, color=ORANGE).move_to(square_point(z_vec.get_end()))
        )
        w_vec = always_redraw(
            lambda: Arrow(
                [0, 0, 0], square_point(z_vec.get_end()), buff=0.0, color=ORANGE,
                max_stroke_width_to_length_ratio=6, stroke_width=4
            )
        )
        w_label = always_redraw(
            lambda: MathTex(r"z^2", font_size=36).next_to(w_tip_dot, UR, buff=0.2)
        )

        self.add(w_vec, w_tip_dot)
        self.play(Write(w_label), run_time=0.8)
        # One full turn of z; z^2 turns twice and changes length accordingly
        self.play(Rotate(z_group, angle=TAU, about_point=ORIGIN), run_time=6.0)
        self.play(FadeOut(w_label), run_time=0.6)
        self.remove(w_vec, w_tip_dot)

        # Demonstrate multiplication by a + bi via a linear map on R^2
        aM, bM = 1.2, 0.6
        det = aM * aM + bM * bM
        M2 = np.array([[aM, -bM], [bM, aM]])
        M3 = np.array([
            [M2[0, 0], M2[0, 1], 0],
            [M2[1, 0], M2[1, 1], 0],
            [0, 0, 1],
        ])
        Minv2 = (1.0 / det) * np.array([[aM, bM], [-bM, aM]])
        Minv3 = np.array([
            [Minv2[0, 0], Minv2[0, 1], 0],
            [Minv2[1, 0], Minv2[1, 1], 0],
            [0, 0, 1],
        ])

        plane_copy = plane.copy().set_stroke(opacity=0.8)
        overlay_mul = Text("Multiply by a + bi = rotate + scale", font_size=36).to_edge(UP)
        self.add_fixed_in_frame_mobjects(overlay_mul)
        self.play(FadeIn(overlay_mul, shift=0.2 * UP), FadeIn(plane_copy), run_time=0.6)

        self.play(
            plane_copy.animate.apply_matrix(M3),
            z_vec.animate.apply_matrix(M3),
            z_dot.animate.apply_matrix(M3),
            run_time=3.0,
        )
        self.wait(0.6)
        self.play(
            z_vec.animate.apply_matrix(Minv3),
            z_dot.animate.apply_matrix(Minv3),
            FadeOut(plane_copy),
            run_time=1.2,
        )
        self.play(FadeOut(overlay_mul), run_time=0.6)
        self.remove_fixed_in_frame_mobjects(overlay_mul)
        # Reposition label near the restored dot
        self.play(z_label.animate.next_to(z_dot, UR, buff=0.2), run_time=0.6)

        # 3D visualization: height = |z^2 + 1|
        self.set_camera_orientation(phi=70 * DEGREES, theta=45 * DEGREES, zoom=1.0)

        def height_abs_z2_plus_1(x, y):
            # |z^2 + 1| where z = x + iy
            real = x * x - y * y + 1.0
            imag = 2.0 * x * y
            return math.sqrt(real * real + imag * imag)

        surface = ParametricSurface(
            lambda u, v: np.array([u, v, height_abs_z2_plus_1(u, v)]),
            u_range=[-3, 3], v_range=[-3, 3],
            resolution=(28, 28),
            checkerboard_colors=[BLUE_E, BLUE_B],
            fill_opacity=0.8,
            stroke_color=WHITE, stroke_opacity=0.12,
        )

        self.play(Create(surface), run_time=2.6)

        overlay1 = Text("Height = |z^2 + 1|", font_size=36).to_edge(UP)
        self.add_fixed_in_frame_mobjects(overlay1)
        self.play(FadeIn(overlay1, shift=0.2 * UP), run_time=0.8)

        # Mark the roots where |z^2 + 1| = 0: z = i and z = -i (height 0)
        root_i = Dot([0, 1, 0], color=RED, radius=0.08)
        root_minusi = Dot([0, -1, 0], color=RED, radius=0.08)
        i_label = MathTex(r"i", font_size=36).next_to(root_i, UR, buff=0.1)
        mi_label = MathTex(r"-i", font_size=36).next_to(root_minusi, DR, buff=0.1)
        self.play(FadeIn(root_i, scale=1.2), FadeIn(root_minusi, scale=1.2), run_time=0.8)
        self.add(i_label, mi_label)

        # Rotate the camera to explore the landscape
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(22.0)

        self.play(FadeOut(overlay1), run_time=0.8)
        self.stop_ambient_camera_rotation()
        self.remove_fixed_in_frame_mobjects(overlay1)

        # Wrap up
        self.play(FadeOut(surface), run_time=2.0)
        outro = Text("Multiply = rotate + scale; roots: height 0", font_size=36).to_edge(UP)
        self.add_fixed_in_frame_mobjects(outro)
        self.play(FadeIn(outro, shift=0.2 * UP), run_time=1.2)
        self.wait(1.8)
        self.play(FadeOut(outro), run_time=0.8)
        self.remove_fixed_in_frame_mobjects(outro)
        # End with the original 2D scene visible for a moment
        self.wait(0.6)
