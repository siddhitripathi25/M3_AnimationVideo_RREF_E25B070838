# AI Disclosure

**Tool:** Claude Code (Anthropic), an AI coding assistant running in the creator's terminal.

## What the AI assistant did
- Audited the earlier version of this project (`~/Desktop/maths_animation_video`, built with a different AI assistant, Google Antigravity / Gemini) and identified defects.
- Proposed the visual redesign (`docs/DESIGN.md`) and wrote the animation source code in `beyond/` and `scenes/`.
- Wrote the exact-arithmetic test suite, the render/assembly tools, and the procedural music generator.
- Drafted the narration script and these documents.
- Rendered previews and inspected frames to fix layout and geometry problems.

## What the creator did
- Specified the topic, the vectors, the matrix, every row operation and all mathematical conclusions.
- Set the creative direction, palette and scene structure, and approved the design.
- Records the narration in their own voice.
- Reviews and edits the script, credits and final film.

## What was NOT used
- No AI-generated or text-to-speech voice.
- No AI-generated images or video. Every frame is rendered by Manim from code.
- No third-party music.

## How correctness was protected
The AI assistant did not decide any mathematics. All on-screen numbers are computed from a single data module and verified by
automated tests using exact fractions (`tests/test_math.py`). During development these tests caught an error in the assistant's
own design notes: a distance it had written as √(2/3) is actually √(1/2). It was corrected before any animation used it.

*Edit this file so it matches your institution's disclosure requirements.*
