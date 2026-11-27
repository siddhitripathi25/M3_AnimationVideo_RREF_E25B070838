"""AnimatedMatrix: a 3x3 matrix whose entries, rows and columns are individually animatable.

No LaTeX: entries are STIX Two glyphs on a fixed grid, brackets are drawn paths, so
every number can roll, flash, travel or morph on its own.
"""

from __future__ import annotations

import numpy as np
from manim import (
    VGroup, VMobject, RoundedRectangle, Rectangle, FadeIn, FadeOut, AnimationGroup,
    UP, DOWN, LEFT, RIGHT, ORIGIN, smooth,
)

from .palette import WHITE, VIOLET, CYAN, YELLOW, BLUE_CORE
from .typeset import Math, num
from .fx import glow

COL_COLORS = (CYAN, YELLOW, BLUE_CORE)


class AnimatedMatrix(VGroup):
    def __init__(self, data, dx=1.4, dy=1.05, size=62, col_colors=COL_COLORS,
                 bracket_color=VIOLET, **kw):
        super().__init__(**kw)
        self.data = [list(r) for r in data]
        self.dx, self.dy, self.size = dx, dy, size
        self.col_colors = list(col_colors) if col_colors else [WHITE] * 3
        self.cells = [[None] * 3 for _ in range(3)]
        self.entries = VGroup()
        for r in range(3):
            for c in range(3):
                m = self._make(self.data[r][c], c)
                m.move_to(self.slot(r, c))
                self.cells[r][c] = m
                self.entries.add(m)
        self.brackets = self._brackets(bracket_color)
        self.add(self.brackets, self.entries)
        self._bw0 = self.brackets.width

    @property
    def k(self):
        """Current scale relative to construction (slots/frames follow .scale())."""
        return self.brackets.width / self._bw0

    # geometry ---------------------------------------------------------------
    def slot(self, r, c):
        if not len(self.submobjects):
            return np.array([(c - 1) * self.dx, (1 - r) * self.dy, 0])
        k = self.k
        return self.brackets.get_center() + k * np.array([(c - 1) * self.dx, (1 - r) * self.dy, 0])

    def _make(self, v, c, color=None):
        return Math(num(v), self.size, color=color or self.col_colors[c])

    def _brackets(self, color):
        h = 3 * self.dy * 0.5 + 0.12
        w = 1.5 * self.dx + 0.12
        lip = 0.22
        left = VMobject().set_points_as_corners([[-w + lip, h, 0], [-w, h, 0], [-w, -h, 0], [-w + lip, -h, 0]])
        right = VMobject().set_points_as_corners([[w - lip, h, 0], [w, h, 0], [w, -h, 0], [w - lip, -h, 0]])
        g = VGroup(glow(left.set_stroke(width=4), color=color, width=4),
                   glow(right.set_stroke(width=4), color=color, width=4))
        return g

    # access -----------------------------------------------------------------
    def row(self, r):
        return VGroup(*self.cells[r])

    def col(self, c):
        return VGroup(*[self.cells[r][c] for r in range(3)])

    def row_frame(self, r, color=VIOLET, pad=0.18):
        rr = RoundedRectangle(corner_radius=0.12, width=3 * self.dx + 0.25, height=self.dy * 0.92,
                              stroke_color=color, stroke_width=3, fill_color=color, fill_opacity=0.10)
        return rr.scale(self.k).move_to(self.slot(r, 1))

    def col_frame(self, c, color, width_scale=0.9):
        rr = RoundedRectangle(corner_radius=0.12, width=self.dx * width_scale, height=3 * self.dy + 0.1,
                              stroke_color=color, stroke_width=3, fill_color=color, fill_opacity=0.10)
        return rr.scale(self.k).move_to(self.slot(1, c))

    # animation --------------------------------------------------------------
    def roll_to(self, r, c, v, color=None, travel=0.45):
        """Rolling-digit change of one entry. Returns an AnimationGroup."""
        old = self.cells[r][c]
        new = self._make(v, c, color).scale(self.k).move_to(self.slot(r, c))
        self.cells[r][c] = new
        self.data[r][c] = v
        self.entries.remove(old)
        self.entries.add(new)
        return AnimationGroup(FadeOut(old, shift=travel * UP), FadeIn(new, shift=travel * UP))

    def set_row(self, r, values, color=None):
        anims = []
        for c, v in enumerate(values):
            if v != self.data[r][c] or color is not None:
                anims.append(self.roll_to(r, c, v, color))
        return anims
