"""Scene base classes shared by all six scenes."""

from __future__ import annotations

import numpy as np
from manim import (
    ThreeDScene, MovingCameraScene, ValueTracker, always_redraw, FadeIn, FadeOut,
    VGroup, smooth, DEGREES,
)

from .palette import BG
from .fx import GlowVector, trail, glow_dot
from .space3d import P

V1 = np.array([1.0, 2.0, 1.0])
V2 = np.array([2.0, 4.0, 2.0])
V3 = np.array([1.0, 1.0, 0.0])


class Marks:
    """Log the exact time of key moments -> media/marks/<Scene>.json (narration + SFX sync)."""

    def mark(self, name):
        if not hasattr(self, "_marks"):
            self._marks = {}
        self._marks[name] = round(float(self.renderer.time), 2)

    def tear_down(self):
        super().tear_down()
        import json
        from pathlib import Path
        out = Path(__file__).resolve().parents[1] / "media" / "marks"
        out.mkdir(parents=True, exist_ok=True)
        data = dict(getattr(self, "_marks", {}))
        data["_end"] = round(float(self.renderer.time), 2)
        (out / f"{type(self).__name__}.json").write_text(json.dumps(data, indent=1))


class Base3D(Marks, ThreeDScene):
    def setup(self):
        super().setup()
        self.camera.background_color = BG

    # Heads-up display: text glued to the screen, not to the 3D world.
    # NOTE: Cairo caches its context at the first rendered frame (frame_center =
    # ORIGIN in every scene), so fixed-in-frame text is NOT displaced when the
    # camera's frame_center moves later. Never start a scene with a non-zero
    # frame_center, or HUD text will be offset.
    def hud(self, *mobs):
        self.add_fixed_in_frame_mobjects(*mobs)
        self.remove(*mobs)  # added by the animation that shows them
        return mobs[0] if len(mobs) == 1 else VGroup(*mobs)

    def live_hud(self, func):
        """A screen-fixed mobject rebuilt every frame by `func` (live numbers).

        always_redraw alone fails in 3D: the rebuilt submobjects are not in the
        camera's fixed-in-frame set, so they get projected into 3D. Re-register.
        """
        mob = func()

        def upd(m):
            m.become(func())
            self.camera.add_fixed_in_frame_mobjects(m)

        mob.add_updater(upd)
        self.add_fixed_in_frame_mobjects(mob)
        self.remove(mob)
        return mob

    def swap(self, old, new, run_time=0.9, shift=0.15):
        """Sequenced caption change, so two texts never overlap mid-fade."""
        from manim import LaggedStart, UP
        self.play(LaggedStart(FadeOut(old, shift=shift * UP), FadeIn(new, shift=shift * UP), lag_ratio=0.55),
                  run_time=run_time)

    def label3d(self, mob, point, offset=np.array([0.0, 0.0, 0.0])):
        """A label that stays facing the camera, anchored to a 3D point."""
        mob.move_to(np.asarray(point) + offset)
        self.add_fixed_orientation_mobjects(mob)
        self.remove(mob)
        return mob

    def growing_vector(self, v, color, core_color=None, width=5.0):
        """(vector mobject, tracker) — vector length follows tracker in [0, 1]."""
        k = ValueTracker(0.0)
        vec = always_redraw(lambda: GlowVector(P(0, 0, 0), P(np.asarray(v) * max(k.get_value(), 1e-3)),
                                               color, width=width, core_color=core_color))
        return vec, k


class Base2D(Marks, MovingCameraScene):
    def setup(self):
        super().setup()
        self.camera.background_color = BG
