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
        # Camera setup
        self.set_camera_orientation(phi=70*DEGREES, theta=45*DEGREES, zoom=1.0)

        # Ground plane (desert)
        sand = ParametricSurface(
            lambda u, v: np.array([u, 0, v]),
            u_range=[-8, 8], v_range=[-8, 8],
            resolution=(8, 8),
            checkerboard_colors=None,
            color=Color("#c2b280")  # sand
        )
        sand.set_opacity(1.0)

        # Subtle wind ribbons near the ground
        wind_phase = ValueTracker(0.0)
        def wind_wave(z0=0.0, amp=0.07, elev=0.06, k=2.0):
            return ParametricFunction(
                lambda t: np.array([
                    t,
                    elev + amp*np.sin(k*t + wind_phase.get_value()),
                    z0
                ]),
                t_range=[-7, 7],
                color=WHITE,
                stroke_opacity=0.28,
                use_smoothing=True
            )
        wind_lines = VGroup(
            always_redraw(lambda: wind_wave(z0=-3.0, amp=0.07, elev=0.05, k=2.0)),
            always_redraw(lambda: wind_wave(z0=0.0,  amp=0.06, elev=0.07, k=2.3)),
            always_redraw(lambda: wind_wave(z0=3.0,  amp=0.05, elev=0.05, k=2.1)),
        )

        # Helpers to build parametric cylinder and sphere (y is vertical)
        def make_cylinder(radius=0.3, height=1.0, color=GRAY_B):
            return ParametricSurface(
                lambda u, v: np.array([
                    radius*np.cos(u),
                    v,
                    radius*np.sin(u)
                ]),
                u_range=[0, TAU], v_range=[0, height],
                resolution=(28, 6), checkerboard_colors=None, color=color
            )

        def make_disk(radius=0.5, thickness=0.05, color=DARK_BROWN):
            # Thin cylinder used as a brim
            return ParametricSurface(
                lambda u, v: np.array([
                    radius*np.cos(u),
                    v,
                    radius*np.sin(u)
                ]),
                u_range=[0, TAU], v_range=[-thickness/2, thickness/2],
                resolution=(28, 2), checkerboard_colors=None, color=color
            )

        def make_sphere(radius=0.25, color=LIGHT_BROWN):
            # Centered so bottom touches ground when shifted up by radius
            return ParametricSurface(
                lambda u, v: np.array([
                    radius*np.cos(u)*np.sin(v),
                    radius*np.cos(v) + radius,
                    radius*np.sin(u)*np.sin(v)
                ]),
                u_range=[0, TAU], v_range=[0, PI],
                resolution=(28, 14), checkerboard_colors=None, color=color
            )

        # Cowboy builder
        def make_cowboy(base_x=0.0, facing="right", body_color=Color("#8b5a2b"), hat_color=Color("#4e342e")):
            body_h = 1.2
            body_r = 0.35
            head_r = 0.25

            # Body
            body = make_cylinder(radius=body_r, height=body_h, color=body_color)
            body.shift([base_x, 0, 0])

            # Head
            head = make_sphere(radius=head_r, color=interpolate_color(body_color, WHITE, 0.2))
            head.shift([base_x, body_h, 0])

            # Hat: brim + crown
            brim = make_disk(radius=0.55, thickness=0.06, color=hat_color)
            brim.shift([base_x, body_h + head_r*0.85, 0])
            crown = make_cylinder(radius=0.28, height=0.28, color=hat_color)
            crown.shift([base_x, body_h + head_r*0.85, 0])

            # Arm + gun (as a thin horizontal cylinder)
            arm_len = 0.9
            arm_r = 0.08
            arm = make_cylinder(radius=arm_r, height=arm_len, color=Color("#6d4c41"))
            # Cylinder's axis is along +y; rotate so axis aligns with +x
            arm.rotate(-PI/2, axis=OUT)  # rotate about z-axis to point along x

            # Shoulder pivot and placement
            shoulder_y = 0.8
            if facing == "right":
                pivot = np.array([base_x + body_r, shoulder_y, 0.0])
                arm.move_to(pivot + np.array([arm_len/2, 0, 0]))
                # Initial lowered angle (downward), then will raise to 0
                arm.rotate(-35*DEGREES, axis=OUT, about_point=pivot)
            else:
                pivot = np.array([base_x - body_r, shoulder_y, 0.0])
                arm.move_to(pivot + np.array([-arm_len/2, 0, 0]))
                arm.rotate(35*DEGREES, axis=OUT, about_point=pivot)

            # Little barrel at the tip
            barrel_len = 0.22
            barrel_r = 0.05
            barrel = make_cylinder(radius=barrel_r, height=barrel_len, color=GRAY_D)
            barrel.rotate(-PI/2, axis=OUT)
            if facing == "right":
                tip_center = pivot + np.array([arm_len, 0, 0])
                barrel.move_to(tip_center + np.array([barrel_len/2, 0, 0]))
                barrel.rotate(-35*DEGREES, axis=OUT, about_point=pivot)
            else:
                tip_center = pivot + np.array([-arm_len, 0, 0])
                barrel.move_to(tip_center + np.array([-barrel_len/2, 0, 0]))
                barrel.rotate(35*DEGREES, axis=OUT, about_point=pivot)

            cowboy = VGroup(body, head, brim, crown, arm, barrel)
            return cowboy, arm, barrel, pivot

        # Build cowboys
        left_cowboy, left_arm, left_barrel, left_pivot = make_cowboy(base_x=-4.0, facing="right")
        right_cowboy, right_arm, right_barrel, right_pivot = make_cowboy(base_x=4.0, facing="left")
        cowboys = VGroup(left_cowboy, right_cowboy)

        # Tumbleweed (sphere)
        tumble_r = 0.32
        tumbleweed = ParametricSurface(
            lambda u, v: np.array([
                tumble_r*np.cos(u)*np.sin(v),
                tumble_r*np.cos(v) + tumble_r,
                tumble_r*np.sin(u)*np.sin(v)
            ]),
            u_range=[0, TAU], v_range=[0, PI],
            resolution=(20, 10), checkerboard_colors=None, color=Color("#c49a6c")
        )
        tumbleweed.set_opacity(0.95)
        tumbleweed.move_to([6.0, tumble_r, -1.5])

        # Title
        title = Text("HIGH NOON", font_size=64, color=WHITE)
        title.set_opacity(0.0)
        title.move_to([0, 3.0, 0])

        # Add objects to scene
        self.add(sand)
        self.add(wind_lines)

        # 0-4s: Establishing wide
        self.play(
            FadeIn(cowboys, lag_ratio=0.1),
            run_time=4
        )

        # 4-10s: Push toward left cowboy, start wind
        self.play(
            self.camera.frame.animate.set_euler_angles(phi=70*DEGREES, theta=70*DEGREES),
            self.camera.frame.animate.set_z(0),
            self.camera.frame.animate.move_to([left_cowboy.get_center()[0], 0.7, 0]),
            self.camera.frame.animate.set_width(6),
            wind_phase.animate.increment_value(2*PI),
            run_time=6,
            rate_func=smooth
        )

        # 10-16s: Tumbleweed rolls across, hold on left
        self.add(tumbleweed)
        self.play(
            tumbleweed.animate.shift([-12.0, 0.0, 3.0]),
            Rotate(tumbleweed, angle=6*PI, axis=OUT, run_time=6, rate_func=linear),
            wind_phase.animate.increment_value(2*PI),
            run_time=6,
            rate_func=linear
        )

        # 16-23s: Pan to right cowboy
        center_right = [right_cowboy.get_center()[0], 0.7, 0]
        self.play(
            self.camera.frame.animate.set_euler_angles(phi=66*DEGREES, theta=-40*DEGREES),
            self.camera.frame.animate.move_to(center_right),
            self.camera.frame.animate.set_width(6),
            run_time=7,
            rate_func=smooth
        )

        # 23-30s: Two-shot center
        mid = [(left_cowboy.get_center()[0] + right_cowboy.get_center()[0])/2, 0.9, 0]
        self.play(
            self.camera.frame.animate.set_euler_angles(phi=56*DEGREES, theta=0*DEGREES),
            self.camera.frame.animate.move_to(mid),
            self.camera.frame.animate.set_width(8.5),
            run_time=7,
            rate_func=smooth
        )

        # 30-36s: Arms raise to level (hinge about shoulder pivot)
        self.play(
            Rotate(left_arm, angle=35*DEGREES, axis=OUT, about_point=left_pivot),
            Rotate(right_arm, angle=-35*DEGREES, axis=OUT, about_point=right_pivot),
            Rotate(left_cowboy[5], angle=35*DEGREES, axis=OUT, about_point=left_pivot),   # left_barrel index 5
            Rotate(right_cowboy[5], angle=-35*DEGREES, axis=OUT, about_point=right_pivot), # right_barrel index 5
            run_time=6,
            rate_func=smooth
        )

        # 36-44s: Slow orbit around them, keep both in frame
        self.play(
            self.camera.frame.animate.set_euler_angles(phi=52*DEGREES, theta=40*DEGREES),
            self.camera.frame.animate.move_to(mid),
            self.camera.frame.animate.set_width(9.0),
            run_time=8,
            rate_func=there_and_back_with_pause
        )

        # 44-52s: Crane up and widen
        self.play(
            self.camera.frame.animate.set_euler_angles(phi=78*DEGREES, theta=25*DEGREES),
            self.camera.frame.animate.move_to([0, 1.2, 0]),
            self.camera.frame.animate.set_width(12.0),
            run_time=8,
            rate_func=smooth
        )

        # 52-60s: Title fade-in, hold
        self.add_fixed_in_frame_mobjects(title)
        self.play(title.animate.set_opacity(1.0), run_time=3)
        self.wait(5)
