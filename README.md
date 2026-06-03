# sleepmusic-loudness

[English](./README.md) | [中文版](./README.zh.md)

A self-contained Claude Code / Agent skill for measuring, judging, and adjusting **VelaSleep Sleep Music** final-audio loudness with FFmpeg.

It is for long-form sleep-background music under `audio_generation/sleepmusic/`, across styles such as `lofi`, `ambient`, `piano`, or future sleepmusic subgenres. It is not limited to lofi.

---

## Who reads what

This package mixes **human-facing docs** and **agent-facing instructions**. Don't confuse them:

| File | Audience | Purpose |
|---|---|---|
| `README.md` / `README.zh.md` | **Humans** | Install, usage, and customization notes. The agent does not read these at runtime. |
| `SKILL.md` | **Agent** | The skill's execution instructions and trigger metadata. |
| `scripts/sleepmusic_loudness.py` | **Agent-executable helper** | Measures loudness, renders audition versions, preserves 44.1 kHz output, and prints table-ready check fields. |
| `agents/openai.yaml` | **Codex UI metadata** | Display name, short description, and default prompt. |

> In one line: **README is for humans, `SKILL.md` is for the agent.** The Python script is the deterministic helper used by the agent.

---

## What it does

The skill supports two operations:

1. **Measure** a sleepmusic audio file and report LUFS / true peak / LRA / sample format.
2. **Render** a quiet loudness-adjusted audition version using FFmpeg `loudnorm`, preserving source files and using VelaSleep naming rules.

It always finishes with table-ready fields:

```text
实测文件：
响度优化目标：
综合响度 Integrated LUFS：
True Peak dBTP：
LRA 动态范围：
响度门限：
采样率：
声道：
位深：
时长：
```

---

## Contents

This repository's **root is the skill package itself** — `SKILL.md` lives at the top level, not inside a wrapper folder. The skill name, repo name, and clone folder name are all the same: `sleepmusic-loudness`.

```
sleepmusic-loudness/                    # repo root = skill package = clone dir
  README.md                             # human docs, English
  README.zh.md                          # human docs, Chinese
  SKILL.md                              # agent instructions: trigger metadata + workflow
  agents/
    openai.yaml                         # Codex UI metadata
  scripts/
    sleepmusic_loudness.py              # FFmpeg helper script
```

The package is portable. It does not depend on the VelaSleep repo path, though its examples use VelaSleep's `audio_generation/sleepmusic/<style>/<Music Title>/` structure.

---

## Requirements

- Python 3.10+
- FFmpeg and FFprobe available in `PATH`, or installed in one of the helper's known local paths:
  - `D:\ffmpeg-8.1.1-essentials_build\bin`
  - `C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin`

---

## Install

> This is a **private** repo. Configure git auth first (be a collaborator + `gh auth login` / SSH key / PAT), otherwise both clone and `npx skills add` will fail.

The skill must end up as a folder named `sleepmusic-loudness` inside a discovered skills directory.

### A. Manual install — for a human

Clone the repo and copy it straight into a skills directory:

```bash
git clone https://github.com/ZimaBlue1226/sleepmusic-loudness.git

# personal Codex skills
cp -r sleepmusic-loudness ~/.codex/skills/
```

You may symlink instead of copy if you want edits in the clone to take effect live.

### B. Automated install — for an agent

The cross-agent installer detects the root-level `SKILL.md` and installs the skill under its frontmatter `name`:

```bash
npx skills add https://github.com/ZimaBlue1226/sleepmusic-loudness
```

If you are an agent installing this skill manually instead, follow these directives:

- This is a **self-contained skill** and the **repo root is the skill**.
- Place the repo's contents into a `sleepmusic-loudness/` directory in the target agent's skills directory.
- The entry point is `SKILL.md`.
- Keep `SKILL.md`, `agents/`, and `scripts/` together.
- Do **not** read `README.md` / `README.zh.md` to operate the skill — they are human documentation. Operate only from `SKILL.md`.

---

## Usage

Measure:

```powershell
python scripts/sleepmusic_loudness.py measure "E:\path\to\audio.wav"
```

Render a conservative sleep-bed audition:

```powershell
python scripts/sleepmusic_loudness.py render "E:\path\to\audio.wav" --i -22 --tp -2 --lra 11
```

The render command writes a new file next to the source, named:

```text
Music Title-YYYYMMDDHHMM.wav
```

The music title is inferred from the parent directory, matching VelaSleep's structure:

```text
audio_generation/sleepmusic/<style>/<Music Title>/<Music Title>-YYYYMMDDHHMM.wav
```

---

## Customizing

Edit `SKILL.md` to change workflow policy, target loudness guidance, or completion reporting fields.

Edit `scripts/sleepmusic_loudness.py` only when the FFmpeg command behavior, file naming logic, or printed check fields need to change. After editing any file, re-push the repo so installs stay in sync.
