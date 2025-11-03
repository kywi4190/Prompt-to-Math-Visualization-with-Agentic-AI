from manim import *
import numpy as np
import math

# Helper functions for geometry
TAU = 2 * math.pi

def torus_point(u, v, R=2.2, r=0.7):
    x = (R + r * math.cos(v)) * math.cos(u)
    y = (R + r * math.cos(v)) * math.sin(u)
    z = r * math.sin(v)
    return np.array([x, y, z], dtype=float)

def axis_angle_rotation_matrix(axis, angle):
    a = np.array(axis, dtype=float)
    a = a / np.linalg.norm(a)
    ax, ay, az = a
    K = np.array([[0, -az, ay], [az, 0, -ax], [-ay, ax, 0]], dtype=float)
    I = np.eye(3)
    R = I + math.sin(angle) * K + (1 - math.cos(angle)) * (K @ K)
    return R

class MorseTorusScene(ThreeDScene):
    def construct(self):
        # Camera setup
        self.set_camera_orientation(phi=65 * DEGREES, theta=45 * DEGREES, zoom=1.1)
        self.begin_ambient_camera_rotation(rate=0.05)

        # Torus parameters and rotation (tilt about a diagonal axis to break symmetry)
        R_major = 2.2
        r_minor = 0.7
        tilt_axis = (RIGHT + UP) / np.sqrt(2)
        tilt_angle = 28 * DEGREES
        Rmat = axis_angle_rotation_matrix(tilt_axis, tilt_angle)

        # Parametric torus surface
        def surf(u, v):
            p = torus_point(u, v, R_major, r_minor)
            return Rmat @ p

        torus = ParametricSurface(
            lambda u, v: surf(u, v),
            u_range=[0, TAU], v_range=[0, TAU],
            resolution=(56, 28),
            fill_opacity=1.0,
            checkerboard_colors=[BLUE_E, BLUE_D]
        )
        torus.set_shade_in_3d(True)

        # A subtle rim to help see the slice
        outline = ParametricSurface(
            lambda u, v: surf(u, v),
            u_range=[0, TAU], v_range=[0, TAU],
            resolution=(24, 12)
        )
        outline.set_style(stroke_color=BLUE_A, stroke_opacity=0.3, stroke_width=1)
        outline.set_fill(opacity=0)

        # Moving horizontal plane: z = h
        h = ValueTracker(-2.2)
        plane_size = 10
        plane = always_redraw(
            lambda: Rectangle(width=plane_size, height=plane_size*0.6, color=YELLOW, fill_opacity=0.25, stroke_opacity=0.0)
            .move_to([0, 0, h.get_value()])
        )
        h_label = always_redraw(
            lambda: MathTex("z=h", color=YELLOW_B).scale(0.8)
            .next_to(plane, UP, buff=0.2).rotate(0, axis=OUT)
        )

        # Critical points (approximate parameters on the tilted torus)
        # Choose distinct samples to represent min, two saddles, and max
        uv_min = (-math.pi/2, -math.pi/2)
        uv_sad1 = (0.35, 0.0)      # near outer rim
        uv_sad2 = (2.6, math.pi)   # near inner rim
        uv_max = (math.pi/2, math.pi/2)

        pts = [Rmat @ torus_point(*uv, R_major, r_minor) for uv in [uv_min, uv_sad1, uv_sad2, uv_max]]
        colors = [TEAL_B, ORANGE, ORANGE, RED_B]
        labels = ["min", "saddle", "saddle", "max"]

        dots = VGroup(*[Dot3D(point=p, radius=0.05, color=c) for p, c in zip(pts, colors)])
        tag_group = VGroup()
        for p, t in zip(pts, labels):
            tag = Text(t, font_size=28, color=WHITE).move_to(p + np.array([0.0, 0.0, 0.18]))
            tag_group.add(tag)

        # Right-side fixed panel showing the evolving level set schematic
        panel_title = Text("Level set  z = h", font_size=36)
        panel_title.to_corner(UR).shift(LEFT*0.3 + DOWN*0.2)

        # Create schematic shapes (in 2D frame coordinates)
        one_loop = Circle(radius=0.6, color=WHITE, stroke_width=5)
        two_loops = VGroup(Circle(radius=0.45, color=WHITE, stroke_width=5).shift(LEFT*0.5),
                           Circle(radius=0.45, color=WHITE, stroke_width=5).shift(RIGHT*0.5))
        # A simple figure-eight curve
        fig8 = ParametricFunction(
            lambda t: np.array([0.8*np.sin(t), 0.5*np.sin(t)*np.cos(t), 0]),
            t_range=[0, TAU], color=WHITE, stroke_width=5
        )
        empty_mark = Cross(stroke_color=GREY_B, stroke_width=6).scale(0.5)

        # Frame container and placement
        frame_box = RoundedRectangle(corner_radius=0.2, width=4.1, height=3.2, color=GREY_B, stroke_opacity=0.6)
        frame_box.next_to(panel_title, DOWN, buff=0.3)
        schematic_center = frame_box.get_center()
        for m in [one_loop, two_loops, fig8, empty_mark]:
            m.move_to(schematic_center)

        # Start with empty schematic
        current_schematic = empty_mark.copy()

        # Fix panel in screen space
        self.add_fixed_in_frame_mobjects(panel_title, frame_box, current_schematic)

        # Add main objects
        self.play(FadeIn(torus, shift=IN), FadeIn(outline, shift=IN), run_time=1.8)
        self.add(plane, h_label)

        # Hook: quick preview sweep
        self.play(h.animate.set_value(2.2), run_time=2.4, rate_func=smooth)
        self.play(h.animate.set_value(-2.2), run_time=1.6, rate_func=smooth)

        # Introduce critical points
        self.play(h.animate.set_value(-1.9), run_time=0.8)
        self.play(*[FadeIn(d, scale=0.5) for d in dots], run_time=1.2)
        self.play(*[FadeIn(t) for t in tag_group], run_time=1.0)
        self.wait(0.6)
        self.play(tag_group.animate.set_opacity(0.35), run_time=0.6)

        # Reset panel content to empty and ensure it's fixed in frame
        self.remove(current_schematic)
        current_schematic = empty_mark.copy()
        self.add_fixed_in_frame_mobjects(current_schematic)

        # Segment 1: Below min -> past min (empty -> one loop)
        self.play(h.animate.set_value(pts[0][2] - 0.25), run_time=1.2)
        self.wait(0.6)
        self.play(h.animate.set_value(pts[0][2] + 0.25), run_time=2.4)
        new1 = one_loop.copy()
        self.play(Transform(current_schematic, new1), run_time=1.0)

        # Between min and first saddle: grow
        self.play(h.animate.set_value((pts[1][2] + pts[0][2]) / 2.0), run_time=2.5)
        self.wait(0.5)

        # At first saddle: one loop pinches to two loops
        self.play(h.animate.set_value(pts[1][2]), run_time=1.8)
        new_fig = fig8.copy()
        self.play(Transform(current_schematic, new_fig), run_time=0.9)
        self.play(h.animate.set_value(pts[1][2] + 0.001), run_time=0.1)  # cross the saddle
        new2 = two_loops.copy()
        self.play(Transform(current_schematic, new2), run_time=0.9)

        # Between saddles: two loops persist
        mid_between_saddles = (pts[1][2] + pts[2][2]) / 2.0
        self.play(h.animate.set_value(mid_between_saddles), run_time=3.0)
        self.wait(0.4)

        # At second saddle: two loops merge back to one
        self.play(h.animate.set_value(pts[2][2]), run_time=2.0)
        new_fig2 = fig8.copy()
        self.play(Transform(current_schematic, new_fig2), run_time=0.9)
        self.play(h.animate.set_value(pts[2][2] + 0.001), run_time=0.1)
        new3 = one_loop.copy()
        self.play(Transform(current_schematic, new3), run_time=0.9)

        # Approach max and vanish
        self.play(h.animate.set_value(pts[3][2] - 0.25), run_time=2.6)
        self.play(h.animate.set_value(pts[3][2] + 0.2), run_time=2.0)
        new_empty = empty_mark.copy()
        self.play(Transform(current_schematic, new_empty), run_time=0.9)

        # Concluding highlight: summarize Morse data
        summary = VGroup(
            MathTex("\\text{critical points: } 1 \, \min,\, 2 \, \text{saddles},\, 1 \, \max", color=WHITE).scale(0.7),
            MathTex("\\text{topology changes only at these heights}", color=YELLOW_B).scale(0.7)
        ).arrange(DOWN, buff=0.2)
        self.add_fixed_in_frame_mobjects(summary)
        summary.next_to(frame_box, DOWN, buff=0.35)
        self.play(FadeIn(summary[0], shift=UP), run_time=1.0)
        self.play(FadeIn(summary[1], shift=UP), run_time=1.0)
        self.wait(1.2)

        # Clean end
        self.play(*[FadeOut(m) for m in [summary, current_schematic, frame_box, panel_title]], run_time=0.8)
        self.wait(0.6)
