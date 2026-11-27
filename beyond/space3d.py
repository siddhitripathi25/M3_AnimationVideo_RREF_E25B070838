"""3D world: coordinates, unfolding grid, component staircases, the plane y = x + z.

Mathematical coordinates (x, y, z) map to scene coordinates by a uniform scale U,
with z pointing up, so geometry on screen is the true geometry (no axis distortion).
"""

from __future__ import annotations

import numpy as np
from manim import VGroup, Line, DashedLine, Polygon, DEGREES

from .palette import GRID, AXIS, CYAN, YELLOW, BLUE, PINK
from .fx import glow

U = 1.0  # scene units per mathematical unit


def P(x, y=None, z=None) -> np.ndarray:
    if y is None:
        x, y, z = x
    return np.array([x, y, z], dtype=float) * U


# ---- camera directions -------------------------------------------------------
def camera_angles_looking_along(d) -> tuple[float, float]:
    """(phi, theta) so the camera sits on the ray +d and looks back at the origin."""
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    return float(np.arccos(d[2])), float(np.arctan2(d[1], d[0]))


NORMAL = np.array([1.0, -1.0, 1.0])            # plane y = x + z
# a direction inside the plane (d . n = 0) with a comfortable elevation:
EDGE_ON_DIR = np.array([1.0, 1.0, 0.0]) + 0.5 * np.array([1.0, 2.0, 1.0])   # v3 + v1/2
assert abs(EDGE_ON_DIR @ NORMAL) < 1e-12
EDGE_ON = camera_angles_looking_along(EDGE_ON_DIR)           # cloud collapses to a line
HERO = (68 * DEGREES, -52 * DEGREES)                         # the opening composition


# ---- grid / axes ---------------------------------------------------------------
def floor_grid(extent: int = 5, step: float = 1.0, color=GRID) -> VGroup:
    """Lines of the z = 0 plane. Each line stores its distance from origin in `.r`."""
    g = VGroup()
    vals = np.arange(-extent, extent + 1e-9, step)
    for v in vals:
        for a, b in ((P(v, -extent, 0), P(v, extent, 0)), (P(-extent, v, 0), P(extent, v, 0))):
            ln = Line(a, b, stroke_width=1.2, color=color)
            fade = max(0.12, 1 - abs(v) / (extent + 0.5))
            ln.set_stroke(opacity=0.85 * fade)
            ln.r = abs(v)
            g.add(ln)
    return g


def axes3d(length: float = 5.2, color=AXIS) -> VGroup:
    g = VGroup()
    for d in (np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])):
        g.add(Line(-P(d) * 0.35 * length, P(d) * length, stroke_width=2, color=color).set_stroke(opacity=0.8))
    return g


def staircase(v, color, width: float = 2.5, dashed: bool = True) -> VGroup:
    """Component path origin -> (x,0,0) -> (x,y,0) -> (x,y,z)."""
    x, y, z = v
    pts = [P(0, 0, 0), P(x, 0, 0), P(x, y, 0), P(x, y, z)]
    g = VGroup()
    for a, b in zip(pts, pts[1:]):
        if np.linalg.norm(b - a) < 1e-6:
            continue
        cls = DashedLine if dashed else Line
        kw = dict(dash_length=0.08) if dashed else {}
        g.add(cls(a, b, stroke_width=width, color=color, **kw))
    return g


def plane_mesh(s_range=(-2.0, 2.0), t_range=(-2.5, 2.5), n: int = 9, color=PINK,
               opacity: float = 0.5, width: float = 1.4) -> VGroup:
    """Mesh of the plane y = x + z parametrised as s*v1 + t*v3 (exact plane)."""
    v1, v3 = np.array([1, 2, 1.0]), np.array([1, 1, 0.0])
    g = VGroup()
    for s in np.linspace(*s_range, n):
        g.add(Line(P(s * v1 + t_range[0] * v3), P(s * v1 + t_range[1] * v3), stroke_width=width, color=color))
    for t in np.linspace(*t_range, n):
        g.add(Line(P(s_range[0] * v1 + t * v3), P(s_range[1] * v1 + t * v3), stroke_width=width, color=color))
    g.set_stroke(opacity=opacity)
    return g


def plane_sheet(s_range=(-2.0, 2.0), t_range=(-2.5, 2.5), color=PINK, opacity: float = 0.08) -> Polygon:
    v1, v3 = np.array([1, 2, 1.0]), np.array([1, 1, 0.0])
    corners = [P(s * v1 + t * v3) for s, t in ((s_range[0], t_range[0]), (s_range[1], t_range[0]),
                                               (s_range[1], t_range[1]), (s_range[0], t_range[1]))]
    return Polygon(*corners, stroke_width=0, fill_color=color, fill_opacity=opacity)
