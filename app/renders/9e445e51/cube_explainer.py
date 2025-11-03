from manim import *

class CubeScene(Scene):
    def construct(self):
        # Base square (front face) vertices
        A = [-2.0, -1.5, 0]
        B = [1.0, -1.5, 0]
        C = [1.0, 1.5, 0]
        D = [-2.0, 1.5, 0]

        # Depth direction (fake 3D) vector
        depth_vec = [1.2, 0.8, 0]

        def shift_point(p, t):
            return [p[0] + depth_vec[0] * t, p[1] + depth_vec[1] * t, 0]

        # Front face
        front = Polygon(A, B, C, D)
        front.set_fill(BLUE, opacity=0.18)
        front.set_stroke(WHITE, width=3)
        front.set_z_index(2)

        # Extrusion tracker
        depth_t = ValueTracker(0.0)

        # Back face (always follows tracker)
        back = always_redraw(
            lambda: Polygon(
                shift_point(A, depth_t.get_value()),
                shift_point(B, depth_t.get_value()),
                shift_point(C, depth_t.get_value()),
                shift_point(D, depth_t.get_value()),
            ).set_fill(GREEN, opacity=0.10).set_stroke(WHITE, width=2)
        )
        back.set_z_index(0)

        # Connectors between corresponding corners
        edge_A = always_redraw(lambda: Line(A, shift_point(A, depth_t.get_value()), stroke_width=2, color=WHITE))
        edge_B = always_redraw(lambda: Line(B, shift_point(B, depth_t.get_value()), stroke_width=2, color=WHITE))
        edge_C = always_redraw(lambda: Line(C, shift_point(C, depth_t.get_value()), stroke_width=2, color=WHITE))
        edge_D = always_redraw(lambda: Line(D, shift_point(D, depth_t.get_value()), stroke_width=2, color=WHITE))
        connectors = VGroup(edge_A, edge_B, edge_C, edge_D)
        connectors.set_z_index(1)

        # Hook: draw the square face
        self.play(Create(front), run_time=1.0)
        sq_label = Text("square face").scale(0.5).next_to(front, DOWN)
        self.play(FadeIn(sq_label, shift=DOWN), run_time=0.7)
        self.wait(0.3)
        self.play(FadeOut(sq_label), run_time=0.3)

        # Show the back face and connectors, then extrude to form the cube wireframe
        self.play(FadeIn(back, connectors), run_time=0.4)
        self.play(depth_t.animate.set_value(1.0), run_time=3.0, rate_func=smooth)

        # Brief cube label
        cube_label = Text("cube").scale(0.6).next_to(front, UP)
        self.play(FadeIn(cube_label), run_time=0.6)
        self.play(FadeOut(cube_label), run_time=0.3)

        # Dimension arrows and labels
        # Length along AB (below the bottom edge)
        len_arrow = Arrow(
            [A[0], A[1] - 0.6, 0],
            [B[0], B[1] - 0.6, 0],
            buff=0,
            stroke_width=6,
            color=YELLOW,
        )
        len_label = Text("length").scale(0.5).next_to(len_arrow, DOWN)

        # Width along AD (to the left of the left edge)
        wid_arrow = Arrow(
            [A[0] - 0.6, A[1], 0],
            [D[0] - 0.6, D[1], 0],
            buff=0,
            stroke_width=6,
            color=TEAL,
        )
        wid_label = Text("width").scale(0.5).next_to(wid_arrow, LEFT)

        # Height along the depth direction from D to D'
        D_prime = shift_point(D, 1.0)
        hgt_arrow = Arrow(D, D_prime, buff=0, stroke_width=6, color=PURPLE)
        hgt_label = Text("height").scale(0.5).next_to(hgt_arrow, UP)

        self.play(GrowArrow(len_arrow), FadeIn(len_label), run_time=0.8)
        self.play(GrowArrow(wid_arrow), FadeIn(wid_label), run_time=0.8)
        self.play(GrowArrow(hgt_arrow), FadeIn(hgt_label), run_time=1.2)

        # Final statement
        final_text = Text("That's a cube.").scale(0.6).to_edge(DOWN)
        self.play(FadeIn(final_text), run_time=0.6)
        self.wait(0.7)
