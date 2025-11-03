from manim import *
import numpy as np
import math

class WesternStandoff(ThreeDScene):
    def construct(self):
        self.camera.background_color = "#F7E8C3"  # warm desert tone
        self.set_camera_orientation(phi=65*DEGREES, theta=-45*DEGREES, zoom=1.0)

        # Ground plane (simple parametric surface)
        ground = Surface(
            lambda u, v: np.array([u, v, 0.0]),
            u_range=[-7, 7], v_range=[-3.5, 0.5],
            resolution=(4, 4),  # low resolution for performance; it's flat
        )
        ground.set_fill(color="#E8D5A7", opacity=1.0)
        ground.set_stroke(width=0)

        # Sun (a simple circle in the sky)
        def circle_param(center=np.array([0, 2.8, 0]), r=0.35):
            return ParametricFunction(
                lambda t: np.array([
                    center[0] + r*np.cos(t),
                    center[1] + r*np.sin(t),
                    0.0
                ]), t_range=[0, TAU], stroke_width=6, color="#FDB813"
            )
        sun = circle_param()

        # Cowboy builder using only allowed primitives
        def make_cowboy(xpos= -4.0, color=WHITE, facing=+1):
            base = np.array([xpos, -0.5, 0.0])
            shoulder = base + np.array([0.0, 1.3, 0.0])
            hip = base + np.array([0.0, 0.9, 0.0])
            head_center = base + np.array([0.0, 1.9, 0.0])
            foot_L = base + np.array([-0.25, 0.0, 0.0])
            foot_R = base + np.array([+0.25, 0.0, 0.0])

            # Head (dot)
            head = Dot(point=head_center, radius=0.07, color=color)

            # Hat: brim and crown (lines)
            brim_y = head_center[1] + 0.12
            brim = Line([head_center[0]-0.4, brim_y, 0.0], [head_center[0]+0.4, brim_y, 0.0], stroke_width=6, color=color)
            crown_top = np.array([head_center[0], brim_y+0.25, 0.0])
            crown_L = Line([head_center[0]-0.22, brim_y, 0.0], crown_top, stroke_width=6, color=color)
            crown_R = Line([head_center[0]+0.22, brim_y, 0.0], crown_top, stroke_width=6, color=color)

            # Torso & legs
            torso = Line(shoulder, hip, stroke_width=6, color=color)
            leg_L = Line(hip, foot_L, stroke_width=6, color=color)
            leg_R = Line(hip, foot_R, stroke_width=6, color=color)

            # Arms
            open_arm = Line(shoulder, shoulder + np.array([-facing*0.55, 0.1, 0.0]), stroke_width=6, color=color)
            holster_point = hip + np.array([facing*0.48, -0.02, 0.0])
            gun_arm = Line(shoulder, holster_point, stroke_width=6, color=color)

            # Holster (short line) and gun (arrow)
            holster = Line(holster_point + np.array([0, 0.1, 0]), holster_point + np.array([0, -0.1, 0]), stroke_width=6, color=color)
            gun = Arrow(
                holster_point + np.array([-facing*0.02, 0.05, 0.0]),
                holster_point + np.array([facing*0.42, -0.1, 0.0]),
                buff=0, stroke_width=6, tip_length=0.12, color=color
            )

            g = VGroup(head, brim, crown_L, crown_R, torso, leg_L, leg_R, open_arm, gun_arm, holster, gun)
            return {
                "group": g,
                "head": head,
                "shoulder": shoulder,
                "hip": hip,
                "holster_point": holster_point,
                "gun_arm": gun_arm,
                "gun": gun,
                "facing": facing
            }

        left = make_cowboy(xpos=-4.2, color=BLACK, facing=+1)
        right = make_cowboy(xpos=+4.2, color=BLACK, facing=-1)

        # Scene: establish
        self.play(Create(ground), run_time=2)
        self.play(Create(sun), run_time=1)
        self.play(Create(left["group"]), run_time=1.5)
        self.play(Create(right["group"]), run_time=1.5)

        # Subtle initial camera drift
        self.move_camera(theta=-35*DEGREES, zoom=1.12, run_time=3)

        # Push to left cowboy
        self.move_camera(frame_center=left["head"].get_center() + np.array([0, -0.3, 0]), zoom=1.28, run_time=3)
        # Hand twitch: tiny rotations about the shoulder
        self.play(Rotate(left["gun_arm"], angle=0.12, about_point=left["shoulder"]), run_time=0.8)
        self.play(Rotate(left["gun_arm"], angle=-0.12, about_point=left["shoulder"]), run_time=0.7)
        self.wait(0.3)

        # Cross to right cowboy
        self.move_camera(frame_center=right["head"].get_center() + np.array([0, -0.3, 0]), zoom=1.28, run_time=3)
        self.play(Rotate(right["gun_arm"], angle=-0.12, about_point=right["shoulder"]), run_time=0.8)
        self.play(Rotate(right["gun_arm"], angle=0.12, about_point=right["shoulder"]), run_time=0.7)
        self.wait(0.3)

        # Overhead tactical view
        mid = np.array([0.0, 0.0, 0.0])
        self.move_camera(phi=78*DEGREES, theta=-45*DEGREES, frame_center=mid, zoom=1.1, run_time=3)

        # Sight lines (arrows between heads)
        left_head = left["head"].get_center()
        right_head = right["head"].get_center()
        sight_LR = Arrow(left_head, right_head, buff=0.1, stroke_width=5, tip_length=0.12, color="#6C3B00")
        sight_RL = Arrow(right_head, left_head, buff=0.1, stroke_width=5, tip_length=0.12, color="#6C3B00")
        self.play(Create(sight_LR), Create(sight_RL), run_time=2)

        # Distance line across the ground (between hips projected on ground)
        left_hip = left["hip"]
        right_hip = right["hip"]
        stage_line = Line([left_hip[0], 0.05, 0], [right_hip[0], 0.05, 0], color=DARK_BROWN, stroke_width=6)
        self.play(Create(stage_line), run_time=1)
        self.wait(0.5)

        # Back to wide cinematic angle
        self.move_camera(phi=65*DEGREES, theta=-40*DEGREES, frame_center=np.array([0, -0.4, 0]), zoom=1.0, run_time=3)

        # Tumbleweed: a rolling circle built from parametric curves
        weed_center_start = np.array([-6.5, -0.1, 0])
        weed_r = 0.32
        weed_outline = ParametricFunction(lambda t: np.array([
            weed_center_start[0] + weed_r*np.cos(t),
            weed_center_start[1] + weed_r*np.sin(t),
            0.0
        ]), t_range=[0, TAU], color=DARK_BROWN, stroke_width=4)
        weed_cross1 = ParametricFunction(lambda t: np.array([
            weed_center_start[0] + 0.25*np.cos(t+0.7),
            weed_center_start[1] + 0.25*np.sin(t+0.7),
            0.0
        ]), t_range=[0, TAU], color=DARK_BROWN, stroke_width=2)
        weed_cross2 = ParametricFunction(lambda t: np.array([
            weed_center_start[0] + 0.18*np.cos(t-0.9),
            weed_center_start[1] + 0.18*np.sin(t-0.9),
            0.0
        ]), t_range=[0, TAU], color=DARK_BROWN, stroke_width=2)
        weed = VGroup(weed_outline, weed_cross1, weed_cross2)
        self.play(Create(weed), run_time=1)
        weed_target = weed.copy().shift(np.array([13.0, 0.0, 0.0]))
        self.play(Transform(weed, weed_target), Rotate(weed, angle=2*PI, about_point=weed.get_center()), run_time=5)

        # Wind lines sliding across the ground
        wind_y = -0.2
        wind1 = Line([-7, wind_y, 0], [-6, wind_y, 0], stroke_width=3, color=DARK_BROWN)
        wind2 = Line([-7.2, wind_y-0.15, 0], [-6.2, wind_y-0.15, 0], stroke_width=2, color=DARK_BROWN)
        wind3 = Line([-7.4, wind_y+0.15, 0], [-6.4, wind_y+0.15, 0], stroke_width=2, color=DARK_BROWN)
        winds = VGroup(wind1, wind2, wind3)
        self.play(Create(winds), run_time=0.8)
        winds_target = winds.copy().shift(np.array([5.5, 0.0, 0.0]))
        self.play(Transform(winds, winds_target), run_time=2.2)
        self.wait(1.0)

        # DRAW: guns aim directly at the opposing head
        def aimed_gun_arrow(holster_point, target_point, length=0.9, color=BLACK):
            vec = target_point - holster_point
            vec[2] = 0.0
            if np.linalg.norm(vec) < 1e-6:
                vec = np.array([1.0, 0.0, 0.0])
            u = vec / np.linalg.norm(vec)
            end = holster_point + u * length
            return Arrow(holster_point, end, buff=0, stroke_width=6, tip_length=0.14, color=color)

        left_aim = aimed_gun_arrow(left["holster_point"], right_head, length=1.0, color=BLACK)
        right_aim = aimed_gun_arrow(right["holster_point"], left_head, length=1.0, color=BLACK)

        self.play(Transform(left["gun"], left_aim), Transform(right["gun"], right_aim), run_time=2.5)

        # Muzzle flashes as brief short arrows
        flash_L = Arrow(
            left_aim.get_end() - 0.15*(left_aim.get_end()-left_aim.get_start()),
            left_aim.get_end() + 0.25*(left_aim.get_end()-left_aim.get_start()),
            buff=0, color=YELLOW, stroke_width=8, tip_length=0.16
        )
        flash_R = Arrow(
            right_aim.get_end() - 0.15*(right_aim.get_end()-right_aim.get_start()),
            right_aim.get_end() + 0.25*(right_aim.get_end()-right_aim.get_start()),
            buff=0, color=YELLOW, stroke_width=8, tip_length=0.16
        )
        self.play(Create(flash_L), Create(flash_R), run_time=0.6)
        self.play(FadeOut(flash_L), FadeOut(flash_R), run_time=1.4)
        self.wait(1.0)

        # Pull back slowly
        self.move_camera(frame_center=np.array([0, -0.4, 0]), zoom=0.95, run_time=3)
        self.wait(4)

        # Fade to title
        title = Text("The Geometry of a Standoff", font_size=52, color=BLACK)
        title.shift(np.array([0, 2.2, 0]))
        self.play(FadeOut(sight_LR), FadeOut(sight_RL), FadeOut(stage_line), FadeOut(weed), FadeOut(winds), run_time=2)
        self.play(Write(title), run_time=2)
        self.wait(6)
