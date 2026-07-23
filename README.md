# Voice Based Concept Understanding Analyser (VBCUA)

VBCUA is an AI-powered application that evaluates how well a user understands a concept from a spoken explanation. It combines speech recognition, semantic analysis, audio feature extraction, scoring, interactive visualizations, and PDF report generation.

## What this project uses

* **Python** and **Streamlit** for the main analytical app
* **FastAPI** for the Python API layer
* **Node.js** and **Express** for the web server and proxy layer
* **OpenAI Whisper** for speech-to-text transcription
* **Sentence-BERT** for semantic similarity scoring
* **Librosa** for audio feature analysis
* **ReportLab** for generating PDF reports
* **HTML, CSS, JavaScript**, and **Chart.js** for the frontend

## Project Structure

* `backend/` - Python backend, analysis modules, and app styling
* `frontend/` - Frontend UI, sample audio, and static assets
* `server/` - Node.js server that serves the frontend and proxies API requests
* `project_video_demo/` - Folder reserved for demo video files and presentation assets
* `MyProject/` - Existing repository folder structure kept intact

## How to clone the repository

If you want to get this project on your computer, use:

```bash
git clone https://github.com
cd Voice-based-concept-understanding-analyser
```

If you already have the repo, you can update it with:

```bash
git pull origin main
```

## Installation

### 1. Python backend requirements
Install the Python dependencies from the backend folder:

```bash
cd "MyProject/voice intern project/backend"
pip install -r requirements.txt
```

### 2. Node.js server requirements
Install the Node.js dependencies from the server folder:

```bash
cd ../server
npm install
```

## How to run the project
There are two main ways to use the project.

### Option 1: Run the Python API + Node server + frontend
Start the Python API first:

```bash
cd "MyProject/voice intern project/backend"
uvicorn api:app --reload --port 8000
```

Then start the Node server in a second terminal:

```bash
cd "MyProject/voice intern project/server"
npm start
```

After that, open the frontend in your browser at the local address shown by the Node server, usually `http://localhost:3000`.

### Option 2: Run the Streamlit app directly
If you want to launch the Streamlit interface directly:

```bash
cd "MyProject/voice intern project/backend"
streamlit run app.py
```

## Features

* Upload or record spoken explanations
* Transcribe speech into text
* Compare the transcript against concept references
* Analyse fluency and audio quality metrics
* Generate score summaries and feedback
* Download a formatted PDF report

## Notes

* Temporary session data is stored under `backend/temp/`.
* The sample audio file used by the frontend is located in `frontend/sample.wav`.
* The repository keeps the original documentation folders at the root, along with the project inside `MyProject/voice intern project/`.
