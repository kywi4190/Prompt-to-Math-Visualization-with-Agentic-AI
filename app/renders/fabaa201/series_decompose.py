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

class DecomposeSeriesScene(ThreeDScene):
    def construct(self):
        # Camera setup
        self.set_camera_orientation(phi=65 * DEGREES, theta=-70 * DEGREES, zoom=1.0)

        # Axes
        axes = Axes(
            x_range=[0, TAU, PI / 2],
            y_range=[-1.5, 1.5, 1],
            x_length=8.0,
            y_length=4.0,
            tips=False,
            axis_config={"stroke_opacity": 0.8, "stroke_width": 2},
        )
        axes.z_index = 0

        # Helper: Fourier partial sum for square wave using odd harmonics up to N
        def fourier_square_partial(x, Nint):
            s = 0.0
            for k in range(1, Nint + 1, 2):
                s += math.sin(k * x) / k
            return (4 / math.pi) * s

        # Square wave target (split to avoid vertical jump connectors)
        eps = 1e-3
        sq_seg_top = ParametricFunction(
            lambda t: axes.c2p(t, 1.0, 0),
            t_range=[0, PI - eps],
            use_smoothing=False,
            stroke_color=YELLOW,
            stroke_width=6,
            stroke_opacity=0.9,
        )
        sq_seg_bot = ParametricFunction(
            lambda t: axes.c2p(t, -1.0, 0),
            t_range=[PI + eps, TAU - eps],
            use_smoothing=False,
            stroke_color=YELLOW,
            stroke_width=6,
            stroke_opacity=0.9,
        )
        for seg in [sq_seg_top, sq_seg_bot]:
            seg.z_index = 1

        # Vertical guide at the jump x = pi (no dashed to keep primitives minimal)
        jump_guide = Line(
            axes.c2p(PI, -1.5, 0),
            axes.c2p(PI, 1.5, 0),
            color=GRAY,
            stroke_opacity=0.4,
        )
        jump_guide.z_index = 0.5

        # Tracker for N (odd only via mapping)
        maxN = 9
        N = ValueTracker(1)

        def odd_from_tracker(val):
            n = int(round(val))
            if n < 1:
                n = 1
            # Map to nearest odd within [1, maxN]
            if n % 2 == 0:
                n = n + 1 if n < maxN else n - 1
            n = max(1, min(maxN, n))
            return n

        # Dynamic partial-sum curve
        def make_partial():
            Nint = odd_from_tracker(N.get_value())
            alpha = (Nint - 1) / (maxN - 1)
            # Ensure both arguments are Manim Color objects (no strings)
            col = interpolate_color(Color(Color(BLUE)), Color(Color("#ffaa00")), alpha)
            return ParametricFunction(
                lambda t: axes.c2p(t, fourier_square_partial(t, Nint), 0),
                t_range=[0, TAU],
                use_smoothing=False,
                stroke_color=col,
                stroke_width=5,
                stroke_opacity=1.0,
            )

        partial_curve = always_redraw(make_partial)
        partial_curve.z_index = 2

        # HUD-style formula and N display (fixed in frame)
        formula = MathTex(r"f_N(x)=\frac{4}{\pi}\sum_{k\,\text{odd}\le N}\frac{\sin(kx)}{k}")
        formula.scale(0.8)
        formula.to_corner(UL)

        n_label = MathTex(r"N=")
        n_value = DecimalNumber(1, num_decimal_places=0)
        n_group = VGroup(n_label, n_value).arrange(RIGHT, buff=0.15)
        n_group.next_to(formula, DOWN, aligned_edge=LEFT)

        def update_n_value(m):
            m.set_value(odd_from_tracker(N.get_value()))
        n_value.add_updater(update_n_value)

        self.add_fixed_in_frame_mobjects(formula, n_group)

        # Build the scene
        self.play(Create(axes), run_time=0.8)
        self.play(Create(sq_seg_top), Create(sq_seg_bot), run_time=1.7)
        self.add(jump_guide)
        self.play(Write(formula), run_time=1.1)
        self.play(Write(n_group), run_time=0.8)
        self.play(Create(partial_curve), run_time=0.9)

        # Gentle camera motion while harmonics step in
        self.begin_ambient_camera_rotation(rate=0.02)

        # Step through odd N values discretely for clarity
        for target in [3, 5, 7, 9]:
            self.play(N.animate.set_value(target), run_time=2.4)

        # Final emphasis: slight zoom in, then hold
        self.move_camera(zoom=1.15, run_time=3.0)
        self.stop_ambient_camera_rotation()
        self.wait(3.0)
