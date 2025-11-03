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

class WesternStandoffScene(ThreeDScene):
    def create_ground(self):
        # Broad desert ground (x-z plane at y=0)
        ground = ParametricSurface(
            lambda u, v: np.array([u, 0.0, v]),
            u_range=(-8, 8), v_range=(-8, 8), resolution=(8, 8),
            fill_color="#cda26b", fill_opacity=1.0, stroke_color="#b58a5c", stroke_opacity=0.2
        )
        # A darker street band
        street = ParametricSurface(
            lambda u, v: np.array([u, 0.001, v]),
            u_range=(-8, 8), v_range=(-1.2, 1.2), resolution=(2, 2),
            fill_color="#b38b5a", fill_opacity=1.0, stroke_opacity=0.0
        )
        return VGroup(ground, street)

    def breeze_lines(self, y=0.25, z_offsets=(-0.8, 0.0, 0.8), color="#f5e3b0"):
        lines = VGroup()
        for k, z0 in enumerate(z_offsets):
            phase = k * 0.6
            curve = ParametricFunction(
                lambda t: np.array([t, y, z0 + 0.15 * np.sin(1.5 * t + phase)]),
                t_range=(-8, 8),
                color=color,
                stroke_width=2,
            )
            curve.set_opacity(0.6)
            lines.add(curve)
        return lines

    def build_cowboy(self, pos=np.array([-4, 0, 0]), body_color=Color("#7b4b2a"), hat_color=Color("#5e3a1e")):
        # Dimensions
        torso_h = 2.0
        torso_r = 0.35
        head_h = 0.35
        head_r = 0.25
        hat_brim_r = 0.60
        hat_brim_h = 0.08
        hat_crown_r = 0.25
        hat_crown_h = 0.35
        shoulder_y = 1.4
        arm_len = 1.4
        arm_r = 0.08
        leg_h = 1.0
        leg_r = 0.15
        boot_h = 0.20
        boot_r = 0.17

        # Torso (upright)
        torso = Cylinder(radius=torso_r, height=torso_h, direction=UP,
                         fill_color=body_color, fill_opacity=1.0, stroke_color=DARK_BROWN)
        torso.move_to(pos + np.array([0, torso_h/2, 0]))

        # Head (cylindrical)
        head = Cylinder(radius=head_r, height=head_h, direction=UP,
                        fill_color=interpolate_color(Color(body_color), Color(Color("#8c5a35")), 0.3), fill_opacity=1.0)
        head.move_to(torso.get_center() + np.array([0, (torso_h/2) + head_h/2, 0]))

        # Hat (brim + crown)
        hat_brim = Cylinder(radius=hat_brim_r, height=hat_brim_h, direction=UP,
                            fill_color=hat_color, fill_opacity=1.0)
        hat_brim.move_to(head.get_center() + np.array([0, (head_h/2) + hat_brim_h/2, 0]))
        hat_crown = Cylinder(radius=hat_crown_r, height=hat_crown_h, direction=UP,
                             fill_color=hat_color, fill_opacity=1.0)
        hat_crown.move_to(hat_brim.get_center() + np.array([0, (hat_brim_h/2) + hat_crown_h/2, 0]))
        hat = VGroup(hat_brim, hat_crown)

        # Arms (right/left), oriented along x (RIGHT)
        # Right arm extends to +x side, pivot near right shoulder
        arm_right = Cylinder(radius=arm_r, height=arm_len, direction=RIGHT,
                             fill_color=body_color, fill_opacity=1.0)
        arm_right.move_to(np.array([
            pos[0] + torso_r + arm_len/2,  # center so that inner end meets shoulder
            shoulder_y,
            pos[2]
        ]))
        # Left arm extends to -x side
        arm_left = Cylinder(radius=arm_r, height=arm_len, direction=RIGHT,
                            fill_color=body_color, fill_opacity=1.0)
        arm_left.move_to(np.array([
            pos[0] - torso_r - arm_len/2,
            shoulder_y,
            pos[2]
        ]))

        # Holsters (short vertical cylinders at hips)
        holster_r = Cylinder(radius=0.12, height=0.4, direction=UP,
                              fill_color=Color("#3d2817"), fill_opacity=1.0)
        holster_r.move_to(np.array([pos[0] + torso_r + 0.12, 0.8, pos[2] + 0.15]))
        holster_l = Cylinder(radius=0.12, height=0.4, direction=UP,
                              fill_color=Color("#3d2817"), fill_opacity=1.0)
        holster_l.move_to(np.array([pos[0] - torso_r - 0.12, 0.8, pos[2] - 0.15]))

        # Legs
        leg_r = Cylinder(radius=leg_r, height=leg_h, direction=UP,
                          fill_color=interpolate_color(Color(body_color), Color(Color("#6a4024")), 0.2), fill_opacity=1.0)
        leg_l = Cylinder(radius=leg_r, height=leg_h, direction=UP,
                          fill_color=interpolate_color(Color(body_color), Color(Color("#6a4024")), 0.2), fill_opacity=1.0)
        leg_r.move_to(np.array([pos[0] + 0.15, leg_h/2, pos[2] + 0.12]))
        leg_l.move_to(np.array([pos[0] - 0.15, leg_h/2, pos[2] - 0.12]))

        # Boots
        boot_r = Cylinder(radius=boot_r, height=boot_h, direction=UP,
                          fill_color=Color("#362414"), fill_opacity=1.0)
        boot_l = Cylinder(radius=boot_r, height=boot_h, direction=UP,
                          fill_color=Color("#362414"), fill_opacity=1.0)
        boot_r.move_to(np.array([pos[0] + 0.15, boot_h/2, pos[2] + 0.12]))
        boot_l.move_to(np.array([pos[0] - 0.15, boot_h/2, pos[2] - 0.12]))

        cowboy = VGroup(torso, head, hat, arm_right, arm_left, holster_r, holster_l, leg_r, leg_l, boot_r, boot_l)

        parts = {
            "group": cowboy,
            "torso": torso,
            "head": head,
            "hat": hat,
            "arm_right": arm_right,
            "arm_left": arm_left,
            "holster_r": holster_r,
            "holster_l": holster_l,
            "boot_r": boot_r,
            "boot_l": boot_l,
            "shoulder_y": shoulder_y,
            "torso_r": torso_r,
            "pos": pos,
        }
        return parts

    def construct(self):
        # Initial camera
        self.set_camera_orientation(phi=70*DEGREES, theta=45*DEGREES, zoom=1.0)

        # Scene elements
        ground = self.create_ground()
        self.play(FadeIn(ground, shift=IN), run_time=2)

        # Cowboys
        left = self.build_cowboy(pos=np.array([-4.5, 0.0, 0.0]), body_color=Color("#7b4b2a"), hat_color=Color("#5e3a1e"))
        right = self.build_cowboy(pos=np.array([4.5, 0.0, 0.0]), body_color=Color("#7b4b2a"), hat_color=Color("#5e3a1e"))
        # Mirror the right cowboy's arms slightly to suggest facing left
        # (We just keep geometry symmetric; the camera conveys direction.)
        self.play(FadeIn(left["group"], shift=OUT), FadeIn(right["group"], shift=OUT), run_time=2.5)

        # Subtle establishing pan
        self.move_camera(theta=35*DEGREES, run_time=2.0)

        # Breeze pass 1
        breeze1 = self.breeze_lines(y=0.25, z_offsets=(-0.8, 0.0, 0.8))
        self.add(breeze1)
        self.play(*[b.animate.shift(RIGHT*3.0) for b in breeze1], run_time=4.0)
        self.remove(breeze1)

        # Prepare tumbleweed
        weed_r = 0.35
        weed = Sphere(radius=weed_r, resolution=(16, 24),
                      fill_color=Color("#caa56a"), fill_opacity=1.0, sheen=0.2)
        # Start at far left, slightly above ground (resting on y=0)
        weed.move_to(np.array([-8.0, weed_r, 0.0]))
        self.add(weed)

        # Camera adjusts as tumbleweed rolls through
        self.play(
            AnimationGroup(
                weed.animate.shift(RIGHT*16.0),
                Rotate(weed, angle=-(16.0/weed_r), axis=OUT),  # Roll without slipping along x
                lag_ratio=0.0,
            ),
            self.camera.animate.set_orientation(phi=65*DEGREES, theta=30*DEGREES),
            run_time=8.0,
        )

        # Push-in to left cowboy; arm dips toward holster
        left_shoulder_pivot = np.array([
            left["pos"][0] + left["torso_r"],
            left["shoulder_y"],
            left["pos"][2],
        ])
        self.play(
            Rotate(left["arm_right"], angle=-50*DEGREES, axis=OUT, about_point=left_shoulder_pivot),
            run_time=3.0,
        )
        self.move_camera(theta=25*DEGREES, zoom=1.25, run_time=1.0)
        self.wait(1.0)

        # Cut to right cowboy; hat tilt + boot tap
        self.move_camera(theta=-25*DEGREES, zoom=1.25, run_time=3.0)
        # Tilt hat slightly forward around the head top
        head_top = right["hat"].get_center()
        self.play(Rotate(right["hat"], angle=-12*DEGREES, axis=RIGHT, about_point=head_top), run_time=1.5)
        # Boot tap (right boot)
        self.play(right["boot_r"].animate.shift(UP*0.06), run_time=0.5)
        self.play(right["boot_r"].animate.shift(DOWN*0.06), run_time=0.5)

        # Back to the wide
        self.move_camera(phi=70*DEGREES, theta=45*DEGREES, zoom=1.0, run_time=3.0)

        # Breeze pass 2
        breeze2 = self.breeze_lines(y=0.22, z_offsets=(-0.5, 0.4), color="#f0dba0")
        self.add(breeze2)
        self.play(*[b.animate.shift(RIGHT*2.5) for b in breeze2], run_time=4.0)
        self.remove(breeze2)

        # Slow orbit to end
        self.begin_ambient_camera_rotation(rate=0.05)
        self.wait(8.0)
        self.stop_ambient_camera_rotation()

        # Final hold
        self.wait(4.0)
