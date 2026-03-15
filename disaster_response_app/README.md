# Smart Disaster Response Assistant (Web App)

A hackathon-ready disaster triage system that ingests social and weather alerts, calculates real-time risk scores, and visualizes hotspots on a custom web dashboard.

## 🏗 Architecture

- **Backend:** FastAPI (Python) with SQLModel & SQLite.
- **Frontend:** HTML5, CSS3, and Vanilla JavaScript with Leaflet.js for mapping.
- **AI Triage:** Rule-based fallback or OpenAI-powered classification.

## Setup

1. **Environment**

   ```bash
   cd disaster_response_app
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

2. **Backend Configuration**

   - Add your `OPENAI_API_KEY` to `.env` for AI classification.

## 🏃‍♂️ Running the App

### 1. Start the Backend (Terminal A)

```bash
uvicorn app.backend.main:app --reload --port 8000
```

### 2. Seed Initial Data (Terminal B)

Wait for the backend to start, then run:

```bash
python -m app.backend.seed_data
```

### 3. Open the Dashboard

Simply open `app/frontend/index.html` in your web browser.

## 📂 Project Structure

```text
disaster_response_app/
├── app/
│   ├── backend/         # FastAPI Logic
│   │   ├── main.py      # API Endpoints
│   │   ├── models.py    # DB Schema
│   │   ├── risk.py      # Risk Scoring
│   │   └── cluster.py   # Spatial Clustering
│   └── frontend/        # Web Assets
│       ├── index.html   # Dashboard UI
│       ├── style.css    # Custom Styling
│       └── main.js      # Map & API Logic
├── data/                # Seed JSON files
└── requirements.txt     # Python dependencies
```
