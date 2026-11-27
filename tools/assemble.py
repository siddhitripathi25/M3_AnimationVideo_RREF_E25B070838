"""Mix your narration with the silent film and the separate music / SFX stems.

    python tools/assemble.py --voice                       # default balance
    python tools/assemble.py --voice --music-db -3         # music 3 dB quieter
    python tools/assemble.py --voice --music-db 2 --sfx-db -6
    python tools/assemble.py --voice --no-sfx

Narration (your own recording) goes in voiceover/audio/ as EITHER
    full_voiceover.(wav|m4a|mp3|aiff)          one take, starting at 0:00
OR  scene1.(wav|m4a|mp3|aiff) ... scene6.*      one per scene; each placed at its scene's start

Mixing: narration normalised to -16 LUFS. Music stem is -28 LUFS before ducking and
dips a further ~6 dB under your voice (sidechain compression). The video is not re-encoded.
Output: deliverables/Beyond_The_Pivots_FINAL_with_Narration.mp4
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from render import duration  # noqa: E402

ORDER = ["S0Title", "S1Mystery", "S2Independence", "S3Revelation", "S4Machine", "S5Pivots", "S6Finale"]
EXTS = ("wav", "m4a", "mp3", "aiff", "aif")
AUDIO = ROOT / "voiceover" / "audio"
MUSIC = ROOT / "assets" / "Pivot_Light_Music.wav"
SFX = ROOT / "assets" / "Pivot_Light_SFX.wav"
VIDEO = ROOT / "deliverables" / "Beyond_The_Pivots_Silent_Final.mp4"
OUT = ROOT / "deliverables" / "Beyond_The_Pivots_FINAL_with_Narration.mp4"


def scene_starts():
    t, out = 0.0, []
    for s in ORDER:
        out.append(t)
        t += json.loads((ROOT / "media" / "marks" / f"{s}.json").read_text())["_end"]
    return out


def find(stem):
    for e in EXTS:
        p = AUDIO / f"{stem}.{e}"
        if p.exists():
            return p
    return None


def voices(vdur):
    full = find("full_voiceover")
    if full:
        return [(full, 0.0)]
    starts, out = scene_starts(), []           # starts[0] = title card, starts[n] = scene n
    for n in range(0, 7):
        p = find(f"scene{n}")
        if p is None:
            if n == 0:
                continue                        # narration over the title card is optional
            sys.exit(f"Missing voiceover/audio/scene{n}.wav (or full_voiceover.wav). See voiceover/RECORDING_GUIDE.md")
        end = starts[n + 1] if n < 6 else vdur
        if duration(p) > end - starts[n] + 0.5:
            print(f"  warning: scene{n} narration ({duration(p):.1f}s) is longer than its scene "
                  f"({end - starts[n]:.1f}s) and will run into the next scene.")
        out.append((p, starts[n]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", action="store_true", help="required: mix your narration")
    ap.add_argument("--music-db", type=float, default=0.0, help="music level change in dB (default 0)")
    ap.add_argument("--sfx-db", type=float, default=0.0, help="sfx level change in dB (default 0)")
    ap.add_argument("--no-sfx", action="store_true")
    a = ap.parse_args()
    if not a.voice:
        sys.exit(__doc__)
    if not VIDEO.exists():
        sys.exit("Run python tools/deliver.py first (builds the silent master).")
    vdur = duration(VIDEO)
    vs = voices(vdur)

    inputs = ["-i", str(VIDEO), "-i", str(MUSIC), "-i", str(SFX)]
    for p, _ in vs:
        inputs += ["-i", str(p)]
    f, labels = [], []
    for k, (_, t) in enumerate(vs):
        ms = int(t * 1000)
        f.append(f"[{k + 3}:a]aformat=sample_rates=44100:channel_layouts=stereo,adelay={ms}|{ms}[v{k}]")
        labels.append(f"[v{k}]")
    f.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,apad[vraw]")
    f.append("[vraw]loudnorm=I=-16:TP=-1.5:LRA=11,asplit=3[vk1][vk2][vm]")
    f.append(f"[1:a]volume={a.music_db}dB[m]")
    f.append(f"[2:a]volume={a.sfx_db if not a.no_sfx else -90}dB[s]")
    f.append("[m][vk1]sidechaincompress=threshold=0.015:ratio=4:attack=40:release=700[md]")
    f.append("[s][vk2]sidechaincompress=threshold=0.015:ratio=4:attack=40:release=700[sd]")
    f.append("[md][sd][vm]amix=inputs=3:normalize=0,alimiter=limit=0.89[out]")
    cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(f),
           "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
           "-t", f"{vdur:.3f}", str(OUT)]
    subprocess.run(cmd, check=True)
    print(OUT)


if __name__ == "__main__":
    main()
