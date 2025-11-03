from manim import *
import numpy as np
import math
# Optional utilities (guarded; some versions may not expose them)
try:
    from manim.utils.color import Color as _Color
except Exception:
    try:
        from manim.utils.color import ManimColor as _Color  # older naming
    except Exception:
        # Last-resort parser: parse_color returns a ManimColor
        from manim.utils.color import parse_color as _parse_color
        class _Color:
            def __new__(cls, x):
                return _parse_color(x)
Color = _Color

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
        # Initial top-down camera for 2D phase
        self.set_camera_orientation(phi=0*DEGREES, theta=-90*DEGREES, zoom=1.0)

        # Number plane
        plane = NumberPlane(x_range=[-4, 4, 1], y_range=[-3, 3, 1],
                            background_line_style={"stroke_color": GREY, "stroke_opacity": 0.5, "stroke_width": 1})
        self.play(Create(plane), run_time=1.0)

        # Arrow representing a complex number a+bi
        vec = Arrow([0, 0, 0], [1.6, 0.8, 0], buff=0, color=BLUE)
        label = always_redraw(lambda: MathTex(r"a+bi").scale(0.7).move_to(vec.get_end() + np.array([0.3, 0.3, 0])))
        self.play(Create(vec), run_time=1.0)
        self.play(Write(label), run_time=0.6)

        # Multiply by i: rotate 90 degrees
        times_i = MathTex(r"\\times\ i").scale(0.8).move_to([0.4, -0.4, 0])
        self.play(FadeIn(times_i, shift=UP*0.1), run_time=0.8)
        self.play(Rotate(vec, about_point=[0, 0, 0], angle=PI/2), run_time=1.5)
        self.play(FadeOut(times_i), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(label), run_time=0.4)

        # Show how squaring warps the plane
        thetas = np.deg2rad(np.array([-60, -20, 20, 60]))
        radii = [0.5, 1.0, 1.5]

        rays = []
        rays_sq = []
        for th in thetas:
            r_curve = ParametricFunction(
                lambda t, th=th: np.array([t*np.cos(th), t*np.sin(th), 0]),
                t_range=[0, 2], color=GREY
            )
            r_curve_sq = ParametricFunction(
                lambda t, th=th: np.array([t**2*np.cos(2*th), t**2*np.sin(2*th), 0]),
                t_range=[0, 2], color=TEAL
            )
            rays.append(r_curve)
            rays_sq.append(r_curve_sq)

        circles = []
        circles_sq = []
        for rr in radii:
            c_curve = ParametricFunction(
                lambda t, rr=rr: np.array([rr*np.cos(t), rr*np.sin(t), 0]),
                t_range=[0, TAU], color=GREY
            )
            c_curve_sq = ParametricFunction(
                lambda t, rr=rr: np.array([rr**2*np.cos(2*t), rr**2*np.sin(2*t), 0]),
                t_range=[0, TAU], color=TEAL
            )
            circles.append(c_curve)
            circles_sq.append(c_curve_sq)

        grid_group = VGroup(*rays, *circles)
        grid_group_sq = VGroup(*rays_sq, *circles_sq)

        self.play(Create(grid_group), run_time=1.5)
        self.play(Transform(grid_group, grid_group_sq), run_time=3.5)
        self.play(grid_group.animate.set_stroke(color=TEAL, width=2), run_time=0.8)

        # Transition to 3D: surface for |z^2 - 1|
        def height(x, y):
            z = complex(x, y)
            val = z*z - 1
            return 1.0/(1.0 + abs(val))

        # Move camera to oblique view
        self.move_camera(phi=70*DEGREES, theta=45*DEGREES, zoom=1.0, run_time=3.0)

        surf = ParametricSurface(
            lambda u, v: np.array([u, v, height(u, v)]),
            u_range=[-3, 3], v_range=[-3, 3],
            resolution=(24, 24),
            fill_opacity=0.8,
            checkerboard_colors=[BLUE_D, BLUE_E],
            stroke_color=BLUE_E,
            stroke_opacity=0.15,
        )
        self.play(FadeIn(surf, shift=OUT*0.2), run_time=1.8)

        # Mark the zeros at z = ±1
        zeros = [1.0, -1.0]
        markers = VGroup()
        for x0 in zeros:
            h = height(x0, 0.0)
            up_arrow = Arrow([x0, 0, 0], [x0, 0, h], buff=0, color=YELLOW)
            top_dot = Dot([x0, 0, h], color=YELLOW).scale(0.7)
            markers.add(VGroup(up_arrow, top_dot))
        self.play(Create(markers), run_time=1.5)

        # Gentle camera drift to feel the surface
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(6.0)
        self.stop_ambient_camera_rotation()
