from manim import *

class DivisionScene(Scene):
    def construct(self):
        # Create a pizza (circle) and slices
        pizza = Circle(radius=2, color=YELLOW).shift(LEFT*3)
        slices = []
        for i in range(4):
            angle = i * PI / 2
            slice = Sector(radius=2, angle=PI/2, color=WHITE, fill_opacity=1)
            slice.move_to(pizza.get_center())
            slice.rotate(angle)
            slices.append(slice)
        pizza_group = VGroup(*slices)

        # Create friends as dots
        friends = [Dot().move_to([x, 0, 0]) for x in range(-2, 3, 2)]
        friends_group = VGroup(*friends).shift(RIGHT*3)

        # Show pizza and friends
        self.play(Create(pizza), FadeIn(friends_group))
        self.wait(1)

        # Show division of slices
        for i, slice in enumerate(slices):
            self.play(Transform(slice, slice.copy().scale(0.5).move_to(friends[i].get_center())))
        self.wait(1)

        # Show the result of division
        result_text = Text('Each friend gets 2 slices').next_to(friends_group, DOWN)
        self.play(FadeIn(result_text))
        self.wait(2)
