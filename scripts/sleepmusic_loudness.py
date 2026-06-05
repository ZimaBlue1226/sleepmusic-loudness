#!/usr/bin/env python
import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


COMMON_BINS = [
    Path(r"D:\ffmpeg-8.1.1-essentials_build\bin"),
    Path(r"C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin"),
]


def find_exe(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    for folder in COMMON_BINS:
        candidate = folder / name
        if candidate.exists():
            return str(candidate)
    raise SystemExit(f"{name} not found. Install FFmpeg or add its bin directory to PATH.")


def run(cmd):
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        print(proc.stdout)
        raise SystemExit(proc.returncode)
    return proc.stdout


def parse_loudnorm(output: str):
    match = re.search(r"\{\s*\"input_i\".*?\}", output, re.S)
    if not match:
        raise SystemExit("Could not find loudnorm JSON in FFmpeg output.")
    return json.loads(match.group(0))


def probe(path: Path):
    ffprobe = find_exe("ffprobe.exe")
    output = run([
        ffprobe,
        "-v", "error",
        "-show_entries", "format=duration,size,bit_rate:stream=codec_name,sample_rate,channels,bits_per_sample",
        "-of", "json",
        str(path),
    ])
    return json.loads(output)


def measure(path: Path, i: float, tp: float, lra: float):
    ffmpeg = find_exe("ffmpeg.exe")
    output = run([
        ffmpeg,
        "-hide_banner",
        "-i", str(path),
        "-af", f"loudnorm=I={i}:TP={tp}:LRA={lra}:print_format=json",
        "-f", "null",
        "-",
    ])
    return parse_loudnorm(output)


def output_name(path: Path, timestamp: str | None = None):
    title = path.parent.name if path.parent.name else strip_timestamp(path.stem)
    stamp = timestamp or datetime.now().strftime("%Y%m%d%H%M")
    return path.with_name(f"{title}-{stamp}.wav")


def format_num(value: float):
    text = f"{value:g}"
    return text.replace("-", "-").replace(".", "p")


def strip_timestamp(stem: str):
    return re.sub(r"-\d{12}$", "", stem)


def format_duration(seconds: float):
    total = int(round(seconds))
    minutes = total // 60
    secs = total % 60
    return f"{minutes}:{secs:02d}"


def render(path: Path, i: float, tp: float, lra: float, sample_rate: int, output: Path | None, timestamp: str | None, overwrite: bool):
    ffmpeg = find_exe("ffmpeg.exe")
    out = output or output_name(path, timestamp)
    if out.exists() and not overwrite:
        raise SystemExit(f"Output already exists: {out}. Use --output or --overwrite.")
    run([
        ffmpeg,
        "-hide_banner",
        "-y" if overwrite else "-n",
        "-i", str(path),
        "-af", f"loudnorm=I={i}:TP={tp}:LRA={lra}:print_format=summary",
        "-ar", str(sample_rate),
        str(out),
    ])
    return out


def print_report(path: Path, info, loud, target: str):
    fmt = info.get("format", {})
    stream = (info.get("streams") or [{}])[0]
    duration = float(fmt.get("duration", 0) or 0)
    channels = stream.get("channels")
    channel_text = "Stereo" if str(channels) == "2" else str(channels)
    bits = stream.get("bits_per_sample")
    print(f"file: {path}")
    print(f"duration: {duration / 60:.2f} min")
    print(f"codec: {stream.get('codec_name')}")
    print(f"sample_rate: {stream.get('sample_rate')}")
    print(f"channels: {stream.get('channels')}")
    print(f"bits_per_sample: {stream.get('bits_per_sample')}")
    print(f"input_i: {loud['input_i']} LUFS")
    print(f"input_tp: {loud['input_tp']} dBTP")
    print(f"input_lra: {loud['input_lra']} LU")
    print(f"input_thresh: {loud['input_thresh']} LUFS")
    print(f"predicted_output_i: {loud.get('output_i')} LUFS")
    print(f"predicted_output_tp: {loud.get('output_tp')} dBTP")
    print(f"predicted_output_lra: {loud.get('output_lra')} LU")
    print(f"target_offset: {loud.get('target_offset')} LU")
    print()
    print("检查信息")
    print("```text")
    print(f"实测文件：{path.name}")
    print(f"响度优化目标：{target}")
    print(f"综合响度：{loud['input_i']} LUFS")
    print(f"True Peak：{loud['input_tp']} dBTP")
    print(f"LRA：{loud['input_lra']} LU")
    print(f"响度门限：{loud['input_thresh']} LUFS")
    print(f"采样率：{stream.get('sample_rate')} Hz")
    print(f"声道：{channel_text}")
    print(f"位深：{bits}-bit PCM" if bits else "位深：")
    print(f"时长：{format_duration(duration)}")
    print("```")


def main():
    parser = argparse.ArgumentParser(description="Measure and render VelaSleep sleepmusic loudness auditions.")
    sub = parser.add_subparsers(dest="command", required=True)

    measure_p = sub.add_parser("measure")
    measure_p.add_argument("file")
    measure_p.add_argument("--i", type=float, default=-20)
    measure_p.add_argument("--tp", type=float, default=-2)
    measure_p.add_argument("--lra", type=float, default=11)

    render_p = sub.add_parser("render")
    render_p.add_argument("file")
    render_p.add_argument("--i", type=float, default=-20)
    render_p.add_argument("--tp", type=float, default=-2)
    render_p.add_argument("--lra", type=float, default=11)
    render_p.add_argument("--sample-rate", type=int, default=44100)
    render_p.add_argument("--output")
    render_p.add_argument("--timestamp", help="Override output timestamp in YYYYMMDDHHMM format.")
    render_p.add_argument("--overwrite", action="store_true")

    args = parser.parse_args()
    path = Path(args.file)
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    if args.command == "measure":
        target = f"I={args.i:g}, TP={args.tp:g}, LRA={args.lra:g}"
        print_report(path, probe(path), measure(path, args.i, args.tp, args.lra), target)
    elif args.command == "render":
        if args.timestamp and not re.fullmatch(r"\d{12}", args.timestamp):
            raise SystemExit("--timestamp must use YYYYMMDDHHMM format.")
        out = render(path, args.i, args.tp, args.lra, args.sample_rate, Path(args.output) if args.output else None, args.timestamp, args.overwrite)
        print(f"created: {out}")
        target = f"I={args.i:g}, TP={args.tp:g}, LRA={args.lra:g}, -ar {args.sample_rate}"
        print_report(out, probe(out), measure(out, args.i, args.tp, args.lra), target)


if __name__ == "__main__":
    main()
