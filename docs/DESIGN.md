# BEYOND THE PIVOTS — Audit & Visual Redesign

*Phase A (audit) + Phase B (design). No source files have been modified.*

---

## PHASE A — AUDIT

### A1. Where things actually are

| Location | What it is | State |
|---|---|---|
| `~/Desktop/maths` | Stated working directory | **Empty** (only this `docs/` folder now) |
| `~/Desktop/maths_animation_video` | The existing film project | 6 scenes, helpers, renders, narration, credits, `.venv` (Manim CE 0.22.1, Py 3.12) |
| `~/Desktop/maths2` | An abandoned restart | Only `src/math_data.py` (exact `Fraction` maths), `tests/test_math.py`, `src/timings.py`, `manim.cfg` (already uses `#070817`). No scenes. |

Reference video: **not used, not searched for** (per your instruction).
Note: `maths_animation_video/scratch/ref_frames/` holds 15 thumbnails that look like frames
extracted from it. I did not open them and will not use them.

### A2. Environment

- Apple M4, 10 cores, 16 GB, 175 GB free — fine for 1080p30 Cairo renders.
- Manim CE **0.22.1** in `maths_animation_video/.venv` (Python 3.12). System Python is 3.15 (Manim does not support it).
- FFmpeg ✓. Pillow ✓ (can write the storyboard PDF; no new dependency needed).
- **LaTeX is NOT installed** → `MathTex` / `Tex` / `Matrix` (LaTeX-based) cannot render.
  Plan: no LaTeX. Typography is built from `Text` using **STIX Two Math / STIX Two Text**
  (real mathematical glyphs: italic variables, ∈, ℝ, subscripts) and **Avenir Next** for titles.
  Matrices are built by a custom helper (grid of entry mobjects + drawn brackets), which is
  also what makes per-entry animation possible.

### A3. Mathematics — verified numerically and with exact arithmetic

All of your stated mathematics is correct:
- Row ops 1→4 reproduce exactly the four intermediate matrices; final RREF `[[1,2,0],[0,0,1],[0,0,0]]`.
- rank A = 2; A·(−2,1,0)ᵀ = 0; every column satisfies x − y + z = 0.

Errors / weaknesses found in the **existing code**:

1. **Wrong notation during row reduction** (`scene4_worked_example.py`): the label stays
   `A =` while the entries change. After a row operation the matrix is *row-equivalent* to A,
   not equal to it. Fix: `A ~ …` / `A → …` chain, ending with `RREF(A) =` (or `R =`).
2. **The film never explains WHY pivot columns of RREF point back to the original vectors.**
   It asserts it. The key fact — *row operations change the columns but preserve every linear
   relation between them* (col₂ = 2·col₁ holds in every intermediate matrix) — is missing.
   This is the conceptual heart of your "IMPORTANT" note, and it becomes a visual centrepiece below.
3. Scene 1 reveals `v₂ = 2v₁` in the first 20 s, which kills the mystery and duplicates Scene 3.
4. Scene 6 colours v₁ and v₃ the same green, which erases their identities just when the viewer needs them.

Visual / technical defects seen in the actual render (2:22, 1080p30):

- Captions swapped with `ReplacementTransform` produce **garbled overlapping text** mid-transition
  (visible in Scene 1 and the Scene 4 step-2 panel).
- Matrix brackets are `Text("[")` glyphs that cover only the middle row, so rows 1 and 3 sit outside the brackets.
- Default serif fallback font; 13–15 pt text is unreadable at 1080p.
- Scene 3's camera orbit ends almost edge-on, so the vectors collapse into a smudge.
- Old palette (pure black, emerald, amber) ≠ new palette.
- Length 2:22, against a target of ~5:00.
- Mostly cards plus FadeIn; no point clouds, trails, or entry-level arithmetic motion.

Reusable pieces: `maths2/src/math_data.py` + tests (exact `Fraction` row-reduction engine),
`main.py` concat/mux logic, the procedural-audio idea, and the existing narration (as raw material).

`CREDITS.md` discloses only "Google Antigravity (Gemini)". If I build this, the disclosure must
also name **Claude Code (Anthropic)**. I will draft it and you can edit it.

---

## PHASE B — VISUAL REDESIGN

### B1. Visual language

**Palette** (exact hex from your brief), each colour with one job:

| Role | Colour |
|---|---|
| background | `#070817` + very faint radial vignette |
| v₁ / originals | Electric Cyan `#00E5FF` |
| v₂ / comparison | Brilliant Yellow `#FFE45E` |
| v₃ | Laser Blue `#247BFF`, with a pale-cyan core stroke so it stays luminous on midnight |
| dependence / relations | Hot Pink `#FF38B8` |
| matrix transformations | Neon Violet `#9D4EDD` |
| pivots / discoveries | Acid Lime `#C8FF00` |
| free variable / solution path | Electric Orange `#FF7A18` |
| equations | White |

Rule: at most three accent colours on screen at once, plus white.

**Glow**, without shaders: every "luminous" object is drawn three times: a wide stroke at about 8%
opacity, a medium stroke at about 25%, and a crisp core. One helper, `glow(mobj)`.

**Trails**: `TracedPath` with `dissipating_time` on moving tips, so motion leaves fading light.

**Type**: STIX Two (maths), Avenir Next (words). Minimum 28 px equivalent at 1080p. No title cards.
Words appear only when they carry mathematics.

**Motion**: custom easing (`smooth`, `rush_from`, plus an overshoot-and-settle for "lock-in" moments).
Each scene ends on a match-cut object that starts the next scene.

### B2. Scene-by-scene (target ≈ 5:05)

---

#### SCENE 1 — THE MYSTERY (≈ 40 s)

1. **Black.** One lime-white point breathes at the origin.
2. A 3D grid unfolds outward from the point, ring by ring (lines grow from the centre, opacity
   falling with distance), and the axes draw themselves.
3. **v₁, v₂, v₃ fire out** from the origin one after another, each tip leaving a glowing trail
   (cyan, yellow, blue). Coordinates tick up beside each tip, e.g. `(1, 2, 1)`.
4. **The mystery experiment (main visual):** about 400 dots spray from the origin. Each dot is a
   random combination `a·v₁ + b·v₂ + c·v₃` with a, b, c ∈ [−1, 1], so each one is a genuinely
   reachable point. We expect a 3D cloud.
5. The camera orbits slowly. At one angle (looking along the normal (1, −1, 1)) the whole cloud
   **collapses into a razor-thin line**. The cloud is flat. Three vectors, but the cloud has no thickness.
6. Question, in two lines:
   *Three vectors.*
   *But are there really three independent directions?*

Match cut: the cloud fades to the single origin point.

---

#### SCENE 2 — THE MEANING OF INDEPENDENCE (≈ 50 s)

A generic pair u, w (not our vectors) teaches the idea before any definition.

1. **One vector → a line.** Dots stream along the line `c·u` as c sweeps from −3 to 3 (ValueTracker).
   The set of everything u can reach glows as a line.
2. **A second, independent vector → a plane.** Each dot on the line splits into its own copy
   moving along w, and the line sweeps into a 2D lattice `c₁u + c₂w`, drawn as a deforming mesh.
   A small parametric curve (a Lissajous path `c₁ = cos 2s, c₂ = sin 3s`) is traced by
   `c₁u + c₂w` to show that any path in the plane is reachable.
3. **Third vector, two cases (split screen, same camera):**
   - left: w₃ off the plane. The lattice **lifts into 3D**: a new direction.
   - right: w₃ inside the plane. Dots slide but **never leave the sheet**: nothing new.
     Pink filaments show w₃ written as a combination of u and w.
4. The formal definition is assembled in STIX:
   `c₁v₁ + c₂v₂ + c₃v₃ = 0  ⇒  c₁ = c₂ = c₃ = 0` (independent).
   A non-zero solution means some vector is redundant.

Match cut: the right-hand "redundant" case dissolves, and our real v₁ appears.

---

#### SCENE 3 — THE BIG REVELATION: v₂ = 2v₁ (≈ 45 s)

1. v₁ (cyan) and v₂ (yellow) share the origin. Each has a **component staircase**: three dashed
   legs along x, then y, then z, from the origin to its tip, so (1, 2, 1) and (2, 4, 2) are
   physically visible.
2. **Scaling (main visual):** `k: 1 → 2` (ValueTracker, slow).
   - v₁'s arrow grows; its staircase legs grow with it: (k, 2k, k).
   - A live readout reads `k · (1, 2, 1) = (k, 2k, k)` with digits rolling.
   - The tip leaves a cyan trail along the line through the origin.
   - At k = 2 the tip lands **exactly** on v₂'s tip, and the two staircases coincide leg for leg.
     Pink flash, the colours merge, and the arrows overlap.
3. The infinite line `span{v₁}` lights up as a beam, and v₂ is shown sitting on it.
   `v₂ = 2v₁` writes itself, then morphs into `−2v₁ + v₂ = 0`.
4. **v₃ is different:** sweep k across [−1, 3]. A pink segment always connects the moving tip
   `k·v₁` to v₃'s tip, and its length never reaches 0. A live distance readout dips to its minimum
   (√(1/2) ≈ 0.71, at k = ½) and rises again. v₃'s staircase (1, 1, 0) has z = 0 where v₁ has z = 1,
   so no multiple fits.
5. v₁ and v₃ sweep a parallelogram that extends into the plane **y = x + z**, drawn as a glowing mesh.

Match cut: the three tip coordinates fly off and become the columns of A.

---

#### SCENE 4 — THE MATRIX TRANSFORMATION MACHINE (≈ 80 s, central)

**Entry:** the coordinates from Scene 3 fly into place as **columns**, each column coloured as its
vector (cyan, yellow, blue). The brackets draw in violet. `A =` is shown.

**Invariant filaments (the key new idea):** thin pink lines connect each entry of column 1 to the
matching entry of column 2, with the label `col₂ = 2·col₁`. These filaments **persist through every
step**. After each operation, a check pulse runs along them (`0 = 2·0 ✓`). This shows visually that
row operations change the columns but never the relations between them.

**Each operation follows the same choreography (helper `RowOp`):**
1. Op text slides in at the right in violet, e.g. `R₂ ← R₂ − 2R₁`.
2. Source row lights violet; target row gets a violet frame.
3. A **ghost copy** of the source row lifts off, scales visibly (`×2`: entries roll 1, 2, 1 → 2, 4, 2),
   and glides onto the target row.
4. Column by column, a mini equation appears over each entry (e.g. `2 − 2`), the digits collide,
   and the result morphs in place (`→ 0`). Small dots flow along a connecting arc from each source
   entry to its target entry while this happens.
5. The new matrix settles. The left-hand label becomes `~`, and the previous matrix shrinks into a
   **history strip** at the top: A ~ M₁ ~ M₂ ~ M₃ ~ RREF.

Steps, all shown, none skipped:
- Step 1: `R₂ ← R₂ − 2R₁` then `R₃ ← R₃ − R₁` (two passes, sequential)
- Step 2: `R₂ ← −R₂` (sign flip shown as each digit flipping through a vertical mirror)
- Step 3: `R₃ ← R₃ + R₂` → zero row; row 3 dims and falls slightly back in z ("no information")
- Step 4: `R₁ ← R₁ − R₂` → RREF

**RREF reveal:** the history strip collapses into the final matrix, a staircase line traces the
echelon steps, and the label changes to `RREF(A) =`.

---

#### SCENE 5 — THE PIVOT DISCOVERY (≈ 55 s)

1. RREF centred and large. **Pivot 1** ignites lime (a halo ring, and its column fills with light).
   Then **pivot 3**. Column 2 stays orange: no pivot, so it is **free**.
2. **Back-link:** the original A fades in above as a ghost. Lime beams rise from pivot columns
   1 and 3 of the RREF to columns 1 and 3 **of A**, then to small v₁ and v₃ arrows.
   Caption: *pivot positions in RREF choose columns of the original A*.
   A counter ticks: `pivots: 2 → rank A = 2`.
3. RREF read as equations: `x₁ + 2x₂ = 0`, `x₃ = 0`. Then `x₂ = t` (orange),
   which gives **x = t(−2, 1, 0)**.
4. **Two linked panels (main visual), both driven by one ValueTracker `t`:**
   - Left, *solution space*: 3D axes with the null line through (−2, 1, 0) in orange.
     The vector x(t) slides along it; dots flow along the line.
   - Right, *vector space*: the combination `(−2t)·v₁ + t·v₂ + 0·v₃` drawn **tip to tail**.
     For every t the chain **closes back to the origin**: a pink closed loop that stretches and
     shrinks but never opens.
   - Live readouts in both panels; at t = 1, freeze: **−2v₁ + v₂ = 0**.
   Lesson: *a free variable means a non-zero solution, which means a closed loop, which means dependence.*

---

#### SCENE 6 — THE FINAL REVELATION (≈ 35 s, credits included)

1. **Exact callback to Scene 1:** same camera angle, same 400-dot cloud, same vectors.
2. Now it is explained: the plane y = x + z materialises under the cloud. v₁ and v₃ become lime-ringed
   (pivots). v₂ lies on v₁'s line, connected by a pink filament reading `2v₁`.
3. The camera repeats the Scene 1 orbit to the edge-on view. The cloud collapses to a line again,
   but this time the label reads *2 independent directions*.
4. The final RREF floats in a corner with both pivots lit.
5. Final line, centred, alone:
   **Pivots reveal independence.**
   **Free variables reveal dependence.**
6. Credits: you, course, tools, music (original), AI disclosure. Fade to the single point, then black.

### B3. The most ambitious sequences

1. **S1/S6 collapsing cloud.** About 400 real linear combinations in 3D under an orbiting camera.
2. **S4 invariant filaments + row-op choreography.** Ghost rows, rolling digits, particle arcs,
   and persistent relation lines. This is what will make a teacher notice.
3. **S5 linked panels.** One tracker drives the null line and the closing vector loop at once.

### B4. Engineering plan

```
~/Desktop/maths/
  manim.cfg                 1920×1080, 30 fps, bg #070817
  beyond/
    palette.py              colours, fonts, sizes
    mathdata.py             exact Fraction data + row-op engine (from maths2)
    fx.py                   glow(), trail(), point_cloud(), flow_dots(), easing
    typeset.py              STIX math text, live numbers, no LaTeX
    matrix.py               AnimatedMatrix: entries, brackets, row highlight, RowOp
    space3d.py              grid unfold, vector + component staircase, plane mesh
  scenes/s1_mystery.py … s6_finale.py
  tests/test_math.py        checks every number shown on screen against mathdata
  tools/render.py           preview (480p15) / final (1080p30), concat, contact sheets
  tools/score.py            original procedural music + soft SFX (no licensing)
  tools/storyboard.py       storyboard PDF from rendered frames (Pillow)
  voiceover/                script, timestamps, recording guide, audio/ (empty)
  docs/                     this file, CREDITS.md, AI_DISCLOSURE.md
```

- Every number drawn on screen comes from `mathdata.py`, which is tested, so the visuals cannot drift from the maths.
- Workflow per scene: write it, render at `-ql`, extract a contact sheet, inspect it, fix, then move on.
  Final 1080p30 renders only at the end.
- Audio: a newly written procedural ambient score plus very soft synthesised transition sounds.
  It is original, so there is nothing to license. Narration slots are prepared; no TTS anywhere.
- The old project is left untouched.
