# ─────────────────────────────────────────────────────────────────────────────
# modules/audio_analyser.py  –  Librosa-based audio feature extraction
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from config import (
    FILLER_WORDS,
    MIN_PAUSE_DURATION,
    SILENCE_TOP_DB,
)


# ── Audio I/O ─────────────────────────────────────────────────────────────────

def load_audio(audio_path: str | Path) -> Tuple[np.ndarray, int]:
    """
    Load audio with Librosa and return (waveform, sample_rate).
    Resampled to 16 kHz mono for consistent processing.
    """
    import librosa
    y, sr = librosa.load(str(audio_path), sr=16_000, mono=True)
    return y, sr


# ── Waveform Visualisation ────────────────────────────────────────────────────

def plot_waveform(y: np.ndarray, sr: int, title: str = "Audio Waveform"):
    """
    Return a Matplotlib figure showing the audio waveform with a styled look.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import librosa

    duration = librosa.get_duration(y=y, sr=sr)
    times = np.linspace(0, duration, num=len(y))

    fig, ax = plt.subplots(figsize=(10, 3))
    fig.patch.set_facecolor("#0F0F1A")
    ax.set_facecolor("#0F0F1A")

    # Gradient-like effect via alpha
    ax.fill_between(times, y, alpha=0.35, color="#7C3AED")
    ax.plot(times, y, color="#A78BFA", linewidth=0.6, alpha=0.9)

    ax.set_xlabel("Time (s)", color="#CBD5E1", fontsize=9)
    ax.set_ylabel("Amplitude", color="#CBD5E1", fontsize=9)
    ax.set_title(title, color="#E2E8F0", fontsize=11, pad=10)
    ax.tick_params(colors="#94A3B8", labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#334155")
    ax.set_xlim(0, duration)

    plt.tight_layout()
    return fig


def plot_spectrogram(y: np.ndarray, sr: int):
    """Return a Mel-spectrogram Matplotlib figure."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import librosa
    import librosa.display

    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    S_dB = librosa.power_to_db(S, ref=np.max)

    fig, ax = plt.subplots(figsize=(10, 3))
    fig.patch.set_facecolor("#0F0F1A")
    ax.set_facecolor("#0F0F1A")

    img = librosa.display.specshow(
        S_dB, sr=sr, x_axis="time", y_axis="mel",
        fmax=8000, ax=ax, cmap="magma"
    )
    cbar = fig.colorbar(img, ax=ax, format="%+2.0f dB")
    cbar.ax.yaxis.set_tick_params(color="#94A3B8", labelsize=7)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#94A3B8")

    ax.set_title("Mel Spectrogram", color="#E2E8F0", fontsize=11, pad=10)
    ax.set_xlabel("Time (s)", color="#CBD5E1", fontsize=9)
    ax.set_ylabel("Hz", color="#CBD5E1", fontsize=9)
    ax.tick_params(colors="#94A3B8", labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#334155")

    plt.tight_layout()
    return fig


# ── Energy Metrics ────────────────────────────────────────────────────────────

def compute_rms_energy(y: np.ndarray) -> float:
    """Return mean RMS energy (normalised 0–1 approximation)."""
    import librosa
    rms = librosa.feature.rms(y=y)[0]
    mean_rms = float(np.mean(rms))
    # Typical speech RMS ~ 0.02-0.15 ; clamp to [0,1]
    return min(1.0, mean_rms * 6.0)


def compute_zcr(y: np.ndarray) -> float:
    """Return mean zero-crossing rate (indicator of noisiness/clarity)."""
    import librosa
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    return float(np.mean(zcr))


# ── Pause Analysis ────────────────────────────────────────────────────────────

def detect_pauses(y: np.ndarray, sr: int) -> Dict:
    """
    Detect silent segments and return pause statistics.

    Returns dict with:
        pause_ratio      : fraction of total audio that is silence
        pause_count      : number of distinct pauses
        mean_pause_dur   : mean pause duration in seconds
        max_pause_dur    : longest pause in seconds
        pause_intervals  : list of (start_s, end_s) tuples
    """
    import librosa

    # Non-silent intervals
    non_silent = librosa.effects.split(y, top_db=SILENCE_TOP_DB)

    total_samples  = len(y)
    non_silent_samples = sum((e - s) for s, e in non_silent)
    silent_samples = total_samples - non_silent_samples

    pause_ratio = float(silent_samples / total_samples) if total_samples else 0.0

    # Build pause intervals (gaps between non-silent regions)
    pauses: List[Tuple[float, float]] = []
    for i in range(len(non_silent) - 1):
        gap_start = non_silent[i][1] / sr
        gap_end   = non_silent[i + 1][0] / sr
        gap_dur   = gap_end - gap_start
        if gap_dur >= MIN_PAUSE_DURATION:
            pauses.append((round(gap_start, 3), round(gap_end, 3)))

    pause_durations = [(e - s) for s, e in pauses]
    return {
        "pause_ratio":    round(pause_ratio, 4),
        "pause_count":    len(pauses),
        "mean_pause_dur": round(float(np.mean(pause_durations)), 3) if pause_durations else 0.0,
        "max_pause_dur":  round(float(np.max(pause_durations)), 3)  if pause_durations else 0.0,
        "pause_intervals": pauses,
    }


# ── Filler Words ──────────────────────────────────────────────────────────────

def count_filler_words(transcript: str) -> Dict[str, int]:
    """
    Count occurrences of each filler word/phrase in the transcript.
    Returns a dict  {filler: count}  (only entries with count > 0).
    """
    text  = transcript.lower()
    counts: Dict[str, int] = {}
    for filler in FILLER_WORDS:
        # word-boundary match for single words; phrase match for multi-word
        if " " in filler:
            c = text.count(filler)
        else:
            c = len(re.findall(rf"\b{re.escape(filler)}\b", text))
        if c > 0:
            counts[filler] = c
    return counts


def total_filler_count(filler_dict: Dict[str, int]) -> int:
    return sum(filler_dict.values())


# ── Speaking Rate ─────────────────────────────────────────────────────────────

def compute_speaking_rate(transcript: str, duration_s: float) -> float:
    """
    Words per minute.  Returns 0 if duration is zero/unknown.
    """
    if duration_s <= 0:
        return 0.0
    word_count = len(transcript.split())
    return round((word_count / duration_s) * 60, 1)


# ── Pitch Analysis ────────────────────────────────────────────────────────────

def compute_pitch_stats(y: np.ndarray, sr: int) -> Dict[str, float]:
    """
    Estimate fundamental frequency (F0) using YIN/pyin and return stats.
    """
    import librosa
    try:
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y, fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"), sr=sr
        )
        voiced_f0 = f0[voiced_flag] if voiced_flag is not None else np.array([])
        if len(voiced_f0) == 0:
            return {"mean_hz": 0.0, "std_hz": 0.0, "voiced_ratio": 0.0}
        voiced_ratio = float(np.sum(voiced_flag) / len(voiced_flag))
        return {
            "mean_hz":    round(float(np.nanmean(voiced_f0)), 2),
            "std_hz":     round(float(np.nanstd(voiced_f0)),  2),
            "voiced_ratio": round(voiced_ratio, 4),
        }
    except Exception:
        return {"mean_hz": 0.0, "std_hz": 0.0, "voiced_ratio": 0.0}


# ── Master analysis function ──────────────────────────────────────────────────

def analyse_audio(audio_path: str | Path, transcript: str, duration_s: float) -> Dict:
    """
    Run all audio analyses and return a consolidated result dict.
    """
    y, sr = load_audio(audio_path)

    rms_energy   = compute_rms_energy(y)
    zcr          = compute_zcr(y)
    pause_stats  = detect_pauses(y, sr)
    filler_dict  = count_filler_words(transcript)
    speaking_rate = compute_speaking_rate(transcript, duration_s)
    pitch_stats  = compute_pitch_stats(y, sr)

    return {
        "y": y,
        "sr": sr,
        "rms_energy":    rms_energy,
        "zcr":           zcr,
        "pause_stats":   pause_stats,
        "filler_words":  filler_dict,
        "total_fillers": total_filler_count(filler_dict),
        "speaking_rate": speaking_rate,
        "pitch":         pitch_stats,
        "word_count":    len(transcript.split()),
    }
