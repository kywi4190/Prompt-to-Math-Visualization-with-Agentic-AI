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

class GroupTheoryScene(Scene):
    def construct(self):
        # Helpers
        def rot_z(theta):
            return np.array([
                [math.cos(theta), -math.sin(theta), 0.0],
                [math.sin(theta),  math.cos(theta), 0.0],
                [0.0,              0.0,             1.0],
            ])

        def apply_linear(mobj, M, run_time=1.0):
            # Animate the method directly; M is 3x3.
            self.play(mobj.animate.apply_matrix(M), run_time=run_time)

        # --- Visual hook: an equilateral triangle with labeled vertices ---
        R = 1.5
        base_angle = math.pi/2  # top vertex up
        tri_verts = []
        for k in range(3):
            ang = base_angle + 2*math.pi*k/3
            tri_verts.append([R*math.cos(ang), R*math.sin(ang), 0.0])

        tri_poly = Polygon(*tri_verts, stroke_color=WHITE, stroke_width=4)
        tri_poly.set_fill(Color("#1f77b4"), opacity=0.5)

        v_dots = VGroup(*[Dot(np.array(p), color=YELLOW).scale(0.9) for p in tri_verts])
        tri_group = VGroup(tri_poly, v_dots)

        # Vertex labels that stay upright via updaters (follow the vertex dots)
        labels_txt = [Tex(r"A").scale(0.5), Tex(r"B").scale(0.5), Tex(r"C").scale(0.5)]
        for lab, d in zip(labels_txt, v_dots):
            def updater(m, dt, dot=d):
                m.move_to(dot.get_center() + 0.28*UP)
                m.set_rotation(0)
            lab.add_updater(updater)
        labels = VGroup(*labels_txt)

        # Mirror line for s: vertical line x=0
        mirror_line = Line([-0.0, -3.2, 0.0], [-0.0, 3.2, 0.0], color=GRAY_B, stroke_width=2, z_index=-1)
        mirror_label = Tex(r"s").scale(0.6).set_color(ORANGE).next_to(mirror_line, RIGHT)

        # Generators as matrices
        R120 = rot_z(2*math.pi/3)
        M_ref = np.array([
            [-1.0, 0.0, 0.0],
            [ 0.0, 1.0, 0.0],
            [ 0.0, 0.0, 1.0],
        ])

        # Show triangle and mirror
        self.play(Create(tri_poly), FadeIn(v_dots), run_time=1.0)
        self.play(FadeIn(labels), run_time=0.6)

        r_tag = MathTex(r"r").set_color(BLUE).scale(0.8).move_to([0.0, 2.4, 0.0])
        self.play(Write(r_tag), run_time=0.6)

        # r: rotate by 120 degrees
        apply_linear(tri_group, R120, run_time=1.2)
        # r^3 = e demonstration: two quick rotations to return
        apply_linear(tri_group, R120, run_time=0.5)
        apply_linear(tri_group, R120, run_time=0.5)
        r3e = MathTex(r"r^3=e").scale(0.7).next_to(r_tag, RIGHT)
        self.play(Write(r3e), run_time=0.5)
        self.play(FadeOut(r_tag), FadeOut(r3e), run_time=0.5)

        # s: reflect across vertical line
        s_tag = MathTex(r"s").set_color(ORANGE).scale(0.8).move_to([-2.0, 2.2, 0.0])
        self.play(Create(mirror_line), Write(s_tag), run_time=1.2)
        apply_linear(tri_group, M_ref, run_time=1.2)

        # Shift triangle and mirror left to make room for Cayley graph
        left_group = VGroup(tri_group, mirror_line, mirror_label)
        self.play(left_group.animate.shift(3.2*LEFT), s_tag.animate.shift(3.2*LEFT), run_time=0.8)

        # --- Cayley graph for D3 on the right ---
        center = np.array([3.2, 0.0, 0.0])
        rad = 2.0
        names_order = ["e", "r", "r^2", "sr^2", "sr", "s"]  # clockwise from top
        hex_positions = {}
        for i, name in enumerate(names_order):
            angle = math.pi/2 - i*math.pi/3
            pos = center + np.array([rad*math.cos(angle), rad*math.sin(angle), 0.0])
            hex_positions[name] = pos

        # Nodes and labels
        nodes = {}
        node_dots = VGroup()
        node_labels = VGroup()
        for nm in names_order:
            d = Dot(hex_positions[nm], color=WHITE, radius=0.075)
            nodes[nm] = d
            node_dots.add(d)
            lab = MathTex(nm).scale(0.6).move_to(hex_positions[nm] + 0.35*DOWN)
            node_labels.add(lab)

        self.play(FadeIn(node_dots, lag_ratio=0.1), FadeIn(node_labels, lag_ratio=0.1), run_time=1.4)

        # Edges: r in BLUE, s in ORANGE
        r_edges = VGroup(
            Line(hex_positions["e"],   hex_positions["r"],   color=BLUE, stroke_width=3),
            Line(hex_positions["r"],   hex_positions["r^2"], color=BLUE, stroke_width=3),
            Line(hex_positions["r^2"], hex_positions["e"],   color=BLUE, stroke_width=3),
            Line(hex_positions["sr^2"], hex_positions["sr"], color=BLUE, stroke_width=3),
            Line(hex_positions["sr"],   hex_positions["s"],  color=BLUE, stroke_width=3),
            Line(hex_positions["s"],    hex_positions["sr^2"], color=BLUE, stroke_width=3),
        )
        s_edges = VGroup(
            Line(hex_positions["e"],   hex_positions["s"],    color=ORANGE, stroke_width=3),
            Line(hex_positions["r"],   hex_positions["sr"],   color=ORANGE, stroke_width=3),
            Line(hex_positions["r^2"], hex_positions["sr^2"], color=ORANGE, stroke_width=3),
        )
        r_edges.set_z_index(1)
        s_edges.set_z_index(1)
        self.play(Create(r_edges), Create(s_edges), run_time=1.0)

        # Token to walk the graph; keep above edges
        token = Dot(color=YELLOW).scale(1.0).move_to(hex_positions["e"])
        token.set_z_index(10)
        self.play(FadeIn(token), run_time=0.4)

        # Word to trace
        word = MathTex(r"w = r\, r\, s\, r\, r\, s").scale(0.7).move_to(center + 2.3*DOWN)
        self.play(Write(word), run_time=0.8)

        # Path and simultaneous action on the triangle
        path_nodes = ["e", "r", "r^2", "sr^2", "sr", "s", "e"]
        gens = ["r", "r", "s", "r", "r", "s"]
        gen_colors = {"r": BLUE, "s": ORANGE}
        gen_mats = {"r": R120, "s": M_ref}

        for g, start, end in zip(gens, path_nodes[:-1], path_nodes[1:]):
            self.play(
                token.animate.move_to(hex_positions[end]).set_color(gen_colors[g]),
                tri_group.animate.apply_matrix(gen_mats[g]),
                run_time=1.4,
            )

        # Conclude: highlight e and simplify the word
        e_dot = nodes["e"]
        self.play(e_dot.animate.scale(1.6).set_color(YELLOW), run_time=0.4)
        self.play(e_dot.animate.scale(1/1.6).set_color(WHITE), run_time=0.4)

        word_e = MathTex(r"w = e").scale(0.9).move_to(word.get_center())
        self.play(Transform(word, word_e), run_time=0.8)
        self.wait(0.4)
