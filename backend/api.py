# ─────────────────────────────────────────────────────────────────────────────
# backend/api.py  –  FastAPI REST backend for VBCUA
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import os
import sys
import uuid
import json
import shutil
import traceback
from pathlib import Path
from typing import Optional

# Add backend to path so we can import existing modules
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from config import CONCEPTS, TEMP_DIR, ALLOWED_EXTENSIONS

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="VBCUA API",
    description="Voice-Based Concept Understanding Analyser – Python FastAPI Backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure temp/sessions dirs
SESSIONS_DIR = Path(TEMP_DIR) / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


# ── Helper ────────────────────────────────────────────────────────────────────
def _numpy_safe(obj):
    """Recursively convert numpy types to native Python for JSON serialisation."""
    if isinstance(obj, dict):
        return {k: _numpy_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_numpy_safe(i) for i in obj]
    elif isinstance(obj, tuple):
        return tuple(_numpy_safe(i) for i in obj)
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    return obj


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/concepts")
async def get_concepts():
    """Return all available concept names and their reference descriptions."""
    return {
        "concepts": [
            {"name": name, "preview": desc[:160] + "…"}
            for name, desc in CONCEPTS.items()
        ]
    }


@app.get("/sample.wav")
async def get_sample_wav():
    """Serve the sample audio file directly from frontend/."""
    sample_path = Path(__file__).parent.parent / "frontend" / "sample.wav"
    if not sample_path.exists():
        raise HTTPException(404, "Sample file not found")
    return FileResponse(
        path=str(sample_path),
        filename="sample_audio.wav",
        media_type="audio/wav"
    )


@app.post("/api/analyse")
async def analyse(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    concept: str = Form(...),
    options: str = Form(default="{}"),
):
    """
    Full analysis pipeline:
      1. Save uploaded audio
      2. Whisper transcription
      3. Semantic similarity (SBERT)
      4. Audio feature extraction (Librosa)
      5. Scoring
      6. PDF generation
    Returns JSON with all results + session_id for PDF download.
    """
    # Validate concept
    if concept not in CONCEPTS:
        raise HTTPException(400, f"Unknown concept '{concept}'. "
                            f"Valid: {list(CONCEPTS.keys())}")

    # Validate file extension
    ext = Path(audio.filename).suffix.lower().lstrip(".")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type '.{ext}'.")

    opts = json.loads(options) if options else {}

    # ── Save audio to session dir ─────────────────────────────────────────────
    session_id  = str(uuid.uuid4())
    session_dir = SESSIONS_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    audio_path = session_dir / f"audio.{ext}"
    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    try:
        reference = CONCEPTS[concept]

        # ── Step 1: Transcription ─────────────────────────────────────────────
        from modules.transcriber import transcribe_audio
        trans_result = transcribe_audio(audio_path)
        transcript   = trans_result["text"].strip()
        duration     = trans_result["duration"]
        language     = trans_result["language"]

        if not transcript:
            return JSONResponse(
                {"error": "Empty transcript. Check audio quality or try again."},
                status_code=422,
            )

        # ── Step 2: Audio Analysis ────────────────────────────────────────────
        from modules.audio_analyser import analyse_audio, plot_waveform, plot_spectrogram
        audio_result    = analyse_audio(audio_path, transcript, duration)
        y, sr           = audio_result.pop("y"), audio_result.pop("sr")

        # ── Step 3: Semantic Analysis ─────────────────────────────────────────
        from modules.semantic_analyser import (
            compute_similarity, identify_gaps, sentence_level_similarity
        )
        semantic_sim  = compute_similarity(transcript, reference)
        gap_result    = identify_gaps(transcript, reference)
        sent_sims     = sentence_level_similarity(transcript, reference)

        # ── Step 4: Scoring ───────────────────────────────────────────────────
        from modules.scorer import compute_final_score
        ps = audio_result["pause_stats"]
        score_result = compute_final_score(
            semantic_similarity = semantic_sim,
            rms_energy          = audio_result["rms_energy"],
            pause_ratio         = ps["pause_ratio"],
            total_fillers       = audio_result["total_fillers"],
            word_count          = audio_result["word_count"],
            speaking_rate       = audio_result["speaking_rate"],
        )

        # ── Step 5: Save waveform PNG for report + frontend ───────────────────
        import io, base64
        waveform_fig    = plot_waveform(y, sr, f"Waveform – {concept}")
        spectrogram_fig = plot_spectrogram(y, sr)

        def _fig_to_b64(fig):
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=120,
                        bbox_inches="tight", facecolor="#0F0F1A")
            buf.seek(0)
            import matplotlib.pyplot as plt
            plt.close(fig)
            return base64.b64encode(buf.read()).decode()

        waveform_b64    = _fig_to_b64(waveform_fig)
        spectrogram_b64 = _fig_to_b64(spectrogram_fig)

        # ── Step 6: Generate PDF ──────────────────────────────────────────────
        from modules.report_generator import generate_pdf_report
        waveform_fig2    = plot_waveform(y, sr, f"Waveform – {concept}")
        spectrogram_fig2 = plot_spectrogram(y, sr)

        pdf_bytes = generate_pdf_report(
            concept         = concept,
            transcript      = transcript,
            score_result    = score_result,
            audio_result    = {**audio_result, "y": y, "sr": sr},
            waveform_fig    = waveform_fig2,
            spectrogram_fig = spectrogram_fig2,
            gap_analysis    = gap_result,
        )
        pdf_path = session_dir / "report.pdf"
        pdf_path.write_bytes(pdf_bytes)

        # Waveform data points for JS chart (downsample to 800 pts)
        step = max(1, len(y) // 800)
        waveform_points = y[::step].tolist()

        # ── Build response ────────────────────────────────────────────────────
        payload = {
            "session_id": session_id,
            "concept":    concept,
            "language":   language,
            "duration":   round(float(duration), 2),

            # Transcript
            "transcript": transcript,
            "word_count": audio_result["word_count"],
            "segments":   [
                {"start": round(s.get("start", 0), 2),
                 "end":   round(s.get("end",   0), 2),
                 "text":  s.get("text", "").strip()}
                for s in trans_result.get("segments", [])
            ],

            # Scores
            "scores": {
                "final":    score_result["final_score"],
                "percent":  score_result["percentage"],
                "label":    score_result["label"],
                "emoji":    score_result["emoji"],
                "colour":   score_result["colour"],
                "semantic": score_result["semantic_score"],
                "fluency":  score_result["fluency_score"],
            },

            "feedback": score_result["feedback"],

            # Audio metrics
            "audio": {
                "rms_energy":    audio_result["rms_energy"],
                "zcr":           audio_result["zcr"],
                "speaking_rate": audio_result["speaking_rate"],
                "total_fillers": audio_result["total_fillers"],
                "filler_words":  audio_result["filler_words"],
                "pause_stats":   audio_result["pause_stats"],
                "pitch":         audio_result["pitch"],
            },

            # Semantic details
            "semantic": {
                "similarity":      semantic_sim,
                "gap_analysis":    gap_result,
                "sentence_sims":   [
                    {"text": s[:120], "score": round(sc, 4)}
                    for s, sc in sent_sims
                ],
            },

            # Visuals (base64 PNG)
            "visuals": {
                "waveform_b64":    waveform_b64,
                "spectrogram_b64": spectrogram_b64,
                "waveform_points": waveform_points,
            },

            # PDF available
            "pdf_available": True,
            "pdf_url":       f"/api/report/{session_id}",
        }

        return JSONResponse(_numpy_safe(payload))

    except Exception as exc:
        traceback.print_exc()
        # Cleanup on error
        shutil.rmtree(session_dir, ignore_errors=True)
        raise HTTPException(500, f"Analysis failed: {exc}")


@app.get("/api/report/{session_id}")
async def download_report(session_id: str):
    """Download the generated PDF report for a session."""
    pdf_path = SESSIONS_DIR / session_id / "report.pdf"
    if not pdf_path.exists():
        raise HTTPException(404, "Report not found. Run analysis first.")
    return FileResponse(
        path     = str(pdf_path),
        filename = "VBCUA_Analysis_Report.pdf",
        media_type = "application/pdf",
    )


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
