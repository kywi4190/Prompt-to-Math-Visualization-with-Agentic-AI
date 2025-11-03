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

# -------- Helpers: geometry primitives built from parametric surfaces --------

def cylinder_along_y(radius=0.3, height=1.0, y0=0.0, color="#8d5524", opacity=1.0, res_u=24, res_v=12):
    surf = ParametricSurface(
        lambda u, v: np.array([
            radius * np.cos(u),
            y0 + v * height,
            radius * np.sin(u),
        ]),
        u_min=0,
        u_max=TAU,
        v_min=0,
        v_max=1,
        resolution=(res_u, res_v),
        fill_opacity=opacity,
        color=color,
        stroke_width=0.5,
        stroke_color=BLACK,
    )
    return surf


def sphere(center=np.array([0.0, 0.0, 0.0]), r=0.5, color="#c28e0e", opacity=0.7, res_u=28, res_v=14):
    cx, cy, cz = center
    surf = ParametricSurface(
        lambda u, v: np.array([
            cx + r * np.cos(u) * np.sin(v),
            cy + r * np.cos(v),
            cz + r * np.sin(u) * np.sin(v),
        ]),
        u_min=0,
        u_max=TAU,
        v_min=0,
        v_max=PI,
        resolution=(res_u, res_v),
        fill_opacity=opacity,
        color=color,
        stroke_width=0.6,
        stroke_color=Color("#8a6f12"),
    )
    return surf


def tumbleweed(center=np.array([0.0, 0.5, 0.0]), r=0.5):
    base = sphere(center=center, r=r, color="#d2a84a", opacity=0.55)
    cx, cy, cz = center
    # Add a few latitudinal and twisted meridian-like lines to suggest twigs
    rings = VGroup()
    lat_vals = [0.35 * PI, 0.55 * PI, 0.75 * PI]
    for i, vv in enumerate(lat_vals):
        ring = ParametricFunction(
            lambda u, vv=vv: np.array([
                cx + r * np.cos(u) * np.sin(vv),
                cy + r * np.cos(vv),
                cz + r * np.sin(u) * np.sin(vv),
            ]),
            t_min=0,
            t_max=TAU,
            color=Color("#7f6a00"),
            stroke_opacity=0.8,
            stroke_width=1.6,
        )
        rings.add(ring)
    # Skewed loops (twisted vines)
    for k, ang in enumerate([0.0, 0.6, -0.9]):
        loop = ParametricFunction(
            lambda u, ang=ang: np.array([
                cx + r * np.cos(u) * np.cos(ang) * 0.9,
                cy + r * np.sin(u) * 0.3,
                cz + r * np.sin(u) * np.sin(ang) * 0.9,
            ]),
            t_min=0,
            t_max=TAU,
            color=Color("#6e5b00"),
            stroke_opacity=0.75,
            stroke_width=1.4,
        )
        rings.add(loop)
    tw = VGroup(base, rings)
    return tw


def cowboy(position=np.array([0.0, 0.0, 0.0]), base_color="#8d5524", accent_color="#5d4037"):
    parts = []
    # Legs
    leg_gap = 0.24
    leg_h = 1.0
    leg_r = 0.18
    leg1 = cylinder_along_y(radius=leg_r, height=leg_h, y0=0.0, color=base_color)
    leg1.shift(np.array([-leg_gap, 0, 0]))
    leg2 = cylinder_along_y(radius=leg_r, height=leg_h, y0=0.0, color=base_color)
    leg2.shift(np.array([+leg_gap, 0, 0]))
    parts += [leg1, leg2]
    # Torso
    torso = cylinder_along_y(radius=0.34, height=1.2, y0=leg_h, color=base_color)
    parts.append(torso)
    # Belt (thin band)
    belt = cylinder_along_y(radius=0.35, height=0.05, y0=leg_h + 0.55, color=accent_color, opacity=1.0, res_u=24, res_v=4)
    parts.append(belt)
    # Head
    head = cylinder_along_y(radius=0.24, height=0.35, y0=leg_h + 1.2, color=base_color)
    parts.append(head)
    # Hat brim (wide, thin)
    brim = cylinder_along_y(radius=0.6, height=0.06, y0=leg_h + 1.55 + 0.35, color=accent_color, opacity=1.0, res_u=32, res_v=4)
    parts.append(brim)
    # Hat crown
    crown = cylinder_along_y(radius=0.28, height=0.32, y0=leg_h + 1.61 + 0.35, color=accent_color)
    parts.append(crown)
    # Arms (at sides)
    arm_r = 0.12
    arm_h = 0.9
    arm_offset_x = 0.58
    arm_y0 = leg_h + 0.2
    arm1 = cylinder_along_y(radius=arm_r, height=arm_h, y0=arm_y0, color=base_color)
    arm1.shift(np.array([-arm_offset_x, 0, 0]))
    arm2 = cylinder_along_y(radius=arm_r, height=arm_h, y0=arm_y0, color=base_color)
    arm2.shift(np.array([+arm_offset_x, 0, 0]))
    parts += [arm1, arm2]
    guy = VGroup(*parts)
    guy.shift(position)
    return guy


class WesternStandoffScene(ThreeDScene):
    def construct(self):
        # Camera: low, wide, slightly angled
        self.set_camera_orientation(phi=88 * DEGREES, theta=20 * DEGREES, zoom=1.0)

        # Ground plane (desert)
        ground = ParametricSurface(
            lambda u, v: np.array([u, 0.0, v]),
            u_min=-8,
            u_max=8,
            v_min=-6,
            v_max=6,
            resolution=(16, 12),
            color=Color("#e3c07b"),
            fill_opacity=1.0,
            stroke_color=Color("#d2b48c"),
            stroke_width=0.6,
        )

        # Cowboys built from cylinders
        left_cowboy = cowboy(position=np.array([-4.0, 0.0, 0.0]), base_color="#8d5524", accent_color="#5d4037")
        right_cowboy = cowboy(position=np.array([4.0, 0.0, 0.0]), base_color="#c68642", accent_color="#6d4c41")

        self.play(FadeIn(ground, shift=DOWN), run_time=1.0)
        self.play(FadeIn(VGroup(left_cowboy, right_cowboy), shift=UP), run_time=1.2)

        # Slow establishing sweep
        self.move_camera(theta=-20 * DEGREES, run_time=4.0)

        # Close-up bias to the left
        self.move_camera(theta=-60 * DEGREES, zoom=1.25, run_time=4.0)

        # Close-up bias to the right
        self.move_camera(theta=60 * DEGREES, zoom=1.25, run_time=4.0)

        # Return to center, slightly higher look
        self.move_camera(theta=0 * DEGREES, phi=80 * DEGREES, zoom=1.0, run_time=2.0)

        # Tumbleweed: a rolling sphere that crosses the scene
        tw_radius = 0.5
        tw = tumbleweed(center=np.array([-6.0, tw_radius, 0.0]), r=tw_radius)
        self.add(tw)

        speed = 1.7  # units per second along +x

        def roll_update(mobj, dt):
            mobj.shift(np.array([speed * dt, 0.0, 0.0]))
            # Rotate around z-axis (OUT) to mimic rolling on the ground plane y=0
            mobj.rotate(-speed * dt / tw_radius, axis=OUT, about_point=mobj.get_center())

        tw.add_updater(roll_update)
        self.begin_ambient_camera_rotation(rate=0.08)
        self.wait(7.0)
        tw.remove_updater(roll_update)
        self.stop_ambient_camera_rotation()

        # Wind lines: light streaks sweeping across
        wind_lines = VGroup()
        wind_updaters = []
        z_offsets = [-0.7, 0.0, 0.8]
        for i, z0 in enumerate(z_offsets):
            y0 = 0.6 + 0.04 * i
            line = ParametricFunction(
                lambda t, y0=y0, z0=z0, i=i: np.array([t, y0 + 0.04 * np.sin(2 * t + 1.2 * i), z0]),
                t_min=-8,
                t_max=-4,
                color=Color("#ffffff"),
                stroke_opacity=0.6,
                stroke_width=2.0,
            )
            def make_updater():
                def wind_update(m, dt):
                    m.shift(np.array([2.0 * dt, 0.0, 0.0]))
                    if m.get_center()[0] > 8:
                        m.shift(np.array([-12.0, 0.0, 0.0]))
                return wind_update
            upd = make_updater()
            line.add_updater(upd)
            wind_updaters.append(upd)
            wind_lines.add(line)

        self.play(FadeIn(wind_lines), run_time=0.8)
        self.wait(3.0)
        for ln, upd in zip(wind_lines, wind_updaters):
            ln.remove_updater(upd)

        # Hero wide shot
        self.move_camera(phi=70 * DEGREES, theta=45 * DEGREES, zoom=1.2, run_time=4.0)

        # Fade to black
        self.play(FadeOut(VGroup(wind_lines, left_cowboy, right_cowboy, tw, ground)), run_time=1.0)
