"""Generate the narration script and the timestamp table from the rendered film.

Each cue is anchored to a key moment logged by the scene itself (media/marks/*.json)
plus an offset, so timestamps stay exact even after scenes are edited and re-rendered.

    python tools/narration.py   -> voiceover/NARRATION_SCRIPT.md, docs/TIMESTAMPS.md
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENES = [
    ("S0Title", "Title: Beyond the Pivots · Siddhi Tripathi"),
    ("S1Mystery", "Scene 1: The Mystery"),
    ("S2Independence", "Scene 2: The Meaning of Independence"),
    ("S3Revelation", "Scene 3: The Big Revelation, v₂ = 2v₁"),
    ("S4Machine", "Scene 4: The Matrix Transformation Machine"),
    ("S5Pivots", "Scene 5: The Pivot Discovery"),
    ("S6Finale", "Scene 6: The Final Revelation"),
]

# (scene, mark, offset seconds, narration). Text in *[...]* is a stage direction, not read aloud.
CUES = [
    ("S0Title", "title", 0.0, "*[title card: no narration needed; optionally:]* \"Beyond the Pivots, by Siddhi Tripathi.\""),
    ("S1Mystery", "point", 0.2, "*[a single point appears in darkness; let it breathe]*"),
    ("S1Mystery", "point", 3.2, "Every vector starts somewhere. Let's start here, at the origin."),
    ("S1Mystery", "vectors", 0.0, "Three vectors: **v-one**, **v-two**, and **v-three**."),
    ("S1Mystery", "cloud", 0.0, "Now let's mix them. Each of these dots is a different combination: some amount of v-one, plus some of v-two, plus some of v-three."),
    ("S1Mystery", "edge_on", 0.0, "Three vectors in three-dimensional space. You'd expect them to fill a cloud with depth…"),
    ("S1Mystery", "edge_on", 5.6, "…but look at it from here. The whole cloud is **perfectly flat**."),
    ("S1Mystery", "question", 0.3, "Three vectors. But are there really **three independent directions**?"),

    ("S2Independence", "line", 0.0, "Forget our vectors for a moment. Take one vector, **u**. Stretch it and flip it, and all you ever get is a **line**."),
    ("S2Independence", "plane", 0.0, "Add a second vector, **w**, pointing somewhere new. Now every point on the line can move in a new direction, and the line sweeps out a **plane**."),
    ("S2Independence", "lissajous", 0.3, "Any path in that plane can be traced by choosing the right amounts, a and b, of u and w."),
    ("S2Independence", "third_off", 0.4, "A third vector that **leaves** the plane adds a genuinely new direction. The plane lifts into **three dimensions**."),
    ("S2Independence", "third_in", 0.5, "But if the third vector already **lies in** the plane, it is just a combination of u and w. The dots slide around, but they never leave the sheet. **Nothing new.**"),
    ("S2Independence", "definition", 0.5, "That is the definition. Vectors are **linearly independent** if the only way to combine them to get zero is to use zero of each. If some non-zero combination gives zero, they are **dependent**: one of them is built from the others."),

    ("S3Revelation", "v1v2", 0.0, "Back to our vectors. Here is **v-two**, two, four, two, and **v-one**, one, two, one, each drawn with its x, y and z steps."),
    ("S3Revelation", "stretch", 0.0, "Let's stretch v-one by a factor k. Every component grows together: k, two-k, k."),
    ("S3Revelation", "land", 0.0, "At k equals two, it lands **exactly** on v-two. Every component matches."),
    ("S3Revelation", "reveal", 0.0, "So **v-two is two times v-one**. They lie on the same line through the origin. Rearranged: minus two v-one, plus v-two, **equals zero**. A non-zero combination giving zero. That is dependence."),
    ("S3Revelation", "v3", 0.0, "What about **v-three**? Can any multiple of v-one reach it? Watch the distance as k changes."),
    ("S3Revelation", "v3", 7.0, "It gets closest at k equals one-half, about zero point seven one, but **never zero**. v-one rises in z, v-three stays flat. No single k fits all three components. So v-three is a **new direction**."),
    ("S3Revelation", "plane", 0.0, "Together, v-one and v-three sweep out a whole plane: **y equals x plus z**. All three vectors satisfy it."),
    ("S3Revelation", "handoff", 0.0, "Now let's prove all of this systematically, by putting the vectors into a matrix."),

    ("S4Machine", "matrix", 0.0, "The vectors become the **columns** of a matrix, A."),
    ("S4Machine", "filaments", 0.6, "Keep an eye on these pink links. In every row, column two is **twice** column one. Watch whether row reduction breaks that."),
    ("S4Machine", "op1a", 0.0, "Step one. Replace row two with row two minus **two times row one**. Two, four, one, minus two, four, two, gives zero, zero, minus one."),
    ("S4Machine", "op1b", 0.0, "Then row three minus row one: zero, zero, minus one. Column one is now clear below the first pivot."),
    ("S4Machine", "op2", 0.0, "Step two. Multiply row two by **minus one**, so its leading entry becomes a one."),
    ("S4Machine", "op3", 0.0, "Step three. Row three plus row two. The last row becomes **all zeros**: it carried no new information."),
    ("S4Machine", "op4", 0.0, "Step four. Row one minus row two clears the entry above the second pivot."),
    ("S4Machine", "op4", 6.0, "Notice the pink relation survived **every** step. Row operations change the columns, but they never change the relationships between them."),
    ("S4Machine", "rref", 0.0, "This is the **reduced row-echelon form** of A."),

    ("S5Pivots", "pivots", 0.0, "The leading ones are the **pivots**: one in column one, one in column three. Column two has **no pivot**."),
    ("S5Pivots", "pivots", 5.0, "Two pivots means **rank two**."),
    ("S5Pivots", "backlink", 0.5, "Here is the key idea. The RREF has different columns from A, but because the relationships are preserved, the pivot **positions** point back to columns one and three of the **original** matrix. So v-one and v-three are independent, and v-two depends on them."),
    ("S5Pivots", "equations", 0.5, "Read the RREF as equations: x-one plus two x-two equals zero, and x-three equals zero."),
    ("S5Pivots", "equations", 5.0, "x-two has no pivot, so it is **free**. Call it t. Then x equals t times minus two, one, zero."),
    ("S5Pivots", "panels", 0.0, "On the left, every value of t gives a solution on this line. On the right, the same numbers combine the vectors: out along v-one, and **straight back to zero**. Every time."),
    ("S5Pivots", "final", 0.5, "At t equals one: **minus two v-one plus v-two equals zero**. A free variable gives a non-zero solution, and a non-zero solution means **dependence**."),

    ("S6Finale", "callback", 0.0, "So let's return to where we started."),
    ("S6Finale", "plane", 0.0, "The flat cloud was the plane y equals x plus z. **v-one and v-three** are the pivot directions; v-two is just two v-one."),
    ("S6Finale", "edge_on", 0.0, "Seen edge-on, the cloud collapses again. Three vectors, but only **two** independent directions. A plane, not all of space."),
    ("S6Finale", "sentence", 1.5, "**Pivots reveal independence. Free variables reveal dependence.**"),
    ("S6Finale", "credits", 0.0, "*(credits; optional)* Thank you for watching."),
]


def ts(x: float) -> str:
    m, s = divmod(max(x, 0.0), 60)
    return f"{int(m)}:{s:04.1f}"


def main():
    marks, starts, ends, t0 = {}, {}, {}, 0.0
    for cls, _ in SCENES:
        m = json.loads((ROOT / "media" / "marks" / f"{cls}.json").read_text())
        marks[cls] = m
        starts[cls], ends[cls] = t0, t0 + m["_end"]
        t0 += m["_end"]
    total = t0

    # ---- timestamps table
    rows = ["# Scene timestamps (exact, from the rendered film)", "",
            f"Total running time: **{ts(total)}** ({total:.2f} s) · 1920×1080 · 30 fps", "",
            "| # | Scene | Start | End | Duration |", "|---|---|---|---|---|"]
    for i, (cls, title) in enumerate(SCENES):
        rows.append(f"| {i} | {title.split(': ', 1)[1]} | {ts(starts[cls])} | {ts(ends[cls])} | {ends[cls] - starts[cls]:.1f} s |")
    rows += ["", "## Key moments", "", "| Time | Scene | Moment |", "|---|---|---|"]
    for i, (cls, _) in enumerate(SCENES):
        for k, v in marks[cls].items():
            if not k.startswith("_"):
                rows.append(f"| {ts(starts[cls] + v)} | {i} | {k} |")
    (ROOT / "docs" / "TIMESTAMPS.md").write_text("\n".join(rows) + "\n")

    # ---- narration script
    words = sum(len(t.split()) for *_, t in CUES if not t.startswith("*"))
    out = ["# BEYOND THE PIVOTS: Narration Script", "",
           "*For you to record in your own voice. No AI voice or TTS is used anywhere in this project.*", "",
           f"- Film length: **{ts(total)}** (1920×1080, 30 fps). Generated by `tools/narration.py` from the rendered film, so the times are exact.",
           f"- About {words} spoken words, roughly {words / (total / 60):.0f} words per minute. Leave the silences: the visuals are timed to breathe.",
           "- **Bold** words are the ones worth leaning on slightly. Lines in *[italics]* describe the screen; don't read them.",
           "- Recording and file naming: see `RECORDING_GUIDE.md`. Per-scene files are placed at each scene's start automatically.", ""]
    for i, (cls, title) in enumerate(SCENES):
        out += ["---", "", f"## {title} · {ts(starts[cls])} – {ts(ends[cls])} ({ends[cls] - starts[cls]:.0f} s)", "",
                "| Cue | Film time | Time in scene | Narration |", "|---|---|---|---|"]
        k = 0
        for c, mk, off, text in CUES:
            if c != cls:
                continue
            k += 1
            rel = marks[cls][mk] + off
            out.append(f"| {i}.{k} | {ts(starts[cls] + rel)} | {ts(rel)} | {text} |")
        out.append("")
    (ROOT / "voiceover" / "NARRATION_SCRIPT.md").write_text("\n".join(out))
    print("voiceover/NARRATION_SCRIPT.md, docs/TIMESTAMPS.md written;", ts(total))


if __name__ == "__main__":
    main()
