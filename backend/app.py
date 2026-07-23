# ─────────────────────────────────────────────────────────────────────────────
# app.py  –  VBCUA Main Streamlit Application
# Voice-Based Concept Understanding Analyser
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import os
import time
from pathlib import Path

import streamlit as st

from config import (
    APP_ICON, APP_TITLE, APP_VERSION,
    ALLOWED_EXTENSIONS, CONCEPTS, TEMP_DIR,
)

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": f"**{APP_TITLE}** v{APP_VERSION}\n\n"
                 "AI-powered speech analysis for conceptual understanding evaluation."
    },
)


# ── CSS loader ────────────────────────────────────────────────────────────────
def _load_css():
    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


_load_css()

# ── Ensure temp dir ───────────────────────────────────────────────────────────
Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar Navigation
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 1rem 0 1.5rem;">
          <div style="font-size:2.8rem; margin-bottom:0.3rem;">🎙️</div>
          <div style="font-size:1.1rem; font-weight:800;
                      background:linear-gradient(135deg,#A78BFA,#67E8F9);
                      -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            VBCUA
          </div>
          <div style="font-size:0.7rem; color:#64748B; letter-spacing:0.1em; margin-top:2px;">
            v{version}
          </div>
        </div>
        """.format(version=APP_VERSION),
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        ["🏠 Home", "🔬 Analyse", "📋 About"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:0.75rem; color:#475569; line-height:1.6;">
          <b style="color:#7C3AED;">AI Models Used</b><br/>
          🤖 OpenAI Whisper (ASR)<br/>
          🧠 Sentence-BERT (NLP)<br/>
          🎵 Librosa (Audio DSP)<br/>
          📄 ReportLab (PDF)
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Page: Home
# ─────────────────────────────────────────────────────────────────────────────
if page == "🏠 Home":
    st.markdown(
        """
        <div class="vbcua-hero">
          <h1>🎙️ Voice-Based Concept Understanding Analyser</h1>
          <p style="color:#94A3B8; font-size:1rem; max-width:650px; margin:0 auto 1.5rem;">
            An AI-powered platform that evaluates how well you understand and explain
            conceptual topics through spoken communication.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Feature cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="metric-card" style="text-align:center; padding:1.8rem 1rem;">
              <div style="font-size:2.2rem; margin-bottom:0.8rem;">🧠</div>
              <div style="font-weight:700; color:#A78BFA; margin-bottom:0.5rem; font-size:1rem;">
                Semantic Analysis
              </div>
              <div style="color:#94A3B8; font-size:0.83rem; line-height:1.5;">
                Sentence-BERT compares your explanation to the reference definition
                and identifies conceptual gaps with precision.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="metric-card" style="text-align:center; padding:1.8rem 1rem;">
              <div style="font-size:2.2rem; margin-bottom:0.8rem;">🎵</div>
              <div style="font-weight:700; color:#67E8F9; margin-bottom:0.5rem; font-size:1rem;">
                Fluency Metrics
              </div>
              <div style="color:#94A3B8; font-size:0.83rem; line-height:1.5;">
                Librosa-powered analysis of filler words, pause ratio, RMS energy,
                pitch variability, and speaking rate.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="metric-card" style="text-align:center; padding:1.8rem 1rem;">
              <div style="font-size:2.2rem; margin-bottom:0.8rem;">📄</div>
              <div style="font-weight:700; color:#34D399; margin-bottom:0.5rem; font-size:1rem;">
                PDF Reports
              </div>
              <div style="color:#94A3B8; font-size:0.83rem; line-height:1.5;">
                Download a fully formatted PDF with waveform images, scores,
                feedback, and transcript — ready for academic use.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div class='vbcua-divider'></div>", unsafe_allow_html=True)

    # How it works
    st.markdown("### ⚡ How It Works")
    steps = [
        ("1", "🎤", "Upload Audio", "Record or upload your spoken explanation as a WAV, MP3, M4A, or OGG file."),
        ("2", "🔤", "Transcribe", "OpenAI Whisper converts your speech to text with high accuracy."),
        ("3", "🧠", "Semantic Score", "Sentence-BERT computes cosine similarity with the reference concept description."),
        ("4", "🎵", "Audio Analysis", "Librosa extracts fluency metrics: energy, pauses, fillers, pitch, and more."),
        ("5", "📊", "Score & Report", "A composite score is computed and a downloadable PDF report is generated."),
    ]

    for num, icon, title, desc in steps:
        st.markdown(
            f"""
            <div class="step-indicator">
              <span style="background:linear-gradient(135deg,#7C3AED,#06B6D4);
                           -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                           font-weight:800; font-size:1.1rem; min-width:20px;">{num}</span>
              <span style="font-size:1.2rem;">{icon}</span>
              <span style="font-weight:600; color:#E2E8F0;">{title}</span>
              <span style="color:#94A3B8; font-size:0.85rem;">— {desc}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div class='vbcua-divider'></div>", unsafe_allow_html=True)

    # Available concepts
    st.markdown("### 📚 Available Concepts")
    concept_names = list(CONCEPTS.keys())
    cols = st.columns(5)
    for i, concept in enumerate(concept_names):
        with cols[i % 5]:
            st.markdown(
                f"""
                <div style="background:#13131F; border:1px solid #1E2A40;
                            border-radius:10px; padding:0.6rem 0.8rem;
                            margin-bottom:0.5rem; font-size:0.8rem;
                            color:#A78BFA; font-weight:500; text-align:center;">
                  {concept}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div class='vbcua-footer'>VBCUA v{} — Voice-Based Concept Understanding Analyser</div>".format(APP_VERSION),
                unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Page: Analyse
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔬 Analyse":

    st.markdown(
        """
        <div style="margin-bottom:1.5rem;">
          <h1 style="font-size:1.8rem; font-weight:800; margin-bottom:0.3rem;">
            🔬 Concept Analysis
          </h1>
          <p style="color:#94A3B8; font-size:0.9rem;">
            Upload your audio explanation and select the concept to evaluate.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Input panel ──────────────────────────────────────────────────────────
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown("#### 🎤 Upload Audio")
        uploaded_file = st.file_uploader(
            "Drop your audio file here",
            type=ALLOWED_EXTENSIONS,
            help="Supported formats: WAV, MP3, M4A, OGG, FLAC, WebM",
            label_visibility="collapsed",
        )

        st.markdown("#### 📚 Select Concept")
        concept_name = st.selectbox(
            "Concept",
            list(CONCEPTS.keys()),
            index=0,
            label_visibility="collapsed",
        )

        st.markdown("#### ⚙️ Options")
        opt_col1, opt_col2 = st.columns(2)
        with opt_col1:
            show_spectrogram = st.checkbox("Show Spectrogram", value=True)
            show_sentence_level = st.checkbox("Sentence-Level Similarity", value=True)
        with opt_col2:
            show_gap_analysis = st.checkbox("Keyword Gap Analysis", value=True)
            generate_pdf = st.checkbox("Generate PDF Report", value=True)

        analyse_btn = st.button("🚀 Analyse Speech", use_container_width=True, type="primary")

    with right_col:
        st.markdown("#### 📖 Reference Concept")
        ref_text = CONCEPTS[concept_name]
        st.markdown(
            f"""
            <div style="background:#13131F; border:1px solid #1E2A40;
                        border-radius:12px; padding:1.2rem;
                        font-size:0.85rem; color:#CBD5E1; line-height:1.7;
                        max-height:280px; overflow-y:auto;">
              <div style="color:#7C3AED; font-weight:700; margin-bottom:0.6rem;
                          font-size:0.9rem; text-transform:uppercase;
                          letter-spacing:0.06em;">
                {concept_name}
              </div>
              {ref_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div class='vbcua-divider'></div>", unsafe_allow_html=True)

    # ── Analysis Pipeline ─────────────────────────────────────────────────────
    if analyse_btn:
        if uploaded_file is None:
            st.error("⚠️ Please upload an audio file before analysing.")
            st.stop()

        # Save audio
        from modules.transcriber import save_uploaded_audio
        audio_path = save_uploaded_audio(uploaded_file, TEMP_DIR)

        reference = CONCEPTS[concept_name]

        # ── Progress tracking ─────────────────────────────────────────────────
        progress_bar = st.progress(0, text="Initialising…")
        status_box   = st.empty()

        def update(pct: int, msg: str):
            progress_bar.progress(pct, text=msg)
            status_box.markdown(
                f"<div style='color:#7C3AED; font-size:0.85rem;'>{msg}</div>",
                unsafe_allow_html=True,
            )

        # ── Step 1: Transcription ─────────────────────────────────────────────
        update(5, "🎙️ Loading Whisper model…")
        from modules.transcriber import transcribe_audio

        def _transcription_progress(p: float):
            update(int(5 + p * 30), f"🎙️ Transcribing audio… {int(p*100)}%")

        try:
            trans_result = transcribe_audio(audio_path, _transcription_progress)
        except Exception as e:
            st.error(f"Transcription failed: {e}")
            st.stop()

        transcript = trans_result["text"]
        duration   = trans_result["duration"]
        language   = trans_result["language"]

        if not transcript.strip():
            st.warning("⚠️ The audio produced an empty transcript. Please check your recording and try again.")
            st.stop()

        update(40, "✅ Transcription complete. Running audio analysis…")

        # ── Step 2: Audio Analysis ────────────────────────────────────────────
        from modules.audio_analyser import analyse_audio, plot_waveform, plot_spectrogram
        try:
            audio_result = analyse_audio(audio_path, transcript, duration)
        except Exception as e:
            st.error(f"Audio analysis failed: {e}")
            st.stop()

        update(60, "🧠 Computing semantic similarity…")

        # ── Step 3: Semantic Analysis ─────────────────────────────────────────
        from modules.semantic_analyser import (
            compute_similarity, identify_gaps, sentence_level_similarity
        )
        try:
            semantic_sim = compute_similarity(transcript, reference)
            gap_result   = identify_gaps(transcript, reference) if show_gap_analysis else {}
            sent_sims    = sentence_level_similarity(transcript, reference) if show_sentence_level else []
        except Exception as e:
            st.error(f"Semantic analysis failed: {e}")
            st.stop()

        update(80, "📊 Computing final score…")

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

        update(90, "🎨 Rendering results…")

        # ── Generate figures ──────────────────────────────────────────────────
        y, sr = audio_result["y"], audio_result["sr"]
        waveform_fig    = plot_waveform(y, sr, f"Waveform – {concept_name}")
        spectrogram_fig = plot_spectrogram(y, sr) if show_spectrogram else None

        # ── PDF ───────────────────────────────────────────────────────────────
        pdf_bytes = None
        if generate_pdf:
            from modules.report_generator import generate_pdf_report
            try:
                pdf_bytes = generate_pdf_report(
                    concept         = concept_name,
                    transcript      = transcript,
                    score_result    = score_result,
                    audio_result    = audio_result,
                    waveform_fig    = waveform_fig,
                    spectrogram_fig = spectrogram_fig,
                    gap_analysis    = gap_result if show_gap_analysis else None,
                )
            except Exception as e:
                st.warning(f"PDF generation encountered an issue: {e}")

        progress_bar.progress(100, text="✅ Analysis Complete!")
        status_box.empty()
        time.sleep(0.5)
        progress_bar.empty()

        # ══════════════════════════════════════════════════════════════════════
        # RESULTS DASHBOARD
        # ══════════════════════════════════════════════════════════════════════
        st.markdown("<div class='vbcua-divider'></div>", unsafe_allow_html=True)

        # ── Score Banner ──────────────────────────────────────────────────────
        pct   = score_result["percentage"]
        label = score_result["label"]
        emoji = score_result["emoji"]
        color = score_result["colour"]
        sem_pct = score_result["semantic_score"] * 100
        flu_pct = score_result["fluency_score"]  * 100

        score_class_map = {
            "Strong Understanding":   "score-strong",
            "Moderate Understanding": "score-moderate",
            "Poor Understanding":     "score-poor",
        }
        badge_cls = score_class_map.get(label, "score-moderate")

        st.markdown(
            f"""
            <div style="background:linear-gradient(135deg,#0D0A20,#0A1428);
                        border:1px solid #1E2A40; border-radius:18px;
                        padding:2rem; text-align:center; margin-bottom:1.5rem;
                        position:relative; overflow:hidden;">
              <div style="font-size:4rem; font-weight:800; color:{color};
                          line-height:1; margin-bottom:0.3rem;">
                {pct}%
              </div>
              <div class="score-badge {badge_cls}" style="margin-bottom:1rem;">
                {emoji} {label}
              </div>
              <div style="display:flex; justify-content:center; gap:3rem;
                          color:#94A3B8; font-size:0.85rem;">
                <span>🧠 Semantic <b style='color:#A78BFA'>{sem_pct:.1f}%</b></span>
                <span>🎵 Fluency <b style='color:#67E8F9'>{flu_pct:.1f}%</b></span>
                <span>🌐 Language <b style='color:#94A3B8'>{language.upper()}</b></span>
                <span>📝 Words <b style='color:#94A3B8'>{audio_result['word_count']}</b></span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Download PDF ──────────────────────────────────────────────────────
        if pdf_bytes:
            st.download_button(
                label     = "⬇️  Download PDF Report",
                data      = pdf_bytes,
                file_name = f"VBCUA_{concept_name.replace(' ','_')}_Report.pdf",
                mime      = "application/pdf",
                use_container_width=True,
            )

        st.markdown("<div class='vbcua-divider'></div>", unsafe_allow_html=True)

        # ── Tabs ──────────────────────────────────────────────────────────────
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📝 Transcript",
            "🧠 Semantic",
            "🎵 Fluency",
            "📊 Visualisations",
            "🔍 Detailed Scores",
        ])

        # ══ Tab 1: Transcript ══════════════════════════════════════════════════
        with tab1:
            st.markdown("### 📝 Transcribed Explanation")
            st.markdown(
                f"""
                <div style="background:#13131F; border:1px solid #1E2A40;
                            border-radius:12px; padding:1.5rem;
                            font-size:0.95rem; color:#E2E8F0; line-height:1.8;">
                  {transcript}
                </div>
                """,
                unsafe_allow_html=True,
            )

            m1, m2, m3 = st.columns(3)
            m1.metric("Word Count",     str(audio_result["word_count"]))
            m2.metric("Duration (approx.)", f"{duration:.1f}s" if duration else "N/A")
            m3.metric("Language",       language.upper())

            if trans_result.get("segments"):
                with st.expander("⏱️ Timed Segments"):
                    import pandas as pd
                    seg_data = [
                        {
                            "Start (s)": round(s.get("start", 0), 2),
                            "End (s)":   round(s.get("end",   0), 2),
                            "Text":      s.get("text", "").strip(),
                        }
                        for s in trans_result["segments"]
                    ]
                    st.dataframe(pd.DataFrame(seg_data), use_container_width=True)

        # ══ Tab 2: Semantic Analysis ═══════════════════════════════════════════
        with tab2:
            st.markdown("### 🧠 Semantic Similarity Analysis")

            c1, c2 = st.columns(2)
            c1.metric("Cosine Similarity", f"{semantic_sim:.4f}", f"{sem_pct:.1f}%")
            c2.metric("Semantic Score Weight", "60%", "of final score")

            # Similarity meter
            st.markdown("**Semantic Similarity Meter**")
            st.progress(int(sem_pct), text=f"{sem_pct:.1f}% semantic overlap")

            # Feedback
            st.markdown(
                f"""
                <div style="background:#13131F; border-left:3px solid #7C3AED;
                            border-radius:0 12px 12px 0; padding:1rem 1.2rem;
                            margin:1rem 0; font-size:0.9rem; color:#CBD5E1; line-height:1.7;">
                  {score_result['feedback']}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Sentence-level similarity
            if show_sentence_level and sent_sims:
                st.markdown("**Sentence-Level Similarity Breakdown**")
                for sentence, sim_score in sent_sims:
                    bar_color = (
                        "#10B981" if sim_score >= 0.7 else
                        "#F59E0B" if sim_score >= 0.5 else "#EF4444"
                    )
                    st.markdown(
                        f"""
                        <div style="margin-bottom:0.8rem;">
                          <div style="font-size:0.82rem; color:#94A3B8; margin-bottom:4px;
                                      display:flex; justify-content:space-between;">
                            <span style="max-width:85%; overflow:hidden;
                                         text-overflow:ellipsis;">{sentence[:120]}…</span>
                            <b style="color:{bar_color};">{sim_score*100:.0f}%</b>
                          </div>
                          <div style="background:#1A1A2E; border-radius:4px; height:6px;">
                            <div style="width:{sim_score*100:.0f}%; height:100%;
                                        background:{bar_color}; border-radius:4px;"></div>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # Keyword gap analysis
            if show_gap_analysis and gap_result:
                st.markdown("**Keyword Coverage Analysis**")
                covered   = [k for k, v in gap_result.items() if v]
                uncovered = [k for k, v in gap_result.items() if not v]
                coverage_pct = len(covered) / len(gap_result) * 100 if gap_result else 0

                st.progress(int(coverage_pct), text=f"{coverage_pct:.0f}% of key concepts covered")

                kw_col1, kw_col2 = st.columns(2)
                with kw_col1:
                    st.markdown("**✅ Concepts Covered**")
                    st.markdown(
                        " ".join(f'<span class="keyword-covered">{k}</span>' for k in covered) or
                        "<i style='color:#475569'>None detected</i>",
                        unsafe_allow_html=True,
                    )
                with kw_col2:
                    st.markdown("**❌ Concepts Missing**")
                    st.markdown(
                        " ".join(f'<span class="keyword-missing">{k}</span>' for k in uncovered) or
                        "<i style='color:#10B981'>All concepts covered! 🎉</i>",
                        unsafe_allow_html=True,
                    )

        # ══ Tab 3: Fluency Metrics ═════════════════════════════════════════════
        with tab3:
            st.markdown("### 🎵 Fluency & Speech Metrics")

            # Top metrics
            fl1, fl2, fl3, fl4 = st.columns(4)
            fl1.metric("Fluency Score",   f"{flu_pct:.1f}%")
            fl2.metric("Speaking Rate",   f"{audio_result['speaking_rate']:.0f} WPM")
            fl3.metric("Pause Ratio",     f"{ps['pause_ratio']*100:.1f}%")
            fl4.metric("Total Fillers",   str(audio_result["total_fillers"]))

            st.markdown("<div class='vbcua-divider'></div>", unsafe_allow_html=True)

            fc1, fc2 = st.columns(2)

            with fc1:
                st.markdown("**⏸️ Pause Analysis**")
                p_data = {
                    "Metric": ["Pause Count", "Mean Duration", "Longest Pause", "Pause Ratio"],
                    "Value":  [
                        str(ps["pause_count"]),
                        f"{ps['mean_pause_dur']:.2f}s",
                        f"{ps['max_pause_dur']:.2f}s",
                        f"{ps['pause_ratio']*100:.1f}%",
                    ],
                    "Status": [
                        "🟢 OK" if ps["pause_count"] <= 10 else "🟡 High",
                        "🟢 OK" if ps["mean_pause_dur"] < 0.8 else "🟡 Long",
                        "🟢 OK" if ps["max_pause_dur"]  < 2.0 else "🔴 Very Long",
                        "🟢 OK" if 0.15 <= ps["pause_ratio"] <= 0.30 else "🟡 Check",
                    ]
                }
                import pandas as pd
                st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)

            with fc2:
                st.markdown("**🎶 Pitch Analysis**")
                pit = audio_result["pitch"]
                pit_data = {
                    "Metric": ["Mean F0", "Pitch Variability", "Voiced Ratio"],
                    "Value":  [
                        f"{pit['mean_hz']:.1f} Hz",
                        f"{pit['std_hz']:.1f} Hz",
                        f"{pit['voiced_ratio']*100:.1f}%",
                    ],
                }
                st.dataframe(pd.DataFrame(pit_data), use_container_width=True, hide_index=True)

                st.markdown("**⚡ Energy Level**")
                rms_val = audio_result["rms_energy"]
                energy_label = (
                    "🔊 Confident" if rms_val > 0.6 else
                    "📢 Moderate"  if rms_val > 0.35 else "🤫 Quiet"
                )
                st.progress(int(rms_val * 100), text=f"{energy_label} — {rms_val:.4f}")

            # Filler word breakdown
            filler_dict = audio_result.get("filler_words", {})
            if filler_dict:
                st.markdown("**🗣️ Filler Word Breakdown**")
                max_count = max(filler_dict.values())
                for word, count in sorted(filler_dict.items(), key=lambda x: -x[1]):
                    pct_bar = int((count / max_count) * 100)
                    st.markdown(
                        f"""
                        <div class="filler-bar-wrap">
                          <div class="filler-bar-label">
                            <span>"{word}"</span><span>{count}×</span>
                          </div>
                          <div class="filler-bar-bg">
                            <div class="filler-bar-fill" style="width:{pct_bar}%;"></div>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.success("🎉 No filler words detected! Excellent delivery.")

        # ══ Tab 4: Visualisations ══════════════════════════════════════════════
        with tab4:
            st.markdown("### 📊 Audio Visualisations")

            st.markdown("**🌊 Waveform**")
            st.pyplot(waveform_fig, use_container_width=True)

            if show_spectrogram and spectrogram_fig:
                st.markdown("**🎛️ Mel Spectrogram**")
                st.pyplot(spectrogram_fig, use_container_width=True)

            # Plotly filler pie chart
            if filler_dict:
                st.markdown("**🥧 Filler Word Distribution**")
                import plotly.graph_objects as go
                labels = list(filler_dict.keys())
                values = list(filler_dict.values())
                fig_pie = go.Figure(go.Pie(
                    labels=labels, values=values,
                    hole=0.45,
                    marker=dict(
                        colors=["#7C3AED","#06B6D4","#10B981","#F59E0B","#EF4444",
                                "#8B5CF6","#0EA5E9","#34D399","#FBBF24","#F87171"],
                        line=dict(color="#0F0F1A", width=2),
                    ),
                    textfont_size=12,
                ))
                fig_pie.update_layout(
                    paper_bgcolor="#0F0F1A", plot_bgcolor="#0F0F1A",
                    font_color="#E2E8F0", legend_font_color="#94A3B8",
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=320,
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            # Plotly score radar
            st.markdown("**🕸️ Score Radar**")
            import plotly.graph_objects as go
            categories = ["Semantic", "Fluency", "Energy", "Clarity", "Pacing"]
            clarity_approx = max(0, 1.0 - audio_result["total_fillers"] * 0.05)
            pacing_raw     = audio_result["speaking_rate"]
            pacing_approx  = 1.0 if 110 <= pacing_raw <= 160 else max(0, 0.6 - abs(pacing_raw - 135) * 0.004)
            values_radar   = [
                score_result["semantic_score"],
                score_result["fluency_score"],
                min(1.0, audio_result["rms_energy"]),
                clarity_approx,
                pacing_approx,
            ]
            # close the radar
            categories += [categories[0]]
            values_radar  += [values_radar[0]]

            fig_radar = go.Figure(go.Scatterpolar(
                r=values_radar, theta=categories,
                fill="toself",
                fillcolor="rgba(124,58,237,0.2)",
                line=dict(color="#A78BFA", width=2),
                marker=dict(size=6, color="#A78BFA"),
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="#13131F",
                    radialaxis=dict(
                        visible=True, range=[0, 1],
                        gridcolor="#1E2A40", tickfont=dict(color="#94A3B8", size=9),
                        tickformat=".0%",
                    ),
                    angularaxis=dict(
                        gridcolor="#1E2A40", tickfont=dict(color="#CBD5E1", size=11),
                    ),
                ),
                paper_bgcolor="#0F0F1A",
                font_color="#E2E8F0",
                margin=dict(l=40, r=40, t=30, b=30),
                height=350,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        # ══ Tab 5: Detailed Scores ═════════════════════════════════════════════
        with tab5:
            st.markdown("### 🔍 Detailed Score Breakdown")

            bd = score_result["breakdown"]

            det_data = {
                "Component": [
                    "Semantic Similarity", "Semantic Weight",
                    "Fluency Score", "Fluency Weight",
                    "Final Composite Score",
                    "RMS Energy", "Pause Ratio",
                    "Filler Count", "Speaking Rate (WPM)",
                ],
                "Value": [
                    f"{score_result['semantic_score']*100:.2f}%",
                    f"{bd['semantic_weight']*100:.0f}%",
                    f"{score_result['fluency_score']*100:.2f}%",
                    f"{bd['fluency_weight']*100:.0f}%",
                    f"{score_result['final_score']*100:.2f}%",
                    f"{bd['energy_contribution']:.4f}",
                    f"{bd['pause_ratio']*100:.2f}%",
                    str(bd["filler_count"]),
                    str(bd["speaking_rate_wpm"]),
                ],
                "Notes": [
                    "Cosine similarity via Sentence-BERT",
                    "Contribution to final score",
                    "Composite of energy/pauses/fillers/rate",
                    "Contribution to final score",
                    "Weighted: 60% semantic + 40% fluency",
                    "Mean RMS energy (speech loudness)",
                    "Fraction of audio that is silent",
                    "Total filler words detected",
                    "Words per minute",
                ],
            }
            st.dataframe(pd.DataFrame(det_data), use_container_width=True, hide_index=True)

            st.markdown("<div class='vbcua-divider'></div>", unsafe_allow_html=True)
            st.markdown("#### 💬 AI Feedback")
            st.info(score_result["feedback"])

    else:
        # Placeholder state
        st.markdown(
            """
            <div style="background:#13131F; border:2px dashed #1E2A40;
                        border-radius:16px; padding:3rem; text-align:center;
                        margin-top:1rem;">
              <div style="font-size:3rem; margin-bottom:1rem;">🎙️</div>
              <div style="font-weight:600; color:#7C3AED; font-size:1.1rem;
                          margin-bottom:0.5rem;">Ready to Analyse</div>
              <div style="color:#64748B; font-size:0.88rem;">
                Upload an audio file, select a concept, and click <b>Analyse Speech</b> to begin.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Page: About
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📋 About":
    st.markdown(
        """
        <div class="vbcua-hero">
          <h1>📋 About VBCUA</h1>
          <p style="color:#94A3B8; max-width:600px; margin:0 auto;">
            Voice-Based Concept Understanding Analyser — an AI-powered educational
            assessment platform built with Python and Streamlit.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### 🏗️ Architecture")
        st.markdown("""
        | Layer | Technology |
        |-------|-----------|
        | **Web Framework** | Streamlit |
        | **Speech-to-Text** | OpenAI Whisper (`base`) |
        | **Semantic NLP** | Sentence-BERT (`all-MiniLM-L6-v2`) |
        | **Audio DSP** | Librosa + SciPy |
        | **Visualisation** | Matplotlib + Plotly |
        | **PDF Reports** | ReportLab |
        | **Backend** | Python 3.10+ |
        """)

    with col_b:
        st.markdown("### 📐 Scoring Formula")
        st.markdown(r"""
        The **final score** is a weighted combination:

        $$\text{Score} = 0.60 \times S_{sem} + 0.40 \times S_{flu}$$

        Where:
        - $S_{sem}$ = Sentence-BERT cosine similarity
        - $S_{flu}$ = Fluency sub-score:

        $$S_{flu} = 0.25 \cdot E + 0.30 \cdot P + 0.25 \cdot F + 0.20 \cdot R$$

        | Symbol | Meaning |
        |--------|---------|
        | $E$ | RMS energy score |
        | $P$ | Pause quality score |
        | $F$ | Filler word score |
        | $R$ | Speaking rate score |
        """)

    st.markdown("<div class='vbcua-divider'></div>", unsafe_allow_html=True)

    st.markdown("### 🎓 Use Cases")
    uc_col1, uc_col2, uc_col3 = st.columns(3)

    use_cases = [
        ("🎓", "Students", "Evaluate conceptual understanding before exams or interviews with AI-powered feedback."),
        ("👨‍🏫", "Educators", "Assess spoken explanations at scale and generate individual PDF reports per student."),
        ("💼", "Job Seekers", "Practise technical interview answers and measure delivery fluency before the real thing."),
    ]
    for col, (icon, title, desc) in zip([uc_col1, uc_col2, uc_col3], use_cases):
        with col:
            st.markdown(
                f"""
                <div class="metric-card" style="text-align:center; padding:1.5rem 1rem;">
                  <div style="font-size:2rem; margin-bottom:0.6rem;">{icon}</div>
                  <div style="font-weight:700; color:#A78BFA; margin-bottom:0.4rem;">{title}</div>
                  <div style="color:#94A3B8; font-size:0.82rem; line-height:1.5;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div class='vbcua-divider'></div>", unsafe_allow_html=True)
    st.markdown("### 📦 Concepts Available")
    st.markdown(", ".join(f"**{c}**" for c in CONCEPTS.keys()))

    st.markdown(
        f"<div class='vbcua-footer'>VBCUA v{APP_VERSION} · Built with ❤️ using Python + Streamlit</div>",
        unsafe_allow_html=True,
    )
