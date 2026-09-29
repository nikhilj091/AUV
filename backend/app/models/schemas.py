from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class HealthState(BaseModel):
    health_index: float
    status: str

class AnomalyState(BaseModel):
    score: float
    flag: bool
    severity: str
    affected_features: List[str] = []

class DegradationState(BaseModel):
    trend: str

class EngineTwinState(BaseModel):
    engine_id: str
    timestamp: datetime
    cycle: int
    operating_conditions: Dict[str, float]
    sensor_state: Dict[str, float]
    health_state: HealthState
    anomaly_state: AnomalyState
    degradation_state: DegradationState
    predicted_rul: float
    confidence: float
    model_version: str
    last_update: datetime
    
class ExplanationPoint(BaseModel):
    feature: str
    importance: float
    direction: str

class EngineExplanation(BaseModel):
    engine_id: str
    top_contributors: List[ExplanationPoint]

class ReplayStatus(BaseModel):
    status: str
    engine_id: Optional[str]
    current_cycle: int
    total_cycles: int
    speed: float
