from manim import *
try:
    ParametricSurface
except NameError:
    ParametricSurface = Surface
from manim import *
import numpy as np
import math

class RiemannSqrtScene(ThreeDScene):
    def construct(self):
        # Camera setup
        self.set_camera_orientation(phi=70*DEGREES, theta=45*DEGREES, zoom=1.0)

        # Base z-plane
        plane = NumberPlane(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            background_line_style={"stroke_color": GREY_B, "stroke_opacity": 0.4, "stroke_width": 1},
        )
        plane.set_z_index(-2)
        z_label = Text("z-plane", font_size=28, color=GREY_B).move_to([2.4, -2.2, 0])

        # Equation label
        eq = MathTex("w^2 = z", color=WHITE).scale(0.9)
        eq.to_corner(UR).shift([-0.5, -0.5, 0])

        # Branch cut on negative real axis
        cut = Line([0, 0, 0], [-3, 0, 0], color=RED).set_stroke(width=3, opacity=0.8)

        # Riemann surface for w^2 = z, embedded as height = Re(w) = sqrt(r) cos(theta/2)
        Rmax = 3.0
        def surface_param(sign=1):
            return ParametricSurface(
                lambda u, v: np.array([
                    u * np.cos(v),
                    u * np.sin(v),
                    sign * np.sqrt(max(u, 0.0)) * np.cos(v / 2.0),
                ]),
                u_range=[0.0, Rmax],
                v_range=[-np.pi, np.pi],
                resolution=(36, 28),
            )

        surf_plus = surface_param(+1).set_fill(color=TEAL, opacity=0.7).set_stroke(TEAL, width=0.5, opacity=0.6)
        surf_minus = surface_param(-1).set_fill(color=ORANGE, opacity=0.7).set_stroke(ORANGE, width=0.5, opacity=0.6)

        # Path in the base plane and its lift
        rho = 2.0
        circle_path = ParametricFunction(lambda t: np.array([rho*np.cos(t), rho*np.sin(t), 0]), t_range=[0, TAU], color=YELLOW)

        t_tracker = ValueTracker(0.0)

        def base_point():
            t = t_tracker.get_value()
            return np.array([rho*np.cos(t), rho*np.sin(t), 0])

        def lift_point():
            t = t_tracker.get_value()
            return np.array([rho*np.cos(t), rho*np.sin(t), np.sqrt(rho)*np.cos(t/2.0)])

        dot_base = always_redraw(lambda: Dot(point=base_point(), color=YELLOW, radius=0.06))
        dot_lift = always_redraw(lambda: Dot(point=lift_point(), color=WHITE, radius=0.065))
        connector = always_redraw(lambda: Line(base_point(), lift_point(), color=WHITE, stroke_opacity=0.3, stroke_width=2))

        # Intro: show plane and surfaces
        self.add(plane)
        self.play(FadeIn(z_label, shift=0.3*DOWN), run_time=1.0)
        self.play(Create(surf_plus), run_time=2.5)
        self.play(Create(surf_minus), run_time=2.0)
        self.play(Write(eq), run_time=1.2)

        # Show the branch cut
        self.play(Create(cut), run_time=1.0)

        # Add loop on the base and the lifted point
        self.play(Create(circle_path), FadeIn(dot_base), FadeIn(dot_lift), FadeIn(connector), run_time=1.5)

        # Slow ambient camera rotation during the loop
        self.begin_ambient_camera_rotation(rate=0.02)

        # First circuit: t from 0 to 2pi — ends on the other sheet
        self.play(t_tracker.animate.set_value(2*math.pi), rate_func=linear, run_time=20.0)
        self.wait(1.0)

        # Second circuit: t from 2pi to 4pi — returns to start sheet
        self.play(t_tracker.animate.set_value(4*math.pi), rate_func=linear, run_time=16.0)

        self.stop_ambient_camera_rotation()
        self.wait(8.0)
