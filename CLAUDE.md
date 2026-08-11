@.github/copilot-instructions.md

## Claude Code

This repo's canonical instructions live in `.github/copilot-instructions.md`
(imported above) so Copilot and Claude share one source of truth.

`pose-tools` is the library half of the pose split: general pose, video and geometry utilities,
shared across the pose projects. `abyss` owns viewers, screens and rendering and depends on this
repo by git tag. The dependency is strictly one-way: `pose-tools` must never import a consumer.

Planning lives in `scratch_space/`, one numbered folder per initiative, `tracking.md` first.
