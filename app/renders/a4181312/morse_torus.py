from manim import *
try:
    ParametricSurface
except NameError:
    ParametricSurface = Surface
from manim import *
import numpy as np
import math

class MorseTorusScene(ThreeDScene):
    def construct(self):
        # Parameters for the torus
        R = 2.2  # major radius
        r = 0.9  # minor radius
        eps = 0.03

        # Camera setup
        self.set_camera_orientation(phi=70*DEGREES, theta=45*DEGREES, zoom=1.0)
        self.begin_ambient_camera_rotation(rate=0.02)

        # Torus surface (parametric)
        def torus_func(u, v):
            x = (R + r * math.cos(v)) * math.cos(u)
            y = (R + r * math.cos(v)) * math.sin(u)
            z = r * math.sin(v)
            return np.array([x, y, z])

        torus = ParametricSurface(
            lambda u, v: torus_func(u, v),
            u_range=[0, TAU],
            v_range=[0, TAU],
            resolution=(36, 18),
            fill_color=BLUE_E,
            checkerboard_colors=[BLUE_E, BLUE_D],
        )
        torus.set_style(fill_opacity=0.65, stroke_color=WHITE, stroke_opacity=0.25, stroke_width=0.5)

        # Bring in the torus
        self.add(torus)
        self.play(FadeIn(torus), run_time=1.5)

        # Title (fixed in frame)
        title = Text("Morse theory by slicing a torus", font_size=42)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1.0)
        self.wait(0.6)
        self.play(FadeOut(title), run_time=0.7)

        # Height tracker for slicing plane
        h = ValueTracker(-r - 0.6)

        # Slicing plane (a large square oriented in the xy-plane)
        plane = Square(side_length=8.0)
        plane.set_fill(YELLOW, opacity=0.15)
        plane.set_stroke(YELLOW, opacity=0.2, width=2)
        plane.add_updater(lambda m: m.move_to(np.array([0.0, 0.0, h.get_value()])))
        self.add(plane)

        # Level-set circles: intersection of torus with z = h
        def level_circles(curr_h: float) -> VGroup:
            vg = VGroup()
            if abs(curr_h) > r + 1e-6:
                return vg
            # Clamp safely
            val = max(-1.0, min(1.0, curr_h / r))
            v1 = math.asin(val)
            v2 = math.pi - v1
            a1 = R + r * math.cos(v1)
            a2 = R + r * math.cos(v2)
            # Near the critical heights, show a single circle
            if abs(abs(curr_h) - r) <= 1e-3:
                a = R
                loop = ParametricFunction(
                    lambda t: np.array([a * math.cos(t), a * math.sin(t), curr_h]),
                    t_range=[0, TAU],
                    color=YELLOW,
                )
                loop.set_stroke(width=6, opacity=0.95)
                vg.add(loop)
                return vg
            # Generic case: two circles, inner and outer
            for a, col, wid in [
                (a1, BLUE_C, 4),
                (a2, RED_C, 4),
            ]:
                loop = ParametricFunction(
                    lambda t, aa=a: np.array([aa * math.cos(t), aa * math.sin(t), curr_h]),
                    t_range=[0, TAU],
                    color=col,
                )
                loop.set_stroke(width=wid, opacity=0.95)
                vg.add(loop)
            return vg

        curves = always_redraw(lambda: level_circles(h.get_value()))
        self.add(curves)

        # HUD: counter for number of loops
        hud_label = Text("Loops:", font_size=36)
        hud_label.to_corner(UR).shift(LEFT*0.4)
        hud_num = Integer(0, font_size=36)

        def loops_count(val: float) -> int:
            if abs(val) < r - eps:
                return 2
            if abs(abs(val) - r) <= eps:
                return 1
            return 0

        def upd_num(m: Integer):
            m.set_value(loops_count(h.get_value()))
            m.next_to(hud_label, RIGHT, buff=0.25)
        hud_num.add_updater(upd_num)

        self.add_fixed_in_frame_mobjects(hud_label, hud_num)

        # Beat labels (fixed in frame)
        birth = Text("birth of a loop", font_size=36, color=YELLOW)
        birth.to_corner(DL).shift(UP*0.3)
        saddle = Text("saddle level", font_size=36, color=TEAL_C)
        saddle.to_corner(DL).shift(UP*0.3)
        merge = Text("merge to one loop", font_size=36, color=ORANGE)
        merge.to_corner(DL).shift(UP*0.3)
        summary = Text("0 → 1 → 2 → 1 → 0", font_size=44)
        summary.to_edge(UP).shift(DOWN*0.3)
        topo1 = Text("Critical heights encode topology", font_size=40)
        topo1.to_edge(UP).shift(DOWN*0.3)
        topo2 = Text("Morse theory = topology from slices", font_size=40)
        topo2.to_edge(UP).shift(DOWN*0.3)

        # Animate the sweep: up to bottom critical height
        self.play(h.animate.set_value(-r), run_time=4.0, rate_func=smooth)
        self.add_fixed_in_frame_mobjects(birth)
        self.play(FadeIn(birth), run_time=0.4)
        self.wait(0.8)
        self.play(FadeOut(birth), run_time=0.4)

        # Bottom to middle (show two loops)
        self.play(h.animate.set_value(0.0), run_time=8.0, rate_func=linear)
        self.add_fixed_in_frame_mobjects(saddle)
        self.play(FadeIn(saddle), run_time=0.4)
        self.wait(2.0)
        self.play(FadeOut(saddle), run_time=0.4)

        # Middle to top critical height
        self.play(h.animate.set_value(+r), run_time=8.0, rate_func=linear)
        self.add_fixed_in_frame_mobjects(merge)
        self.play(FadeIn(merge), run_time=0.4)
        self.wait(1.2)
        self.play(FadeOut(merge), run_time=0.4)

        # Past the top: no loops
        self.play(h.animate.set_value(+r + 0.6), run_time=3.0, rate_func=smooth)
        self.wait(1.4)

        # Summary and topology connection
        self.add_fixed_in_frame_mobjects(summary)
        self.play(FadeIn(summary), run_time=0.6)
        self.wait(3.8)
        self.play(FadeOut(summary), run_time=0.6)

        self.add_fixed_in_frame_mobjects(topo1)
        self.play(FadeIn(topo1), run_time=0.6)
        self.wait(4.8)
        self.play(FadeOut(topo1), run_time=0.6)

        self.add_fixed_in_frame_mobjects(topo2)
        self.play(FadeIn(topo2), run_time=0.6)
        self.wait(6.8)
        self.play(FadeOut(topo2), run_time=0.6)

        self.wait(2.0)

        # Clean up updaters
        plane.clear_updaters()
        hud_num.clear_updaters()
        self.stop_ambient_camera_rotation()
