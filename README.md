# AeroTwin
**AI-Enabled Real-Time Digital Twin System for Health Monitoring, Fault Prediction and Mission Reliability Enhancement of Aero Piston Engines used in MALE UAVs**

*MONITOR. DETECT. PREDICT. PROTECT.*

**Disclaimer:** This is a research/demo prototype validating the predictive-health-monitoring architecture using public aerospace prognostics data. It is not certified for operational aircraft decisions and is not trained on actual MALE UAV piston engine data.

## Project Structure

```text
AeroTwin/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── models/
│   │   ├── twin/
│   │   ├── replay/
│   ├── data/                 # Raw and preprocessed dataset files
│   ├── trained_models/       # ML Models (RandomForest, IsolationForest)
│   ├── results/              # Evaluation metrics
│   └── requirements.txt
├── frontend/                 # React + Vite + TailwindCSS Dashboard
├── scripts/
│   ├── download_data.py
│   ├── preprocess.py
│   ├── train_anomaly.py
│   ├── train_rul.py
│   └── evaluate.py
└── README.md
```

## 1. Dataset Setup Instructions

NASA C-MAPSS dataset is used as a placeholder due to the lack of public MALE-UAV run-to-failure datasets.
*If the `download_data.py` script fails, please manually download the dataset.*

1. Go to NASA Prognostics Data Repository or a public mirror of CMAPSS data.
2. Download `train_FD001.txt`, `test_FD001.txt`, and `RUL_FD001.txt`.
3. Place these files inside `backend/data/`.

## 2. Model Training Instructions

Once the dataset is placed in `backend/data/`:

```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # (Windows)
# source venv/bin/activate    # (Linux/Mac)

# Install dependencies
pip install -r backend/requirements.txt

# Run preprocessing and model training
python scripts/preprocess.py
python scripts/train_anomaly.py
python scripts/train_rul.py
python scripts/evaluate.py
```

## 3. How to Start Backend

```bash
# Ensure virtual environment is active
.\venv\Scripts\Activate.ps1
# Run FastAPI server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
API Documentation will be available at `http://localhost:8000/docs`

## 4. How to Start Frontend

```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

## 5. Dashboard Features

- **Real Dataset Processing:** Visualizes predictions from actual trained models.
- **Replay Engine:** Simulates real-time telemetry streaming from historic test files.
- **Engine Health & RUL:** Shows predicted remaining useful life and computed health score.
- **Digital Twin State:** Maintains the latest computation state of the selected engine.
- **Explainable AI:** Highlights the features contributing most to anomaly severity.

## 6. Implementation Status

This prototype implements ~35% of the overall conceptual architecture:
- ✅ Backend Architecture & REST API
- ✅ Data Preprocessing & Scaling Pipeline
- ✅ Baseline ML Models (Isolation Forest, Random Forest)
- ✅ Replay Engine & Live Twin State
- ✅ Working Interactive Dashboard
- ❌ Actual MALE UAV Data (Placeholder used)
- ❌ Physics-based Engine Simulation (Pure data-driven prototype)
- ❌ Edge deployment / C++ Embedded logic
- ❌ Live WebSockets (HTTP Polling used for prototype simplicity)
