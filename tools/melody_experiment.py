#!/usr/bin/env python3
"""メロディ抽出パイプライン実験(song-analysis拡張の検証用)

手順: 音源の指定区間を切り出し → demucsでボーカル分離 → pyinでF0抽出
      → ノート化 → キー基準で移動ド変換 → 検証用に出力

使い方:
  python3 tools/melody_experiment.py <音源> <開始秒> <終了秒> <キー(例:E)> [BPM]
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
# 移動ド(メジャーキー基準、半音12段)
SOLFEGE = ["ド", "ド#", "レ", "レ#", "ミ", "ファ", "ファ#", "ソ", "ソ#", "ラ", "ラ#", "シ"]


def crop(src: str, start: float, end: float, out: Path) -> None:
    subprocess.run(
        [FFMPEG, "-y", "-i", src, "-ss", str(start), "-to", str(end),
         "-ac", "2", "-ar", "44100", str(out)],
        check=True, capture_output=True)


def separate_vocals(wav: Path, outdir: Path) -> Path:
    subprocess.run(
        [sys.executable, "-m", "demucs", "--two-stems=vocals",
         "-o", str(outdir), str(wav)],
        check=True)
    hits = list(outdir.glob(f"*/{wav.stem}/vocals.wav"))
    if not hits:
        raise FileNotFoundError("demucs出力のvocals.wavが見つからない")
    return hits[0]


def extract_notes(vocal_wav: Path, key_root: int, bpm: float, t_offset: float):
    import librosa
    import numpy as np

    y, sr = librosa.load(str(vocal_wav), sr=22050, mono=True)
    f0, voiced, prob = librosa.pyin(
        y, fmin=librosa.note_to_hz("E2"), fmax=librosa.note_to_hz("C6"),
        sr=sr, frame_length=2048)
    times = librosa.times_like(f0, sr=sr)
    midi = np.full_like(f0, np.nan)
    ok = ~np.isnan(f0)
    midi[ok] = librosa.hz_to_midi(f0[ok])

    # フレーム→ノート化: 半音丸めが同じ値で連続する区間をまとめる
    notes = []
    cur = None  # [pitch, t_start, t_end]
    min_dur = 0.09  # 90ms未満は捨てる(ビブラート・ノイズ)
    for t, m, v in zip(times, midi, voiced):
        p = int(round(m)) if (v and not np.isnan(m)) else None
        if cur is not None and p == cur[0]:
            cur[2] = t
        else:
            if cur is not None and cur[2] - cur[1] >= min_dur:
                notes.append(tuple(cur))
            cur = [p, t, t] if p is not None else None
    if cur is not None and cur[2] - cur[1] >= min_dur:
        notes.append(tuple(cur))

    beat = 60.0 / bpm
    out = []
    for p, t0, t1 in notes:
        if p is None:
            continue
        deg = (p - key_root) % 12
        octave = p // 12 - 1
        out.append({
            "time": round(t_offset + t0, 2),
            "beats": round((t1 - t0) / beat, 2),
            "note": f"{NOTE_NAMES[p % 12]}{octave}",
            "solfege": SOLFEGE[deg],
            "in_scale": deg in (0, 2, 4, 5, 7, 9, 11),
        })
    return out


def main():
    src, start, end, key = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    bpm = float(sys.argv[5]) if len(sys.argv) > 5 else 120.0
    key_root = NOTE_NAMES.index(key)
    work = Path("songs/_audio/_work")
    work.mkdir(parents=True, exist_ok=True)
    seg = work / "segment.wav"

    print(f"[1/3] 切り出し {start}-{end}s ...")
    crop(src, start, end, seg)
    print("[2/3] demucsボーカル分離(数分かかる)...")
    vocals = separate_vocals(seg, work)
    print("[3/3] pyinピッチ抽出→ノート化...")
    notes = extract_notes(vocals, key_root, bpm, start)

    print(f"\n=== 抽出ノート({len(notes)}個) キー{key}メジャー基準 ===")
    print("時刻s | 拍 | 音名 | 移動ド | スケール内")
    for n in notes:
        flag = "" if n["in_scale"] else " ⚠スケール外"
        print(f"{n['time']:7.2f} | {n['beats']:4.2f} | {n['note']:4} | {n['solfege']:3}{flag}")


if __name__ == "__main__":
    main()
