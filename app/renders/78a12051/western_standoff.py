from manim import *
try:
    ParametricSurface
except NameError:
    ParametricSurface = Surface
from manim import *
import numpy as np
import math

class WesternStandoffScene(ThreeDScene):
    def construct(self):
        # Camera setup
        self.set_camera_orientation(phi=80*DEGREES, theta=60*DEGREES, zoom=1.4)

        # Helpers: parametric cylinder and sphere
        def cylinder_surface(r=0.3, h=1.0, color=GRAY_E, opacity=1.0, resolution=(32, 12)):
            surf = ParametricSurface(
                lambda u, v: np.array([r*np.cos(u), r*np.sin(u), v]),
                u_min=0, u_max=TAU, v_min=0, v_max=h,
                resolution=resolution,
            )
            surf.set_color(color)
            surf.set_opacity(opacity)
            return surf

        def sphere_surface(R=0.4, color=YELLOW_E, opacity=1.0, resolution=(32, 16)):
            # v in [0, pi], u in [0, 2pi]
            surf = ParametricSurface(
                lambda u, v: np.array([
                    R*np.cos(u)*np.sin(v),
                    R*np.sin(u)*np.sin(v),
                    R*np.cos(v),
                ]),
                u_min=0, u_max=TAU, v_min=0, v_max=PI,
                resolution=resolution,
            )
            surf.set_color(color)
            surf.set_opacity(opacity)
            return surf

        # Ground plane (sand) and distant vertical sky panel
        ground = Surface(
            lambda u, v: np.array([u, v, 0]),
            u_range=[-7, 7], v_range=[-4, 4], resolution=(8, 8)
        )
        ground.set_style(fill_color=Color("#C2B280"), fill_opacity=1.0, stroke_width=0)

        sky = Surface(
            lambda u, v: np.array([u, -6, v]),
            u_range=[-8, 8], v_range=[0, 4], resolution=(6, 4)
        )
        sky.set_style(fill_color=interpolate_color(BLUE_E, Color("#FFD37F"), 0.25), fill_opacity=1.0, stroke_width=0)

        # Wind streamlines across ground plane
        def wind(point):
            x, y = point[0], point[1]
            return np.array([1.2 + 0.3*np.sin(0.3*y), 0.15*np.cos(0.4*x), 0])

        streams = StreamLines(
            wind,
            x_range=[-7, 7, 1.8], y_range=[-4, 4, 1.8],
            stroke_width=1.0, opacity=0.4, color=GRAY_B,
            padding=1
        )

        # Cowboy factory (stacked cylinders)
        def make_cowboy(body_color=GREY_E, leg_color=BLUE_D, hat_color=MAROON_D):
            # Dimensions
            leg_h = 0.9
            leg_r = 0.12
            boot_h = 0.1
            boot_r = 0.14
            body_h = 1.0
            body_r = 0.28
            head_h = 0.25
            head_r = 0.18
            brim_h = 0.04
            brim_r = 0.40
            crown_h = 0.20
            crown_r = 0.20

            # Legs
            left_leg = cylinder_surface(leg_r, leg_h, color=leg_color)
            right_leg = left_leg.copy()
            left_leg.shift(np.array([-0.16, 0, leg_h/2]))  # center at half height
            right_leg.shift(np.array([0.16, 0, leg_h/2]))

            # Boots (short cylinders at base)
            left_boot = cylinder_surface(boot_r, boot_h, color=Color("#6B4F2A"))
            right_boot = left_boot.copy()
            left_boot.shift(np.array([-0.16, 0, boot_h/2]))
            right_boot.shift(np.array([0.16, 0, boot_h/2]))

            # Torso
            body = cylinder_surface(body_r, body_h, color=body_color)
            body.shift(np.array([0, 0, leg_h + body_h/2]))

            # Head
            head = cylinder_surface(head_r, head_h, color=GREY_B)
            head.shift(np.array([0, 0, leg_h + body_h + head_h/2]))

            # Hat: brim + crown
            brim = cylinder_surface(brim_r, brim_h, color=hat_color)
            brim.shift(np.array([0, 0, leg_h + body_h + head_h + brim_h/2]))
            crown = cylinder_surface(crown_r, crown_h, color=hat_color)
            crown.shift(np.array([0, 0, leg_h + body_h + head_h + brim_h + crown_h/2]))

            # Arms: horizontal thin cylinders at chest height
            arm_r = 0.07
            arm_len = 0.75
            chest_z = leg_h + 0.7
            left_arm = cylinder_surface(arm_r, arm_len, color=body_color)
            right_arm = left_arm.copy()
            # Rotate from z-axis to x-axis
            left_arm.rotate(-PI/2, axis=Y_AXIS)
            right_arm.rotate(-PI/2, axis=Y_AXIS)
            left_arm.move_to(np.array([-0.55, 0, chest_z]))
            right_arm.move_to(np.array([0.55, 0, chest_z]))

            cowboy = VGroup(left_leg, right_leg, left_boot, right_boot, body, head, brim, crown, left_arm, right_arm)
            # Annotate for later animation
            cowboy.left_arm = left_arm
            cowboy.right_arm = right_arm
            cowboy.height_total = leg_h + body_h + head_h + brim_h + crown_h
            return cowboy

        # Create two cowboys
        cowboy_left = make_cowboy(body_color=GREY_E, leg_color=BLUE_D, hat_color=MAROON_D)
        cowboy_right = make_cowboy(body_color=GREY_E, leg_color=BLUE_D, hat_color=MAROON_D)

        # Position them apart on the street
        left_pos = np.array([-3.0, 0.0, 0.0])
        right_pos = np.array([3.0, 0.0, 0.0])
        cowboy_left.shift(left_pos)
        cowboy_right.shift(right_pos)

        # Tumbleweed (sphere) setup
        R_weed = 0.35
        weed = sphere_surface(R=R_weed, color=YELLOW_E, opacity=0.8)
        weed_group = VGroup(weed)
        start_x = -6.5
        end_x = 6.5
        weed_group.move_to(np.array([start_x, 0, R_weed]))

        s_tracker = ValueTracker(start_x)
        last_s = [start_x]

        def update_weed(mob, dt):
            s_val = s_tracker.get_value()
            ds = s_val - last_s[0]
            mob.move_to(np.array([s_val, 0, R_weed]))
            if abs(ds) > 1e-8:
                mob.rotate(-ds / R_weed, axis=Y_AXIS, about_point=mob.get_center())
            last_s[0] = s_val

        weed_group.add_updater(update_weed)

        # Add background first
        self.add(ground, sky)
        self.add(cowboy_left, cowboy_right)
        self.add(streams)
        streams.start_animation(warm_up=False, flow_speed=1.0)

        # Scene 1: Low-angle boots (0-4s)
        boot_view = left_pos + np.array([0.0, 0.0, 0.35])
        self.camera.frame.move_to(boot_view)
        self.play(self.camera.frame.animate.shift(np.array([0.2, 0.0, 0.05])), run_time=4, rate_func=smooth)

        # Scene 2: Tilt up first cowboy (4-10s)
        self.move_camera(phi=60*DEGREES, theta=40*DEGREES, run_time=3)
        self.play(self.camera.frame.animate.shift(np.array([0.0, 0.0, 1.2])), run_time=3, rate_func=smooth)

        # Scene 3: Cut to rival (10-16s)
        self.play(self.camera.frame.animate.move_to(right_pos + np.array([0.0, 0.0, 0.9])), run_time=3, rate_func=smooth)
        self.move_camera(phi=60*DEGREES, theta=120*DEGREES, run_time=3)

        # Scene 4: Wide shot (16-22s)
        self.play(self.camera.frame.animate.move_to(np.array([0.0, 0.0, 1.0])), run_time=3, rate_func=smooth)
        self.move_camera(phi=70*DEGREES, theta=45*DEGREES, zoom=1.1, run_time=3)

        # Scene 5-7: Tumbleweed crosses (22-36s)
        self.add(weed_group)
        self.play(
            s_tracker.animate.set_value(end_x),
            self.camera.frame.animate.move_to(np.array([3.0, 0.0, 1.0])),
            run_time=14,
            rate_func=linear,
        )
        weed_group.clear_updaters()

        # Scene 8-9: Passing moment and drift (36-46s)
        # Small arm twitches (there and back)
        self.play(
            Rotate(cowboy_left.left_arm, angle=0.18, axis=Z_AXIS, about_point=cowboy_left.left_arm.get_center()),
            Rotate(cowboy_right.right_arm, angle=-0.18, axis=Z_AXIS, about_point=cowboy_right.right_arm.get_center()),
            run_time=4,
            rate_func=there_and_back,
        )
        # Subtle camera pan
        self.move_camera(phi=68*DEGREES, theta=55*DEGREES, run_time=6)

        # Scene 10-12: Settle and soften (46-58s)
        self.play(self.camera.frame.animate.move_to(np.array([0.0, 0.0, 1.0])), run_time=4)
        self.wait(4)
        self.play(FadeOut(weed_group), FadeOut(streams), run_time=4)

        # Scene 13-14: Pull back and fade (58-64s)
        self.move_camera(zoom=1.2, phi=75*DEGREES, theta=45*DEGREES, run_time=4)
        self.play(FadeOut(cowboy_left), FadeOut(cowboy_right), FadeOut(ground), FadeOut(sky), run_time=2)
        self.wait(0.5)
