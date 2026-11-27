""""Pivot Light": original score for BEYOND THE PIVOTS.

Fully original and synthesised from sine waves and filtered noise in numpy: no samples,
no loops, no third-party recordings, so there is nothing to license.
Timing comes from media/marks/*.json (written by each scene while it renders), so the
music follows the picture exactly.

Layers
  pads     warm, filtered chords; one harmonic colour per scene, long crossfades
  piano    additive piano voice (inharmonic partials, hammer attack); sparse motifs
  shimmer  high detuned sine clusters with slow tremolo + a breath of filtered air
  pulse    soft mallet pulses on chord tones; enters in Scene 3, builds through the
           matrix machine (4) and pivot discovery (5), dissolves in the finale
  resolve  D major in the finale, under the final sentence

Mix rules (for narration): high-passed at 100 Hz (no heavy bass), no drums, no impacts,
no foreground melody; master normalised to -44 LUFS integrated, true peak below -2 dBTP.

    python tools/score.py
      -> assets/Pivot_Light_Music.wav        music only           (-44 LUFS)
      -> assets/Pivot_Light_SFX.wav          transition shimmer + discovery chimes
      -> assets/Pivot_Light_Music_plus_SFX.wav
"""

from __future__ import annotations

import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

ROOT = Path(__file__).resolve().parents[1]
SR = 44100
ORDER = ["S0Title", "S1Mystery", "S2Independence", "S3Revelation", "S4Machine", "S5Pivots", "S6Finale"]
TARGET_LUFS = -44.0   # very quiet, subtle bed
rng = np.random.default_rng(2026)


def hz(note: str) -> float:
    names = {"C": 0, "C#": 1, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "Ab": 8,
             "A": 9, "Bb": 10, "B": 11}
    n, o = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((names[n] + 12 * (o + 1) - 69) / 12)


def load_marks():
    marks, t0, starts = {}, 0.0, {}
    for s in ORDER:
        m = json.loads((ROOT / "media" / "marks" / f"{s}.json").read_text())
        starts[s] = t0
        marks[s] = {k: t0 + v for k, v in m.items()}
        t0 += m["_end"]
    return marks, starts, t0


def place(buf, clip, t):
    i = int(max(t, 0) * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(clip))
    buf[i:j] += clip[: j - i]


def pan(sig, p):
    """p in [-1, 1] -> stereo (constant power)."""
    a = (p + 1) * np.pi / 4
    return np.stack([sig * np.cos(a), sig * np.sin(a)], 1)


# ---------------------------------------------------------------- instruments
def pad(f, dur, amp, bright=0.3):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for ch, det in enumerate((-0.002, 0.002)):
        sig = np.zeros(n)
        for h, a in ((1, 1.0), (2, bright), (3, bright * 0.3), (4, bright * 0.1)):
            ph = rng.uniform(0, 2 * np.pi)
            lfo = 1 + 0.0012 * np.sin(2 * np.pi * 0.11 * t + ph)
            sig += a / h * np.sin(2 * np.pi * f * h * (1 + det) * lfo * t + ph)
        out[:, ch] = sig
    a_len, r_len = min(int(3.0 * SR), n // 2), min(int(4.0 * SR), n // 2)
    env = np.ones(n)
    env[:a_len] = np.sin(np.linspace(0, np.pi / 2, a_len)) ** 2
    env[-r_len:] *= np.cos(np.linspace(0, np.pi / 2, r_len)) ** 2
    return out * env[:, None] * amp


def piano(f, vel=0.5, dur=5.0, p=0.0):
    """Additive piano: slightly inharmonic partials, faster decay up high, two detuned strings."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    B = 0.00035
    sig = np.zeros(n)
    base_decay = 2.6 * (261.6 / f) ** 0.35
    for k in range(1, 11):
        fk = k * f * np.sqrt(1 + B * k * k)
        if fk > 12000:
            break
        a = vel * (1.0 / k ** 1.5) * (0.6 if k == 2 else 1.0)
        d = base_decay / (1 + 0.45 * (k - 1))
        for det in (-0.0007, 0.0007):
            sig += 0.5 * a * np.sin(2 * np.pi * fk * (1 + det) * t) * np.exp(-t / d)
    hammer = rng.standard_normal(n) * np.exp(-t / 0.004) * 0.02 * vel
    sig = sig + hammer
    sig *= np.minimum(1, t / 0.002)
    sig *= np.minimum(1, (dur - t) / 0.3).clip(0, 1)
    return pan(sig, p)


def mallet(f, vel=0.5, bright=0.3):
    """Soft pulse: rounded sine with a touch of octave, short decay."""
    dur = 0.7
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * f * t) + bright * 0.35 * np.sin(4 * np.pi * f * t)
           + bright * 0.12 * np.sin(2 * np.pi * 3.01 * f * t)) * np.exp(-t / (0.16 + 0.1 * bright))
    sig *= np.minimum(1, t / 0.008)
    return sig * vel


def shimmer(freqs, dur, amp):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for f in freqs:
        for ch in (0, 1):
            ph = rng.uniform(0, 2 * np.pi)
            trem = 0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.07, 0.25) * t + ph)
            out[:, ch] += np.sin(2 * np.pi * f * (1 + rng.uniform(-0.003, 0.003)) * t + ph) * trem ** 2
    env = np.sin(np.linspace(0, np.pi, n)) ** 1.5
    return out * env[:, None] * amp / max(1, len(freqs))


def air(dur, amp):
    n = int(dur * SR)
    noise = rng.standard_normal((n, 2))
    sos = butter(2, [4000, 9000], btype="band", fs=SR, output="sos")
    x = np.stack([sosfilt(sos, noise[:, c]) for c in range(2)], 1)
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    return x * env[:, None] * amp


def bell(f, dur=3.0, amp=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for r, a, d in ((1.0, 1.0, 1.6), (2.01, 0.4, 1.1), (2.76, 0.2, 0.8), (5.4, 0.08, 0.4)):
        sig += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d)
    sig *= np.minimum(1, t / 0.004)
    return np.stack([sig, sig], 1) * amp


def reverb(x, seconds=3.6, mix=0.4):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-t / (seconds / 5.5))[:, None]
    ir[:, 1] = np.roll(ir[:, 1], 211)
    ir[: int(0.012 * SR)] = 0  # pre-delay keeps attacks clear
    wet = np.stack([fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    wet *= (np.std(x) + 1e-12) / (np.std(wet) + 1e-12)
    return (1 - mix) * x + mix * wet


def envelope(t, pts):
    xs, ys = zip(*sorted(pts))
    return float(np.interp(t, xs, ys))


# ---------------------------------------------------------------- composition
HARMONY = {   # one voicing per segment; roots kept at octave 2-3, high-passed later
    "S0Title":        [["D3", "A3", "F4", "C5"]],
    "S1Mystery":      [["D3", "A3", "F4", "C5"], ["Bb2", "F3", "D4", "A4"], ["D3", "A3", "E4", "F4"]],
    "S2Independence": [["F3", "C4", "A4", "E5"], ["G3", "D4", "Bb4", "F5"], ["D3", "A3", "F4", "E5"], ["Bb2", "F3", "D4", "A4"]],
    "S3Revelation":   [["D3", "A3", "F4", "C5"], ["G3", "D4", "Bb4", "D5"], ["Bb2", "F3", "D4", "A4"], ["C3", "G3", "E4", "D5"]],
    "S4Machine":      [["D3", "A3", "F4", "A4"], ["Bb2", "F3", "D4", "F4"], ["G2", "D3", "Bb3", "F4"], ["A2", "E3", "C#4", "G4"]],
    "S5Pivots":       [["F3", "C4", "A4", "E5"], ["C3", "G3", "E4", "D5"], ["Bb2", "F3", "D4", "A4"], ["A2", "E3", "C#4", "E4"]],
    "S6Finale":       [["D3", "A3", "F4", "C5"], ["Bb2", "F3", "D4", "A4"], ["D3", "A3", "F#4", "E5"], ["D3", "A3", "F#4", "A4"]],
}


def chord_timeline(starts, marks):
    tl = []
    for s in ORDER:
        t0, t1 = starts[s], marks[s]["_end"]
        segs = HARMONY[s]
        L = (t1 - t0) / len(segs)
        for i, c in enumerate(segs):
            tl.append((t0 + i * L, t0 + (i + 1) * L, c))
    return tl


def chord_at(tl, t):
    for a, b, c in tl:
        if a <= t < b:
            return c
    return tl[-1][2]


def up(note, octs):
    return note[:-1] + str(int(note[-1]) + octs)


def compose():
    marks, starts, total = load_marks()
    # stems are exactly the film length, so the fade-out ends on the last frame
    n = int(total * SR)
    pads, keys, shim, pulse, sfx = (np.zeros((n, 2)) for _ in range(5))
    tl = chord_timeline(starts, marks)
    M = lambda s, k: marks[s][k]

    # ── pads (with long overlaps: no abrupt changes between scenes) ──────────
    for a, b, c in tl:
        for note in c:
            low = hz(note) < 160
            place(pads, pad(hz(note), b - a + 4.5, 0.09 if low else 0.12, bright=0.22), a - 1.5)

    # ── shimmer: high chord tones, more present as the film opens up ─────────
    shim_level = [(0, 0.5), (M("S1Mystery", "cloud"), 0.9), (M("S2Independence", "plane"), 1.0),
                  (M("S4Machine", "matrix"), 0.7), (M("S5Pivots", "pivots"), 1.2), (M("S6Finale", "sentence"), 1.4),
                  (total, 0.6)]
    for a, b, c in tl:
        lvl = envelope((a + b) / 2, shim_level)
        place(shim, shimmer([hz(up(x, 2)) for x in c[1:]], b - a + 4, 0.05 * lvl), a - 1.0)
        place(shim, air(b - a + 4, 0.006 * lvl), a - 1.0)

    # ── piano motifs (sparse; never on top of key narration beats) ──────────
    P = []  # (time, note, velocity, pan)
    for i, (dt, nt) in enumerate([(2.5, "A4"), (7.5, "F4"), (13.0, "D5"), (20.0, "C5"), (26.0, "A4"), (31.5, "E4")]):
        P.append((starts["S1Mystery"] + dt, nt, 0.32, (-0.3, 0.3)[i % 2]))
    s2 = starts["S2Independence"]
    for dt, nt in [(1.5, "F4"), (2.1, "A4"), (7.0, "G4"), (7.6, "D5"), (13.0, "A4"), (19.5, "Bb4"),
                   (20.1, "F5"), (27.5, "A4"), (28.1, "E5"), (37.5, "D5"), (43.0, "A4")]:
        P.append((s2 + dt, nt, 0.28, 0.2))
    for k, nt in enumerate(["D4", "F4", "A4", "D5"]):                       # the reveal: rising D minor
        P.append((M("S3Revelation", "land") + 0.15 + 0.32 * k, nt, 0.40, -0.2 + 0.15 * k))
    for dt, nt in [(4.0, "C5"), (9.0, "G4"), (12.0, "E5")]:
        P.append((M("S3Revelation", "plane") + dt, nt, 0.26, 0.25))
    P.append((M("S4Machine", "rref") + 1.0, "D5", 0.36, 0.0))
    P.append((M("S4Machine", "rref") + 1.35, "A5", 0.28, 0.2))
    P.append((M("S5Pivots", "pivots") + 0.1, "A4", 0.36, -0.25))            # pivot 1
    P.append((M("S5Pivots", "pivots") + 2.1, "E5", 0.36, 0.25))             # pivot 3
    for k, nt in enumerate(["C#5", "E5", "A5"]):
        P.append((M("S5Pivots", "final") + 0.7 + 0.3 * k, nt, 0.30, 0.1 * k))
    # finale: resolve to D major
    f0 = M("S6Finale", "callback")
    for dt, nt in [(3.0, "A4"), (9.0, "F#4"), (15.0, "D5")]:
        P.append((f0 + dt, nt, 0.30, 0.0))
    sen = M("S6Finale", "sentence")
    for k, nt in enumerate(["D3", "A3", "D4", "F#4", "A4", "D5"]):          # gentle rolled chord
        P.append((sen + 1.0 + 0.11 * k, nt, 0.30 if k < 2 else 0.34, -0.4 + 0.16 * k))
    for k, nt in enumerate(["F#5", "E5", "D5"]):
        P.append((M("S6Finale", "credits") + 2.0 + 2.2 * k, nt, 0.24, 0.15))
    P.append((M("S6Finale", "_end") - 4.0, "D4", 0.22, 0.0))
    P.append((M("S6Finale", "_end") - 4.0, "A4", 0.20, 0.0))
    for t, nt, v, p in P:
        place(keys, piano(hz(nt), v, 6.0, p), t)

    # ── pulse: enters in Scene 3, builds through 4 and 5, dissolves in 6 ─────
    bpm = 84.0
    eighth = 60 / bpm / 2
    level = [(0, 0), (M("S3Revelation", "stretch"), 0), (M("S3Revelation", "stretch") + 3, 0.25),
             (M("S3Revelation", "reveal") + 6, 0.12), (M("S3Revelation", "plane"), 0.25),
             (M("S4Machine", "matrix"), 0.35), (M("S4Machine", "op1a"), 0.5), (M("S4Machine", "op4"), 0.75),
             (M("S4Machine", "rref"), 0.85), (M("S4Machine", "rref") + 3, 0.45),
             (M("S5Pivots", "pivots"), 0.55), (M("S5Pivots", "panels"), 0.9), (M("S5Pivots", "final"), 1.0),
             (M("S5Pivots", "_end"), 0.35), (M("S6Finale", "edge_on"), 0.2), (M("S6Finale", "sentence"), 0.0),
             (total, 0)]
    density = [(0, 0), (M("S3Revelation", "stretch"), 2), (M("S4Machine", "matrix"), 1),
               (M("S5Pivots", "panels"), 0.5), (M("S5Pivots", "_end"), 1), (M("S6Finale", "callback") + 8, 2), (total, 2)]
    pattern = [0, 2, 1, 3, 2, 1, 3, 2]
    t, k = M("S3Revelation", "stretch"), 0
    while t < M("S6Finale", "sentence"):
        lv = envelope(t, level)
        step = eighth * envelope(t, density)               # 2 = quarters, 1 = eighths, 0.5 = sixteenths
        step = eighth * (2 if step > 1.5 * eighth else 1 if step > 0.75 * eighth else 0.5)
        if lv > 0.01:
            c = chord_at(tl, t)
            note = up(c[1:][pattern[k % 8] % 3], 1)
            bright = 0.15 + 0.6 * lv                         # the filter 'opens' as it builds
            accent = 1.0 if k % 4 == 0 else 0.7
            clip = mallet(hz(note), 0.11 * lv * accent, bright)
            place(pulse, pan(clip, 0.35 * np.sin(k * 0.9)), t)
        t += step
        k += 1

    # ── sound effects (separate stem, very subtle) ──────────────────────────
    for s in ORDER[1:]:   # all cuts are match cuts: a soft airy swell, not a whoosh
        place(sfx, air(2.4, 0.05), starts[s] - 1.2)
    for tt, nt in [(M("S1Mystery", "edge_on") + 5.6, "A5"), (M("S3Revelation", "land") + 0.05, "D6"),
                   (M("S4Machine", "rref") + 2.0, "F#5"), (M("S5Pivots", "pivots") + 0.05, "A5"),
                   (M("S5Pivots", "pivots") + 2.05, "E6"), (M("S5Pivots", "final") + 0.65, "C#6"),
                   (M("S6Finale", "edge_on") + 4.8, "A5"), (M("S6Finale", "sentence") + 1.0, "D6")]:
        place(sfx, bell(hz(nt), 3.0, 0.05), tt)

    music = pads * 0.8 + keys * 1.1 + shim * 1.1 + pulse * 0.55
    music = reverb(music, 3.8, 0.42)
    sfx = reverb(sfx, 2.6, 0.35)
    hp = butter(2, 150, btype="high", fs=SR, output="sos")          # light: no heavy bass
    lp = butter(2, 8000, btype="low", fs=SR, output="sos")          # soft top, no sparkle that fights speech
    music = np.stack([sosfilt(lp, sosfilt(hp, music[:, c])) for c in range(2)], 1)
    sfx = np.stack([sosfilt(hp, sfx[:, c]) for c in range(2)], 1)
    fi, fo = int(4 * SR), int(5 * SR)                                  # smooth fade-in / fade-out
    for x in (music, sfx):
        x[:fi] *= (np.sin(np.linspace(0, np.pi / 2, fi)) ** 2)[:, None]
        x[-fo:] *= (np.cos(np.linspace(0, np.pi / 2, fo)) ** 2)[:, None]
    return music, sfx


# ---------------------------------------------------------------- loudness
def write_wav(path: Path, x):
    path.parent.mkdir(parents=True, exist_ok=True)
    y = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(y.tobytes())


def measure(path: Path):
    out = subprocess.run(["ffmpeg", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summ = out[out.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ).group(1))
    return i, tp


def normalise(x, path, target):
    write_wav(path, x / (np.max(np.abs(x)) + 1e-9) * 0.5)
    i, _ = measure(path)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.5 * 10 ** ((target - i) / 20)
    write_wav(path, x)
    i, tp = measure(path)
    print(f"{path.name:34s} {len(x) / SR:6.1f}s   {i:6.1f} LUFS   true peak {tp:5.1f} dBFS")
    return x


if __name__ == "__main__":
    music, sfx = compose()
    A = ROOT / "assets"
    m = normalise(music, A / "Pivot_Light_Music.wav", TARGET_LUFS)
    s = normalise(sfx, A / "Pivot_Light_SFX.wav", TARGET_LUFS - 14)
    both = m + s
    write_wav(A / "Pivot_Light_Music_plus_SFX.wav", both)
    i, tp = measure(A / "Pivot_Light_Music_plus_SFX.wav")
    print(f"{'Pivot_Light_Music_plus_SFX.wav':34s} {len(both) / SR:6.1f}s   {i:6.1f} LUFS   true peak {tp:5.1f} dBFS")
