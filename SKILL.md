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
5. Judge risk before rendering:
   - Low risk: complete full-mix sleepmusic, integrated loudness below about `-35 LUFS`, true peak below about `-10 dBTP`, and LRA roughly `6-14 LU`. If the user explicitly asked to process/optimize, continue automatically.
   - Medium risk: integrated loudness already near target (`-25` to `-20 LUFS`), LRA above `15 LU`, true peak above `-4 dBTP`, long quiet intro/outro, or unclear whether dynamic loudnorm is appropriate. Stop after measurement, explain the risk, propose the processing mode, and wait for user confirmation.
   - High risk: file appears to be a stem/effect/rain/bird/loop file, integrated loudness below about `-50 LUFS`, LRA below about `2 LU`, suspected missing tracks, or user goal is ambiguous. Stop after measurement and wait for user confirmation. Do not auto-render.
6. Choose processing mode:
   - Use dynamic `loudnorm` for clearly quiet full-mix sleepmusic.
   - Use linear gain (`volume=XdB`) when the file is already close to target and only needs a small overall lift.
   - Do not default to finished-track loudnorm for stems or sound effects.
7. Preserve source files. Write new files using `Music Title-YYYYMMDDHHMM.wav`.
8. Explicitly preserve `44100 Hz` output with `-ar 44100` unless the user asks otherwise.
9. After every measure or render task, finish with a code-block "检查信息" block in the exact field format below.

## Risk Examples

`Rain on Petals.wav` around `-38.60 LUFS / -22.12 dBTP / LRA 10.60` is low risk: complete mix, clearly quiet, dynamic loudnorm to `I=-22, TP=-2, LRA=11` is acceptable.

`Forest Light.wav` around `-23.72 LUFS / -7.84 dBTP / LRA 18.00` is medium risk: already near target but with high LRA. Dynamic loudnorm can lift quiet intros and make low-level noise/electric hiss obvious. Stop after measuring and propose linear gain instead.

Rain, bird, ambience, or other effect stems are high risk. Measure them if requested, but do not normalize them to finished-track loudness unless the user explicitly confirms the goal.

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

Always provide the user a concise code-block after completing measurement or rendering. Do not use a Markdown table for this project. Include these exact fields when available:

```text
实测文件：
响度优化目标：
综合响度：
True Peak：
LRA：
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
