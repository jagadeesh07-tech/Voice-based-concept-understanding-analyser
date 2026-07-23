/* ═══════════════════════════════════════════════════════════════════════════
   VBCUA  –  app.js  (Vanilla JS Frontend Logic)
   Connects to Node.js server → Python FastAPI backend
═══════════════════════════════════════════════════════════════════════════ */

"use strict";

/* ── Config ────────────────────────────────────────────────────────────── */
const API_BASE = window.location.protocol === "file:" ? "http://localhost:8000" : "";
let   analysisResult = null;  // store last result globally

/* ══════════════════════════════════════════════════════════════════════════
   PARTICLES BACKGROUND
══════════════════════════════════════════════════════════════════════════ */
(function initParticles() {
  const canvas = document.getElementById("particles-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let W, H, particles;

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function createParticles() {
    particles = Array.from({ length: 60 }, () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      r: Math.random() * 1.5 + .3,
      dx: (Math.random() - .5) * .3,
      dy: (Math.random() - .5) * .3,
      alpha: Math.random() * .5 + .1,
    }));
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(124,58,237,${p.alpha})`;
      ctx.fill();
      p.x += p.dx;
      p.y += p.dy;
      if (p.x < 0 || p.x > W) p.dx *= -1;
      if (p.y < 0 || p.y > H) p.dy *= -1;
    });
    requestAnimationFrame(draw);
  }

  resize();
  createParticles();
  draw();
  window.addEventListener("resize", () => { resize(); createParticles(); });
})();


/* ══════════════════════════════════════════════════════════════════════════
   NAVIGATION
══════════════════════════════════════════════════════════════════════════ */
const navItems   = document.querySelectorAll(".nav-item");
const pages      = document.querySelectorAll(".page");
const hamburger  = document.getElementById("hamburger");
const sidebar    = document.getElementById("sidebar");

function navigateTo(pageId) {
  navItems.forEach(n => n.classList.toggle("active", n.dataset.page === pageId));
  pages.forEach(p => p.classList.toggle("active", p.id === `page-${pageId}`));
  if (window.innerWidth <= 900) sidebar.classList.remove("open");
}

navItems.forEach(item => {
  item.addEventListener("click", () => navigateTo(item.dataset.page));
});

hamburger?.addEventListener("click", () => sidebar.classList.toggle("open"));

// Hero buttons
document.getElementById("hero-analyse-btn")?.addEventListener("click", () => navigateTo("analyse"));
document.getElementById("hero-learn-btn")?.addEventListener("click",   () => navigateTo("about"));
document.getElementById("go-analyse-btn")?.addEventListener("click",   () => navigateTo("analyse"));


/* ══════════════════════════════════════════════════════════════════════════
   TOAST
══════════════════════════════════════════════════════════════════════════ */
const toastEl = document.getElementById("toast");
let toastTimer;

function showToast(msg, type = "info", duration = 3500) {
  toastEl.textContent = msg;
  toastEl.className   = `toast toast-${type} show`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toastEl.classList.remove("show"), duration);
}


/* ══════════════════════════════════════════════════════════════════════════
   LOAD CONCEPTS FROM API
══════════════════════════════════════════════════════════════════════════ */
async function loadConcepts() {
  try {
    const res  = await fetch(`${API_BASE}/api/concepts`);
    const data = await res.json();

    // Populate select
    const sel = document.getElementById("concept-select");
    data.concepts.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.name;
      opt.textContent = c.name;
      sel.appendChild(opt);
    });

    // Populate home concepts grid
    const grid = document.getElementById("home-concepts-grid");
    data.concepts.forEach(c => {
      const chip = document.createElement("div");
      chip.className = "concept-chip";
      chip.textContent = c.name;
      chip.addEventListener("click", () => {
        navigateTo("analyse");
        document.getElementById("concept-select").value = c.name;
        updateReference(c.name);
      });
      grid.appendChild(chip);
    });

    // Store reference texts
    window._conceptPreviews = {};
    data.concepts.forEach(c => { window._conceptPreviews[c.name] = c.preview; });

  } catch (e) {
    console.warn("Could not load concepts (API offline?):", e);
    showToast("⚠️ Could not reach API. Is the server running?", "error", 6000);
  }
}

function updateReference(conceptName) {
  const box     = document.getElementById("reference-box");
  const preview = window._conceptPreviews?.[conceptName] || "";
  if (!conceptName) {
    box.innerHTML = `<div class="reference-placeholder">
      <div style="font-size:2rem; margin-bottom:.5rem">📚</div>
      <div>Select a concept to see its reference description</div>
    </div>`;
    return;
  }
  box.innerHTML = `
    <div class="reference-concept-name">${conceptName}</div>
    <div>${preview}</div>
  `;
}

document.getElementById("concept-select")?.addEventListener("change", (e) => {
  updateReference(e.target.value);
  checkAnalyseReady();
});


/* ══════════════════════════════════════════════════════════════════════════
   FILE UPLOAD
══════════════════════════════════════════════════════════════════════════ */
const uploadZone  = document.getElementById("upload-zone");
const audioInput  = document.getElementById("audio-input");
const filePreview = document.getElementById("file-preview");
const audioPlayer = document.getElementById("audio-player");
let   selectedFile = null;

uploadZone.addEventListener("click", () => audioInput.click());

uploadZone.addEventListener("dragover", e => {
  e.preventDefault();
  uploadZone.classList.add("drag-over");
});
uploadZone.addEventListener("dragleave", () => uploadZone.classList.remove("drag-over"));
uploadZone.addEventListener("drop", e => {
  e.preventDefault();
  uploadZone.classList.remove("drag-over");
  const file = e.dataTransfer.files[0];
  if (file) handleFileSelect(file);
});

audioInput.addEventListener("change", () => {
  if (audioInput.files[0]) handleFileSelect(audioInput.files[0]);
});

document.getElementById("file-remove")?.addEventListener("click", () => {
  selectedFile = null;
  filePreview.style.display = "none";
  audioPlayer.style.display = "none";
  audioPlayer.src = "";
  audioInput.value = "";
  checkAnalyseReady();
});

document.getElementById("use-sample-btn")?.addEventListener("click", async () => {
  try {
    showToast("⚡ Loading sample audio...", "info");
    const res = await fetch("/sample.wav");
    if (!res.ok) throw new Error("Sample audio file not found on server.");
    const blob = await res.blob();
    const file = new File([blob], "sample_audio.wav", { type: "audio/wav" });
    handleFileSelect(file);
    
    // Auto-select Machine Learning concept since the sample explains it
    const conceptSel = document.getElementById("concept-select");
    if (conceptSel) {
      conceptSel.value = "Machine Learning";
      updateReference("Machine Learning");
      checkAnalyseReady();
    }
  } catch (err) {
    showToast(`❌ Failed to load sample: ${err.message}`, "error");
  }
});

function handleFileSelect(file) {
  const allowed = ["audio/wav","audio/mpeg","audio/mp4","audio/m4a",
                   "audio/ogg","audio/flac","audio/webm","video/webm"];
  if (!allowed.some(t => file.type.includes(t.split("/")[1])) &&
      !file.name.match(/\.(wav|mp3|m4a|ogg|flac|webm)$/i)) {
    showToast("❌ Unsupported file type. Use WAV, MP3, M4A, OGG, or FLAC.", "error");
    return;
  }

  selectedFile = file;
  document.getElementById("file-name").textContent = file.name;
  document.getElementById("file-meta").textContent =
    `${(file.size / 1024).toFixed(1)} KB  ·  ${file.type || "audio"}`;
  filePreview.style.display = "flex";

  // Audio player preview
  const url = URL.createObjectURL(file);
  audioPlayer.src = url;
  audioPlayer.style.display = "block";

  checkAnalyseReady();
  showToast("✅ Audio file loaded!", "success");
}

function checkAnalyseReady() {
  const concept = document.getElementById("concept-select").value;
  const btn     = document.getElementById("analyse-btn");
  btn.disabled  = !(selectedFile && concept);
}


/* ══════════════════════════════════════════════════════════════════════════
   ANALYSIS PIPELINE
══════════════════════════════════════════════════════════════════════════ */
document.getElementById("analyse-btn")?.addEventListener("click", runAnalysis);

async function runAnalysis() {
  if (!selectedFile) return showToast("Upload an audio file first.", "error");
  const concept = document.getElementById("concept-select").value;
  if (!concept)   return showToast("Select a concept first.", "error");

  // UI → processing state
  document.getElementById("analyse-btn").disabled = true;
  document.getElementById("reference-box").style.display = "none";
  const procPanel = document.getElementById("processing-panel");
  procPanel.style.display = "block";

  const steps = ["step-transcribe","step-audio","step-semantic","step-score","step-pdf"];
  steps.forEach(s => {
    const el = document.getElementById(s);
    el.classList.remove("active","done");
  });

  // Animated progress simulation
  let currentStep = 0;
  setStep(0);

  function setStep(i) {
    currentStep = i;
    steps.forEach((s, idx) => {
      const el = document.getElementById(s);
      el.classList.toggle("active", idx === i);
      el.classList.toggle("done",   idx < i);
    });
    const labels  = ["🎙️ Transcribing speech…","🎵 Extracting audio features…",
                     "🧠 Computing semantic similarity…","📊 Calculating scores…",
                     "📄 Generating PDF report…"];
    const subText = ["This may take 20–60 seconds depending on audio length",
                     "Analysing energy, pauses, pitch, and filler words",
                     "Running Sentence-BERT comparison",
                     "Applying weighted scoring formula",
                     "Building downloadable PDF report"];
    document.getElementById("processing-title").textContent = labels[i]  || "Processing…";
    document.getElementById("processing-sub").textContent   = subText[i] || "";

    const pcts = [15, 40, 65, 82, 95];
    updateProgress(pcts[i] || 10);
  }

  function updateProgress(pct) {
    document.getElementById("progress-fill").style.width = pct + "%";
    document.getElementById("progress-label").textContent = pct + "%";
  }

  // Simulate step advances while waiting
  const stepTimers = [
    setTimeout(() => setStep(1), 8000),
    setTimeout(() => setStep(2), 20000),
    setTimeout(() => setStep(3), 35000),
    setTimeout(() => setStep(4), 45000),
  ];

  // Build FormData
  const fd = new FormData();
  fd.append("audio",   selectedFile, selectedFile.name);
  fd.append("concept", concept);
  fd.append("options", JSON.stringify({
    spectrogram:   document.getElementById("opt-spectrogram").checked,
    sentence_sims: document.getElementById("opt-sentence").checked,
    gap:           document.getElementById("opt-gap").checked,
    pdf:           document.getElementById("opt-pdf").checked,
  }));

  try {
    const res = await fetch(`${API_BASE}/api/analyse`, {
      method: "POST",
      body:   fd,
    });

    // Clear simulated timers
    stepTimers.forEach(t => clearTimeout(t));

    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: res.statusText }));
      throw new Error(err.error || err.detail || "Analysis failed");
    }

    updateProgress(100);
    setStep(4);
    await delay(600);

    const data = await res.json();
    analysisResult = data;

    // Show results
    renderResults(data);
    navigateTo("results");

    // Badge
    const badge = document.getElementById("results-badge");
    badge.style.display = "inline";

    showToast("✅ Analysis complete!", "success", 4000);

  } catch (err) {
    stepTimers.forEach(t => clearTimeout(t));
    showToast(`❌ ${err.message}`, "error", 6000);
    console.error(err);
  } finally {
    procPanel.style.display = "none";
    document.getElementById("reference-box").style.display = "block";
    document.getElementById("analyse-btn").disabled = false;
  }
}

function delay(ms) { return new Promise(r => setTimeout(r, ms)); }


/* ══════════════════════════════════════════════════════════════════════════
   RENDER RESULTS
══════════════════════════════════════════════════════════════════════════ */
function renderResults(data) {
  const { scores, transcript, word_count, duration, language,
          audio, semantic, visuals, segments, feedback,
          session_id, pdf_url } = data;

  /* ── Page subtitle ──────────────────────────────────────────────────── */
  document.getElementById("results-subtitle").textContent =
    `Concept: ${data.concept}  ·  Language: ${(language||"").toUpperCase()}  ·  ${word_count} words`;

  /* ── Score banner ───────────────────────────────────────────────────── */
  document.getElementById("score-banner").style.display = "flex";
  document.getElementById("results-tabs").style.display = "block";
  document.getElementById("empty-results").style.display = "none";

  // Animate ring
  const pct       = scores.percent;
  const circumference = 2 * Math.PI * 42;
  const offset    = circumference * (1 - pct / 100);
  const ring      = document.getElementById("score-ring-fill");
  ring.style.stroke = scores.colour || "#7C3AED";
  setTimeout(() => ring.style.strokeDashoffset = offset, 100);

  // Counter animation
  animateCounter(document.getElementById("score-pct"), 0, pct, 1200, v => v + "%");

  // Label badge
  const labelBadge = document.getElementById("score-label-badge");
  labelBadge.textContent = `${scores.emoji || ""} ${scores.label}`;
  const cls = scores.label.toLowerCase().includes("strong")   ? "label-strong"
            : scores.label.toLowerCase().includes("moderate") ? "label-moderate"
            :                                                    "label-poor";
  labelBadge.className = `score-label-badge ${cls}`;

  // Meta grid
  document.getElementById("sm-semantic").textContent = `${(scores.semantic * 100).toFixed(1)}%`;
  document.getElementById("sm-fluency").textContent  = `${(scores.fluency  * 100).toFixed(1)}%`;
  document.getElementById("sm-words").textContent    = word_count;
  document.getElementById("sm-wpm").textContent      = `${(audio.speaking_rate || 0).toFixed(0)}`;

  // Feedback
  document.getElementById("ai-feedback-box").textContent = feedback;

  const dlBtn = document.getElementById("download-pdf-btn");
  dlBtn.style.display = "inline-flex";
  dlBtn.onclick = () => {
    const link = document.createElement("a");
    link.href = `${API_BASE}${pdf_url}`;
    link.download = `VBCUA_Analysis_Report_${session_id}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  /* ── TAB: Transcript ────────────────────────────────────────────────── */
  document.getElementById("transcript-box").textContent = transcript || "(Empty transcript)";

  document.getElementById("transcript-metrics").innerHTML = `
    <div class="mini-metric"><div class="mv">${word_count}</div><div class="ml">Words</div></div>
    <div class="mini-metric"><div class="mv">${duration ? duration.toFixed(1)+"s" : "—"}</div><div class="ml">Duration</div></div>
    <div class="mini-metric"><div class="mv">${(language||"").toUpperCase()}</div><div class="ml">Language</div></div>
    <div class="mini-metric"><div class="mv">${(audio.speaking_rate||0).toFixed(0)}</div><div class="ml">WPM</div></div>
  `;

  const segCont = document.getElementById("segments-container");
  if (segments && segments.length > 0) {
    segCont.innerHTML = `
      <details>
        <summary style="cursor:pointer; font-size:.85rem; color:var(--cyan); font-weight:600; padding:.5rem 0">
          ⏱️ Timed Segments (${segments.length})
        </summary>
        <div style="margin-top:.75rem; overflow-x:auto">
          <table class="segments-table">
            <thead><tr><th>Start</th><th>End</th><th>Text</th></tr></thead>
            <tbody>
              ${segments.map(s => `
                <tr>
                  <td style="font-family:var(--mono); color:var(--violet-l)">${s.start}s</td>
                  <td style="font-family:var(--mono); color:var(--violet-l)">${s.end}s</td>
                  <td>${s.text}</td>
                </tr>`).join("")}
            </tbody>
          </table>
        </div>
      </details>
    `;
  } else { segCont.innerHTML = ""; }

  /* ── TAB: Semantic ──────────────────────────────────────────────────── */
  const semPct = semantic.similarity * 100;
  document.getElementById("sem-big-metric").textContent = `${semPct.toFixed(1)}%`;
  document.getElementById("sem-meter").style.width = semPct + "%";

  // Keyword coverage
  const gapData    = semantic.gap_analysis || {};
  const covered    = Object.entries(gapData).filter(([,v]) => v).map(([k]) => k);
  const missing    = Object.entries(gapData).filter(([,v]) => !v).map(([k]) => k);
  const covPct     = gapData && Object.keys(gapData).length
    ? (covered.length / Object.keys(gapData).length * 100).toFixed(0)
    : 0;

  document.getElementById("coverage-fill").style.width = covPct + "%";
  document.getElementById("coverage-pct").textContent   = covPct + "%";

  document.getElementById("keyword-covered").innerHTML =
    (covered.length
      ? `<div style="font-size:.75rem;color:var(--emerald);margin-bottom:.3rem;font-weight:600">✅ Covered</div>` +
        covered.map(k => `<span class="pill-covered">${k}</span>`).join("")
      : "") ;

  document.getElementById("keyword-missing").innerHTML =
    (missing.length
      ? `<div style="font-size:.75rem;color:var(--red);margin-bottom:.3rem;font-weight:600;margin-top:.5rem">❌ Missing</div>` +
        missing.map(k => `<span class="pill-missing">${k}</span>`).join("")
      : `<div style="color:var(--emerald);font-size:.8rem;margin-top:.5rem">🎉 All concepts covered!</div>`);

  // Sentence-level sims
  const sentList = document.getElementById("sentence-sims-list");
  const sents    = semantic.sentence_sims || [];
  sentList.innerHTML = sents.length
    ? sents.map(s => {
        const c = s.score >= .7 ? "var(--emerald)" : s.score >= .5 ? "var(--amber)" : "var(--red)";
        return `<div class="sent-sim-item">
          <div class="sent-sim-text">"${s.text}${s.text.length >= 120 ? "…" : ""}"</div>
          <div class="sent-sim-bar-wrap">
            <div class="sent-sim-track">
              <div class="sent-sim-fill" style="width:${(s.score*100).toFixed(0)}%; background:${c}"></div>
            </div>
            <span class="sent-sim-val" style="color:${c}">${(s.score*100).toFixed(0)}%</span>
          </div>
        </div>`;
      }).join("")
    : `<div style="color:var(--text-3);font-size:.83rem">No sentence breakdown available.</div>`;

  /* ── TAB: Fluency ───────────────────────────────────────────────────── */
  const ps = audio.pause_stats || {};
  const pit = audio.pitch || {};

  const fluencyCards = [
    { icon: "⚡", val: `${(scores.fluency * 100).toFixed(1)}%`,   lbl: "Fluency Score",  status: scores.fluency >= .75 ? "🟢 Good" : scores.fluency >= .5 ? "🟡 OK" : "🔴 Low", statusCls: scores.fluency >= .75 ? "status-ok" : scores.fluency >= .5 ? "status-warn" : "status-bad" },
    { icon: "🗣️", val: `${(audio.speaking_rate||0).toFixed(0)}`,  lbl: "WPM",            status: audio.speaking_rate >= 110 && audio.speaking_rate <= 160 ? "🟢 Ideal" : "🟡 Check", statusCls: audio.speaking_rate >= 110 && audio.speaking_rate <= 160 ? "status-ok" : "status-warn" },
    { icon: "⏸️", val: `${((ps.pause_ratio||0)*100).toFixed(1)}%`, lbl: "Pause Ratio",   status: ps.pause_ratio >= .15 && ps.pause_ratio <= .30 ? "🟢 Natural" : "🟡 Check", statusCls: ps.pause_ratio >= .15 && ps.pause_ratio <= .30 ? "status-ok" : "status-warn" },
    { icon: "🔊", val: `${((audio.rms_energy||0)*100).toFixed(0)}`, lbl: "Energy",        status: audio.rms_energy >= .6 ? "🟢 Confident" : audio.rms_energy >= .35 ? "🟡 Moderate" : "🔴 Quiet", statusCls: audio.rms_energy >= .6 ? "status-ok" : audio.rms_energy >= .35 ? "status-warn" : "status-bad" },
    { icon: "🗣️", val: audio.total_fillers,                         lbl: "Filler Words",  status: audio.total_fillers <= 2 ? "🟢 Clean" : audio.total_fillers <= 5 ? "🟡 Some" : "🔴 Many", statusCls: audio.total_fillers <= 2 ? "status-ok" : audio.total_fillers <= 5 ? "status-warn" : "status-bad" },
    { icon: "🎶", val: `${(pit.mean_hz||0).toFixed(0)} Hz`,         lbl: "Mean Pitch",    status: "—", statusCls: "" },
    { icon: "📊", val: ps.pause_count || 0,                          lbl: "Pause Count",   status: ps.pause_count <= 10 ? "🟢 OK" : "🟡 High", statusCls: ps.pause_count <= 10 ? "status-ok" : "status-warn" },
    { icon: "🎯", val: `${((pit.voiced_ratio||0)*100).toFixed(0)}%`, lbl: "Voiced Ratio", status: "—", statusCls: "" },
  ];

  document.getElementById("fluency-metrics-grid").innerHTML = fluencyCards.map(c => `
    <div class="fluency-card">
      <div class="fc-icon">${c.icon}</div>
      <div class="fc-val">${c.val}</div>
      <div class="fc-lbl">${c.lbl}</div>
      ${c.status !== "—" ? `<div class="fc-status ${c.statusCls}" style="font-size:.7rem; margin-top:.3rem">${c.status}</div>` : ""}
    </div>
  `).join("");

  // Pause table
  document.getElementById("pause-table").innerHTML = `
    <table class="data-table">
      <thead><tr><th>Metric</th><th>Value</th><th>Status</th></tr></thead>
      <tbody>
        <tr><td>Pause Count</td><td>${ps.pause_count||0}</td><td><span class="${ps.pause_count<=10?"status-ok":"status-warn"}">${ps.pause_count<=10?"🟢 OK":"🟡 High"}</span></td></tr>
        <tr><td>Mean Pause</td><td>${(ps.mean_pause_dur||0).toFixed(2)}s</td><td><span class="${ps.mean_pause_dur<.8?"status-ok":"status-warn"}">${ps.mean_pause_dur<.8?"🟢 OK":"🟡 Long"}</span></td></tr>
        <tr><td>Longest Pause</td><td>${(ps.max_pause_dur||0).toFixed(2)}s</td><td><span class="${ps.max_pause_dur<2?"status-ok":"status-bad"}">${ps.max_pause_dur<2?"🟢 OK":"🔴 Very Long"}</span></td></tr>
        <tr><td>Pause Ratio</td><td>${((ps.pause_ratio||0)*100).toFixed(1)}%</td><td><span class="${ps.pause_ratio>=.15&&ps.pause_ratio<=.30?"status-ok":"status-warn"}">${ps.pause_ratio>=.15&&ps.pause_ratio<=.30?"🟢 Natural":"🟡 Check"}</span></td></tr>
      </tbody>
    </table>
    <div style="margin-top:1rem">
      <table class="data-table">
        <thead><tr><th>Pitch Metric</th><th>Value</th></tr></thead>
        <tbody>
          <tr><td>Mean F0</td><td>${(pit.mean_hz||0).toFixed(1)} Hz</td></tr>
          <tr><td>Variability (Std)</td><td>${(pit.std_hz||0).toFixed(1)} Hz</td></tr>
          <tr><td>Voiced Ratio</td><td>${((pit.voiced_ratio||0)*100).toFixed(1)}%</td></tr>
        </tbody>
      </table>
    </div>
  `;

  // Filler bars
  const fillerDict = audio.filler_words || {};
  const fillerKeys = Object.keys(fillerDict).sort((a,b) => fillerDict[b] - fillerDict[a]);
  const maxF       = Math.max(1, ...Object.values(fillerDict));
  document.getElementById("filler-bars").innerHTML = fillerKeys.length
    ? fillerKeys.map(w => `
        <div class="filler-item">
          <div class="filler-header">
            <span>"${w}"</span><span>${fillerDict[w]}×</span>
          </div>
          <div class="filler-track">
            <div class="filler-fill" style="width:${(fillerDict[w]/maxF*100).toFixed(0)}%"></div>
          </div>
        </div>`).join("")
    : `<div style="color:var(--emerald);font-size:.88rem;padding:.75rem;background:rgba(16,185,129,.06);border-radius:8px;border:1px solid rgba(16,185,129,.2)">
        🎉 No filler words detected! Excellent delivery.
       </div>`;

  /* ── TAB: Visuals ───────────────────────────────────────────────────── */

  // Waveform chart (Chart.js)
  renderWaveformChart(visuals.waveform_points || []);

  // Spectrogram image
  const specImg = document.getElementById("spectrogram-img");
  if (visuals.spectrogram_b64) {
    specImg.src = `data:image/png;base64,${visuals.spectrogram_b64}`;
    specImg.style.display = "block";
  }

  // Radar chart
  renderRadarChart(scores, audio, semantic);

  // Donut chart
  renderDonutChart(scores);

  /* ── TAB: Breakdown ─────────────────────────────────────────────────── */
  document.getElementById("breakdown-table").innerHTML = `
    <table class="data-table">
      <thead><tr><th>Component</th><th>Value</th><th>Notes</th></tr></thead>
      <tbody>
        <tr><td>Semantic Similarity</td><td style="color:var(--violet-l);font-family:var(--mono)">${(scores.semantic*100).toFixed(2)}%</td><td>Cosine similarity via Sentence-BERT</td></tr>
        <tr><td>Semantic Weight</td><td style="font-family:var(--mono)">60%</td><td>Contribution to final score</td></tr>
        <tr><td>Fluency Score</td><td style="color:var(--cyan);font-family:var(--mono)">${(scores.fluency*100).toFixed(2)}%</td><td>Energy + Pauses + Fillers + Rate</td></tr>
        <tr><td>Fluency Weight</td><td style="font-family:var(--mono)">40%</td><td>Contribution to final score</td></tr>
        <tr><td><strong>Final Score</strong></td><td style="color:${scores.colour};font-family:var(--mono);font-weight:700">${(scores.final*100).toFixed(2)}%</td><td>Weighted composite</td></tr>
        <tr><td>RMS Energy</td><td style="font-family:var(--mono)">${(audio.rms_energy||0).toFixed(4)}</td><td>Mean speech loudness</td></tr>
        <tr><td>Pause Ratio</td><td style="font-family:var(--mono)">${((ps.pause_ratio||0)*100).toFixed(2)}%</td><td>Fraction of audio that is silent</td></tr>
        <tr><td>Filler Count</td><td style="font-family:var(--mono)">${audio.total_fillers}</td><td>Total filler words detected</td></tr>
        <tr><td>Speaking Rate</td><td style="font-family:var(--mono)">${(audio.speaking_rate||0).toFixed(0)} WPM</td><td>Words per minute</td></tr>
      </tbody>
    </table>
  `;

  document.getElementById("feedback-full").textContent = feedback;
}


/* ══════════════════════════════════════════════════════════════════════════
   CHARTS
══════════════════════════════════════════════════════════════════════════ */
function getThemeColor(darkVal, lightVal) {
  return document.body.classList.contains("light") ? lightVal : darkVal;
}

let waveformChart = null;
let radarChart    = null;
let donutChart    = null;

function renderWaveformChart(points) {
  const ctx = document.getElementById("waveform-chart").getContext("2d");
  if (waveformChart) waveformChart.destroy();

  const labels = points.map((_, i) => i);
  const gradient = ctx.createLinearGradient(0, 0, 0, 120);
  gradient.addColorStop(0, "rgba(124,58,237,.6)");
  gradient.addColorStop(1, "rgba(6,182,212,.05)");

  waveformChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [{
        data:            points,
        borderColor:     "#A78BFA",
        borderWidth:     1.2,
        backgroundColor: gradient,
        pointRadius:     0,
        fill:            true,
        tension:         0.1,
      }],
    },
    options: {
      responsive:  true,
      animation:   { duration: 800 },
      plugins:     { legend: { display: false }, tooltip: { enabled: false } },
      scales: {
        x: { display: false },
        y: {
          display: true,
          grid:    { color: getThemeColor("rgba(255,255,255,.04)", "rgba(15,23,42,.06)") },
          ticks:   { color: "#64748B", font: { size: 9 } },
        },
      },
    },
  });
}

function renderRadarChart(scores, audio, semantic) {
  const ctx = document.getElementById("radar-chart").getContext("2d");
  if (radarChart) radarChart.destroy();

  const clarityScore  = Math.max(0, 1 - (audio.total_fillers || 0) * .05);
  const rate          = audio.speaking_rate || 0;
  const pacingScore   = (rate >= 110 && rate <= 160) ? 1
                       : Math.max(0, 0.6 - Math.abs(rate - 135) * 0.004);

  radarChart = new Chart(ctx, {
    type: "radar",
    data: {
      labels: ["Semantic", "Fluency", "Energy", "Clarity", "Pacing"],
      datasets: [{
        data:            [scores.semantic, scores.fluency,
                          Math.min(1, audio.rms_energy || 0),
                          clarityScore, pacingScore],
        backgroundColor: "rgba(124,58,237,.2)",
        borderColor:     "#A78BFA",
        borderWidth:     2,
        pointBackgroundColor: "#A78BFA",
        pointRadius:     5,
      }],
    },
    options: {
      responsive: true,
      animation:  { duration: 1000 },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => `${ctx.label}: ${(ctx.raw*100).toFixed(1)}%`
          }
        }
      },
      scales: {
        r: {
          min: 0, max: 1,
          ticks:        { display: false },
          grid:         { color: getThemeColor("rgba(255,255,255,.06)", "rgba(15,23,42,.08)") },
          angleLines:   { color: getThemeColor("rgba(255,255,255,.08)", "rgba(15,23,42,.1)") },
          pointLabels:  { color: getThemeColor("#CBD5E1", "#1E293B"), font: { size: 12, weight: "600" } },
        },
      },
    },
  });
}

function renderDonutChart(scores) {
  const ctx = document.getElementById("donut-chart").getContext("2d");
  if (donutChart) donutChart.destroy();

  const semContrib = scores.semantic * .6 * 100;
  const fluContrib = scores.fluency  * .4 * 100;

  donutChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Semantic (60%)", "Fluency (40%)"],
      datasets: [{
        data:            [semContrib, fluContrib],
        backgroundColor: ["rgba(124,58,237,.8)", "rgba(6,182,212,.8)"],
        borderColor:     ["#7C3AED", "#06B6D4"],
        borderWidth:     2,
        hoverOffset:     8,
      }],
    },
    options: {
      responsive: true,
      animation:  { duration: 1000 },
      cutout: "60%",
      plugins: {
        legend: {
          position: "bottom",
          labels:   { color: getThemeColor("#94A3B8", "#475569"), font: { size: 12 }, padding: 16 },
        },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.label}: ${ctx.raw.toFixed(1)} pts`,
          }
        }
      },
    },
  });
}


/* ══════════════════════════════════════════════════════════════════════════
   TABS (Results page)
══════════════════════════════════════════════════════════════════════════ */
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const tabId = btn.dataset.tab;
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.toggle("active", b === btn));
    document.querySelectorAll(".tab-panel").forEach(p => {
      p.classList.toggle("active", p.id === `tab-${tabId}`);
    });

    // Resize charts when visuals tab opens
    if (tabId === "visuals") {
      setTimeout(() => {
        waveformChart?.resize();
        radarChart?.resize();
        donutChart?.resize();
      }, 50);
    }
  });
});


/* ══════════════════════════════════════════════════════════════════════════
   HELPERS
══════════════════════════════════════════════════════════════════════════ */
function animateCounter(el, from, to, duration, fmt = v => v) {
  const start = performance.now();
  function step(now) {
    const p    = Math.min(1, (now - start) / duration);
    const ease = p < .5 ? 2 * p * p : -1 + (4 - 2 * p) * p;
    el.textContent = fmt(Math.round(from + (to - from) * ease));
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}


/* ══════════════════════════════════════════════════════════════════════════
   INIT
══════════════════════════════════════════════════════════════════════════ */
document.addEventListener("DOMContentLoaded", () => {
  loadConcepts();

  // Set sample audio href dynamically based on API_BASE
  const sampleLink = document.getElementById("download-sample-link");
  if (sampleLink) {
    sampleLink.href = `${API_BASE || window.location.origin}/sample.wav`;
  }

  // API health check
  fetch(`${API_BASE}/api/health`)
    .then(r => r.json())
    .then(d => console.log("✅ API online:", d))
    .catch(() => {
      showToast("⚠️ Python API offline. Start the FastAPI server on port 8000.", "error", 8000);
    });

  // Theme Toggle Logic
  const themeToggleBtn = document.getElementById("theme-toggle");
  const themeToggleIcon = document.getElementById("theme-toggle-icon");
  const themeToggleText = document.getElementById("theme-toggle-text");

  // Load saved theme or default to dark
  const savedTheme = localStorage.getItem("theme") || "dark";
  if (savedTheme === "light") {
    document.body.classList.add("light");
    if (themeToggleIcon) themeToggleIcon.textContent = "🌙";
    if (themeToggleText) themeToggleText.textContent = "Dark Mode";
  }

  themeToggleBtn?.addEventListener("click", () => {
    const isLight = document.body.classList.toggle("light");
    localStorage.setItem("theme", isLight ? "light" : "dark");
    
    if (themeToggleIcon) themeToggleIcon.textContent = isLight ? "🌙" : "☀️";
    if (themeToggleText) themeToggleText.textContent = isLight ? "Dark Mode" : "Light Mode";

    // Re-render charts to apply theme colors if results are showing
    if (analysisResult) {
      renderResults(analysisResult);
    }
  });
});
