"""Light, trails and motion helpers. Glow is faked with layered strokes (no shaders)."""

from __future__ import annotations

import numpy as np
from manim import (
    VGroup, VMobject, Dot, Line, Circle, TracedPath, Cone, Arc,
    ORIGIN, OUT, WHITE, interpolate_color, ManimColor,
)

from .palette import WHITE as PWHITE


# ---------------------------------------------------------------- easing
def overshoot(t: float, s: float = 1.6) -> float:
    """Ease-out-back: lands slightly past 1 and settles. For 'lock-in' moments."""
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def ease_in_out_cubic(t: float) -> float:
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


# ---------------------------------------------------------------- glow
GLOW_LAYERS = ((7.0, 0.07), (3.6, 0.16), (2.0, 0.34))


def glow(m: VMobject, color=None, width: float | None = None, layers=GLOW_LAYERS) -> VGroup:
    """Return VGroup(halo layers..., crisp core). Core is `m` itself."""
    color = color or m.get_stroke_color()
    w = width if width is not None else max(m.get_stroke_width(), 2)
    halos = VGroup()
    for k, op in layers:
        h = m.copy().set_fill(opacity=0).set_stroke(color=color, width=w * k, opacity=op)
        halos.add(h)
    m.set_stroke(color=color, width=w)
    g = VGroup(*halos, m)
    g.core = m
    return g


def glow_dot(point, color, radius: float = 0.05, intensity: float = 1.0) -> VGroup:
    halo2 = Dot(point, radius=radius * 4.0, color=color, fill_opacity=0.07 * intensity)
    halo1 = Dot(point, radius=radius * 2.2, color=color, fill_opacity=0.20 * intensity)
    core = Dot(point, radius=radius, color=interpolate_color(ManimColor(color), ManimColor(PWHITE), 0.35),
               fill_opacity=1.0)
    g = VGroup(halo2, halo1, core)
    return g


# ---------------------------------------------------------------- vectors
class GlowVector(VGroup):
    """A luminous 3D (or 2D) vector: layered shaft + cone head.

    Works in ThreeDScene; for flat scenes pass flat=True to use a triangle tip.
    """

    def __init__(self, start, end, color, width: float = 4.0, head: float = 0.16,
                 core_color=None, flat: bool = False, **kw):
        super().__init__(**kw)
        start, end = np.array(start, float), np.array(end, float)
        d = end - start
        L = np.linalg.norm(d)
        u = d / L if L > 1e-9 else OUT
        hl = min(head * 1.6, 0.45 * L) if L > 1e-9 else 0
        shaft_end = end - u * hl * 0.9
        core = Line(start, shaft_end if L > 1e-9 else end + 1e-4 * OUT, stroke_width=width,
                    color=core_color or color)
        self.shaft = glow(core, color=color, width=width)
        if core_color is not None:
            self.shaft.core.set_stroke(color=core_color)
        self.add(self.shaft)
        if L > 1e-9:
            if flat:
                from manim import Triangle
                tip = Triangle(fill_color=color, fill_opacity=1, stroke_width=0).scale(head)
                tip.rotate(np.arctan2(u[1], u[0]) - np.pi / 2).move_to(end - u * hl * 0.45)
            else:
                tip = Cone(base_radius=head * 0.62, height=hl, direction=u, resolution=(2, 12),
                           fill_color=color, fill_opacity=1.0, stroke_width=0,
                           checkerboard_colors=False, show_base=True)
                tip.shift(end - tip.get_end() if hasattr(tip, "get_end") else 0)
                tip.move_to(end - u * hl / 2)
            self.tip = tip
            self.add(tip)


# ---------------------------------------------------------------- trails
def trail(func, color, width: float = 3.0, life: float = 1.4) -> TracedPath:
    return TracedPath(func, stroke_color=color, stroke_width=width, dissipating_time=life,
                      stroke_opacity=[0, 1])


# ---------------------------------------------------------------- dots
def dot_cloud(points, color, radius: float = 0.022, halo: bool = True, opacity: float = 1.0) -> VGroup:
    g = VGroup()
    for p in points:
        if halo:
            g.add(VGroup(Dot(p, radius=radius * 2.6, color=color, fill_opacity=0.16 * opacity),
                         Dot(p, radius=radius, color=color, fill_opacity=opacity)))
        else:
            g.add(Dot(p, radius=radius, color=color, fill_opacity=opacity))
    return g


def pulse_ring(center, color, r0: float = 0.1, r1: float = 0.6, width: float = 4.0) -> Circle:
    return Circle(radius=r0, color=color, stroke_width=width).move_to(center)


def dimmed(m, factor: float):
    """Copy of `m` with every layer's opacity scaled by `factor`.

    set_opacity() would flatten layered glow into one opaque tube; this keeps
    the halo/core proportions.
    """
    c = m.copy()
    for sm in c.family_members_with_points():
        so = sm.get_stroke_opacity() if hasattr(sm, "get_stroke_opacity") else 1
        fo = sm.get_fill_opacity() if hasattr(sm, "get_fill_opacity") else 1
        sm.set_stroke(opacity=so * factor)
        sm.set_fill(opacity=fo * factor)
    return c
