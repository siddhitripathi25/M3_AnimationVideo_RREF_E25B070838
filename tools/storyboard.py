"""Storyboard PDF from the actual rendered film.

One panel per logged key moment (media/marks/*.json): real frame + timestamp +
what happens on screen + the matching narration cue.

    python tools/storyboard.py          -> docs/Storyboard_BeyondThePivots.pdf
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ORDER = [("S0Title", "s0_title", "Title"), ("S1Mystery", "s1_mystery", "1 · The Mystery"), ("S2Independence", "s2_independence", "2 · The Meaning of Independence"),
         ("S3Revelation", "s3_revelation", "3 · The Big Revelation: v₂ = 2v₁"), ("S4Machine", "s4_machine", "4 · The Matrix Transformation Machine"),
         ("S5Pivots", "s5_pivots", "5 · The Pivot Discovery"), ("S6Finale", "s6_finale", "6 · The Final Revelation")]

# (scene, mark): (seconds after the mark to grab, description)
BEATS = {
    ("S0Title", "title"): (7.5, "Title card: BEYOND THE PIVOTS · SIDDHI TRIPATHI · URN E25B070838, then a fade into darkness."),
    ("S1Mystery", "point"): (1.2, "Darkness. A single lime point breathes at the origin; a 3D grid unfolds ring by ring."),
    ("S1Mystery", "vectors"): (4.0, "v₁, v₂, v₃ fire from the origin with glowing trails; coordinates appear at each tip."),
    ("S1Mystery", "cloud"): (4.5, "360 random combinations a·v₁ + b·v₂ + c·v₃ spray outward. We expect a 3D cloud."),
    ("S1Mystery", "edge_on"): (8.0, "The camera turns to a direction inside the plane y = x + z: the whole cloud collapses to a line."),
    ("S1Mystery", "question"): (3.0, "\"Three vectors. But are there really three independent directions?\""),
    ("S2Independence", "line"): (3.5, "One vector u: its multiples a·u form a line (81 dots, all real combinations)."),
    ("S2Independence", "plane"): (4.0, "A second independent vector w: the line sweeps out a plane, drawn as a lattice."),
    ("S2Independence", "lissajous"): (3.5, "A Lissajous path traced by a·u + b·w with live coefficients: any path in the plane is reachable."),
    ("S2Independence", "third_off"): (4.5, "A third vector off the plane: the lattice lifts into 3D layers, a new direction."),
    ("S2Independence", "third_in"): (8.0, "A third vector inside the plane (w₃ = 0.6u + 0.7w): edge-on, the layers never leave the sheet."),
    ("S2Independence", "definition"): (7.5, "The formal definition: only the trivial combination gives 0 → independent; otherwise dependent."),
    ("S3Revelation", "v1v2"): (3.0, "v₁ and v₂ with their x, y, z component staircases."),
    ("S3Revelation", "stretch"): (3.5, "k: 1 → 2 stretches v₁; live readout k·(1,2,1) = (k, 2k, k)."),
    ("S3Revelation", "land"): (1.5, "At k = 2 the tip lands exactly on v₂; staircases coincide leg for leg."),
    ("S3Revelation", "reveal"): (2.2, "v₂ = 2v₁ → −2v₁ + v₂ = 0; the line span{v₁} glows with flowing particles."),
    ("S3Revelation", "v3"): (14.0, "Can k·v₁ reach v₃? Live distance: minimum √½ ≈ 0.71 at k = ½, never 0."),
    ("S3Revelation", "plane"): (8.5, "v₁ and v₃ sweep the plane y = x + z; every vector satisfies it."),
    ("S4Machine", "matrix"): (3.0, "The coordinates become the columns of A; violet brackets draw in."),
    ("S4Machine", "filaments"): (4.0, "Pink filaments: col₂ = 2·col₁, re-checked after every operation."),
    ("S4Machine", "op1a"): (6.0, "R₂ ← R₂ − 2R₁: the ghost of R₁ scales by −2 and travels along particle arcs; digits roll."),
    ("S4Machine", "op1b"): (7.0, "R₃ ← R₃ − R₁; the relation still holds: (2,0,0) = 2·(1,0,0)."),
    ("S4Machine", "op2"): (3.5, "R₂ ← −R₂: each digit flips through a mirror line."),
    ("S4Machine", "op3"): (9.0, "R₃ ← R₃ + R₂: a whole row of zeros appears and dims."),
    ("S4Machine", "op4"): (8.0, "R₁ ← R₁ − R₂: the last operation; the history strip records A ~ … ~ RREF."),
    ("S4Machine", "rref"): (4.5, "RREF(A) with the echelon staircase traced in lime."),
    ("S5Pivots", "pivots"): (5.0, "Pivots ignite in columns 1 and 3; column 2 has no pivot. 2 pivots ⇒ rank A = 2."),
    ("S5Pivots", "backlink"): (12.0, "Lime beams carry pivot positions back to columns 1 and 3 of the ORIGINAL A (v₁, v₃)."),
    ("S5Pivots", "equations"): (7.0, "Rows become equations; x₂ = t is free; x = t(−2, 1, 0)."),
    ("S5Pivots", "panels"): (5.0, "One tracker t drives both panels: x(t) on the null line, and the combination that returns to 0."),
    ("S5Pivots", "final"): (4.0, "−2v₁ + v₂ = 0. A free variable → a non-zero solution → dependence."),
    ("S6Finale", "callback"): (5.0, "The Scene 1 composition returns: same camera, same 360 combinations."),
    ("S6Finale", "plane"): (6.5, "The plane y = x + z appears under the cloud; v₁ and v₃ ringed as pivots; v₂ = 2v₁."),
    ("S6Finale", "edge_on"): (8.0, "Edge-on again: 3 vectors, 2 independent directions, a plane, not all of space."),
    ("S6Finale", "sentence"): (5.5, "\"Pivots reveal independence. Free variables reveal dependence.\""),
    ("S6Finale", "credits"): (6.0, "Credits and disclosures; fade to a single point."),
}

W, H = 2480, 1754  # A4 landscape @ 300 dpi
BG, FG, MUTED, ACC = (7, 8, 23), (240, 240, 250), (138, 144, 192), (200, 255, 0)


def font(size, bold=False):
    try:
        return ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", size, index=0 if not bold else 2)
    except OSError:
        return ImageFont.load_default()


def mfont(size):
    """STIX Two Text has the subscript digits (v₁, x₂) that Avenir lacks."""
    try:
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/STIXTwoText.ttf", size)
    except OSError:
        return font(size)


MATH_ONLY = set("→⇒≈√≠∈ℝ←−·½")


def _mathf(size):
    return ImageFont.truetype("/System/Library/Fonts/Supplemental/STIXTwoMath.otf", size)


def mlen(draw, text, f):
    mf = _mathf(int(f.size))
    return sum(draw.textlength(c, font=mf if c in MATH_ONLY else f) for c in text)


def mtext(draw, xy, text, f, fill):
    """Draw text, taking symbols STIX Two Text lacks from STIX Two Math."""
    x, y = xy
    mf = _mathf(int(f.size))
    for c in text:
        ff = mf if c in MATH_ONLY else f
        draw.text((x, y), c, font=ff, fill=fill)
        x += draw.textlength(c, font=ff)


def wrap(draw, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if mlen(draw, t, f) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def video_for(mod):
    for q in ("1080p30", "480p15"):
        p = ROOT / "media" / "videos" / mod / q / f"{ORDER_MAP[mod]}.mp4"
        if p.exists():
            return p
    raise FileNotFoundError(mod)


ORDER_MAP = {mod: cls for cls, mod, _ in ORDER}


def grab(video, t, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", str(out)], check=True)
    return Image.open(out).convert("RGB")


def main():
    pages, t0 = [], 0.0
    tmp = Path(tempfile.mkdtemp())
    panels = []
    for cls, mod, title in ORDER:
        marks = json.loads((ROOT / "media" / "marks" / f"{cls}.json").read_text())
        vid = video_for(mod)
        for name, t in marks.items():
            if (cls, name) not in BEATS:
                continue
            off, desc = BEATS[(cls, name)]
            at = min(t + off, marks["_end"] - 0.2)
            img = grab(vid, at, tmp / f"{cls}_{name}.png")
            panels.append((title, t0 + at, img, desc))
        t0 += marks["_end"]

    # cover page
    cover = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(cover)
    d.text((160, 560), "BEYOND THE PIVOTS", font=font(150, True), fill=FG)
    d.text((165, 760), "Understanding linear independence through reduced row-echelon form", font=font(64), fill=MUTED)
    d.text((165, 900), f"Storyboard  ·  {len(panels)} frames from the rendered film  ·  runtime {int(t0 // 60)}:{int(t0 % 60):02d}",
           font=font(52), fill=ACC)
    d.text((165, 1000), "1920×1080 · 30 fps · Manim Community Edition · original score", font=font(46), fill=MUTED)
    pages.append(cover)

    per = 4
    for i in range(0, len(panels), per):
        page = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(page)
        for j, (title, ts, img, desc) in enumerate(panels[i:i + per]):
            col, row = j % 2, j // 2
            x, y = 100 + col * 1170, 90 + row * 830
            th = img.resize((1100, int(1100 * img.height / img.width)))
            page.paste(th, (x, y))
            d.rectangle([x, y, x + th.width, y + th.height], outline=(60, 66, 140), width=3)
            ty = y + th.height + 18
            d.text((x, ty), f"{int(ts // 60)}:{ts % 60:04.1f}", font=font(40, True), fill=ACC)
            mtext(d, (x + 190, ty + 2), title, mfont(40), MUTED)
            for k, line in enumerate(wrap(d, desc, mfont(40), 1100)[:3]):
                mtext(d, (x, ty + 56 + k * 46), line, mfont(40), FG)
        d.text((W - 420, H - 70), f"page {len(pages) + 1}", font=font(32), fill=MUTED)
        pages.append(page)

    out = ROOT / "docs" / "Storyboard_BeyondThePivots.pdf"
    pages[0].save(out, save_all=True, append_images=pages[1:], resolution=300)
    print(out, f"{len(pages)} pages")


if __name__ == "__main__":
    main()
