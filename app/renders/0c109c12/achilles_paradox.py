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

class AchillesParadoxScene(Scene):
    def construct(self):
        # Parameters
        xA0 = -4.0
        xT0 = -1.0
        vA = 2.0
        vT = 1.0
        r = vT / vA  # 0.5
        t_meet = (xT0 - xA0) / (vA - vT)  # 3.0
        x_meet = xA0 + vA * t_meet        # 2.0

        # Track line
        track = Line([-6, 0, 0], [6, 0, 0], color=GRAY_B)

        # Dots
        a_dot = Dot(color=BLUE).move_to([xA0, 0, 0])
        t_dot = Dot(color=ORANGE).move_to([xT0, 0, 0])

        # Labels with updaters to follow dots
        a_lab = Text("Achilles", font_size=28)
        a_lab.set_color(BLUE)
        a_lab.next_to(a_dot, UP, buff=0.15)
        a_lab.add_updater(lambda m: m.next_to(a_dot, UP, buff=0.15))

        t_lab = Text("Tortoise", font_size=28)
        t_lab.set_color(ORANGE)
        t_lab.next_to(t_dot, UP, buff=0.15)
        t_lab.add_updater(lambda m: m.next_to(t_dot, UP, buff=0.15))

        # Speed annotations
        v_text = VGroup(
            MathTex(r"v_A = 2", substrings_to_isolate=["A"]).set_color(BLUE),
            MathTex(r"v_T = 1", substrings_to_isolate=["T"]).set_color(ORANGE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_corner(UL).shift(DOWN*0.3)

        # Initial head start indicator
        head_line = Line([xA0, 0.2, 0], [xT0, 0.2, 0], color=YELLOW)
        head_label = Text("head start", font_size=26, color=YELLOW).next_to(head_line, UP, buff=0.1)

        # Intro
        self.play(Create(track), run_time=1.5)
        self.play(FadeIn(a_dot), FadeIn(t_dot), run_time=1.0)
        self.play(Write(a_lab), Write(t_lab), run_time=0.6)
        self.play(Write(v_text), run_time=1.1)
        self.play(Create(head_line), FadeIn(head_label, shift=UP*0.1), run_time=0.9)
        self.wait(0.4)

        # Geometric chase steps (Zeno's sequence)
        colors = [RED, GOLD, GREEN, TEAL, PURPLE, PINK]
        segments = VGroup()
        xA = xA0
        xT = xT0
        # Scale times so the geometric sum of step durations ~ 16s
        base_time_scale = 16.0 / t_meet
        n_steps = 6
        for i in range(n_steps):
            xT_prev = xT
            # time Achilles needs to reach the tortoise's previous position
            gap = xT_prev - xA
            dt = gap / vA
            # new tortoise position after that time
            xT_new = xT_prev + vT * dt
            # Achilles travels from xA to xT_prev
            seg = Line([xA, 0, 0], [xT_prev, 0, 0], color=colors[i % len(colors)], stroke_width=6)
            segments.add(seg)
            # Animate motion and draw segment together
            rt = max(0.15, base_time_scale * dt)
            anims = [a_dot.animate.move_to([xT_prev, 0, 0]), t_dot.animate.move_to([xT_new, 0, 0])]
            if abs(xT_prev - xA) > 1e-6:
                self.play(Create(seg), *anims, run_time=rt)
            else:
                self.play(*anims, run_time=rt)
            # Update state
            xA = xT_prev
            xT = xT_new

        # Emphasize the halving of intervals (r = v_T / v_A)
        shrink_text = VGroup(
            Text("Intervals shrink by half", font_size=30).set_color(YELLOW),
            MathTex(r"r = v_T / v_A = 1/2").set_color(YELLOW),
        ).arrange(DOWN, buff=0.2).to_edge(UP)
        self.play(FadeIn(shrink_text, shift=UP*0.2), run_time=1.2)
        self.wait(1.2)

        # Move the track to the left, make room for graph on the right
        track_group = VGroup(track, a_dot, t_dot, a_lab, t_lab, head_line, head_label, segments)
        self.play(track_group.animate.scale(0.9).to_edge(LEFT), run_time=3.0)

        # Axes: time vs position
        axes = Axes(
            x_range=[0, 3.3, 1],
            y_range=[-4.5, 6.0, 1],
            x_length=5.5,
            y_length=3.6,
            tips=False,
        )
        axes.to_edge(RIGHT).shift(DOWN*0.3)
        x_label = MathTex(r"t").next_to(axes.x_axis, RIGHT, buff=0.1)
        y_label = Text("position", font_size=24).next_to(axes.y_axis, UP, buff=0.1)

        fA = lambda t: xA0 + vA * t
        fT = lambda t: xT0 + vT * t
        graphA = axes.plot(fA, x_range=[0, 3.0, 0.01], color=BLUE)
        graphT = axes.plot(fT, x_range=[0, 3.0, 0.01], color=ORANGE)

        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label), run_time=1.2)
        self.play(Create(graphA), Create(graphT), run_time=1.3)

        # Moving dots along graphs with a shared time tracker
        tau = ValueTracker(0.0)
        dotA_graph = always_redraw(lambda: Dot(color=BLUE).move_to(axes.c2p(tau.get_value(), fA(tau.get_value()), 0)))
        dotT_graph = always_redraw(lambda: Dot(color=ORANGE).move_to(axes.c2p(tau.get_value(), fT(tau.get_value()), 0)))
        t_line = always_redraw(lambda: Line(
            axes.c2p(tau.get_value(), axes.y_range[0] + 0.1, 0),
            axes.c2p(tau.get_value(), axes.y_range[1] - 0.1, 0),
            color=GRAY,
            stroke_width=2
        ).set_opacity(0.4))

        self.add(dotA_graph, dotT_graph, t_line)
        self.play(tau.animate.set_value(t_meet), run_time=16.0, rate_func=linear)

        # Highlight meeting in both views
        meet_graph_dot = Dot(color=WHITE).scale(1.1).move_to(axes.c2p(t_meet, x_meet, 0))
        self.play(FadeIn(meet_graph_dot, scale=1.5), run_time=0.8)
        self.wait(0.7)

        # Snap the track dots to the meeting point to resolve the paradox visually
        self.play(a_dot.animate.move_to([x_meet, 0, 0]), t_dot.animate.move_to([x_meet, 0, 0]), run_time=2.2)
        meet_track_circle = Circle(radius=0.18, color=WHITE).move_to([x_meet, 0, 0])
        self.play(Create(meet_track_circle), run_time=0.8)

        # Outro statement (fixed newline)
        outro = Text("Infinite steps can sum to a finite time.\nAchilles catches the tortoise.", font_size=34)
        outro.set_color_by_t2c({"finite": YELLOW})
        outro.to_edge(DOWN)
        self.play(FadeIn(outro, shift=UP*0.2), run_time=1.6)
        self.wait(2.0)

        # Clean up updaters if needed (not strictly necessary before scene end)
        a_lab.remove_updater(lambda m: m.next_to(a_dot, UP, buff=0.15))
        t_lab.remove_updater(lambda m: m.next_to(t_dot, UP, buff=0.15))
