"""SCENE 2 — THE MEANING OF INDEPENDENCE.

One family of 81 dots, each one an actual linear combination:
    a·u                   -> a line
    a·u + b·w             -> a plane (lattice + a Lissajous path traced inside it)
    a·u + b·w + c·w3      -> w3 off the plane: the lattice lifts into 3D layers
                          -> w3 inside the plane: the layers slide, never leave the sheet
Then the formal definition.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from beyond.palette import *
from beyond.typeset import Math, Words, num
from beyond.fx import GlowVector, glow_dot, trail
from beyond.space3d import P, floor_grid, camera_angles_looking_along
from beyond.base import Base3D

U_ = np.array([1.5, 0.35, 0.0])
W_ = np.array([0.3, 1.3, 0.0])
W3_OFF = np.array([0.25, -0.2, 1.3])       # leaves the plane z = 0
W3_IN = 0.6 * U_ + 0.7 * W_                # lies in the plane: w3 = 0.6u + 0.7w

A_VALS = np.linspace(-1.6, 1.6, 9)
B_VALS = np.linspace(-1.6, 1.6, 9)
C_VALS = (-1.0, -0.5, 0.5, 1.0)


class S2Independence(Base3D):
    def construct(self):
        self.set_camera_orientation(phi=58 * DEGREES, theta=-62 * DEGREES, zoom=1.25)
        origin = glow_dot(ORIGIN, LIME, radius=0.055)
        self.add_fixed_orientation_mobjects(origin)
        grid = floor_grid(extent=5)
        grid.set_stroke(opacity=0.25)
        self.play(FadeIn(grid), run_time=1.2)

        # trackers: line spread, plane spread, layer spread
        s1, s2, s3 = ValueTracker(0), ValueTracker(0), ValueTracker(0)
        w3 = {"v": W3_OFF}

        def lattice_point(a, b, c=0.0):
            return P(s1.get_value() * a * U_ + s2.get_value() * b * W_ + s3.get_value() * c * w3["v"])

        base = VGroup()
        for a in A_VALS:
            for b in B_VALS:
                d = VGroup(Dot(radius=0.075, color=CYAN, fill_opacity=0.15), Dot(radius=0.03, color=WHITE))
                d.ab = (a, b)
                base.add(d)
        layers = VGroup()
        for c in C_VALS:
            for a in A_VALS[::2]:
                for b in B_VALS[::2]:
                    d = VGroup(Dot(radius=0.07, color=BLUE, fill_opacity=0.15), Dot(radius=0.028, color=BLUE_CORE))
                    d.abc = (a, b, c)
                    d.set_opacity(0)
                    layers.add(d)

        def place(_):
            for d in base:
                d.move_to(lattice_point(*d.ab))
            for d in layers:
                d.move_to(lattice_point(*d.abc))

        driver = Mobject()
        driver.add_updater(place)
        self.add(driver)
        place(None)
        self.add_fixed_orientation_mobjects(*base, *layers)

        # mesh lines of the lattice (base sheet)
        def mesh():
            g = VGroup()
            if s1.get_value() < 1e-3:
                return g
            for b in B_VALS:
                g.add(Line(lattice_point(A_VALS[0], b), lattice_point(A_VALS[-1], b), stroke_width=1.3,
                           color=CYAN, stroke_opacity=0.35))
            if s2.get_value() > 1e-3:
                for a in A_VALS:
                    g.add(Line(lattice_point(a, B_VALS[0]), lattice_point(a, B_VALS[-1]), stroke_width=1.3,
                               color=YELLOW, stroke_opacity=0.3))
            return g

        mesh_m = always_redraw(mesh)
        self.add(mesh_m)

        # ── 1. one vector -> a line ─────────────────────────────────────────
        self.mark("line")
        u_vec = GlowVector(P(0, 0, 0), P(U_), CYAN, width=6)
        u_lbl = self.label3d(Math("u", 40, color=CYAN), P(U_), np.array([0.25, -0.35, 0.25]))
        self.play(GrowFromPoint(u_vec, ORIGIN), FadeIn(u_lbl), run_time=1.2)
        cap = Math("a·u", 46, colors={"u": CYAN}).to_corner(UL, buff=0.75)
        cap2 = Words("every multiple of one vector:  a line", 28, color=MUTED).next_to(cap, DOWN, aligned_edge=LEFT)
        self.hud(cap, cap2)
        self.play(FadeIn(cap), FadeIn(cap2), s1.animate.set_value(1), run_time=2.6, rate_func=smooth)
        self.wait(1.2)

        # ── 2. a second, independent vector -> a plane ──────────────────────
        self.mark("plane")
        w_vec = GlowVector(P(0, 0, 0), P(W_), YELLOW, width=6)
        w_lbl = self.label3d(Math("w", 40, color=YELLOW), P(W_), np.array([-0.3, 0.2, 0.3]))
        self.play(GrowFromPoint(w_vec, ORIGIN), FadeIn(w_lbl), run_time=1.0)
        cap_b = Math("a·u + b·w", 46, colors={"u": CYAN, "w": YELLOW}).to_corner(UL, buff=0.75)
        cap2_b = Words("a new direction:  the line sweeps out a plane", 28, color=MUTED).next_to(cap_b, DOWN, aligned_edge=LEFT)
        self.hud(cap_b, cap2_b)
        self.swap(VGroup(cap, cap2), VGroup(cap_b, cap2_b))
        self.play(s2.animate.set_value(1), run_time=3.0, rate_func=smooth)
        self.wait(0.6)

        # a Lissajous path traced by a combination -- any path in the plane is reachable
        self.mark("lissajous")
        sp = ValueTracker(0)
        coef = lambda: (1.4 * np.cos(2 * sp.get_value()), 1.4 * np.sin(3 * sp.get_value()))
        pen = glow_dot(ORIGIN, WHITE, radius=0.05)
        pen.add_updater(lambda m: m.move_to(P(coef()[0] * U_ + coef()[1] * W_)))
        self.add_fixed_orientation_mobjects(pen)
        path = TracedPath(pen.get_center, stroke_color=PINK, stroke_width=4, dissipating_time=2.6)
        readout = self.live_hud(lambda: Math(
            f"a = {round(coef()[0], 2) + 0.0:+.2f}    b = {round(coef()[1], 2) + 0.0:+.2f}", 32,
            colors={"a": CYAN, "b": YELLOW}).to_corner(UR, buff=0.7))
        self.add(path)
        self.play(FadeIn(readout), run_time=0.3)
        self.play(sp.animate.set_value(2 * PI), run_time=6.0, rate_func=linear)
        self.play(FadeOut(pen), FadeOut(readout), run_time=0.5)
        self.remove(path)

        # ── 3a. third vector OFF the plane -> 3D ────────────────────────────
        self.mark("third_off")
        w3a = GlowVector(P(0, 0, 0), P(W3_OFF), BLUE, width=6, core_color=BLUE_CORE)
        w3a_lbl = self.label3d(Math("w₃", 40, color=BLUE_CORE), P(W3_OFF), np.array([0.3, 0, 0.25]))
        cap_c = Math("a·u + b·w + c·w₃", 46, colors={"u": CYAN, "w": YELLOW, "w₃": BLUE_CORE}).to_corner(UL, buff=0.75)
        cap2_c = Words("the third vector leaves the plane:  a new direction", 28, color=MUTED).next_to(cap_c, DOWN, aligned_edge=LEFT)
        self.hud(cap_c, cap2_c)
        self.swap(VGroup(cap_b, cap2_b), VGroup(cap_c, cap2_c))
        self.play(GrowFromPoint(w3a, ORIGIN), FadeIn(w3a_lbl), run_time=1.2)
        for d in layers:
            d.set_opacity(1)
            d[0].set_opacity(0.15)
        self.move_camera(phi=72 * DEGREES, theta=-40 * DEGREES, run_time=3.0,
                         added_anims=[s3.animate.set_value(1)])
        self.wait(1.2)
        # collapse the layers back
        self.play(s3.animate.set_value(0), FadeOut(w3a), FadeOut(w3a_lbl), FadeOut(cap2_c, shift=0.15 * UP), run_time=1.6)

        # ── 3b. third vector INSIDE the plane -> nothing new ────────────────
        self.mark("third_in")
        w3["v"] = W3_IN
        w3b = GlowVector(P(0, 0, 0), P(W3_IN), BLUE, width=6, core_color=BLUE_CORE)
        w3b_lbl = self.label3d(Math("w₃", 40, color=BLUE_CORE), P(W3_IN), np.array([0.3, 0.1, 0.3]))
        legs = VGroup(DashedLine(P(0, 0, 0), P(0.6 * U_), color=PINK, stroke_width=4),
                      DashedLine(P(0.6 * U_), P(W3_IN), color=PINK, stroke_width=4))
        rel = Math("w₃ = 0.6u + 0.7w", 40, colors={"w₃": BLUE_CORE, "u": CYAN, "w": YELLOW}).to_corner(UR, buff=0.6)
        cap2_d = Words("the third vector lies in the plane:  nothing new", 28, color=MUTED).next_to(cap_c, DOWN, aligned_edge=LEFT)
        self.hud(rel, cap2_d)
        self.play(GrowFromPoint(w3b, ORIGIN), FadeIn(w3b_lbl), run_time=1.0)
        self.play(Create(legs), FadeIn(rel), FadeIn(cap2_d), run_time=1.4)
        self.play(s3.animate.set_value(1), run_time=2.4, rate_func=smooth)
        # edge-on: the layers never left the sheet
        edge = camera_angles_looking_along(np.array([1.0, 0.25, 0.0]))   # exactly inside z = 0
        self.move_camera(phi=edge[0], theta=edge[1], run_time=2.6)
        self.wait(1.0)

        # ── 4. the definition ───────────────────────────────────────────────
        self.play(*[FadeOut(m) for m in (cap_c, cap2_d, rel)], run_time=0.6)
        self.play(FadeOut(VGroup(base, layers, mesh_m, u_vec, w_vec, w3b, legs, grid)),
                  FadeOut(VGroup(u_lbl, w_lbl, w3b_lbl)), FadeOut(origin), run_time=1.0)
        driver.clear_updaters()

        self.mark("definition")
        eq = Math("c₁v₁ + c₂v₂ + c₃v₃ = 0", 56, colors={"v₁": CYAN, "v₂": YELLOW, "v₃": BLUE_CORE})
        eq.move_to(UP * 1.4)
        ind = Math("only  c₁ = c₂ = c₃ = 0   ⇒   independent", 38, colors={"independent": LIME})
        dep = Math("some  cᵢ ≠ 0   ⇒   dependent", 38, colors={"dependent": PINK})
        dep_txt = Words("one vector is a combination of the others", 26, color=MUTED)
        VGroup(ind, dep, dep_txt).arrange(DOWN, buff=0.45).next_to(eq, DOWN, buff=0.8)
        dep_txt.next_to(dep, DOWN, buff=0.15)
        self.hud(eq, ind, dep, dep_txt)
        self.play(FadeIn(eq, shift=0.2 * UP), run_time=1.2)
        self.wait(1.2)
        self.play(FadeIn(ind, shift=0.2 * UP), run_time=1.0)
        self.wait(1.6)
        self.play(FadeIn(dep, shift=0.2 * UP), FadeIn(dep_txt), run_time=1.0)
        self.wait(2.6)
        self.play(FadeOut(VGroup(ind, dep, dep_txt)), eq.animate.scale(0.7).to_edge(UP, buff=0.5), run_time=1.0)
        self.wait(0.6)   # match cut: Scene 3 opens with this exact equation, then dissolves it
