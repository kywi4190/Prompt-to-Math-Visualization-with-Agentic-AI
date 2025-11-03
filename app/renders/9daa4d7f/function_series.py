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

class FunctionSeriesScene(ThreeDScene):
    def construct(self):
        # ------------------- 3D HOOK: vector as sum of orthogonal parts -------------------
        self.set_camera_orientation(phi=60*DEGREES, theta=-45*DEGREES, zoom=1.2)
        axes3d = ThreeDAxes(
            x_range=[0, 2, 1], y_range=[0, 2, 1], z_range=[0, 2, 1],
            x_length=4, y_length=4, z_length=3
        )
        v_end = np.array([1.6, 1.2, 1.0])
        # Remove unsupported tip_length/tip_width kwargs for Arrow3D; use thickness and color
        comp_x = Arrow3D(start=[0, 0, 0], end=[v_end[0], 0, 0], color=RED, thickness=0.04)
        comp_y = Arrow3D(start=[v_end[0], 0, 0], end=[v_end[0], v_end[1], 0], color=GREEN, thickness=0.04)
        comp_z = Arrow3D(start=[v_end[0], v_end[1], 0], end=v_end, color=BLUE, thickness=0.04)
        v_vec = Arrow3D(start=[0, 0, 0], end=v_end, color=YELLOW, thickness=0.06)
        v_vec.set_z_index(3)
        axes3d.set_z_index(1)

        hook_text = Text("Sum of orthogonal components", font_size=36, color=GREY_B)
        hook_text.to_edge(UP)
        self.add_fixed_in_frame_mobjects(hook_text)

        self.play(Create(axes3d), run_time=0.9)
        self.play(Create(VGroup(comp_x, comp_y, comp_z)), run_time=1.0)
        self.play(Create(v_vec), run_time=1.0)
        self.play(Write(hook_text), run_time=0.6)
        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(1.8)
        self.stop_ambient_camera_rotation()
        self.wait(0.2)
        self.move_camera(phi=90*DEGREES, theta=-90*DEGREES, zoom=1.0, run_time=1.0)
        self.play(FadeOut(VGroup(axes3d, comp_x, comp_y, comp_z, v_vec)), run_time=0.6)
        self.remove(hook_text)

        # ------------------- 2D PART: Fourier series for f(x)=x on [-pi, pi] -------------------
        # Axes for function and partial sums
        axes = Axes(
            x_range=[-math.pi, math.pi, math.pi/2],
            y_range=[-3.5, 3.5, 1],
            x_length=8,
            y_length=4.5,
            tips=False,
        )
        axes.to_edge(LEFT, buff=0.6)

        # Plot target function f(x)=x
        graph_f = axes.plot(
            lambda x: x,
            x_range=[-math.pi, math.pi],
            color=GREY_B,
            samples=300,
            use_smoothing=False,
        )
        title = MathTex(r"f(x)=x\;\text{ on }[-\pi,\pi]").scale(0.8)
        title.next_to(axes, UP)

        self.play(Create(axes), run_time=1.0)
        self.play(Create(graph_f), run_time=0.8)
        self.play(FadeIn(title, shift=0.2*UP), run_time=0.6)

        # Fourier sine series partial sums: b_n = 2*(-1)^{n+1}/n
        def fourier_sum(x, N):
            N = int(max(1, N))
            s = 0.0
            for n in range(1, N + 1):
                b = 2*((-1)**(n+1))/n
                s += b * math.sin(n * x)
            return s

        N = ValueTracker(1)
        graph_sn = always_redraw(
            lambda: axes.plot(
                lambda x: fourier_sum(x, int(N.get_value())),
                x_range=[-math.pi, math.pi],
                color=YELLOW,
                samples=400,
                discontinuities=[-math.pi],
                use_smoothing=False,
            )
        )
        self.play(Create(graph_sn), run_time=0.8)
        self.wait(0.6)

        # Side bar chart for coefficients b_n
        bar_ax = Axes(x_range=[0, 10, 1], y_range=[-2.2, 2.2, 1], x_length=4, y_length=4.5, tips=False)
        bar_ax.next_to(axes, RIGHT, buff=0.8)
        b_label = MathTex(r"b_n=\dfrac{2(-1)^{n+1}}{n}").scale(0.8)
        b_label.next_to(bar_ax, UP)

        # Make coefficient bars that grow as N increases
        def make_bar(n):
            bn = 2*((-1)**(n+1))/n
            col = BLUE if bn >= 0 else RED
            base = bar_ax.c2p(n, 0)
            line = Line(base, base, color=col, stroke_width=6)

            def upd(m, n=n, bn=bn):
                currentN = int(np.floor(N.get_value() + 1e-6))
                h = bn if currentN >= n else 0.0
                m.put_start_and_end_on(base, bar_ax.c2p(n, h))
            line.add_updater(upd)
            return line

        bars = VGroup(*[make_bar(n) for n in range(1, 10)])

        # Animate increasing number of terms
        self.play(N.animate.set_value(5), run_time=4.0)
        self.play(Create(bar_ax), FadeIn(VGroup(bars, b_label), shift=0.2*UP), run_time=0.8)
        self.play(N.animate.set_value(9), run_time=4.0)

        compare_text = Tex(r"Fourier: waves \\ Taylor: powers", color=GREY_B).scale(0.7)
        compare_text.to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(compare_text)
        self.play(FadeIn(compare_text, shift=0.2*UP), run_time=0.6)

        self.wait(4.0)
