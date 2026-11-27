# Recording your narration

The film is finished and silent apart from the original music. Your voice is the only missing piece.
This project contains **no AI-generated voice and no placeholder recordings**. `voiceover/audio/` is empty until you record.

## 1. Rehearse with the picture

Open `deliverables/Beyond_The_Pivots_Reference_with_Music.mp4` and read `NARRATION_SCRIPT.md` aloud along with it once or twice.
The cue times are exact.

## 2. Record (Mac)

- **QuickTime Player:** File → New Audio Recording. Choose your mic and set quality to *Maximum*. Record, then File → Export As → Audio Only (`.m4a`).
- **Voice Memos:** record, then Share → Save to Files (`.m4a`).
- **GarageBand / Audacity:** export WAV, 44.1 or 48 kHz.

Tips: use a small, soft-furnished room. Keep the mic about a hand's width from your mouth, slightly off-axis.
Leave 1 second of silence at the start. Re-record a line rather than rushing it.

## 3. Name the files

Pick **one** option and put the files in `voiceover/audio/`:

| Option | Files | Placement |
|---|---|---|
| A: one take | `full_voiceover.m4a` (or `.wav`/`.mp3`/`.aiff`) | starts at 0:00 |
| B: per scene (recommended) | `scene1.m4a` … `scene6.m4a` (+ optional `scene0.m4a` over the title card) | each starts at its scene's first frame |

Scene start times for option B are in each scene heading of `NARRATION_SCRIPT.md` and in `docs/TIMESTAMPS.md`.
Within each file, follow the cue times *relative to the scene start*. Silence at the start of a file is fine.
If a file runs longer than its scene, the assembler warns you.

## 4. Build the final film

```bash
cd ~/Desktop/maths
source .venv/bin/activate
python tools/assemble.py --voice                     # default balance
python tools/assemble.py --voice --music-db -3       # music quieter
python tools/assemble.py --voice --music-db 2        # music louder
python tools/assemble.py --voice --no-sfx            # drop the chimes
```

Output: `deliverables/Beyond_The_Pivots_FINAL_with_Narration.mp4`.
Your voice is normalised to −16 LUFS. The music stem (−28 LUFS) also dips about 6 dB whenever you speak.
Nothing is re-rendered, so each run takes seconds. Listen, adjust `--music-db`, and run again.
If you'd rather mix in your own editor (iMovie, DaVinci Resolve, Premiere), import the silent master and the WAV stems from `deliverables/audio/`. All start at 0:00 and are exactly the film's length.

## 5. Optional: change the credits

Title card text is at the top of `scenes/s0_title.py`; end credits are the `CREDITS` dictionary in `scenes/s6_finale.py`. After editing either:

```bash
python tools/render.py final 0,6 && python tools/narration.py && python tools/score.py && python tools/deliver.py
```
