# ─────────────────────────────────────────────────────────────────────────────
# modules/transcriber.py  –  OpenAI Whisper speech-to-text
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path
from typing import Optional

import streamlit as st

from config import WHISPER_MODEL

# Lazy-load whisper to avoid slow import at startup
_whisper_model = None


def _get_model():
    """Load (and cache) the Whisper model."""
    global _whisper_model
    if _whisper_model is None:
        import whisper
        _whisper_model = whisper.load_model(WHISPER_MODEL)
    return _whisper_model


def transcribe_audio(audio_path: str | Path, progress_callback=None) -> dict:
    """
    Transcribe an audio file using OpenAI Whisper.

    Parameters
    ----------
    audio_path : str | Path
        Path to the audio file (wav, mp3, m4a, etc.)
    progress_callback : callable, optional
        Called with a float 0-1 to report progress.

    Returns
    -------
    dict with keys:
        text       : full transcript string
        language   : detected language code
        duration   : audio duration in seconds
        segments   : list of timed segment dicts
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if progress_callback:
        progress_callback(0.1)

    model = _get_model()

    if progress_callback:
        progress_callback(0.3)

    import librosa
    # Load audio natively to bypass command-line ffmpeg dependency
    audio_data, sr = librosa.load(str(audio_path), sr=16_000, mono=True)
    duration = float(len(audio_data)) / sr

    if progress_callback:
        progress_callback(0.6)

    result = model.transcribe(
        audio_data,
        verbose=False,
        word_timestamps=False,
    )

    if progress_callback:
        progress_callback(1.0)

    return {
        "text":     result.get("text", "").strip(),
        "language": result.get("language", "unknown"),
        "duration": duration,
        "segments": result.get("segments", []),
    }


def save_uploaded_audio(uploaded_file, dest_dir: str | Path) -> Path:
    """
    Persist a Streamlit UploadedFile to disk and return the path.
    """
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(uploaded_file.name).suffix or ".wav"
    dest_path = dest_dir / f"uploaded_audio{suffix}"

    with open(dest_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return dest_path
