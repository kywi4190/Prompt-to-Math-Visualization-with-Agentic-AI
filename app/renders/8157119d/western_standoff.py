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

class StandoffScene(ThreeDScene):
    def construct(self):
        # Required initial camera orientation
        self.set_camera_orientation(phi=70*DEGREES, theta=45*DEGREES, zoom=1.0)
        frame = self.camera.frame

        # Helper for normalization
        def nrm(v):
            vv = np.array(v, dtype=float)
            L = np.linalg.norm(vv)
            return vv if L == 0 else vv / L

        # Desert ground with gentle ripples
        ground = ParametricSurface(
            lambda u, v: np.array([
                u,
                v,
                0.18 * math.sin(0.25*u) * math.cos(0.25*v)
            ]),
            u_min=-9, u_max=9, v_min=-6, v_max=6, resolution=(36, 24)
        )
        ground.set_style(fill_opacity=1.0, stroke_opacity=0.15, stroke_color=Color("#c2a16f"))
        ground.set_color(Color("#d2b48c"))

        # Sky backdrop (vertical plane in x-z, constant y)
        sky = ParametricSurface(
            lambda u, v: np.array([u, -8, v]),
            u_min=-14, u_max=14, v_min=0, v_max=7, resolution=(20, 10)
        )
        sky.set_style(fill_opacity=1.0, stroke_opacity=0.0)
        sky.set_color(Color("#87ceeb"))

        # Sun (simple warm disk far away)
        sun = Circle(radius=0.6, color=Color("#ffd27f"), fill_opacity=1.0, stroke_opacity=0.0)
        sun.move_to(np.array([7.5, -7.5, 4.5]))

        self.add(sky, ground, sun)

        # Tumbleweed: a sphere that rolls along x (y=0) with rotation about y-axis
        radius = 0.35
        tumbleweed = Sphere(radius=radius, resolution=(20, 10))
        tumbleweed.set_color(Color("#8b5a2b"))
        t_param = ValueTracker(0.0)  # 0 -> left, 1 -> right
        start_x, end_x = -6.5, 6.5
        span = end_x - start_x
        tumbleweed.move_to(np.array([start_x, 0, radius]))

        def tw_updater(m, dt):
            x = start_x + span * t_param.get_value()
            m.move_to(np.array([x, 0, radius]))
            # roll without slipping: angle = distance/r
            s = (x - start_x)
            angle = s / radius
            last = getattr(m, "_last_angle", 0.0)
            m.rotate(angle - last, axis=UP, about_point=m.get_center())
            m._last_angle = angle
        tumbleweed.add_updater(tw_updater)

        # Swirling dust rings (rotating around OUT axis)
        ring1 = ParametricFunction(
            lambda t: np.array([
                0.9 * math.cos(t),
                0.00,
                0.14 * math.sin(2*t) + 0.12
            ]),
            t_range=[0, TAU],
            color=Color("#b89463")
        )
        ring2 = ParametricFunction(
            lambda t: np.array([
                0.6 * math.cos(t + 0.7),
                0.00,
                0.10 * math.sin(2*(t+0.7)) + 0.10
            ]),
            t_range=[0, TAU],
            color=Color("#c9ab7a")
        )
        swirl = VGroup(ring1, ring2)
        swirl.shift(np.array([0, 0, 0.05]))

        def swirl_updater(m, dt):
            m.rotate(0.30 * TAU * dt, axis=OUT, about_point=np.array([0, 0, 0.12]))
        swirl.add_updater(swirl_updater)

        # Cowboy factory: cylinders only
        def make_cowboy(base_point, color_hex, facing="right"):
            color = Color(color_hex)
            side = 1 if facing == "right" else -1
            base = np.array(base_point, dtype=float)

            # Torso
            torso_h = 1.6
            torso = Cylinder(radius=0.25, height=torso_h, direction=OUT)
            torso.set_color(color)
            torso.move_to(base + OUT * (torso_h/2))

            # Head (cylinder)
            head_h = 0.32
            head = Cylinder(radius=0.20, height=head_h, direction=OUT)
            head.set_color(color)
            head_center_z = torso_h + head_h/2
            head.move_to(base + OUT * head_center_z)

            # Hat: brim (thin cylinder) + crown (taller cylinder)
            brim_h = 0.06
            brim = Cylinder(radius=0.46, height=brim_h, direction=OUT)
            brim.set_color(color)
            brim.move_to(base + OUT * (torso_h + head_h + brim_h/2))

            crown_h = 0.40
            crown = Cylinder(radius=0.28, height=crown_h, direction=OUT)
            crown.set_color(color)
            crown.move_to(base + OUT * (torso_h + head_h + brim_h + crown_h/2))
            hat = VGroup(brim, crown)

            # Arms: one to each side, slightly downward toward IN
            shoulder_z = torso_h * 0.8
            shoulder_point = base + OUT * shoulder_z

            dir_gun = nrm(side*RIGHT + 0.35*IN)
            L_arm = 1.10
            arm_gun = Cylinder(radius=0.07, height=L_arm, direction=dir_gun)
            arm_gun.set_color(color)
            arm_gun.move_to(shoulder_point + dir_gun * (L_arm/2))

            dir_off = nrm(-side*RIGHT + 0.35*IN)
            arm_off = Cylinder(radius=0.07, height=1.00, direction=dir_off)
            arm_off.set_color(color)
            arm_off.move_to(shoulder_point + dir_off * 0.50)

            # Holster: short vertical cylinder on gun side
            holster = Cylinder(radius=0.12, height=0.32, direction=OUT)
            holster.set_color(color)
            holster.move_to(base + side*RIGHT*0.45 + OUT*0.65)

            # Legs: two cylinders angled outward, feet near ground
            L_leg = 1.30
            foot_L = base + LEFT*0.22 + OUT*0.05
            foot_R = base + RIGHT*0.22 + OUT*0.05
            dir_leg_L = nrm(OUT + 0.18*LEFT)
            dir_leg_R = nrm(OUT + 0.18*RIGHT)
            leg_L = Cylinder(radius=0.09, height=L_leg, direction=dir_leg_L)
            leg_L.set_color(color)
            leg_L.move_to(foot_L + dir_leg_L * (L_leg/2))
            leg_R = Cylinder(radius=0.09, height=L_leg, direction=dir_leg_R)
            leg_R.set_color(color)
            leg_R.move_to(foot_R + dir_leg_R * (L_leg/2))

            cowboy = VGroup(torso, head, hat, arm_gun, arm_off, holster, leg_L, leg_R)
            # Store key pivot points on group for later animation
            cowboy.shoulder_point = shoulder_point
            cowboy.hat_pivot = base + OUT * (torso_h + head_h + brim_h)  # brim level
            cowboy.arm_gun = arm_gun
            cowboy.arm_off = arm_off
            cowboy.hat = hat
            return cowboy

        # Build two cowboys
        left_cowboy = make_cowboy(base_point=[-3.5, 0, 0], color_hex="#6b4f2a", facing="right")
        right_cowboy = make_cowboy(base_point=[3.5, 0, 0], color_hex="#705331", facing="left")

        # Initial cinematic move: low angle on tumbleweed
        self.add(tumbleweed)
        self.play(
            frame.animate.set_euler_angles(theta=-20*DEGREES, phi=15*DEGREES).move_to(np.array([start_x+1.0, 0, 0.3])),
            run_time=2.5
        )
        self.play(t_param.animate.set_value(0.45), run_time=4.0, rate_func=linear)

        # Pull back to reveal the standoff and add dust swirl
        self.play(
            frame.animate.set_euler_angles(theta=-45*DEGREES, phi=55*DEGREES).move_to(np.array([0, 0.1, 0.6])),
            FadeIn(left_cowboy, shift=IN*0.3),
            FadeIn(right_cowboy, shift=IN*0.3),
            run_time=3.0
        )
        self.add(swirl)
        # Let tumbleweed drift a bit more
        self.play(t_param.animate.set_value(0.70), run_time=3.0, rate_func=linear)

        # Push-in to left cowboy's gun hand
        self.play(
            frame.animate.set_euler_angles(theta=-20*DEGREES, phi=35*DEGREES).move_to(left_cowboy.shoulder_point + np.array([0.6, 0.0, 0.2])),
            run_time=3.0
        )
        # Small twitch: rotate gun arm a hair about the shoulder pivot
        self.play(
            left_cowboy.arm_gun.animate.rotate(12*DEGREES, axis=RIGHT, about_point=left_cowboy.shoulder_point),
            run_time=1.8
        )
        self.play(
            left_cowboy.arm_gun.animate.rotate(-9*DEGREES, axis=RIGHT, about_point=left_cowboy.shoulder_point),
            run_time=1.2
        )

        # Slide to the right cowboy's face and tilt the hat
        self.play(
            frame.animate.set_euler_angles(theta=15*DEGREES, phi=28*DEGREES).move_to(right_cowboy.hat_pivot + np.array([-0.5, 0.0, 0.3])),
            run_time=3.0
        )
        self.play(
            right_cowboy.hat.animate.rotate(-14*DEGREES, axis=RIGHT, about_point=right_cowboy.hat_pivot),
            run_time=2.0
        )
        self.play(
            right_cowboy.hat.animate.rotate(8*DEGREES, axis=RIGHT, about_point=right_cowboy.hat_pivot),
            run_time=1.2
        )

        # Let the tumbleweed finish crossing
        self.play(t_param.animate.set_value(1.0), run_time=3.0, rate_func=linear)

        # Over-the-shoulder wide framing
        self.play(
            frame.animate.set_euler_angles(theta=-30*DEGREES, phi=52*DEGREES).move_to(np.array([-1.8, 0.1, 1.0])),
            run_time=4.0
        )

        # Both hands rise slightly (peaceful tension)
        self.play(
            left_cowboy.arm_gun.animate.rotate(18*DEGREES, axis=RIGHT, about_point=left_cowboy.shoulder_point),
            right_cowboy.arm_gun.animate.rotate(-18*DEGREES, axis=RIGHT, about_point=right_cowboy.shoulder_point),
            run_time=4.0
        )

        # A held breath
        self.wait(2.5)

        # Instead of drawing: both hats tip
        self.play(
            left_cowboy.hat.animate.rotate(-12*DEGREES, axis=RIGHT, about_point=left_cowboy.hat_pivot),
            right_cowboy.hat.animate.rotate(-12*DEGREES, axis=RIGHT, about_point=right_cowboy.hat_pivot),
            run_time=3.0
        )

        # Orbit around them slowly, then step closer
        self.play(
            frame.animate.set_euler_angles(theta=-60*DEGREES, phi=58*DEGREES).move_to(np.array([0, 0.2, 0.9])),
            run_time=5.0
        )
        self.play(
            left_cowboy.animate.shift(RIGHT*0.35),
            right_cowboy.animate.shift(LEFT*0.35),
            run_time=3.5
        )

        # Calm wind: slow the dust ring and let it fade
        swirl.remove_updater(swirl_updater)
        self.play(Rotate(swirl, angle=0.5*TAU, axis=OUT, about_point=np.array([0, 0, 0.12])), run_time=4.0, rate_func=linear)
        self.play(FadeOut(swirl, shift=IN*0.2), run_time=2.0)

        # Fade to sand and sky
        self.play(
            FadeOut(left_cowboy, shift=IN*0.2),
            FadeOut(right_cowboy, shift=IN*0.2),
            FadeOut(tumbleweed, shift=RIGHT*0.5),
            run_time=3.5
        )
        self.play(frame.animate.set_euler_angles(theta=-45*DEGREES, phi=60*DEGREES).move_to(np.array([0, 0, 0])).set_z(0), run_time=2.5)
        self.wait(1.0)
