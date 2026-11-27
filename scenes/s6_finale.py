"""SCENE 6 — THE FINAL REVELATION (+ credits).

Exact callback to Scene 1 (same camera, same 360 combinations, same seed), now explained:
the plane y = x + z appears under the cloud, v1 and v3 are marked as pivots, v2 sits on
v1's line. The camera repeats the edge-on move: 3 vectors, 2 independent directions.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from beyond.palette import *
from beyond.typeset import Math, Words
from beyond.fx import GlowVector, glow_dot, overshoot, glow
from beyond.space3d import P, floor_grid, axes3d, plane_mesh, plane_sheet, HERO, EDGE_ON
from beyond.base import Base3D, V1, V2, V3
from beyond.matrix import AnimatedMatrix
from beyond import mathdata as md
from s1_mystery import cloud_data, make_cloud

# ── edit these for your submission ─────────────────────────────────────────
CREDITS = {
    "creator": "SIDDHI TRIPATHI",
    "course": "M3",
}


class S6Finale(Base3D):
    def construct(self):
        self.set_camera_orientation(phi=HERO[0], theta=HERO[1], zoom=1.4)
        origin = glow_dot(ORIGIN, LIME, radius=0.055)
        self.add_fixed_orientation_mobjects(origin)
        self.wait(0.2)                                   # match cut from Scene 5's final point
        self.play(origin.animate.scale(1.35), rate_func=there_and_back, run_time=0.8)

        # ── 1. the opening composition, rebuilt quickly ────────────────────
        self.mark("callback")
        grid, axes = floor_grid(extent=5), axes3d(4.0)
        vecs = VGroup(GlowVector(P(0, 0, 0), P(V2), YELLOW, width=4.0),
                      GlowVector(P(0, 0, 0), P(V1), CYAN, width=5.5),
                      GlowVector(P(0, 0, 0), P(V3), BLUE, width=5.5, core_color=BLUE_CORE))
        _, pts, cols = cloud_data()
        cloud = make_cloud(pts, cols)
        for d in cloud:
            d.move_to(d.target_point)
        self.move_camera(frame_center=P(0.45, 1.25, 0.2), run_time=2.0,
                         added_anims=[FadeIn(grid), FadeIn(axes),
                                      LaggedStart(*[GrowFromPoint(v, ORIGIN) for v in vecs], lag_ratio=0.25)])
        self.add_fixed_orientation_mobjects(*cloud)
        self.remove(*cloud)
        self.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in cloud], lag_ratio=0.004), run_time=2.0)
        back = Words("Back to the beginning.  Now we can explain it.", 30, color=WHITE).to_edge(UP, buff=0.7)
        self.hud(back)
        self.play(FadeIn(back, shift=0.2 * DOWN), run_time=0.8)
        self.wait(1.0)

        # ── 2. the explanation appears in the space itself ─────────────────
        self.mark("plane")
        sheet = plane_sheet((-1.6, 2.4), (-2.2, 2.2), color=LIME, opacity=0.07)
        mesh = plane_mesh((-1.6, 2.4), (-2.2, 2.2), n=11, color=LIME, opacity=0.4, width=1.5)
        self.play(FadeOut(back), FadeIn(sheet), Create(mesh, lag_ratio=0.05), run_time=2.2)
        plane_lbl = Math("every combination lies in the plane  y = x + z", 34, colors={"y = x + z": LIME})
        plane_lbl.to_corner(DR, buff=0.7)
        self.hud(plane_lbl)
        self.play(FadeIn(plane_lbl), run_time=0.8)
        self.wait(1.2)

        tags = VGroup(
            self.label3d(Math("v₁  pivot", 32, colors={"v₁": CYAN, "pivot": LIME}), P(V1), np.array([0.95, 0.3, -0.5])),
            self.label3d(Math("v₂ = 2v₁", 32, colors={"v₂": YELLOW, "v₁": CYAN}, color=PINK), P(V2), np.array([-0.1, -0.5, 0.55])),
            self.label3d(Math("v₃  pivot", 32, colors={"v₃": BLUE_CORE, "pivot": LIME}), P(V3), np.array([0.95, -0.25, -0.35])),
        )
        rings = VGroup()
        for v in (V1, V3):
            ring = glow(Circle(radius=0.16, stroke_width=4, color=LIME), color=LIME, width=4)
            rings.add(self.label3d(ring, P(v)))
        self.play(LaggedStart(*[FadeIn(t, shift=0.1 * UP) for t in tags], lag_ratio=0.4),
                  LaggedStart(*[GrowFromCenter(r) for r in rings], lag_ratio=0.5), run_time=2.0)
        self.wait(1.6)

        # ── 3. the same camera move as Scene 1 ─────────────────────────────
        self.play(FadeOut(plane_lbl), FadeOut(tags), FadeOut(rings), run_time=0.6)
        self.mark("edge_on")
        self.move_camera(phi=EDGE_ON[0], theta=EDGE_ON[1], zoom=1.45, frame_center=P(0.3, 0.5, 0.2),
                         run_time=5.0)
        verdict = VGroup(
            Math("3 vectors", 44, color=WHITE),
            Math("2 independent directions", 44, colors={"2": LIME}),
            Words("a plane, not all of space", 30, color=MUTED),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT).to_corner(UL, buff=0.8)
        self.hud(verdict)
        self.play(LaggedStart(*[FadeIn(v, shift=0.2 * UP) for v in verdict], lag_ratio=0.5), run_time=2.0)
        self.wait(2.4)

        # ── 4. RREF + the sentence ─────────────────────────────────────────
        self.play(FadeOut(VGroup(cloud, vecs, grid, axes, mesh, sheet)), FadeOut(verdict), run_time=1.4)
        R = AnimatedMatrix(md.FINAL_RREF).scale(0.62).move_to(UP * 1.7)
        for r, c in ((0, 0), (1, 2)):
            R.cells[r][c].set_color(LIME)
        R.col(1).set_color(ORANGE)
        piv = VGroup(*[glow(Circle(radius=0.27, stroke_width=4, color=LIME).move_to(R.cells[r][c]), color=LIME, width=4)
                       for r, c in ((0, 0), (1, 2))])
        self.mark("sentence")
        line1 = Words("Pivots reveal independence.", 50, color=WHITE, weight="MEDIUM")
        line2 = Words("Free variables reveal dependence.", 50, color=WHITE, weight="MEDIUM")
        line1[0:6].set_color(LIME)
        line1[-13:-1].set_color(LIME)
        line2[0:13].set_color(ORANGE)
        line2[-11:-1].set_color(PINK)
        lines = VGroup(line1, line2).arrange(DOWN, buff=0.38).move_to(DOWN * 1.35)
        self.hud(R, piv, line1, line2)
        self.play(FadeIn(R, scale=0.9), FadeOut(origin), run_time=1.0)
        self.play(LaggedStart(*[Create(p) for p in piv], lag_ratio=0.4), run_time=1.0)
        self.play(FadeIn(line1, shift=0.25 * UP), run_time=1.2)
        self.wait(0.8)
        self.play(FadeIn(line2, shift=0.25 * UP), run_time=1.2)
        self.wait(3.5)

        # ── 5. credits ─────────────────────────────────────────────────────
        self.mark("credits")
        title = Words("BEYOND THE PIVOTS", 54, color=WHITE, weight="BOLD")
        sub = Words("Linear independence through reduced row-echelon form", 28, color=MUTED)
        who = Words(f"{CREDITS['creator']}   ·   {CREDITS['course']}", 30, color=WHITE)
        rows = VGroup(*[
            VGroup(Words(k, 22, color=VIOLET, weight="BOLD"), Words(v, 24, color=WHITE)).arrange(RIGHT, buff=0.4)
            for k, v in (
                ("ANIMATION", "Manim Community Edition, original Python code"),
                ("MUSIC", "\u201cPivot Light\u201d, original score generated in code for this film (no third-party material)"),
                ("NARRATION", "Recorded by the creator"),
                ("AI DISCLOSURE", "Code developed with assistance from Claude Code (Anthropic)"),
                ("VERIFICATION", "Every number on screen checked by exact-arithmetic tests"),
            )])
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        credits = VGroup(title, sub, who, rows).arrange(DOWN, buff=0.38)
        who.shift(DOWN * 0.05)
        rows.shift(DOWN * 0.25)
        self.hud(credits)
        self.play(LaggedStart(FadeOut(VGroup(R, piv, line1, line2)),
                              AnimationGroup(FadeIn(title, shift=0.2 * UP), FadeIn(sub)), lag_ratio=0.9), run_time=2.0)
        self.play(FadeIn(who), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.25), run_time=1.6)
        self.wait(4.5)
        end = glow_dot(ORIGIN, LIME, radius=0.055)
        self.hud(end)
        self.play(FadeOut(credits), run_time=1.2)
        self.play(GrowFromCenter(end), run_time=0.6)
        self.play(end.animate.scale(0.01).set_opacity(0), run_time=1.2)
        self.wait(1.0)
