// ─────────────────────────────────────────────────────────────────────────────
// server/server.js  –  VBCUA Node.js Express Server
// Serves frontend static files + proxies /api/* to Python FastAPI (port 8000)
// ─────────────────────────────────────────────────────────────────────────────

require("dotenv").config();
const express    = require("express");
const cors       = require("cors");
const morgan     = require("morgan");
const path       = require("path");
const http       = require("http");
const https      = require("https");
const { createProxyMiddleware } = require("http-proxy-middleware");

const app  = express();
const PORT = process.env.PORT || 3000;
const PYTHON_API = process.env.PYTHON_API || "http://localhost:8000";

// ── Middleware ────────────────────────────────────────────────────────────────
app.use(cors());
app.use(morgan("dev"));

// ── API Proxy → Python FastAPI ────────────────────────────────────────────────
// All /api/* requests are forwarded to the Python backend
app.use(
  createProxyMiddleware({
    target:       PYTHON_API,
    changeOrigin: true,
    pathFilter:   "/api",
    // Increase timeout for long AI processing (5 min)
    proxyTimeout: 300_000,
    timeout:      300_000,
    on: {
      error: (err, req, res) => {
        console.error("[Proxy Error]", err.message);
        res.status(502).json({
          error:   "Python backend unreachable",
          detail:  err.message,
          hint:    `Make sure the Python API is running on ${PYTHON_API}`,
        });
      },
    },
  })
);

// ── Static frontend ───────────────────────────────────────────────────────────
const FRONTEND_DIR = path.join(__dirname, "..", "frontend");
app.use(express.static(FRONTEND_DIR));

// SPA fallback – all non-API routes serve index.html
app.get("*", (req, res) => {
  res.sendFile(path.join(FRONTEND_DIR, "index.html"));
});

// ── Start ─────────────────────────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`
  ╔══════════════════════════════════════════════╗
  ║   🎙️  VBCUA Node.js Server                  ║
  ║──────────────────────────────────────────────║
  ║   Frontend : http://localhost:${PORT}           ║
  ║   API Proxy: ${PYTHON_API}/api/*       ║
  ╚══════════════════════════════════════════════╝
  `);
});
