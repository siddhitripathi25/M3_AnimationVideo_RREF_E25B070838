"""SCENE 4 — THE MATRIX TRANSFORMATION MACHINE.

Every operation, none skipped. For each one: the operation, the source row lights,
a ghost of it (scaled) travels to the target row along particle arcs, digits roll to
their new values, and the arithmetic appears beside the matrix.

Invariant filaments: pink arcs tie column 1 to column 2 in every row. After every
operation the relation col2 = 2·col1 is re-checked with the live numbers. Row
operations change the columns, but never the linear relations between them; that
is why pivot positions in the RREF identify columns of the ORIGINAL matrix.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from beyond.palette import *
from beyond.typeset import Math, Words, num
from beyond.fx import glow_dot, glow
from beyond.matrix import AnimatedMatrix
from beyond.base import Base2D
from beyond import mathdata as md

MAT_POS = LEFT * 2.85 + DOWN * 0.3
PANEL_X = 3.75


def vec_str(v):
    return "(" + ", ".join(num(x) for x in v) + ")"


def rref_composition():
    """Final frame of Scene 4 == first frame of Scene 5."""
    R = AnimatedMatrix(md.FINAL_RREF).move_to(RIGHT * 1.1)
    lbl = Math("RREF(A)  =", 50, colors={"RREF": LIME}).next_to(R, LEFT, buff=0.45)
    return R, lbl


class S4Machine(Base2D):
    def construct(self):
        A = AnimatedMatrix(md.A0)
        self.add(A.entries)
        self.wait(0.4)
        self.mark("matrix")
        heads = VGroup(*[Math(n, 38, color=c) for n, c in (("v₁", CYAN), ("v₂", YELLOW), ("v₃", BLUE_CORE))])
        for i, h in enumerate(heads):
            h.move_to(A.slot(0, i) + UP * 0.95)
        a_lbl = Math("A  =", 54).next_to(A, LEFT, buff=0.45)
        self.play(Create(A.brackets), FadeIn(heads, shift=0.2 * DOWN), FadeIn(a_lbl), run_time=1.6)
        cols_txt = Words("the vectors become the columns", 28, color=MUTED).next_to(A, DOWN, buff=0.6)
        self.play(FadeIn(cols_txt), run_time=0.6)
        self.wait(1.4)
        self.play(FadeOut(cols_txt), run_time=0.4)
        self.play(VGroup(A, heads, a_lbl).animate.move_to(MAT_POS + LEFT * 0.55), run_time=1.2)

        # ── invariant filaments: col1 -> col2 in every row ────────────────
        def filaments():
            g = VGroup()
            for r in range(3):
                a, b = A.slot(r, 0) + RIGHT * 0.28 + UP * 0.12, A.slot(r, 1) + LEFT * 0.28 + UP * 0.12
                arc = ArcBetweenPoints(a, b, angle=-TAU / 5, color=PINK, stroke_width=2.5)
                g.add(arc.set_stroke(opacity=0.75))
            return g

        self.mark("filaments")
        fil = always_redraw(filaments)

        def relation_text():
            m = A.data
            c1, c2 = [row[0] for row in m], [row[1] for row in m]
            assert c2 == [2 * x for x in c1], "relation broken"  # never happens: tested in tests/
            return Math(f"col₂ = {vec_str(c2)} = 2·{vec_str(c1)}", 36, color=PINK)

        rel = relation_text().next_to(A, DOWN, buff=0.55)
        tick = Math("✓", 40, color=LIME).next_to(rel, RIGHT, buff=0.2)
        self.play(Create(fil), FadeIn(rel), run_time=1.4)
        self.play(FadeIn(tick, scale=1.6), run_time=0.5)
        note = Words("watch this relation during every step", 26, color=MUTED).next_to(rel, DOWN, buff=0.22)
        self.play(FadeIn(note), run_time=0.6)
        self.wait(1.6)
        self.play(FadeOut(note), run_time=0.5)

        # history strip of row-equivalent matrices
        history = VGroup()
        HIST_Y, HIST_X0, HIST_S = 3.35, -6.5, 0.26

        def push_history():
            mini = AnimatedMatrix(A.data, size=54).scale(HIST_S)
            if len(history) == 0:
                mini.move_to([HIST_X0 + mini.width / 2, HIST_Y, 0])
                lab = Math("A", 30).next_to(mini, LEFT, buff=0.12)
                item = VGroup(lab, mini)
                item.shift(RIGHT * lab.width)
            else:
                tl = Math("~", 36, color=VIOLET).next_to(history[-1], RIGHT, buff=0.18)
                mini.next_to(tl, RIGHT, buff=0.18)
                item = VGroup(tl, mini)
            history.add(item)
            return FadeIn(item, shift=0.2 * UP)

        self.play(push_history(), run_time=0.6)

        panel = VGroup()

        def show_panel(step, op, arith, purpose):
            nonlocal panel
            tag = Words(f"STEP {step}", 28, color=VIOLET, weight="BOLD")
            opm = Math(op, 60, color=WHITE, colors={"R": VIOLET})
            ar = Math(arith, 32, color=WHITE)
            pu = Words(purpose, 25, color=MUTED)
            new = VGroup(tag, opm, ar, pu).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
            new.move_to([PANEL_X, 0.55, 0])
            new.align_to([PANEL_X - 3.05, 0, 0], LEFT)
            ar.set_opacity(0)
            anims = [FadeIn(VGroup(tag, opm, pu), shift=0.25 * LEFT)]
            if len(panel):
                self.play(FadeOut(panel, shift=0.25 * LEFT), run_time=0.45)
            self.play(*anims, run_time=0.8)
            panel = new
            return ar

        def check_relation():
            nonlocal rel, tick
            new_rel = relation_text().move_to(rel)
            new_tick = Math("✓", 40, color=LIME).next_to(new_rel, RIGHT, buff=0.2)
            flash = filaments().set_stroke(width=7, opacity=1, color=PINK)
            self.play(ShowPassingFlash(flash, time_width=0.6), FadeOut(tick),
                      FadeTransform(rel, new_rel), run_time=1.0)
            self.play(FadeIn(new_tick, scale=1.6), run_time=0.4)
            self.wait(0.6)
            rel, tick = new_rel, new_tick

        def particles(src, tgt, color=VIOLET):
            anims = []
            for c in range(3):
                path = ArcBetweenPoints(A.slot(src, c) + RIGHT * 0.32, A.slot(tgt, c) + RIGHT * 0.32,
                                        angle=-PI / 2.2 if tgt > src else PI / 2.2)
                for j in range(3):
                    d = glow_dot(path.get_start(), color, radius=0.035)
                    anims.append(Succession(Wait(0.12 * j + 0.06 * c),
                                            MoveAlongPath(d, path, rate_func=smooth, run_time=1.0),
                                            FadeOut(d, run_time=0.2)))
            return anims

        def replace_op(step, tgt, src, factor, op, purpose):
            before_t, before_s = list(A.data[tgt]), list(A.data[src])
            after = [t + factor * s for t, s in zip(before_t, before_s)]
            sign = "+" if factor > 0 else "−"
            mag = abs(factor)
            coef = "" if mag == 1 else f"{num(mag)}·"
            arith = f"{vec_str(before_t)} {sign} {coef}{vec_str(before_s)} = {vec_str(after)}"
            ar = show_panel(step, op, arith, purpose)
            sf, tf = A.row_frame(src, VIOLET), A.row_frame(tgt, WHITE)
            tf.set_fill(opacity=0.04)
            self.play(FadeIn(sf), Create(tf), run_time=0.7)
            # ghost of the source row, scaled by the factor
            ghost = VGroup(*[Math(num(v), 46, color=VIOLET).move_to(A.slot(src, c) + RIGHT * 0.0)
                             for c, v in enumerate(before_s)])
            self.play(FadeIn(ghost), run_time=0.3)
            scaled = VGroup(*[Math(num(factor * v), 46, color=VIOLET) for v in before_s])
            for c, m in enumerate(scaled):
                m.move_to(A.slot(src, c) + UP * 0.48)
            fac = Math(f"×({num(factor)})", 28, color=VIOLET).next_to(scaled[-1], UR, buff=0.06)
            self.play(Transform(ghost, scaled), FadeIn(fac), run_time=0.8)
            target_pos = VGroup(*[m.copy().move_to(A.slot(tgt, c) + UP * 0.5) for c, m in enumerate(ghost)])
            self.play(*particles(src, tgt), Transform(ghost, target_pos),
                      fac.animate.next_to(target_pos[-1], UR, buff=0.06), run_time=1.4)
            self.play(ar.animate.set_opacity(1), run_time=0.6)
            self.wait(0.8)
            self.play(*A.set_row(tgt, after), FadeOut(ghost, shift=0.4 * DOWN), FadeOut(fac), run_time=1.0)
            self.wait(0.5)
            self.play(FadeOut(sf), FadeOut(tf), run_time=0.4)
            assert [list(r) for r in A.data] is not None
            check_relation()

        def scale_op(step, tgt, factor, op, purpose):
            before = list(A.data[tgt])
            after = [factor * v for v in before]
            arith = f"−{vec_str(before)} = {vec_str(after)}"
            ar = show_panel(step, op, arith, purpose)
            tf = A.row_frame(tgt, VIOLET)
            self.play(FadeIn(tf), run_time=0.5)
            mirror = DashedLine(A.slot(tgt, 0) + LEFT * 0.6, A.slot(tgt, 2) + RIGHT * 0.6, color=VIOLET,
                                stroke_width=2)
            self.play(Create(mirror), ar.animate.set_opacity(1), run_time=0.6)
            self.wait(0.8)
            olds = [A.cells[tgt][c] for c in range(3)]
            self.play(*[o.animate.stretch(0.02, 1) for o in olds], run_time=0.35, rate_func=rate_functions.ease_in_quad)
            news = []
            for c, v in enumerate(after):
                new = A._make(v, c).move_to(A.slot(tgt, c))
                A.entries.remove(olds[c])
                A.entries.add(new)
                A.cells[tgt][c] = new
                A.data[tgt][c] = v
                self.remove(olds[c])
                news.append(new)
            targets = [n.copy() for n in news]
            for n in news:
                n.stretch(0.02, 1)
            self.add(*news)
            self.play(*[Transform(n, t) for n, t in zip(news, targets)], run_time=0.45,
                      rate_func=rate_functions.ease_out_back)
            self.play(FadeOut(mirror), FadeOut(tf), run_time=0.4)
            check_relation()

        # ── the operations ─────────────────────────────────────────────────
        self.mark("op1a")
        replace_op(1, 1, 0, -2, "R₂ ← R₂ − 2R₁", "clear column 1 below the first pivot")
        self.mark("op1b")
        replace_op(1, 2, 0, -1, "R₃ ← R₃ − R₁", "clear column 1 below the first pivot")
        assert tuple(map(tuple, A.data)) == md.ROW_STAGES[0].expected
        self.play(push_history(), run_time=0.6)

        self.mark("op2")
        scale_op(2, 1, -1, "R₂ ← −R₂", "make the second leading entry a 1")
        assert tuple(map(tuple, A.data)) == md.ROW_STAGES[1].expected
        self.play(push_history(), run_time=0.6)

        self.mark("op3")
        replace_op(3, 2, 1, 1, "R₃ ← R₃ + R₂", "clear below the second pivot")
        assert tuple(map(tuple, A.data)) == md.ROW_STAGES[2].expected
        zero = Words("a whole row of zeros", 26, color=MUTED).next_to(A.row(2), RIGHT, buff=0.55)
        self.play(A.row(2).animate.set_opacity(0.35), FadeIn(zero, shift=0.2 * LEFT), run_time=0.8)
        self.wait(1.0)
        self.play(FadeOut(zero), run_time=0.4)
        self.play(push_history(), run_time=0.6)

        self.mark("op4")
        replace_op(4, 0, 1, -1, "R₁ ← R₁ − R₂", "clear above the second pivot")
        assert tuple(map(tuple, A.data)) == md.FINAL_RREF
        self.play(push_history(), run_time=0.6)
        self.wait(0.6)

        # ── RREF reveal ────────────────────────────────────────────────────
        self.play(FadeOut(panel), FadeOut(VGroup(rel, tick)), FadeOut(fil), FadeOut(heads), FadeOut(a_lbl),
                  run_time=0.8)
        self.mark("rref")
        R_final, lbl_final = rref_composition()
        self.play(A.animate.move_to(R_final), FadeOut(history), run_time=1.2)
        A.row(2).set_opacity(1)
        for r in range(3):
            for c in range(3):
                A.cells[r][c].set_color(R_final.cells[r][c].get_color())
        self.play(FadeIn(lbl_final, shift=0.2 * RIGHT), run_time=0.8)
        # echelon staircase
        dx, dy = A.dx, A.dy
        x_left = A.slot(0, 0)[0] - dx / 2
        x_c12 = A.slot(0, 1)[0] + dx / 2
        x_right = A.slot(0, 2)[0] + dx / 2
        y01 = A.slot(0, 0)[1] - dy / 2
        y12 = A.slot(1, 0)[1] - dy / 2
        stair = VMobject().set_points_as_corners([[x_left, y01, 0], [x_c12, y01, 0], [x_c12, y12, 0], [x_right, y12, 0]])
        stair.set_stroke(LIME, 3)
        stair_g = glow(stair, color=LIME, width=3)
        self.play(Create(stair_g), run_time=1.6)
        reduced = Words("Reduced Row-Echelon Form", 34, color=LIME, weight="MEDIUM").to_edge(DOWN, buff=0.9)
        self.play(FadeIn(reduced, shift=0.2 * UP), run_time=0.8)
        self.wait(2.2)
        self.play(FadeOut(stair_g), FadeOut(reduced), run_time=0.8)
        self.wait(0.3)
