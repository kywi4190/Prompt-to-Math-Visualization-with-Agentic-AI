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

class BronsonVectorScene(ThreeDScene):
    def construct(self):
        # Axes
        axes = ThreeDAxes(
            x_range=[0, 3.5, 1], y_range=[0, 3.5, 1], z_range=[0, 3.5, 1],
            x_length=6, y_length=6, z_length=4.8,
        )

        # Camera orientation (avoid zoom kwarg for version safety)
        self.set_camera_orientation(phi=60 * DEGREES, theta=45 * DEGREES)

        # Subtle reference planes using Surface (version-safe)
        xy_plane = Surface(
            lambda u, v: axes.c2p(u, v, 0),
            u_range=[0, 3.2], v_range=[0, 3.2], resolution=(6, 6),
            checkerboard_colors=[GREY_B, GREY_B],
        ).set_opacity(0.08)
        yz_plane = Surface(
            lambda u, v: axes.c2p(0, u, v),
            u_range=[0, 3.2], v_range=[0, 3.2], resolution=(6, 6),
            checkerboard_colors=[GREY_B, GREY_B],
        ).set_opacity(0.08)
        xz_plane = Surface(
            lambda u, v: axes.c2p(u, 0, v),
            u_range=[0, 3.2], v_range=[0, 3.2], resolution=(6, 6),
            checkerboard_colors=[GREY_B, GREY_B],
        ).set_opacity(0.08)
        planes = VGroup(xy_plane, yz_plane, xz_plane)

        # Draw axes and planes
        self.play(Create(axes), run_time=1.2)
        self.play(FadeIn(planes), run_time=0.8)

        # Slow ambient rotation for depth
        self.begin_ambient_camera_rotation(rate=0.05)

        # Basis direction arrows
        origin = axes.c2p(0, 0, 0)
        e1 = Arrow(start=origin, end=axes.c2p(3, 0, 0), buff=0, color=ORANGE, stroke_width=6)
        e2 = Arrow(start=origin, end=axes.c2p(0, 3, 0), buff=0, color=BLUE, stroke_width=6)
        e3 = Arrow(start=origin, end=axes.c2p(0, 0, 3), buff=0, color=GREEN, stroke_width=6)
        self.play(Create(e1), Create(e2), Create(e3), run_time=1.0)

        # Axis labels that face the camera
        x_end = axes.c2p(3.5, 0, 0)
        y_end = axes.c2p(0, 3.5, 0)
        z_end = axes.c2p(0, 0, 3.5)
        lbl_x = Text("Chef", font_size=28, color=ORANGE).move_to(x_end)
        lbl_y = Text("Rap", font_size=28, color=BLUE).move_to(y_end)
        lbl_z = Text("TV", font_size=28, color=GREEN).move_to(z_end)
        axes_labels = VGroup(lbl_x, lbl_y, lbl_z)
        self.add_fixed_orientation_mobjects(axes_labels)
        self.play(FadeIn(axes_labels, shift=0.2 * OUT), run_time=0.8)

        # Title as fixed overlay (screen-space)
        title = Text("A persona as a vector", font_size=36)
        title.to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1.0)
        self.wait(0.5)

        # The persona vector and its components
        a_val, b_val, c_val = 2.6, 1.7, 2.1
        tip = axes.c2p(a_val, b_val, c_val)
        persona_vec = Arrow(start=origin, end=tip, buff=0, color=YELLOW, stroke_width=8)
        self.play(Create(persona_vec), run_time=1.6)
        tip_dot = Dot(point=tip, radius=0.05, color=YELLOW)
        self.play(FadeIn(tip_dot), run_time=0.3)
        self.wait(0.4)

        comp_x = Line(origin, axes.c2p(a_val, 0, 0), color=ORANGE, stroke_width=6)
        comp_y = Line(axes.c2p(a_val, 0, 0), axes.c2p(a_val, b_val, 0), color=BLUE, stroke_width=6)
        comp_z = Line(axes.c2p(a_val, b_val, 0), tip, color=GREEN, stroke_width=6)
        self.play(Create(comp_x), run_time=0.7)
        self.play(Create(comp_y), run_time=0.7)
        self.play(Create(comp_z), run_time=0.7)

        # Keep key items in front for visibility
        self.add_foreground_mobjects(persona_vec, tip_dot, comp_x, comp_y, comp_z)

        # Dashed drops to planes
        drop_xy = DashedLine(tip, axes.c2p(a_val, b_val, 0), dash_length=0.1, color=WHITE, stroke_width=2)
        drop_yz = DashedLine(tip, axes.c2p(0, b_val, c_val), dash_length=0.1, color=WHITE, stroke_width=2)
        drop_xz = DashedLine(tip, axes.c2p(a_val, 0, c_val), dash_length=0.1, color=WHITE, stroke_width=2)
        self.play(Create(VGroup(drop_xy, drop_yz, drop_xz)), run_time=0.9)
        self.wait(0.4)

        # Tags near the tip that face the camera
        tag_rap = Text("rap", font_size=26, color=BLUE_C).move_to(axes.c2p(a_val - 0.2, b_val + 0.35, c_val))
        tag_chef = Text("chef", font_size=26, color=ORANGE).move_to(axes.c2p(a_val + 0.35, b_val - 0.15, c_val + 0.05))
        tag_tv = Text("tv", font_size=26, color=GREEN).move_to(axes.c2p(a_val - 0.15, b_val - 0.25, c_val + 0.35))
        tag_city = Text("city", font_size=26, color=YELLOW_E).move_to(axes.c2p(a_val + 0.25, b_val + 0.2, c_val + 0.2))
        self.add_fixed_orientation_mobjects(tag_rap, tag_chef, tag_tv, tag_city)
        self.add_foreground_mobjects(tag_rap, tag_chef, tag_tv, tag_city)
        self.play(FadeIn(VGroup(tag_rap, tag_chef), shift=0.2 * OUT), run_time=0.6)
        self.play(FadeIn(VGroup(tag_tv, tag_city), shift=0.2 * OUT), run_time=0.6)
        self.wait(0.6)

        # Equation and small screen-space details
        eq = MathTex(r"v \!= (a, b, c)", font_size=44)
        eq.to_corner(DR)
        detail_album = Text("albums", font_size=24).next_to(eq, DOWN, buff=0.2).align_to(eq, RIGHT)
        detail_tv = Text("hours of TV", font_size=24).next_to(detail_album, DOWN, buff=0.15).align_to(eq, RIGHT)
        self.add_fixed_in_frame_mobjects(eq, detail_album, detail_tv)
        self.play(Write(eq), run_time=0.8)
        self.play(FadeIn(detail_album, shift=0.1 * RIGHT), FadeIn(detail_tv, shift=0.1 * RIGHT), run_time=0.8)

        # Intentional change of viewpoint (stop ambient for a smooth programmed move)
        self.stop_ambient_camera_rotation()
        self.wait(0.2)
        self.move_camera(phi=55 * DEGREES, theta=70 * DEGREES, run_time=5.0)
        self.wait(0.6)
        self.move_camera(phi=65 * DEGREES, theta=30 * DEGREES, run_time=5.0)
        self.wait(0.5)

        # Hold briefly to finish
        self.wait(0.5)
