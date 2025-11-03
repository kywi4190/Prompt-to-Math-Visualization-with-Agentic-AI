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

class GradientParaboloidScene(ThreeDScene):
    def construct(self):
        # Camera setup (avoid zoom in set_camera_orientation per critique)
        self.set_camera_orientation(phi=60*DEGREES, theta=-60*DEGREES)
        self.move_camera(zoom=1.25, run_time=0)

        # Title hook (fixed in frame)
        title = Text("Gradient = steepest uphill", weight=BOLD).scale(0.8)
        title.to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        self.play(FadeIn(title, shift=0.4*UP), run_time=1.2)

        # Axes and surface
        axes = ThreeDAxes(x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[0, 9, 1],
                          x_length=6.5, y_length=6.5, z_length=4.5)

        def surf(u, v):
            x = u
            y = v
            z = x*x + y*y
            return np.array([x, y, z])

        surface = ParametricSurface(
            surf,
            u_range=[-2.7, 2.7],
            v_range=[-2.7, 2.7],
            resolution=(32, 32),
        )
        surface.set_style(fill_opacity=0.85, stroke_color=WHITE, stroke_opacity=0.1)
        surface.set_fill(color=PURPLE_B, opacity=0.85)

        # Ground grid (NumberPlane) with stroke opacity only
        plane = NumberPlane(x_range=[-3, 3, 1], y_range=[-3, 3, 1],
                            x_length=6.5, y_length=6.5, faded_line_ratio=2)
        plane.set_stroke(opacity=0.35)
        plane.move_to([0, 0, 0])

        # Order: axes above plane lines in Cairo; just add axes after plane
        self.play(Create(axes), run_time=1.5)
        self.play(FadeIn(surface, shift=0.4*IN), run_time=2.0)
        self.play(FadeIn(plane, shift=0.3*IN), run_time=1.0)

        # Trackers for polar position on plane
        r_tr = ValueTracker(2.0)
        t_tr = ValueTracker(0.0)

        # Helper functions
        def pos2d(r, t):
            return np.array([r*math.cos(t), r*math.sin(t), 0.0])

        def pos3d(r, t):
            x = r*math.cos(t)
            y = r*math.sin(t)
            return np.array([x, y, x*x + y*y])

        def unit_grad(t):
            # Gradient of x^2 + y^2 is (2x,2y) -> direction is (cos t, sin t)
            return np.array([math.cos(t), math.sin(t), 0.0])

        def unit_tan(t):
            # Tangent to circle r=const: (-sin t, cos t)
            return np.array([-math.sin(t), math.cos(t), 0.0])

        # Contour circle on plane (updated with r)
        circle = ParametricFunction(lambda a: pos2d(r_tr.get_value(), a),
                                    t_range=[0, TAU], include_end=False,
                                    color=GRAY_B, stroke_opacity=0.8)
        def circle_updater(m):
            new_curve = ParametricFunction(lambda a: pos2d(r_tr.get_value(), a),
                                           t_range=[0, TAU], include_end=False,
                                           color=GRAY_B, stroke_opacity=0.8)
            m.become(new_curve)
        circle.add_updater(circle_updater)

        # Base dot, lifted dot, vertical connector (3D-aware)
        base_dot = Dot(radius=0.06, color=YELLOW)
        base_dot.add_updater(lambda m: m.move_to(pos2d(r_tr.get_value(), t_tr.get_value())))

        lifted_dot = Dot(radius=0.06, color=YELLOW_B)
        lifted_dot.add_updater(lambda m: m.move_to(pos3d(r_tr.get_value(), t_tr.get_value())))

        vline = Line(start=pos2d(r_tr.get_value(), t_tr.get_value()),
                     end=pos3d(r_tr.get_value(), t_tr.get_value()),
                     color=BLUE_B, stroke_width=2.5)
        def vline_updater(m):
            p = pos2d(r_tr.get_value(), t_tr.get_value())
            q = pos3d(r_tr.get_value(), t_tr.get_value())
            m.put_start_and_end_on(p, q)
        vline.add_updater(vline_updater)

        # Gradient arrow on plane (red)
        grad_arrow = Arrow(start=pos2d(r_tr.get_value(), t_tr.get_value()),
                           end=pos2d(r_tr.get_value(), t_tr.get_value()) + 0.9*unit_grad(t_tr.get_value()),
                           buff=0, color=RED, stroke_width=6)
        def grad_updater(m):
            t = t_tr.get_value()
            p = pos2d(r_tr.get_value(), t)
            u = unit_grad(t)
            # Keep a modest constant length for clarity
            L = 1.0
            m.put_start_and_end_on(p, p + L*u)
        grad_arrow.add_updater(grad_updater)

        # Tangent arrow on plane (cyan)
        tan_arrow = Arrow(start=pos2d(r_tr.get_value(), t_tr.get_value()),
                          end=pos2d(r_tr.get_value(), t_tr.get_value()) + 0.9*unit_tan(t_tr.get_value()),
                          buff=0, color=TEAL_A, stroke_width=6)
        def tan_updater(m):
            t = t_tr.get_value()
            p = pos2d(r_tr.get_value(), t)
            v = unit_tan(t)
            L = 1.0
            m.put_start_and_end_on(p, p + L*v)
        tan_arrow.add_updater(tan_updater)

        # Right-angle marker between gradient and tangent at the base
        gap = 0.07
        seg_len = 0.25
        right_seg1 = Line([0, 0, 0], [seg_len, 0, 0], color=WHITE, stroke_width=3)
        right_seg2 = Line([0, 0, 0], [0, seg_len, 0], color=WHITE, stroke_width=3)
        ra_group = VGroup(right_seg1, right_seg2)
        def right_angle_updater(m):
            t = t_tr.get_value()
            p = pos2d(r_tr.get_value(), t)
            g = unit_grad(t)
            w = unit_tan(t)
            corner = p + gap*(g + w)
            # Reposition segments along g and w
            s1_start = corner
            s1_end = corner + seg_len*g
            s2_start = corner
            s2_end = corner + seg_len*w
            right_seg1.put_start_and_end_on(s1_start, s1_end)
            right_seg2.put_start_and_end_on(s2_start, s2_end)
        ra_group.add_updater(right_angle_updater)

        # Surface ascent direction (green) as an arrow tangent to the surface
        climb = Arrow(start=pos3d(r_tr.get_value(), t_tr.get_value()),
                      end=pos3d(r_tr.get_value(), t_tr.get_value()) + np.array([0.3, 0.0, 0.5]),
                      buff=0, color=GREEN, stroke_width=6)
        def climb_updater(m):
            r = r_tr.get_value()
            t = t_tr.get_value()
            p = pos3d(r, t)
            # Tangent direction along steepest ascent: (cos t, sin t, grad_norm)
            grad_norm = 2.0*r  # |grad f| on the plane equals 2r
            dir3 = np.array([math.cos(t), math.sin(t), grad_norm])
            # Normalize and scale to a modest visible length
            nrm = np.linalg.norm(dir3)
            d = dir3 / nrm if nrm > 1e-6 else np.array([1.0, 0.0, 0.0])
            L = 1.0
            m.put_start_and_end_on(p, p + L*d)
        climb.add_updater(climb_updater)

        # On-screen hint (fixed) about orthogonality
        hint = Tex(r"$\nabla f \perp$ contours", color=YELLOW_B).scale(0.7)
        hint.to_corner(DR).shift(0.2*UP)
        self.add_fixed_in_frame_mobjects(hint)
        hint.set_opacity(0)

        # Bring elements in
        self.play(Create(circle), run_time=1.2)
        self.play(FadeIn(base_dot, scale=1.1), FadeIn(lifted_dot, scale=1.1), run_time=1.0)
        self.play(Create(vline), run_time=1.0)
        self.play(Create(grad_arrow), Create(tan_arrow), run_time=1.0)
        self.play(FadeIn(ra_group, scale=0.9), run_time=0.8)
        self.play(hint.animate.set_opacity(1.0), run_time=0.6)

        # Begin a gentle ambient camera rotation
        self.begin_ambient_camera_rotation(rate=0.07)

        # First orbit around the circle
        self.play(t_tr.animate.set_value(TAU), run_time=8.0, rate_func=linear)
        self.wait(0.5)

        # Increase radius: slope increases outward
        self.play(r_tr.animate.set_value(2.6), run_time=4.0, rate_func=smooth)

        # Another lap
        self.play(t_tr.animate.increment_value(TAU), run_time=6.0, rate_func=linear)

        # Clean camera move: stop ambient, reframe, then resume
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=75*DEGREES, theta=-120*DEGREES, zoom=1.25, run_time=4.0)
        self.begin_ambient_camera_rotation(rate=0.05)

        # Emphasize the surface ascent arrow
        self.play(Create(climb), run_time=1.0)
        self.wait(1.0)

        # Vary radius back inward while rotating a bit more
        self.play(r_tr.animate.set_value(1.8), run_time=6.0, rate_func=smooth)
        self.play(t_tr.animate.increment_value(TAU), run_time=6.0, rate_func=linear)

        # Wrap-up text
        summary = Text("Gradient = fastest increase\nContours = constant height", 
                       t2c={"Gradient": YELLOW_B, "Contours": BLUE_A}).scale(0.7)
        summary.to_corner(UL).shift(0.8*DOWN)
        self.add_fixed_in_frame_mobjects(summary)
        self.play(FadeIn(summary, shift=0.2*UP), run_time=1.2)
        self.wait(2.8)

        # End
        self.stop_ambient_camera_rotation()
        self.play(*[FadeOut(m) for m in [hint, summary, circle, base_dot, lifted_dot, vline, grad_arrow, tan_arrow, ra_group, climb, surface, plane, axes]], run_time=1.6)
