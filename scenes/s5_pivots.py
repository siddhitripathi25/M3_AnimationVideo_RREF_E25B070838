"""SCENE 5 — THE PIVOT DISCOVERY.

Pivots ignite (columns 1 and 3); column 2 is free. Beams carry the pivot positions
back to the ORIGINAL matrix A (RREF changes the columns; it keeps their relations).
RREF rows -> equations -> x2 = t -> x = t(-2, 1, 0).
Two linked panels driven by one tracker t:
  left:  the solution x(t) sliding along the null line
  right: x1·v1 + x2·v2 + x3·v3 drawn tip to tail; it always returns to 0.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from beyond.palette import *
from beyond.typeset import Math, Words, num
from beyond.fx import glow_dot, glow, GlowVector
from beyond.matrix import AnimatedMatrix
from beyond.base import Base2D, V1, V2, V3
from beyond import mathdata as md
from s4_machine import rref_composition

NULL = np.array([-2.0, 1.0, 0.0])


def projector(theta, phi=64 * DEGREES):
    ex = np.array([-np.sin(theta), np.cos(theta), 0.0])
    ey = np.array([-np.cos(phi) * np.cos(theta), -np.cos(phi) * np.sin(theta), np.sin(phi)])
    return lambda p: np.array([ex @ p, ey @ p, 0.0])


def f2(x):
    x = round(float(x), 2) or 0.0          # no "−0.00"
    return f"{x:.2f}".replace("-", "−")


class S5Pivots(Base2D):
    def construct(self):
        R, lbl = rref_composition()
        self.add(R, lbl)
        self.wait(0.6)

        # ── 1. the pivots ignite ───────────────────────────────────────────
        def ignite(r, c):
            cell = R.cells[r][c]
            ring = Circle(radius=0.42, color=LIME, stroke_width=5).move_to(cell)
            ring_g = glow(ring, color=LIME, width=5)
            frame = R.col_frame(c, LIME)
            tag = Words("pivot", 26, color=LIME, weight="MEDIUM").next_to(frame, UP, buff=0.2)
            self.play(Create(ring_g), cell.animate.set_color(LIME).scale(1.15), run_time=0.8,
                      rate_func=rate_functions.ease_out_back)
            self.play(FadeIn(frame), FadeIn(tag, shift=0.15 * DOWN), run_time=0.7)
            return VGroup(ring_g, frame, tag)

        self.mark("pivots")
        p1 = ignite(0, 0)
        self.wait(0.5)
        p3 = ignite(1, 2)
        self.wait(0.4)
        f2frame = R.col_frame(1, ORANGE)
        ftag = Words("no pivot", 26, color=ORANGE, weight="MEDIUM").next_to(f2frame, UP, buff=0.2)
        self.play(FadeIn(f2frame), FadeIn(ftag, shift=0.15 * DOWN), R.col(1).animate.set_color(ORANGE), run_time=0.9)
        rank = Math("2 pivots   ⇒   rank A = 2", 44, colors={"2 pivots": LIME, "rank A = 2": LIME})
        rank.next_to(R, DOWN, buff=0.6).set_x(0)
        self.play(FadeIn(rank, shift=0.2 * UP), run_time=0.9)
        self.wait(1.8)

        # ── 2. back to the ORIGINAL matrix ─────────────────────────────────
        self.mark("backlink")
        rgroup = VGroup(R, p1, p3, f2frame, ftag)
        self.play(FadeOut(lbl), FadeOut(rank), rgroup.animate.scale(0.6).move_to([-4.45, -1.75, 0]), run_time=1.2)
        rl = Math("RREF(A)", 34, colors={"RREF": LIME}).next_to(R, DOWN, buff=0.25)
        A = AnimatedMatrix(md.A0).scale(0.6).move_to([-4.45, 1.95, 0])
        al = Math("A", 38).next_to(A, LEFT, buff=0.25)
        self.play(FadeIn(A), FadeIn(al), FadeIn(rl), run_time=1.0)
        beams = VGroup()
        for c in (0, 2):
            a, b = R.slot(0, c) + UP * 1.05 * R.k, A.slot(2, c) + DOWN * 0.75 * A.k
            ln = Line(a, b, stroke_width=4, color=LIME)
            beams.add(glow(ln, color=LIME, width=4))
        aframes = VGroup(A.col_frame(0, LIME), A.col_frame(2, LIME))
        vtags = VGroup(Math("v₁", 38, color=CYAN).next_to(aframes[0], UP, buff=0.15),
                       Math("v₃", 38, color=BLUE_CORE).next_to(aframes[1], UP, buff=0.15))
        self.play(LaggedStart(*[Create(b) for b in beams], lag_ratio=0.3), run_time=1.4)
        self.play(FadeIn(aframes), FadeIn(vtags, shift=0.15 * DOWN), run_time=0.8)

        lines = VGroup(
            Words("Pivot positions in the RREF", 30, color=WHITE),
            Words("pick out columns 1 and 3 of the ORIGINAL A.", 30, color=WHITE),
            Math("v₁, v₃  are independent       rank A = 2", 36, colors={"v₁": CYAN, "v₃": BLUE_CORE, "rank A = 2": LIME}),
            Math("column 2 has no pivot :  v₂ depends on them", 34, colors={"v₂": YELLOW, "column 2": ORANGE}),
            Words("Row operations change the columns,", 24, color=MUTED),
            Words("but never the relations between them.", 24, color=MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        lines.move_to([0, 0.1, 0]).align_to([-2.1, 0, 0], LEFT)
        lines[4:].shift(DOWN * 0.25)
        lines[2].shift(DOWN * 0.15)
        lines[4].shift(DOWN * 0.25)
        for i, l in enumerate(lines):
            self.play(FadeIn(l, shift=0.2 * LEFT), run_time=0.7)
            self.wait(0.9 if i < 5 else 2.0)

        # ── 3. RREF rows -> equations -> the free variable ─────────────────
        self.play(FadeOut(VGroup(A, al, beams, aframes, vtags, lines)), run_time=0.8)
        self.play(VGroup(rgroup, rl).animate.move_to([-3.4, 0.2, 0]).scale(1.15), run_time=1.0)
        self.mark("equations")
        eqs = VGroup(Math("x₁ + 2x₂ = 0", 46, colors={"x₂": ORANGE}),
                     Math("x₃ = 0", 46),
                     Math("0 = 0", 46, color=MUTED))
        for i, e in enumerate(eqs):
            e.move_to([2.6, R.slot(i, 1)[1], 0]).align_to([0.9, 0, 0], LEFT)
        for i, e in enumerate(eqs):
            fr = R.row_frame(i, WHITE)
            self.play(Create(fr), FadeIn(e, shift=0.3 * RIGHT), run_time=0.8)
            self.play(FadeOut(fr), run_time=0.3)
        free = Math("x₂ = t     (free)", 46, color=ORANGE).next_to(eqs, DOWN, buff=0.6, aligned_edge=LEFT)
        self.play(FadeIn(free, shift=0.2 * UP), run_time=0.8)
        sol = Math("x = t(−2, 1, 0)", 64, colors={"t": ORANGE}).next_to(free, DOWN, buff=0.55, aligned_edge=LEFT)
        box = SurroundingRectangle(sol, color=ORANGE, buff=0.22, corner_radius=0.12, stroke_width=3)
        self.play(FadeIn(sol, scale=1.1), Create(box), run_time=1.2)
        self.wait(2.0)

        # ── 4. linked panels: one tracker t drives both ────────────────────
        self.play(FadeOut(VGroup(rgroup, rl, eqs, free)), VGroup(sol, box).animate.scale(0.7).to_edge(UP, buff=0.4),
                  run_time=1.0)
        self.mark("panels")
        t = ValueTracker(0.0)
        th = ValueTracker(-58 * DEGREES)
        LC, RC = np.array([-3.55, -0.1, 0]), np.array([3.55, -0.1, 0])
        LS, RS = 0.88, 0.6

        def axes_at(center, scale, length):
            pr = projector(th.get_value())
            g = VGroup()
            for d in np.eye(3):
                g.add(Line(center + scale * pr(-0.4 * length * d), center + scale * pr(length * d),
                           stroke_width=1.6, color=AXIS).set_stroke(opacity=0.6))
            return g

        def left_panel():
            pr = projector(th.get_value())
            P = lambda p: LC + LS * pr(p)
            g = VGroup(axes_at(LC, LS, 2.4))
            line = Line(P(-1.6 * NULL), P(1.6 * NULL), stroke_width=3, color=ORANGE)
            g.add(glow(line, color=ORANGE, width=3))
            tv = t.get_value()
            if abs(tv) > 1e-3:
                g.add(GlowVector(P(np.zeros(3)), P(tv * NULL), ORANGE, width=5, flat=True, head=0.18))
            g.add(glow_dot(P(tv * NULL), WHITE, radius=0.05))
            return g

        def right_panel():
            pr = projector(th.get_value())
            P = lambda p: RC + RS * pr(p)
            g = VGroup(axes_at(RC, RS, 3.2))
            tv = t.get_value()
            a = -2 * tv * V1                      # x1 v1
            b = a + tv * V2                       # + x2 v2  (= 0 exactly)
            o = P(np.zeros(3))
            if abs(tv) > 1e-3:
                d = P(a) - o
                n = np.array([-d[1], d[0], 0]) / (np.linalg.norm(d) + 1e-9) * 0.13   # lane offset (display only)
                g.add(GlowVector(o + n, P(a) + n, CYAN, width=5, flat=True, head=0.17))
                g.add(GlowVector(P(a) - n, P(b) - n, YELLOW, width=5, flat=True, head=0.17))
            g.add(glow_dot(o, PINK, radius=0.07))
            return g

        lp, rp = always_redraw(left_panel), always_redraw(right_panel)
        lh = Words("the solutions  x", 28, color=ORANGE).move_to(LC + UP * 2.35)
        rh = Math("x₁v₁ + x₂v₂ + x₃v₃", 36, colors={"v₁": CYAN, "v₂": YELLOW, "v₃": BLUE_CORE}).move_to(RC + UP * 2.35)
        div = DashedLine(UP * 2.2, DOWN * 3.6, color=GRID, stroke_width=2)
        self.play(FadeIn(lp), FadeIn(rp), FadeIn(lh), FadeIn(rh), Create(div), run_time=1.2)

        lread = always_redraw(lambda: Math(
            f"t = {f2(t.get_value())}     x = ({f2(-2 * t.get_value())}, {f2(t.get_value())}, 0)", 32,
            colors={"t": ORANGE}).move_to(LC + DOWN * 3.05))
        rread = always_redraw(lambda: Math(
            f"({f2(-2 * t.get_value())})v₁ + ({f2(t.get_value())})v₂ + 0·v₃ = 0", 32,
            colors={"v₁": CYAN, "v₂": YELLOW, "v₃": BLUE_CORE}).move_to(RC + DOWN * 3.05))
        self.play(FadeIn(lread), FadeIn(rread), run_time=0.6)
        self.play(t.animate.set_value(1.0), th.animate.set_value(-40 * DEGREES), run_time=3.0, rate_func=smooth)
        home = Math("out along v₁, then straight back to 0", 30, colors={"v₁": CYAN, "0": PINK}).move_to(RC + UP * 1.75)
        self.play(FadeIn(home), run_time=0.6)
        self.play(t.animate.set_value(-0.9), th.animate.set_value(-75 * DEGREES), run_time=4.0, rate_func=smooth)
        self.play(t.animate.set_value(0.5), th.animate.set_value(-50 * DEGREES), run_time=3.0, rate_func=smooth)
        self.play(t.animate.set_value(1.0), run_time=1.6, rate_func=smooth)
        self.wait(0.4)

        self.mark("final")
        final = Math("−2v₁ + v₂ = 0", 64, colors={"v₁": CYAN, "v₂": YELLOW})
        final.scale(0.85).move_to(DOWN * 3.35)
        self.play(FadeOut(lread), FadeOut(rread), FadeOut(lh), FadeOut(rh), FadeOut(home),
                  VGroup(sol, box).animate.set_opacity(0.0), run_time=0.6)
        self.play(FadeIn(final, scale=1.2), run_time=1.0)
        moral = Words("a free variable  →  a non-zero solution  →  dependence", 28, color=WHITE)
        moral.next_to(final, UP, buff=0.2)
        moral[0:15].set_color(ORANGE)
        moral[-10:].set_color(PINK)
        self.play(FadeIn(moral, shift=0.2 * UP), run_time=0.9)
        self.wait(3.0)
        seed = glow_dot(RC, PINK, radius=0.07)              # the right panel's origin (the "0")
        self.add(seed)
        lime = glow_dot(ORIGIN, LIME, radius=0.055)         # identical to Scene 6's first frame
        self.play(FadeOut(VGroup(lp, rp, div, moral, final)), Transform(seed, lime, rate_func=smooth), run_time=1.6)
