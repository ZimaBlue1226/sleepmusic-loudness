---
name: sleepmusic-loudness
description: Measure, judge, and adjust long-form VelaSleep Sleep Music loudness with FFmpeg. Use when Codex needs to analyze WAV/AAC/MP3 sleep-background music across any sleepmusic style such as lofi, ambient, piano, or nature-pad; report LUFS / true peak / LRA; create quiet loudnorm audition versions; preserve 44.1 kHz output; or decide sleep-safe loudness targets.
---

# Sleep Music Loudness

## Core Rule

Treat VelaSleep sleepmusic as sleep-background music, not normal music, podcasts, YouTube loudness, study beats, or chill mixes. `lofi` is only one current style under `audio_generation/sleepmusic/`, not the skill boundary.

Do not default to `-16 LUFS`. Use it only when the user explicitly wants a much louder non-sleep target. For sleep-bed auditions, start with:

```text
I=-20
TP=-2.0
LRA=11
```

If the user says it still feels loud or too present, try `I=-22` or `I=-23` before changing other parameters.

## Workflow

1. Read `project_context.md` first if working inside the VelaSleep repo.
2. Identify the exact audio file. Confirm when several similarly named files exist.
3. Measure before changing anything.
4. Report the useful fields:
   - `input_i`: integrated loudness in LUFS.
   - `input_tp`: true peak in dBTP.
   - `input_lra`: loudness range in LU.
   - duration, format, sample rate, channels, bit depth when relevant.
5. Judge for sleep use:
   - Below about `-35 LUFS`: usually too quiet for a finished sleep-bed file.
   - Around `-22` to `-20 LUFS`: useful audition range for VelaSleep sleep beds.
   - `-16 LUFS`: usually too loud / too present for this product context.
   - `TP` near `0 dBTP`: risky for later AAC/MP3 encoding; prefer `-2.0 dBTP`.
   - `LRA` above about `15 LU`: may feel dynamically active or uneven for sleep.
6. Generate audition files only after the user asks.
7. Preserve source files. Write new files using `Music Title-YYYYMMDDHHMM.wav`.
8. Explicitly preserve `44100 Hz` output with `-ar 44100` unless the user asks otherwise.
9. After every measure or render task, finish with a table-ready "检查信息" block for the user.

## Recommended Commands

Prefer the bundled helper script:

```powershell
python C:\Users\周润泽\.codex\skills\sleepmusic-loudness\scripts\sleepmusic_loudness.py measure "E:\path\to\file.wav"
python C:\Users\周润泽\.codex\skills\sleepmusic-loudness\scripts\sleepmusic_loudness.py render "E:\path\to\file.wav" --i -20 --tp -2 --lra 11
```

The script looks for `ffmpeg.exe` / `ffprobe.exe` in `PATH` and common local install paths, including `D:\ffmpeg-8.1.1-essentials_build\bin`.

Manual measure:

```powershell
ffmpeg -hide_banner -i "input.wav" -af loudnorm=I=-20:TP=-2:LRA=11:print_format=json -f null -
```

Manual audition render:

```powershell
ffmpeg -hide_banner -y -i "input.wav" -af loudnorm=I=-20:TP=-2:LRA=11:print_format=summary -ar 44100 "Music Title-YYYYMMDDHHMM.wav"
```

## Completion Output

Always provide the user a concise table-ready block after completing measurement or rendering. Include these fields when available:

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

For render tasks, use the newly generated file as `实测文件` and report its measured values, not only FFmpeg's predicted output. If the source and output differ, mention the source file separately before the block.

## Naming

Use the music directory name as the title when the file lives under `audio_generation/sleepmusic/<style>/<Music Title>/`.

Examples:

```text
audio_generation/sleepmusic/lofi/Valley in Silver/Valley in Silver-202606031452.wav
audio_generation/sleepmusic/ambient/Example Title/Example Title-YYYYMMDDHHMM.wav
```

For newly generated loudness-adjusted audio, update the timestamp instead of appending processing details:

```text
Spring Before Sunrise-202606031722.wav
Valley in Silver-202606031720.wav
```

Do not generate names like:

```text
*_production.wav
*_loudnorm_I-20_TP-2_LRA-11_44k.wav
```

## Current VelaSleep Calibration

Known 2026-06-03 reference measurements from the current `lofi` style:

```text
Valley in Silver-202606031452.wav
Input:  -47.40 LUFS / -26.84 dBTP / LRA 15.90
Render with I=-20, TP=-2, LRA=11: about -21.7 LUFS / -2.0 dBTP / LRA 11.7
User feedback: good direction, still slightly loud.
Render with I=-22, TP=-2, LRA=11 as Valley in Silver-202606031720.wav: about -23.67 LUFS / -2.91 dBTP / LRA 11.70

Spring Before Sunrise-202606031446.wav
Input:  -38.16 LUFS / -17.32 dBTP / LRA 19.70
Render with I=-22, TP=-2, LRA=11, -ar 44100 as Spring Before Sunrise-202606031722.wav: about -23.07 LUFS / -2.00 dBTP / LRA 15.70
```

Use `I=-20, TP=-2, LRA=11` as an initial audition baseline when there is no feedback. If it feels too present, use the more conservative `I=-22, TP=-2, LRA=11` baseline.
