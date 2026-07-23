# ─────────────────────────────────────────────────────────────────────────────
# modules/report_generator.py  –  PDF report using ReportLab
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import io
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


# ── Colour helpers ────────────────────────────────────────────────────────────

def _hex_to_rgb(hex_color: str):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


# ── Main export function ──────────────────────────────────────────────────────

def generate_pdf_report(
    concept: str,
    transcript: str,
    score_result: Dict,
    audio_result: Dict,
    waveform_fig=None,
    spectrogram_fig=None,
    gap_analysis: Optional[Dict[str, bool]] = None,
) -> bytes:
    """
    Build a styled PDF report and return the raw bytes.

    Parameters
    ----------
    concept         : selected concept name
    transcript      : Whisper transcript
    score_result    : output of scorer.compute_final_score()
    audio_result    : output of audio_analyser.analyse_audio()
    waveform_fig    : optional Matplotlib Figure for waveform
    spectrogram_fig : optional Matplotlib Figure for spectrogram
    gap_analysis    : optional dict {keyword: covered_bool}

    Returns
    -------
    bytes – the PDF file content
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, Image as RLImage, PageBreak
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.pdfgen import canvas

    # Colour constants
    C_PRIMARY  = colors.HexColor("#7C3AED")
    C_CYAN     = colors.HexColor("#06B6D4")
    C_SUCCESS  = colors.HexColor("#10B981")
    C_WARNING  = colors.HexColor("#F59E0B")
    C_DANGER   = colors.HexColor("#EF4444")
    C_DARK     = colors.HexColor("#0F172A")
    C_CARD     = colors.HexColor("#1E293B")
    C_TEXT     = colors.HexColor("#E2E8F0")
    C_MUTED    = colors.HexColor("#94A3B8")
    C_WHITE    = colors.white
    C_SCORE    = colors.HexColor(score_result.get("colour", "#7C3AED"))

    PAGE_W, PAGE_H = A4
    buffer = io.BytesIO()

    # ── Document setup ─────────────────────────────────────────────────────────
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=25*mm, bottomMargin=20*mm,
        title="VBCUA Analysis Report",
        author="Voice-Based Concept Understanding Analyser",
    )

    styles = getSampleStyleSheet()

    def _style(name, **kwargs):
        base = ParagraphStyle(name, **kwargs)
        return base

    H1 = _style("H1", fontSize=22, textColor=C_WHITE, fontName="Helvetica-Bold",
                 spaceAfter=6, alignment=TA_CENTER)
    H2 = _style("H2", fontSize=14, textColor=C_CYAN,  fontName="Helvetica-Bold",
                 spaceAfter=4, spaceBefore=10)
    H3 = _style("H3", fontSize=11, textColor=C_TEXT,  fontName="Helvetica-Bold",
                 spaceAfter=3)
    BODY = _style("BODY", fontSize=9, textColor=C_TEXT, fontName="Helvetica",
                  leading=14, spaceAfter=4, alignment=TA_JUSTIFY)
    MUTED = _style("MUTED", fontSize=8, textColor=C_MUTED, fontName="Helvetica",
                   leading=12, spaceAfter=2)
    SCORE_LABEL = _style("SCORE_LABEL", fontSize=28, textColor=C_SCORE,
                         fontName="Helvetica-Bold", alignment=TA_CENTER)

    story = []

    # ── Header card ────────────────────────────────────────────────────────────
    header_data = [[
        Paragraph(f"🎙️ VBCUA Analysis Report", H1),
    ]]
    header_table = Table(header_data, colWidths=[PAGE_W - 40*mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_DARK),
        ("ROUNDEDCORNERS", [8]),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6*mm))

    # Meta info
    now = datetime.now().strftime("%d %B %Y, %H:%M")
    meta_data = [
        ["Concept", concept],
        ["Generated",  now],
        ["Language",   "English (auto-detected)"],
        ["Word Count", str(audio_result.get("word_count", 0))],
        ["Duration",   f"{audio_result.get('pause_stats', {}).get('pause_ratio', 0):.0%} silence, "
                       f"{audio_result.get('speaking_rate', 0):.0f} WPM"],
    ]
    meta_table = Table(meta_data, colWidths=[50*mm, (PAGE_W - 40*mm - 50*mm)])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (0, -1), C_CARD),
        ("BACKGROUND",   (1, 0), (1, -1), C_DARK),
        ("TEXTCOLOR",    (0, 0), (0, -1), C_CYAN),
        ("TEXTCOLOR",    (1, 0), (1, -1), C_TEXT),
        ("FONTNAME",     (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",     (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=C_PRIMARY, spaceAfter=6))

    # ── Overall Score Banner ───────────────────────────────────────────────────
    story.append(Paragraph("OVERALL SCORE", H2))
    pct = score_result.get("percentage", 0)
    lbl = score_result.get("label", "Unknown")
    score_data = [[
        Paragraph(f"{pct}%", SCORE_LABEL),
        Paragraph(
            f"<b>{lbl}</b><br/><font size='8' color='#94A3B8'>"
            f"Semantic: {score_result['semantic_score']*100:.1f}% &nbsp;|&nbsp; "
            f"Fluency: {score_result['fluency_score']*100:.1f}%</font>",
            _style("SC2", fontSize=13, textColor=C_TEXT,
                   fontName="Helvetica-Bold", leading=20, alignment=TA_LEFT)
        ),
    ]]
    score_table = Table(score_data, colWidths=[50*mm, (PAGE_W - 40*mm - 50*mm)])
    score_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), C_CARD),
        ("TOPPADDING",   (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 12),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 4*mm))

    # Feedback paragraph
    story.append(Paragraph("AI Feedback", H3))
    story.append(Paragraph(score_result.get("feedback", ""), BODY))
    story.append(Spacer(1, 5*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#334155"), spaceAfter=5))

    # ── Transcript ─────────────────────────────────────────────────────────────
    story.append(Paragraph("📝 Transcript", H2))
    transcript_safe = transcript.replace("<", "&lt;").replace(">", "&gt;")
    story.append(Paragraph(transcript_safe if transcript_safe else "(No transcript available)", BODY))
    story.append(Spacer(1, 5*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#334155"), spaceAfter=5))

    # ── Semantic Analysis ──────────────────────────────────────────────────────
    story.append(Paragraph("🧠 Semantic Analysis", H2))

    sem_score = score_result.get("semantic_score", 0)
    sem_rows = [
        ["Metric", "Value"],
        ["Semantic Similarity Score", f"{sem_score:.4f}  ({sem_score*100:.1f}%)"],
        ["Weight in Final Score", f"{score_result['breakdown']['semantic_weight']*100:.0f}%"],
    ]
    if gap_analysis:
        covered   = [k for k, v in gap_analysis.items() if v]
        uncovered = [k for k, v in gap_analysis.items() if not v]
        sem_rows.append(["Keywords Covered",   ", ".join(covered)   or "None"])
        sem_rows.append(["Keywords Missing",   ", ".join(uncovered) or "None"])

    sem_table = Table(sem_rows, colWidths=[70*mm, (PAGE_W - 40*mm - 70*mm)])
    sem_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  C_PRIMARY),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  C_WHITE),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("BACKGROUND",   (0, 1), (-1, -1), C_DARK),
        ("TEXTCOLOR",    (0, 1), (-1, -1), C_TEXT),
        ("FONTNAME",     (0, 1), (0,  -1), "Helvetica-Bold"),
        ("FONTNAME",     (1, 1), (1,  -1), "Helvetica"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
    ]))
    story.append(sem_table)
    story.append(Spacer(1, 5*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#334155"), spaceAfter=5))

    # ── Fluency Metrics ────────────────────────────────────────────────────────
    story.append(Paragraph("🎵 Fluency & Speech Metrics", H2))

    bd = score_result.get("breakdown", {})
    ps = audio_result.get("pause_stats", {})
    pit = audio_result.get("pitch", {})

    flu_rows = [
        ["Metric", "Value", "Ideal Range"],
        ["Fluency Score",         f"{score_result.get('fluency_score',0)*100:.1f}%",  "≥ 75% = Good"],
        ["Speaking Rate",         f"{bd.get('speaking_rate_wpm',0):.0f} WPM",         "110–160 WPM"],
        ["Total Filler Words",    str(bd.get('filler_count', 0)),                      "< 3 per response"],
        ["RMS Energy Level",      f"{bd.get('energy_contribution',0):.4f}",            "Higher = louder"],
        ["Pause Ratio",           f"{bd.get('pause_ratio',0)*100:.1f}%",               "15–30% = natural"],
        ["Number of Pauses",      str(ps.get('pause_count', 0)),                       "—"],
        ["Mean Pause Duration",   f"{ps.get('mean_pause_dur', 0):.2f}s",               "< 0.8s"],
        ["Longest Pause",         f"{ps.get('max_pause_dur', 0):.2f}s",                "< 2.0s"],
        ["Mean Pitch (F0)",       f"{pit.get('mean_hz', 0):.1f} Hz",                  "80–300 Hz"],
        ["Pitch Variability",     f"{pit.get('std_hz', 0):.1f} Hz",                   "Higher = expressive"],
        ["Voiced Ratio",          f"{pit.get('voiced_ratio', 0)*100:.1f}%",            "—"],
    ]
    flu_table = Table(flu_rows, colWidths=[70*mm, 45*mm, (PAGE_W - 40*mm - 115*mm)])
    flu_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  C_CYAN),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  C_DARK),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("BACKGROUND",   (0, 1), (-1, -1), C_DARK),
        ("ROWBACKGROUNDS",(0, 1),(-1, -1), [C_DARK, C_CARD]),
        ("TEXTCOLOR",    (0, 1), (-1, -1), C_TEXT),
        ("FONTNAME",     (0, 1), (0,  -1), "Helvetica-Bold"),
        ("FONTNAME",     (1, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
    ]))
    story.append(flu_table)
    story.append(Spacer(1, 4*mm))

    # Filler word breakdown
    filler_words = audio_result.get("filler_words", {})
    if filler_words:
        story.append(Paragraph("Filler Word Breakdown", H3))
        fw_rows = [["Word", "Count"]] + [[k, str(v)] for k, v in sorted(filler_words.items(), key=lambda x: -x[1])]
        fw_table = Table(fw_rows, colWidths=[60*mm, 40*mm])
        fw_table.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0),  C_WARNING),
            ("TEXTCOLOR",    (0, 0), (-1, 0),  C_DARK),
            ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("BACKGROUND",   (0, 1), (-1, -1), C_DARK),
            ("TEXTCOLOR",    (0, 1), (-1, -1), C_TEXT),
            ("FONTSIZE",     (0, 0), (-1, -1), 9),
            ("TOPPADDING",   (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
            ("LEFTPADDING",  (0, 0), (-1, -1), 8),
            ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
        ]))
        story.append(fw_table)

    story.append(Spacer(1, 5*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#334155"), spaceAfter=5))

    # ── Waveform image ─────────────────────────────────────────────────────────
    if waveform_fig is not None:
        story.append(Paragraph("📊 Audio Waveform", H2))
        wav_buf = io.BytesIO()
        waveform_fig.savefig(wav_buf, format="png", dpi=130,
                             bbox_inches="tight", facecolor="#0F0F1A")
        wav_buf.seek(0)
        img = RLImage(wav_buf, width=PAGE_W - 45*mm, height=60*mm)
        story.append(img)
        story.append(Spacer(1, 3*mm))

    if spectrogram_fig is not None:
        story.append(Paragraph("🎛️ Mel Spectrogram", H2))
        sp_buf = io.BytesIO()
        spectrogram_fig.savefig(sp_buf, format="png", dpi=130,
                                bbox_inches="tight", facecolor="#0F0F1A")
        sp_buf.seek(0)
        img2 = RLImage(sp_buf, width=PAGE_W - 45*mm, height=60*mm)
        story.append(img2)
        story.append(Spacer(1, 3*mm))

    # ── Footer ─────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=C_PRIMARY, spaceAfter=4))
    story.append(Paragraph(
        f"Generated by VBCUA v1.0.0 &nbsp;|&nbsp; {now} &nbsp;|&nbsp; "
        "Voice-Based Concept Understanding Analyser",
        _style("FOOT", fontSize=7, textColor=C_MUTED, fontName="Helvetica",
               alignment=TA_CENTER)
    ))

    doc.build(story)
    return buffer.getvalue()
