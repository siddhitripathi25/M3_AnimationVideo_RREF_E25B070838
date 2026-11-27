"""Collect every deliverable into ./deliverables.

    python tools/deliver.py

  Beyond_The_Pivots_Silent_Final.mp4             the complete film, video only (no audio track)
  Beyond_The_Pivots_Reference_with_Music.mp4     same picture + music/SFX, for rehearsal only
  audio/Pivot_Light_Music.wav                    music stem, -44 LUFS, starts at 0:00
  audio/Pivot_Light_SFX.wav                      transition shimmer + discovery chimes stem
  audio/Pivot_Light_Music_plus_SFX.wav           both stems pre-mixed
  scenes_1080p/SceneN_*.mp4                      each scene at full quality
  scene_previews_480p/SceneN_*.mp4               each scene, low-quality preview
  docs/                                          narration script, timestamps, storyboard, credits, AI disclosure
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "deliverables"
SCENES = [("s0_title", "S0Title", "Scene0_Title"), ("s1_mystery", "S1Mystery", "Scene1_The_Mystery"), ("s2_independence", "S2Independence", "Scene2_Independence"),
          ("s3_revelation", "S3Revelation", "Scene3_The_Big_Revelation"), ("s4_machine", "S4Machine", "Scene4_Matrix_Transformation_Machine"),
          ("s5_pivots", "S5Pivots", "Scene5_Pivot_Discovery"), ("s6_finale", "S6Finale", "Scene6_Final_Revelation")]


def run(*a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)


def main():
    for sub in ("scenes_1080p", "scene_previews_480p", "audio", "docs"):
        (D / sub).mkdir(parents=True, exist_ok=True)

    lst = D / "concat_list.txt"
    lst.write_text("".join(f"file '{ROOT / 'media' / 'videos' / m / '1080p30' / f'{c}.mp4'}'\n" for m, c, _ in SCENES))
    master = D / "Beyond_The_Pivots_Silent_Final.mp4"
    run("-f", "concat", "-safe", "0", "-i", str(lst), "-map", "0:v", "-c", "copy", "-an", "-aspect", "16:9", "-movflags", "+faststart", str(master))
    lst.unlink()

    for m, c, name in SCENES:
        shutil.copy2(ROOT / "media" / "videos" / m / "1080p30" / f"{c}.mp4", D / "scenes_1080p" / f"{name}_1080p.mp4")
        prev = ROOT / "media" / "videos" / m / "480p15" / f"{c}.mp4"
        if prev.exists():
            shutil.copy2(prev, D / "scene_previews_480p" / f"{name}_preview_480p.mp4")

    for f in ("Pivot_Light_Music.wav", "Pivot_Light_SFX.wav", "Pivot_Light_Music_plus_SFX.wav"):
        shutil.copy2(ROOT / "assets" / f, D / "audio" / f)
    run("-i", str(master), "-i", str(ROOT / "assets" / "Pivot_Light_Music_plus_SFX.wav"), "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart",
        str(D / "Beyond_The_Pivots_Reference_with_Music.mp4"))

    for src in ("voiceover/NARRATION_SCRIPT.md", "voiceover/RECORDING_GUIDE.md", "docs/TIMESTAMPS.md",
                "docs/Storyboard_BeyondThePivots.pdf", "docs/CREDITS.md", "docs/AI_DISCLOSURE.md"):
        shutil.copy2(ROOT / src, D / "docs" / Path(src).name)
    print(f"deliverables ready in {D}")


if __name__ == "__main__":
    main()
