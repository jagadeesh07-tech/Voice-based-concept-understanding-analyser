# ─────────────────────────────────────────────────────────────────────────────
# modules/scorer.py  –  Weighted scoring & qualitative feedback generation
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from typing import Dict

from config import (
    SCORE_MODERATE,
    SCORE_STRONG,
    WEIGHT_FLUENCY,
    WEIGHT_SEMANTIC,
)

# ── Fluency sub-score ─────────────────────────────────────────────────────────

def compute_fluency_score(
    rms_energy: float,
    pause_ratio: float,
    total_fillers: int,
    word_count: int,
    speaking_rate: float,
) -> float:
    """
    Combine audio features into a fluency score in [0, 1].

    Sub-components:
      energy_score   – higher RMS → better vocal presence
      pause_score    – too many pauses hurt; some pauses are natural
      filler_score   – fewer fillers per 100 words → better
      rate_score     – ideal WPM band 110-160
    """
    # 1. Energy (0-1)
    energy_score = min(1.0, rms_energy)

    # 2. Pause ratio penalty (ideal ≈ 15-25 %)
    if pause_ratio <= 0.15:
        pause_score = 0.75  # too fast / no breath
    elif pause_ratio <= 0.30:
        pause_score = 1.0
    elif pause_ratio <= 0.50:
        pause_score = 0.70
    else:
        pause_score = max(0.0, 1.0 - (pause_ratio - 0.30) * 2)

    # 3. Filler density (fillers per 100 words)
    if word_count > 0:
        filler_density = (total_fillers / word_count) * 100
    else:
        filler_density = 0.0

    if filler_density == 0:
        filler_score = 1.0
    elif filler_density <= 2:
        filler_score = 0.9
    elif filler_density <= 5:
        filler_score = 0.7
    elif filler_density <= 10:
        filler_score = 0.5
    else:
        filler_score = max(0.0, 0.4 - (filler_density - 10) * 0.02)

    # 4. Speaking rate (WPM)
    if speaking_rate <= 0:
        rate_score = 0.5   # unknown
    elif 110 <= speaking_rate <= 160:
        rate_score = 1.0
    elif 80 <= speaking_rate < 110 or 160 < speaking_rate <= 200:
        rate_score = 0.75
    elif 50 <= speaking_rate < 80 or 200 < speaking_rate <= 250:
        rate_score = 0.5
    else:
        rate_score = 0.3

    fluency = (
        0.25 * energy_score +
        0.30 * pause_score  +
        0.25 * filler_score +
        0.20 * rate_score
    )
    return round(min(1.0, max(0.0, fluency)), 4)


# ── Final composite score ─────────────────────────────────────────────────────

def compute_final_score(
    semantic_similarity: float,
    rms_energy: float,
    pause_ratio: float,
    total_fillers: int,
    word_count: int,
    speaking_rate: float,
) -> Dict:
    """
    Compute the final weighted score and return a full result dict.

    Returns
    -------
    dict with:
        semantic_score  : float 0-1
        fluency_score   : float 0-1
        final_score     : float 0-1
        percentage      : int 0-100
        label           : "Strong" | "Moderate" | "Poor"
        emoji           : str
        colour          : hex colour string
        feedback        : str – qualitative feedback paragraph
        breakdown       : dict of sub-scores
    """
    fluency_score = compute_fluency_score(
        rms_energy, pause_ratio, total_fillers, word_count, speaking_rate
    )

    final = (
        WEIGHT_SEMANTIC * semantic_similarity +
        WEIGHT_FLUENCY  * fluency_score
    )
    final = round(min(1.0, max(0.0, final)), 4)
    percentage = int(round(final * 100))

    # Label
    if final >= SCORE_STRONG:
        label  = "Strong Understanding"
        emoji  = "🟢"
        colour = "#10B981"
        feedback = _feedback_strong(semantic_similarity, fluency_score, total_fillers, speaking_rate)
    elif final >= SCORE_MODERATE:
        label  = "Moderate Understanding"
        emoji  = "🟡"
        colour = "#F59E0B"
        feedback = _feedback_moderate(semantic_similarity, fluency_score, total_fillers, speaking_rate)
    else:
        label  = "Poor Understanding"
        emoji  = "🔴"
        colour = "#EF4444"
        feedback = _feedback_poor(semantic_similarity, fluency_score, total_fillers, speaking_rate)

    return {
        "semantic_score": round(semantic_similarity, 4),
        "fluency_score":  round(fluency_score, 4),
        "final_score":    final,
        "percentage":     percentage,
        "label":          label,
        "emoji":          emoji,
        "colour":         colour,
        "feedback":       feedback,
        "breakdown": {
            "energy_contribution":  round(rms_energy, 4),
            "pause_ratio":          round(pause_ratio, 4),
            "filler_count":         total_fillers,
            "speaking_rate_wpm":    speaking_rate,
            "semantic_weight":      WEIGHT_SEMANTIC,
            "fluency_weight":       WEIGHT_FLUENCY,
        },
    }


# ── Qualitative feedback generators ──────────────────────────────────────────

def _feedback_strong(sem: float, flu: float, fillers: int, rate: float) -> str:
    lines = [
        "Excellent work! Your explanation demonstrates a strong command of the concept.",
    ]
    if sem >= 0.80:
        lines.append("Your explanation aligns closely with the reference definition — you've captured the core ideas with precision.")
    if flu >= 0.75:
        lines.append("Your delivery was confident and clear, with good speaking pace and minimal hesitation.")
    if fillers == 0:
        lines.append("Notably, your response contained no filler words, reflecting high communication fluency.")
    if 110 <= rate <= 160:
        lines.append(f"Your speaking rate of {rate:.0f} WPM is within the ideal range for comprehension.")
    lines.append("Keep practising to maintain this level of expertise!")
    return " ".join(lines)


def _feedback_moderate(sem: float, flu: float, fillers: int, rate: float) -> str:
    lines = [
        "Good effort! Your explanation covers some of the key ideas but there is room for improvement.",
    ]
    if sem < 0.65:
        lines.append("Focus on deepening your understanding of the core concepts and include more specific technical terminology.")
    if flu < 0.65:
        lines.append("Work on your delivery — try to reduce hesitation pauses and maintain a steadier speaking pace.")
    if fillers > 3:
        lines.append(f"You used {fillers} filler word(s). Practising deliberate pauses instead of fillers will improve your fluency.")
    if rate < 100:
        lines.append("Your speaking pace was slightly slow — aim for 110–160 WPM for a more natural flow.")
    elif rate > 180:
        lines.append("Your speaking pace was a little fast — slowing down will help your audience follow along.")
    lines.append("Review the reference concept and practise delivering it confidently to improve your score.")
    return " ".join(lines)


def _feedback_poor(sem: float, flu: float, fillers: int, rate: float) -> str:
    lines = [
        "Your explanation needs significant improvement. Don't be discouraged — use this as a learning opportunity!",
    ]
    if sem < 0.45:
        lines.append("The content of your explanation diverged considerably from the expected definition. Study the concept thoroughly before your next attempt.")
    if flu < 0.45:
        lines.append("Your speech fluency was low. Work on speaking more smoothly and confidently without long pauses or excessive fillers.")
    if fillers > 6:
        lines.append(f"You used {fillers} filler word(s), which disrupts clarity. Practise mindful speaking and deliberate pauses.")
    lines.append("Consider reviewing study materials, recording practice sessions, and seeking feedback from peers or educators.")
    return " ".join(lines)
