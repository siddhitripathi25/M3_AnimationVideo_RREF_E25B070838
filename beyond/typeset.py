"""Mathematical typography without LaTeX.

`Math("−2v₁ + v₂ = 0")` italicises single-letter variables (v, x, t, c, k, …)
automatically, keeps digits, operators and words upright, and uses STIX Two.
"""

from __future__ import annotations

import re

from manim import MarkupText, Text, VGroup, DOWN, ORIGIN

from .palette import MATH_FONT, WORD_FONT, WHITE, MUTED

_SUBS = "₀₁₂₃₄₅₆₇₈₉ᵀ"
# a lone latin letter (optionally followed by subscripts) not part of a longer word
_VAR = re.compile(rf"(?<![A-Za-z])([a-zA-Z])(?![A-Za-z])")


def _esc_italic(s: str) -> str:
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("-", "−")
    return _VAR.sub(r"<i>\1</i>", s)


def _markup(s: str, colors: dict[str, str] | None) -> str:
    """Colour keys are swapped for placeholders first (longest first), so a key
    like '0' can never match inside markup inserted for another key."""
    s = s.replace("-", "−")
    slots = []
    if colors:
        for key in sorted(colors, key=len, reverse=True):
            k = key.replace("-", "−")
            if k in s:
                slots.append((chr(0xE000 + len(slots)), k, colors[key]))
                s = s.replace(k, slots[-1][0])
    out = _esc_italic(s)
    for ph, k, col in slots:
        out = out.replace(ph, f'<span foreground="{col}">{_esc_italic(k)}</span>')
    return out


def Math(s: str, size: float = 40, color: str = WHITE, colors: dict[str, str] | None = None,
         weight: str = "NORMAL") -> MarkupText:
    """Mathematical expression. `colors` maps substrings (e.g. 'v₁') to colours."""
    m = MarkupText(_markup(s, colors), font=MATH_FONT, font_size=size, color=color, weight=weight)
    return m


def Words(s: str, size: float = 30, color: str = WHITE, weight: str = "MEDIUM") -> Text:
    return Text(s, font=WORD_FONT, font_size=size, color=color, weight=weight)


def Caption(s: str, size: float = 28, color: str = MUTED) -> Text:
    return Text(s, font=WORD_FONT, font_size=size, color=color, weight="NORMAL")


def num(x: float | int) -> str:
    """Integer-looking numbers without '.0'; true minus sign."""
    if abs(x - round(x)) < 1e-9:
        x = int(round(x))
        return f"{x}".replace("-", "−")
    return f"{x:.2f}".replace("-", "−")
