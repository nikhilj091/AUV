from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os
import json
import joblib
from app.twin.engine import twin_engine
from app.replay.engine import replay_engine
from app.models.schemas import EngineTwinState, ReplayStatus

router = APIRouter()

# --- Health & Models ---
@router.get("/health")
def get_health():
    return {"status": "ok", "backend": "online"}

@router.get("/models")
def get_models():
    return {
        "anomaly_model": "Isolation Forest",
        "rul_model": "Random Forest Regressor",
        "version": twin_engine.model_version
    }

@router.get("/model/metrics")
def get_model_metrics():
    base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
    metrics_path = os.path.join(base_dir, 'results', 'metrics.json')
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            return json.load(f)
    return {"error": "Metrics not found"}

@router.get("/dataset/summary")
def get_dataset_summary():
    base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
    models_dir = os.path.join(base_dir, 'trained_models')
    try:
        meta = joblib.load(os.path.join(models_dir, 'meta.pkl'))
        features = len(meta['features'])
    except:
        features = 14
        
    return {
        "name": "NASA C-MAPSS",
        "type": "Aerospace Prognostics",
        "engines": 100, # Approx for FD001
        "features": features
    }

# --- Engine Data ---
@router.get("/engine/{engine_id}/history")
def get_engine_history(engine_id: str):
    history = twin_engine.get_history(engine_id)
    return history

@router.get("/engine/{engine_id}/health")
def get_engine_health(engine_id: str):
    state = twin_engine.get_state(engine_id)
    if state:
        return state.health_state
    raise HTTPException(status_code=404, detail="Engine not found or no state")

@router.get("/engine/{engine_id}/rul")
def get_engine_rul(engine_id: str):
    state = twin_engine.get_state(engine_id)
    if state:
        return {"predicted_rul": state.predicted_rul}
    raise HTTPException(status_code=404, detail="Engine not found")

@router.get("/engine/{engine_id}/anomalies")
def get_engine_anomalies(engine_id: str):
    state = twin_engine.get_state(engine_id)
    if state:
        return state.anomaly_state
    raise HTTPException(status_code=404, detail="Engine not found")
    
@router.get("/engine/{engine_id}/degradation")
def get_engine_degradation(engine_id: str):
    state = twin_engine.get_state(engine_id)
    if state:
        return state.degradation_state
    raise HTTPException(status_code=404, detail="Engine not found")

@router.get("/sensors/{engine_id}")
def get_engine_sensors(engine_id: str):
    state = twin_engine.get_state(engine_id)
    if state:
        return state.sensor_state
    raise HTTPException(status_code=404, detail="Engine not found")

@router.get("/explain/{engine_id}")
def get_engine_explanation(engine_id: str):
    exp = twin_engine.get_explanation(engine_id)
    if exp:
        return exp
    raise HTTPException(status_code=404, detail="Explanation not found")

# --- Digital Twin ---
@router.get("/twin/state/{engine_id}", response_model=EngineTwinState)
def get_twin_state(engine_id: str):
    state = twin_engine.get_state(engine_id)
    if state:
        return state
    raise HTTPException(status_code=404, detail="Engine twin state not found")

# --- Replay Engine ---
class ReplayStartRequest(BaseModel):
    engine_id: str
    
class ReplaySpeedRequest(BaseModel):
    speed: float

@router.post("/replay/start")
async def start_replay(req: ReplayStartRequest):
    replay_engine.start(req.engine_id)
    return {"status": "started", "engine_id": req.engine_id}

@router.post("/replay/pause")
async def pause_replay():
    replay_engine.pause()
    return {"status": "paused"}

@router.post("/replay/resume")
async def resume_replay():
    replay_engine.resume()
    return {"status": "resumed"}

@router.post("/replay/stop")
async def stop_replay():
    replay_engine.stop()
    return {"status": "stopped"}

@router.post("/replay/reset")
async def reset_replay():
    replay_engine.reset()
    return {"status": "reset"}

@router.post("/replay/speed")
async def set_replay_speed(req: ReplaySpeedRequest):
    replay_engine.set_speed(req.speed)
    return {"status": "speed updated", "speed": req.speed}

@router.get("/replay/status", response_model=ReplayStatus)
def get_replay_status():
    total = len(replay_engine.data) if replay_engine.data is not None else 0
    return ReplayStatus(
        status=replay_engine.status,
        engine_id=replay_engine.engine_id,
        current_cycle=replay_engine.current_index,
        total_cycles=total,
        speed=replay_engine.speed
    )
