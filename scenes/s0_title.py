"""SCENE 0 — TITLE CARD.

Title, creator and URN, then a fade into the darkness that opens Scene 1.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from beyond.palette import *
from beyond.typeset import Words
from beyond.fx import glow, glow_dot
from beyond.base import Base2D

# ── edit these if needed ────────────────────────────────────────────────────
TITLE = "BEYOND THE PIVOTS"
SUBTITLE = "Understanding linear independence through reduced row-echelon form"
CREATOR = "SIDDHI TRIPATHI"
URN = "E25B070838"


class S0Title(Base2D):
    def construct(self):
        self.mark("title")
        self.wait(0.6)

        # a thin lime line opens from the centre, carried by two points
        line = Line(LEFT * 0.01, RIGHT * 0.01, color=LIME, stroke_width=2.5).shift(UP * 0.35)
        line_g = glow(line, color=LIME, width=2.5)
        ends = VGroup(glow_dot(line.get_start(), LIME, 0.045), glow_dot(line.get_end(), LIME, 0.045))
        self.add(line_g, ends)
        target = Line(LEFT * 3.6, RIGHT * 3.6).shift(UP * 0.35)
        self.play(
            *[m.animate.put_start_and_end_on(target.get_start(), target.get_end()) for m in line_g],
            ends[0].animate.move_to(target.get_start()), ends[1].animate.move_to(target.get_end()),
            run_time=1.4, rate_func=smooth,
        )

        title = Words(TITLE, 80, color=WHITE, weight="BOLD").next_to(line, UP, buff=0.45)
        sub = Words(SUBTITLE, 28, color=MUTED).next_to(line, DOWN, buff=0.35)
        self.play(FadeIn(title, shift=0.25 * UP), run_time=1.3)
        self.play(FadeIn(sub, shift=0.15 * DOWN), run_time=0.9)

        name = Words(CREATOR, 40, color=WHITE, weight="MEDIUM")
        urn = Words(f"URN:  {URN}", 30, color=CYAN)
        who = VGroup(name, urn).arrange(DOWN, buff=0.22).next_to(sub, DOWN, buff=0.85)
        self.play(FadeIn(name, shift=0.15 * UP), run_time=0.9)
        self.play(FadeIn(urn, shift=0.15 * UP), run_time=0.8)
        self.wait(3.2)

        # into the darkness where Scene 1 begins
        self.play(FadeOut(VGroup(title, sub, name, urn)), run_time=1.2)
        self.play(*[m.animate.put_start_and_end_on(UP * 0.35 + LEFT * 0.01, UP * 0.35 + RIGHT * 0.01) for m in line_g],
                  ends[0].animate.move_to(UP * 0.35), ends[1].animate.move_to(UP * 0.35), run_time=1.0)
        self.play(FadeOut(line_g), FadeOut(ends), run_time=0.6)
        self.wait(0.4)
