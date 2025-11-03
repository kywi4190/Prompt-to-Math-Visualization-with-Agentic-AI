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

class SeriesDecompositionScene(Scene):
    def construct(self):
        # Axes for f(x) on the left
        axes = Axes(
            x_range=[-math.pi, math.pi, math.pi/2],
            y_range=[-3.5, 3.5, 1],
            x_length=7,
            y_length=4.5,
            tips=False,
        ).to_edge(LEFT, buff=0.6)
        x_label = axes.get_x_axis_label(MathTex(r"x"))
        y_label = axes.get_y_axis_label(MathTex(r"f(x)"))

        self.play(Create(axes), run_time=1.0)
        self.play(FadeIn(VGroup(x_label, y_label), shift=0.2*UP), run_time=0.8)

        # Sine "building blocks" (use x_range step for sampling density; no 'samples' kw)
        step = 0.01
        basis1 = axes.plot(lambda x: math.sin(x), x_range=[-math.pi, math.pi, step], color=BLUE_B).set_stroke(opacity=0.7)
        basis2 = axes.plot(lambda x: 0.5*math.sin(2*x), x_range=[-math.pi, math.pi, step], color=GREEN_B).set_stroke(opacity=0.5)
        basis3 = axes.plot(lambda x: (1/3)*math.sin(3*x), x_range=[-math.pi, math.pi, step], color=PURPLE_B).set_stroke(opacity=0.5)
        basis_label = Text("Sine building blocks", font_size=32).next_to(axes, UP).shift(0.2*UP)
        self.play(FadeIn(VGroup(basis1, basis2, basis3, basis_label)), run_time=1.2)

        # Target sawtooth on (-pi, pi): f(x) = x
        saw = axes.plot(lambda x: x, x_range=[-math.pi, math.pi], color=YELLOW).set_z_index(1)
        self.play(Create(saw), run_time=1.2)
        self.play(FadeOut(VGroup(basis1, basis2, basis3, basis_label)), run_time=0.6)

        # Coefficient panel on the right
        panel_rect = Rectangle(width=4.5, height=4.6, color=GRAY_D)
        panel_rect.move_to([3.3, 0.0, 0.0])
        left = panel_rect.get_left()[0]
        right = panel_rect.get_right()[0]
        bottom = panel_rect.get_bottom()[1]
        top = panel_rect.get_top()[1]
        center_y = panel_rect.get_center()[1]

        base_line = Line(
            [left + 0.15, center_y, 0],
            [right - 0.15, center_y, 0],
            color=GRAY_B
        )
        y_axis_line = Line(
            [left + 0.25, bottom + 0.2, 0],
            [left + 0.25, top - 0.2, 0],
            color=GRAY_B
        )

        # Ticks along the baseline at bar centers
        max_n = 15
        cx_positions = np.linspace(left + 0.3, right - 0.3, max_n)
        ticks = VGroup(*[
            Line([cx, center_y - 0.07, 0], [cx, center_y + 0.07, 0], color=GRAY_B)
            for cx in cx_positions
        ])

        # Bars for coefficients a_n of sawtooth: 2*(-1)^{n+1}/n (sine series)
        def coeff(n):
            return 2*((-1)**(n+1))/n

        avail_half_h = (top - bottom)/2 - 0.35
        scale = 0.9 * (avail_half_h / 2.0)  # ensures max |2|*scale stays inside panel

        N_tracker = ValueTracker(1)

        bars = VGroup()
        for i, n in enumerate(range(1, max_n + 1)):
            cx = float(cx_positions[i])
            c = coeff(n)
            # Start as a point on the baseline
            bar = Line([cx, center_y, 0], [cx, center_y, 0], stroke_width=10)
            bar.set_z_index(1)

            def make_updater(mobj, n=n, cx=cx, c=c):
                def updater(mobj):
                    # Smooth per-bar growth as N crosses n
                    alpha = np.clip(N_tracker.get_value() - (n - 1), 0.0, 1.0)
                    target_y = center_y + math.copysign(abs(c)*scale, c)
                    current_y = center_y + alpha * (target_y - center_y)
                    # Color fades from gray to sign-colored
                    inc_color = BLUE_C if c > 0 else RED_C
                    col = interpolate_color(Color(Color(GRAY_B)), Color(Color(inc_color)), alpha)
                    new_bar = Line([cx, center_y, 0], [cx, current_y, 0], color=col, stroke_width=10)
                    new_bar.set_z_index(1)
                    mobj.become(new_bar)
                return updater
            bar.add_updater(make_updater(bar))
            bars.add(bar)

        panel_group = VGroup(panel_rect, base_line, y_axis_line)
        self.play(Create(panel_group), run_time=1.2)
        self.play(FadeIn(ticks), run_time=0.6)
        self.play(FadeIn(bars), run_time=0.4)

        # Partial sum S_N(x)
        def partial_sum(x, N):
            N_int = max(1, int(round(N)))
            s = 0.0
            for n in range(1, N_int + 1):
                s += 2*((-1)**(n+1))*math.sin(n*x)/n
            return s

        sN_graph = always_redraw(
            lambda: axes.plot(
                lambda x: partial_sum(x, N_tracker.get_value()),
                x_range=[-math.pi, math.pi, step],
                color=RED,
            ).set_stroke(width=3).set_z_index(2)
        )
        sN_label = always_redraw(
            lambda: MathTex(f"S_{{{max(1, int(round(N_tracker.get_value())))}}}(x)", font_size=36)
            .next_to(axes, UP, buff=0.1)
        )

        self.play(FadeIn(VGroup(sN_graph, sN_label)), run_time=0.6)
        self.play(N_tracker.animate.set_value(max_n), run_time=9.0, rate_func=linear)

        # Gibbs phenomenon pointer near x ~ pi
        gibbs_arrow = Arrow(
            start=axes.c2p(2.3, 2.7),
            end=axes.c2p(2.95, 3.1),
            color=WHITE,
            max_tip_length_to_length_ratio=0.2
        )
        gibbs_label = Text("Gibbs", font_size=28).next_to(gibbs_arrow, UP, buff=0.1)
        self.play(FadeIn(VGroup(gibbs_arrow, gibbs_label)), run_time=0.6)
        self.wait(1.4)
        self.play(FadeOut(VGroup(gibbs_arrow, gibbs_label)), run_time=0.6)

        # Outro pause
        self.wait(2.0)
