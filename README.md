# Beyond the Pivots

*Understanding linear independence through reduced row-echelon form.* An original mathematical film (about 5:20) made with Manim CE.

## Deliverables (`deliverables/`, built by `python tools/deliver.py`)

| File | What |
|---|---|
| `Beyond_The_Pivots_Silent_Final.mp4` | **The complete film**: 1920×1080, 16:9, 30 fps, H.264, video only (no audio track) |
| `audio/Pivot_Light_Music.wav` | Original music stem, −28 LUFS, starts at 0:00, exactly the film's length |
| `audio/Pivot_Light_SFX.wav` | Separate stem: soft transition shimmer and discovery chimes |
| `audio/Pivot_Light_Music_plus_SFX.wav` | Both stems pre-mixed |
| `Beyond_The_Pivots_Reference_with_Music.mp4` | Picture + music, for rehearsing narration only |
| `scenes_1080p/`, `scene_previews_480p/` | Each scene on its own, full quality and preview |
| `docs/` | Narration script, timestamps, storyboard PDF, credits, AI disclosure, recording guide |
| `Beyond_The_Pivots_FINAL_with_Narration.mp4` | Appears after you record and run `python tools/assemble.py --voice` |

## Scenes (`scenes/`)

| # | File | Runtime (exact: `docs/TIMESTAMPS.md`) | Main visual |
|---|---|---|---|
| 0 | `s0_title.py` | 0:00–0:12 | Title card: BEYOND THE PIVOTS · SIDDHI TRIPATHI · URN E25B070838 |
| 1 | `s1_mystery.py` | see TIMESTAMPS | 360 real combinations spray out, then collapse to a line when viewed from inside the plane |
| 2 | `s2_independence.py` | see TIMESTAMPS | One family of dots: line → plane → 3D layers, or stays flat; Lissajous path |
| 3 | `s3_revelation.py` | see TIMESTAMPS | k·v₁ stretches onto v₂ with component staircases; live distance to v₃ never reaches 0 |
| 4 | `s4_machine.py` | see TIMESTAMPS | Every row operation: ghost rows, particle arcs, rolling digits; col₂ = 2·col₁ re-checked after each step |
| 5 | `s5_pivots.py` | see TIMESTAMPS | Pivots ignite and beam back to the original A; linked panels driven by one t |
| 6 | `s6_finale.py` | see TIMESTAMPS | Scene 1 callback, explained; final sentence; credits |

## Code (`beyond/`)

- `mathdata.py`: the single source of mathematical truth (exact fractions).
- `matrix.py`: `AnimatedMatrix`, with per-entry animation and scale-aware rows and columns.
- `fx.py`: glow, trails, glowing vectors, dot clouds and easing.
- `space3d.py`: true-scale 3D coordinates, grid, staircases, the plane y = x + z, and the exact edge-on camera angle.
- `typeset.py`: maths typography without LaTeX (STIX Two).
- `base.py`: scene bases (HUD text, live readouts, caption swaps, and timing marks written to `media/marks/`).

## Commands (after `source .venv/bin/activate`)

```bash
python -m pytest tests                 # exact checks of every on-screen claim
python tools/render.py preview 3       # fast 480p15 preview of scene 3
python tools/render.py sheet 3         # contact sheet of that preview
python tools/render.py final all       # 1080p30 renders (~20 min)
python tools/narration.py              # narration script + docs/TIMESTAMPS.md from the render
python tools/score.py                  # regenerate the original score "Pivot Light" from the timing marks
python tools/storyboard.py             # docs/Storyboard_BeyondThePivots.pdf from real frames
python tools/deliver.py                # silent master + stems + scene files -> deliverables/
python tools/assemble.py --voice [--music-db -3]   # after recording: mix your narration
```

## Documents (`docs/`)

`DESIGN.md` (audit + redesign), `TIMESTAMPS.md`, `Storyboard_BeyondThePivots.pdf`, `CREDITS.md`, `AI_DISCLOSURE.md`.

Title-card text: top of `scenes/s0_title.py`. End credits: `CREDITS` in `scenes/s6_finale.py`.
