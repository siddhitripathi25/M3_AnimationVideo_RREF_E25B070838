"""Render helper.

    python tools/render.py preview 1        # 480p15 preview of scene 1
    python tools/render.py preview all
    python tools/render.py final all        # 1920x1080 @ 30 fps
    python tools/render.py sheet 1          # contact sheet PNG of the latest preview
    python tools/render.py concat preview   # join scenes -> renders/
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIM = ROOT / ".venv" / "bin" / "manim"
SCENES = {
    "0": ("s0_title", "S0Title"),
    "1": ("s1_mystery", "S1Mystery"),
    "2": ("s2_independence", "S2Independence"),
    "3": ("s3_revelation", "S3Revelation"),
    "4": ("s4_machine", "S4Machine"),
    "5": ("s5_pivots", "S5Pivots"),
    "6": ("s6_finale", "S6Finale"),
}
QUALITY = {"preview": ["-ql"], "final": ["-qh", "--fps", "30"]}
FOLDER = {"preview": "480p15", "final": "1080p30"}


def video(n: str, mode: str) -> Path:
    mod, cls = SCENES[n]
    return ROOT / "media" / "videos" / mod / FOLDER[mode] / f"{cls}.mp4"


def render(n: str, mode: str) -> None:
    mod, cls = SCENES[n]
    cmd = [str(MANIM), *QUALITY[mode], str(ROOT / "scenes" / f"{mod}.py"), cls]
    print(" ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=ROOT)


def duration(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True).stdout
    return float(out.strip())


def sheet(n: str, mode: str = "preview", every: float = 2.0, out_dir: Path | None = None) -> Path:
    src = video(n, mode)
    out_dir = out_dir or ROOT / "media" / "sheets"
    out_dir.mkdir(parents=True, exist_ok=True)
    d = duration(src)
    count = int(d / every) + 1
    cols = 5
    rows = (count + cols - 1) // cols
    out = out_dir / f"scene{n}_{mode}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf",
                    f"fps=1/{every},scale=384:-1,"
                    f"tile={cols}x{rows}", "-frames:v", "1", str(out)], check=True)
    print(f"{out}  ({d:.1f}s)")
    return out


def concat(mode: str) -> Path:
    out_dir = ROOT / "renders"
    out_dir.mkdir(exist_ok=True)
    lst = out_dir / f"concat_{mode}.txt"
    lst.write_text("".join(f"file '{video(n, mode)}'\n" for n in SCENES))
    out = out_dir / ("BeyondThePivots_preview_480p.mp4" if mode == "preview" else "BeyondThePivots_silent_1080p30.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)],
                   check=True)
    print(f"{out}  ({duration(out):.1f}s)")
    return out


if __name__ == "__main__":
    action, arg = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "all"
    targets = list(SCENES) if arg == "all" else arg.split(",")
    if action in QUALITY:
        for n in targets:
            render(n, action)
            print(f"  -> {video(n, action)}  ({duration(video(n, action)):.1f}s)")
    elif action == "sheet":
        for n in targets:
            sheet(n)
    elif action == "concat":
        concat(arg)
