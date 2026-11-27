"""SCENE 3 — THE BIG REVELATION: v2 = 2 v1.

v1 and v2 with their component staircases. k: 1 -> 2 stretches v1 along its own
direction; components (k, 2k, k) grow with it; the tip lands exactly on v2.
Then v3: no multiple of v1 ever reaches it (distance never below sqrt(1/2)).
v1 and v3 sweep the plane y = x + z.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from beyond.palette import *
from beyond.typeset import Math, Words
from beyond.fx import GlowVector, glow_dot, trail, overshoot, dimmed
from beyond.space3d import P, floor_grid, axes3d, staircase, plane_mesh, plane_sheet
from beyond.base import Base3D, V1, V2, V3
from beyond.matrix import AnimatedMatrix
from beyond import mathdata as md


def fmt(x):
    x = round(float(x), 2) or 0.0          # no "−0.00"
    return f"{x:.2f}".replace("-", "−")


class S3Revelation(Base3D):
    def construct(self):
        self.set_camera_orientation(phi=66 * DEGREES, theta=-38 * DEGREES, zoom=1.35)
        handoff = Math("c₁v₁ + c₂v₂ + c₃v₃ = 0", 56, colors={"v₁": CYAN, "v₂": YELLOW, "v₃": BLUE_CORE})
        handoff.scale(0.7).to_edge(UP, buff=0.5)          # identical to Scene 2's final frame
        self.add_fixed_in_frame_mobjects(handoff)         # present from the very first frame
        grid, axes = floor_grid(extent=5), axes3d(4.0)
        self.play(FadeIn(grid), FadeIn(axes), FadeOut(handoff, shift=0.2 * UP), run_time=1.4)
        self.move_camera(frame_center=P(0.6, 1.4, 0.5), run_time=1.2)

        # ── 1. v1 and v2 with their components ─────────────────────────────
        self.mark("v1v2")
        v2_vec = GlowVector(P(0, 0, 0), P(V2), YELLOW, width=4.5)
        v2_st = staircase(V2, YELLOW, width=2.5)
        v2_lbl = self.label3d(Math("v₂ = (2, 4, 2)", 34, color=YELLOW), P(V2), np.array([-0.1, -0.4, 0.5]))
        self.play(GrowFromPoint(v2_vec, ORIGIN), run_time=1.0)
        self.play(Create(v2_st), FadeIn(v2_lbl), run_time=1.4)

        k = ValueTracker(1.0)
        v1_vec = always_redraw(lambda: GlowVector(P(0, 0, 0), P(V1 * k.get_value()), CYAN, width=6.5))
        v1_st = always_redraw(lambda: staircase(V1 * k.get_value(), CYAN, width=3.5, dashed=False))
        v1_lbl = self.label3d(Math("v₁ = (1, 2, 1)", 34, color=CYAN), P(V1), np.array([0.95, 0.2, -0.45]))
        self.play(GrowFromPoint(v1_vec, ORIGIN), run_time=1.0)
        self.play(Create(v1_st), FadeIn(v1_lbl), run_time=1.2)
        self.wait(0.6)

        # ── 2. stretch v1:  k·(1, 2, 1) = (k, 2k, k) ──────────────────────
        self.mark("stretch")
        formula = Math("k·v₁ = k·(1, 2, 1) = (k, 2k, k)", 40, colors={"v₁": CYAN}).to_corner(UL, buff=0.7)
        live = self.live_hud(lambda: Math(
            f"k = {fmt(k.get_value())}      ({fmt(k.get_value())}, {fmt(2 * k.get_value())}, {fmt(k.get_value())})",
            36, color=CYAN).next_to(formula, DOWN, aligned_edge=LEFT, buff=0.3))
        self.hud(formula)
        self.play(FadeIn(formula), FadeIn(live), FadeOut(v1_lbl), Transform(v2_vec, dimmed(v2_vec, 0.45)),
                  run_time=1.0)
        tip = glow_dot(ORIGIN, CYAN, radius=0.06)
        tip.add_updater(lambda m: m.move_to(P(V1 * k.get_value())))
        self.add_fixed_orientation_mobjects(tip)
        tr = trail(tip.get_center, CYAN, width=8, life=2.5)
        self.add(tr)
        self.play(k.animate.set_value(2.0), run_time=5.0, rate_func=smooth)
        self.remove(tr)
        tip.clear_updaters()
        self.remove(tip)

        # landing: flash at the tip of v2
        self.mark("land")
        ring = Circle(radius=0.1, color=PINK, stroke_width=6)
        self.label3d(ring, P(V2))
        self.play(ring.animate.scale(6).set_stroke(opacity=0),
                  Flash(P(V2), color=PINK, line_length=0.35, num_lines=14, flash_radius=0.35),
                  run_time=1.0)
        same = Words("The components match exactly:  (2, 4, 2)", 28, color=WHITE)
        same.next_to(live, DOWN, aligned_edge=LEFT, buff=0.3)
        self.hud(same)
        self.play(FadeIn(same), run_time=0.6)
        self.wait(1.4)

        # ── 3. the reveal ──────────────────────────────────────────────────
        self.mark("reveal")
        eq1 = Math("v₂ = 2v₁", 76, colors={"v₂": YELLOW, "v₁": CYAN}).to_edge(DOWN, buff=0.9)
        eq2 = Math("−2v₁ + v₂ = 0", 76, colors={"v₂": YELLOW, "v₁": CYAN}).to_edge(DOWN, buff=0.9)
        self.hud(eq1, eq2)
        self.play(FadeOut(VGroup(formula, live, same)), FadeIn(eq1, scale=1.15), run_time=1.0)
        live.clear_updaters()
        # the line span{v1}: everything v1 can reach
        beam = Line(P(-1.6 * V1), P(2.8 * V1), color=PINK, stroke_width=3)
        beam_g = VGroup(beam.copy().set_stroke(width=16, opacity=0.08), beam.copy().set_stroke(width=8, opacity=0.18), beam)
        flow = ValueTracker(0)
        runners = VGroup(*[glow_dot(ORIGIN, PINK, radius=0.035) for _ in range(14)])
        for i, d in enumerate(runners):
            d.add_updater(lambda m, i=i: m.move_to(P(V1 * (-1.6 + ((i / 14 + flow.get_value()) % 1) * 4.4))))
        self.add_fixed_orientation_mobjects(*runners)
        self.play(Create(beam_g), FadeIn(runners), flow.animate.set_value(0.3), run_time=1.6, rate_func=linear)
        line_lbl = Words("both live on one line through the origin", 28, color=PINK).to_corner(UL, buff=0.7)
        self.hud(line_lbl)
        self.play(FadeIn(line_lbl), flow.animate.set_value(0.6), run_time=1.4, rate_func=linear)
        self.play(FadeOut(eq1, shift=0.3 * UP), flow.animate.set_value(0.75), run_time=0.8, rate_func=linear)
        self.play(FadeIn(eq2, shift=0.3 * UP), flow.animate.set_value(0.9), run_time=0.8, rate_func=linear)
        self.play(flow.animate.set_value(1.3), run_time=1.8, rate_func=linear)
        self.play(FadeOut(runners), FadeOut(beam_g), FadeOut(line_lbl), FadeOut(v1_st), FadeOut(v2_st),
                  FadeOut(v2_lbl), eq2.animate.scale(0.55).to_corner(DR, buff=0.6), run_time=1.0)

        # ── 4. v3: no multiple of v1 reaches it ────────────────────────────
        self.mark("v3")
        k.set_value(1.0)
        v3_vec = GlowVector(P(0, 0, 0), P(V3), BLUE, width=6.5, core_color=BLUE_CORE)
        v3_st = staircase(V3, BLUE_CORE, width=3)
        v3_lbl = self.label3d(Math("v₃ = (1, 1, 0)", 34, color=BLUE_CORE), P(V3), np.array([0.9, -0.3, -0.25]))
        self.move_camera(phi=62 * DEGREES, theta=-62 * DEGREES, frame_center=P(0.6, 1.0, 0.3), run_time=1.4,
                         added_anims=[GrowFromPoint(v3_vec, ORIGIN)])
        self.play(Create(v3_st), FadeIn(v3_lbl), run_time=1.0)

        gap = always_redraw(lambda: DashedLine(P(V1 * k.get_value()), P(V3), color=PINK, stroke_width=4,
                                               dash_length=0.08))
        q = Math("Can  k·v₁  ever equal  v₃ ?", 40, colors={"v₁": CYAN, "v₃": BLUE_CORE}).to_corner(DL, buff=0.7).shift(1.75 * UP)
        dist = lambda: float(np.linalg.norm(V3 - k.get_value() * V1))
        dlive = self.live_hud(lambda: Math(f"k = {fmt(k.get_value())}      distance = {fmt(dist())}", 34,
                                          colors={"distance": PINK}).next_to(q, DOWN, aligned_edge=LEFT, buff=0.3))
        self.hud(q)
        self.play(FadeOut(eq2), FadeOut(v3_lbl), run_time=0.5)
        self.play(FadeIn(q), FadeIn(dlive), Create(gap), run_time=1.0)
        self.play(k.animate.set_value(-0.4), run_time=2.0, rate_func=smooth)
        self.play(k.animate.set_value(1.6), run_time=3.0, rate_func=smooth)
        self.play(k.animate.set_value(0.5), run_time=2.0, rate_func=smooth)
        never = Math("closest at k = ½ :  distance √½ ≈ 0.71 — never 0", 32, colors={"0.71": PINK})
        never.next_to(dlive, DOWN, aligned_edge=LEFT, buff=0.3)
        why = Math("v₁ has z = 1 but v₃ has z = 0 :  no k fits all three components", 30,
                   colors={"v₁": CYAN, "v₃": BLUE_CORE}, color=MUTED)
        why.next_to(never, DOWN, aligned_edge=LEFT, buff=0.25)
        self.hud(never, why)
        self.play(FadeIn(never), run_time=0.8)
        self.play(FadeIn(why), run_time=0.8)
        self.wait(2.0)
        dlive.clear_updaters()
        self.play(FadeOut(VGroup(q, dlive, never, why)), FadeOut(gap), FadeOut(v3_st), run_time=0.8)

        # ── 5. v1 and v3 sweep a plane:  y = x + z ─────────────────────────
        k.set_value(1.0)
        self.mark("plane")
        sweep = ValueTracker(0.01)
        mesh = always_redraw(lambda: plane_mesh((-1.2 * sweep.get_value(), 2.2 * sweep.get_value()),
                                                (-1.6 * sweep.get_value(), 2.2 * sweep.get_value()),
                                                n=9, color=LIME, opacity=0.45, width=1.6))
        sheet = always_redraw(lambda: plane_sheet((-1.2 * sweep.get_value(), 2.2 * sweep.get_value()),
                                                  (-1.6 * sweep.get_value(), 2.2 * sweep.get_value()),
                                                  color=LIME, opacity=0.07))
        self.add(sheet, mesh)
        plane_eq = Math("s·v₁ + t·v₃  fill the plane   y = x + z", 40,
                        colors={"v₁": CYAN, "v₃": BLUE_CORE, "y = x + z": LIME}).to_corner(UL, buff=0.7)
        self.hud(plane_eq)
        self.play(sweep.animate.set_value(1.0), FadeIn(plane_eq), run_time=3.0, rate_func=smooth)
        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(4.0)
        self.stop_ambient_camera_rotation()
        check = Math("v₁: 2 = 1 + 1     v₂: 4 = 2 + 2     v₃: 1 = 1 + 0", 32, color=WHITE,
                     colors={"v₁": CYAN, "v₂": YELLOW, "v₃": BLUE_CORE}).next_to(plane_eq, DOWN, aligned_edge=LEFT, buff=0.3)
        self.hud(check)
        self.play(FadeIn(check), run_time=0.8)
        self.wait(2.2)

        # ── 6. hand-off: the coordinates become the columns of A ───────────
        self.mark("handoff")
        A = AnimatedMatrix(md.A0)        # identical layout to the opening of Scene 4
        cols = VGroup(*[A.col(c) for c in range(3)])
        self.hud(cols)
        self.play(FadeOut(VGroup(plane_eq, check)), run_time=0.6)
        self.play(*[FadeOut(m) for m in (mesh, sheet, grid, axes, v1_vec, v2_vec, v3_vec)],
                  LaggedStart(*[FadeIn(c, shift=0.4 * DOWN) for c in cols], lag_ratio=0.3), run_time=2.0)
        self.wait(0.5)
