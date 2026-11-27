"""SCENE 1 — THE MYSTERY.

A point in darkness -> a grid unfolds -> three vectors fire out -> 360 random linear
combinations a·v1 + b·v2 + c·v3 spray into space. We expect a 3D cloud. The camera
swings to a direction lying inside the plane y = x + z and the whole cloud collapses
to a line: the cloud has no thickness.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from beyond.palette import *
from beyond.typeset import Math, Words
from beyond.fx import GlowVector, glow_dot, trail, overshoot
from beyond.space3d import P, floor_grid, axes3d, HERO, EDGE_ON
from beyond.base import Base3D, V1, V2, V3


def cloud_data(n=360, spread=0.5, seed=11):
    """Random coefficients and their combinations. Shared with Scene 6 (same seed)."""
    rng = np.random.default_rng(seed)
    coeffs = rng.uniform(-spread, spread, (n, 3))
    pts = [a * V1 + b * V2 + c * V3 for a, b, c in coeffs]
    cols = []
    for a, b, c in np.abs(coeffs):
        w = np.array([a, b, c]) + 1e-6
        w /= w.sum()
        rgb = sum(wi * color_to_rgb(ci) for wi, ci in zip(w, (CYAN, YELLOW, BLUE)))
        cols.append(rgb_to_color(np.clip(rgb * 1.15, 0, 1)))
    return coeffs, pts, cols


def make_cloud(pts, cols, radius=0.034):
    dots = VGroup()
    for p, c in zip(pts, cols):
        d = VGroup(Dot(radius=radius * 2.8, color=c, fill_opacity=0.14),
                   Dot(radius=radius, color=c, fill_opacity=0.95))
        d.target_point = P(p)
        dots.add(d)
    return dots


class S1Mystery(Base3D):
    def construct(self):
        self.set_camera_orientation(phi=HERO[0], theta=HERO[1], zoom=1.4)

        # ── 1. darkness, one breathing point ───────────────────────────────
        origin = glow_dot(ORIGIN, LIME, radius=0.055)
        self.add_fixed_orientation_mobjects(origin)
        self.remove(origin)
        self.wait(0.8)
        self.mark("point")
        self.play(GrowFromCenter(origin), run_time=1.2, rate_func=lambda t: overshoot(t, 2.0))
        for _ in range(2):
            self.play(origin.animate.scale(1.35), rate_func=there_and_back, run_time=0.9)

        # ── 2. the grid unfolds ring by ring ───────────────────────────────
        grid = floor_grid(extent=5)
        order = sorted(grid, key=lambda m: m.r)
        axes = axes3d(4.0)
        self.move_camera(
            frame_center=P(0.45, 1.25, 0.2), run_time=3.2,
            added_anims=[LaggedStart(*[Create(m) for m in order], lag_ratio=0.06),
                         LaggedStart(*[Create(a) for a in axes], lag_ratio=0.3)],
        )

        # ── 3. three vectors fire from the origin ──────────────────────────
        self.mark("vectors")
        specs = [(V1, CYAN, None, "v₁ = (1, 2, 1)", np.array([0.9, 0.35, -0.55])),
                 (V2, YELLOW, None, "v₂ = (2, 4, 2)", np.array([-0.2, -0.5, 0.55])),
                 (V3, BLUE, BLUE_CORE, "v₃ = (1, 1, 0)", np.array([0.9, -0.2, -0.3]))]
        vectors, labels = [], []
        # v2 drawn first so the shorter v1 stays visible on top of it
        for idx in (1, 0, 2):
            v, col, core, text, off = specs[idx]
            vec, k = self.growing_vector(v, col, core_color=core, width=5.5 if idx != 1 else 4.0)
            head = glow_dot(ORIGIN, col, radius=0.06)
            head.add_updater(lambda m, v=v, k=k: m.move_to(P(v * k.get_value())))
            self.add_fixed_orientation_mobjects(head)
            tr = trail(head.get_center, col, width=7, life=0.9)
            self.add(tr, vec)
            self.play(k.animate.set_value(1.0), run_time=1.0, rate_func=rush_from)
            lbl = self.label3d(Math(text, 30, color=col), P(v), off)
            self.play(FadeOut(head, scale=2.5), FadeIn(lbl, shift=0.1 * UP), run_time=0.6)
            vec.clear_updaters()
            self.remove(tr)
            vectors.append(vec)
            labels.append(lbl)
        self.wait(0.6)

        # ── 4. 360 random combinations spray outward ───────────────────────
        self.mark("cloud")
        coeffs, pts, cols = cloud_data()
        cloud = make_cloud(pts, cols)
        rng = np.random.default_rng(3)
        delays = rng.uniform(0, 0.6, len(cloud))
        s = ValueTracker(0)

        def place(_):
            sv = s.get_value()
            for d, dl in zip(cloud, delays):
                u = np.clip((sv - dl) / 0.4, 0, 1)
                d.move_to(d.target_point * smooth(u))

        for d in cloud:
            d.move_to(ORIGIN)
        self.add_fixed_orientation_mobjects(*cloud)
        driver = Mobject()          # updaters only run on mobjects in the scene
        driver.add_updater(place)
        self.add(driver)
        recipe = Math("a·v₁ + b·v₂ + c·v₃", 40, colors={"v₁": CYAN, "v₂": YELLOW, "v₃": BLUE}).to_corner(UL, buff=0.6)
        sub = Words("360 random choices of  a, b, c", 24, color=MUTED).next_to(recipe, DOWN, aligned_edge=LEFT, buff=0.18)
        self.hud(recipe, sub)
        self.play(FadeIn(recipe, shift=0.2 * DOWN), FadeIn(sub), run_time=0.8)
        self.begin_ambient_camera_rotation(rate=0.05)
        self.play(s.animate.set_value(1.0), run_time=4.0, rate_func=linear)
        driver.clear_updaters()
        self.wait(1.5)
        self.stop_ambient_camera_rotation()

        # ── 5. the camera finds the angle where the cloud has no thickness ─
        self.play(FadeOut(VGroup(*labels)), FadeOut(sub), run_time=0.6)
        self.mark("edge_on")
        self.move_camera(phi=EDGE_ON[0], theta=EDGE_ON[1], zoom=1.45, frame_center=P(0.3, 0.5, 0.2), run_time=6.0,
                         rate_func=lambda t: smooth(t))
        self.wait(1.0)
        flat = Words("Seen from here, the cloud is perfectly flat.", 28, color=WHITE)
        flat.to_edge(UP, buff=0.9)
        self.hud(flat)
        self.play(FadeOut(recipe), run_time=0.5)
        self.play(FadeIn(flat, shift=0.2 * DOWN), run_time=0.8)
        self.wait(2.0)

        # ── 6. the question ────────────────────────────────────────────────
        self.mark("question")
        q1 = Words("Three vectors.", 44, color=WHITE, weight="SEMIBOLD")
        q2 = Words("But are there really three independent directions?", 34, color=WHITE)
        q = VGroup(q1, q2).arrange(DOWN, buff=0.28).to_edge(DOWN, buff=0.7)
        self.hud(q1, q2)
        self.play(FadeOut(flat), FadeIn(q1, shift=0.2 * UP), run_time=0.9)
        self.play(FadeIn(q2, shift=0.2 * UP), run_time=1.0)
        self.wait(3.2)

        # ── 7. everything returns to the single point (match cut) ──────────
        back = ValueTracker(1.0)
        driver.add_updater(lambda _: [d.move_to(d.target_point * back.get_value()) for d in cloud])
        self.play(
            back.animate.set_value(0.0),
            *[FadeOut(v) for v in vectors], FadeOut(grid), FadeOut(axes), FadeOut(q),
            run_time=2.2, rate_func=rate_functions.ease_in_cubic,
        )
        self.remove(cloud)
        self.play(origin.animate.scale(1.5), rate_func=there_and_back, run_time=0.8)
        self.wait(0.4)
