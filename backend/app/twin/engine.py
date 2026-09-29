import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from app.models.schemas import (
    EngineTwinState, HealthState, AnomalyState, 
    DegradationState, ExplanationPoint, EngineExplanation
)

class DigitalTwinEngine:
    def __init__(self):
        self.state: dict[str, EngineTwinState] = {}
        self.explanations: dict[str, EngineExplanation] = {}
        self.history: dict[str, list] = {}
        self.model_version = "v1.0"
        
        self.load_models()
        self.initialize_baseline()
        
    def load_models(self):
        base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        models_dir = os.path.join(base_dir, 'trained_models')
        
        try:
            self.anomaly_model = joblib.load(os.path.join(models_dir, 'anomaly_model.pkl'))
            self.rul_model = joblib.load(os.path.join(models_dir, 'rul_model.pkl'))
            self.meta = joblib.load(os.path.join(models_dir, 'meta.pkl'))
            self.features = self.meta['features']
        except Exception as e:
            print(f"Warning: Models not loaded. {e}")
            self.anomaly_model = None
            self.rul_model = None
            self.features = []

    def initialize_baseline(self):
        base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        data_file = os.path.join(base_dir, 'data', 'test_preprocessed.csv')
        if os.path.exists(data_file):
            try:
                df = pd.read_csv(data_file)
                for eng_id, unit_n in [("ENGINE_001", 1), ("ENGINE_002", 2), ("ENGINE_003", 3)]:
                    sub = df[df['unit_number'] == unit_n]
                    if not sub.empty:
                        first_row = sub.iloc[0]
                        self.update_state(eng_id, int(first_row['time_cycles']), first_row)
            except Exception as e:
                print(f"Baseline init warning: {e}")

    def _determine_status(self, health_index: float, anomaly_flag: bool) -> str:
        if health_index < 40:
            return "CRITICAL"
        if anomaly_flag or health_index < 70:
            return "WARNING"
        if health_index < 85:
            return "ATTENTION"
        return "NORMAL"
        
    def _determine_severity(self, anomaly_score: float) -> str:
        # isolation forest score goes from -0.5 to 0 (sometimes up to 0.5 depending on implementation)
        # where negative is anomalous. Let's normalize it for the prototype.
        # Scikit-learn IF: lower is more anomalous. We map lower values to HIGH severity.
        if anomaly_score < -0.15:
            return "HIGH"
        elif anomaly_score < 0:
            return "MEDIUM"
        return "LOW"

    def update_state(self, engine_id: str, cycle: int, data_row: pd.Series):
        if self.anomaly_model is None or self.rul_model is None:
            return None
            
        # Extract features
        x = data_row[self.features].values.reshape(1, -1)
        x_df = pd.DataFrame(x, columns=self.features)
        
        # Predict anomaly
        anomaly_pred = self.anomaly_model.predict(x_df)[0] # 1 for normal, -1 for anomaly
        anomaly_score_val = self.anomaly_model.score_samples(x_df)[0] # negative is anomalous
        is_anomaly = bool(anomaly_pred == -1)
        
        # Simple prototype explainability for IF (not true SHAP, but mock based on deviation from mean)
        # In a real app we'd use SHAP, here we just pick highest absolute deviation features for speed
        deviations = np.abs(x_df.values[0] - 0.5) # assuming normalized 0-1
        top_indices = deviations.argsort()[-3:][::-1]
        
        affected_feats = []
        explanation_points = []
        for idx in top_indices:
            feat_name = self.features[idx]
            affected_feats.append(feat_name)
            explanation_points.append(
                ExplanationPoint(
                    feature=feat_name,
                    importance=float(deviations[idx]),
                    direction="increasing anomaly"
                )
            )
            
        self.explanations[engine_id] = EngineExplanation(
            engine_id=engine_id,
            top_contributors=explanation_points
        )
        
        # Predict RUL
        rul_pred = float(self.rul_model.predict(x_df)[0])
        
        # Health Index calculation (prototype formula)
        # Assume max RUL is ~130. Health is bounded 0-100.
        health_index = max(0.0, min(100.0, (rul_pred / 130.0) * 100.0))
        if is_anomaly:
            health_index = max(0.0, health_index - 15.0) # Penalty for anomaly
            
        # Degradation trend
        trend = "Stable"
        if engine_id in self.history and len(self.history[engine_id]) > 5:
            past_health = self.history[engine_id][-5].health_state.health_index
            if past_health - health_index > 5:
                trend = "Accelerated"
            elif past_health - health_index > 1:
                trend = "Moderate"
                
        status = self._determine_status(health_index, is_anomaly)
        severity = self._determine_severity(anomaly_score_val)
        
        # Convert operating conditions and sensor states
        op_conds = {
            "op_setting_1": float(data_row.get("op_setting_1", 0)),
            "op_setting_2": float(data_row.get("op_setting_2", 0)),
            "op_setting_3": float(data_row.get("op_setting_3", 0))
        }
        
        sensor_state = {f: float(data_row.get(f, 0)) for f in self.features}
        
        new_state = EngineTwinState(
            engine_id=engine_id,
            timestamp=datetime.utcnow(),
            cycle=cycle,
            operating_conditions=op_conds,
            sensor_state=sensor_state,
            health_state=HealthState(health_index=round(health_index, 1), status=status),
            anomaly_state=AnomalyState(
                score=round(float(anomaly_score_val), 3),
                flag=is_anomaly,
                severity=severity,
                affected_features=affected_feats
            ),
            degradation_state=DegradationState(trend=trend),
            predicted_rul=round(rul_pred, 1),
            confidence=0.85, # mock confidence
            model_version=self.model_version,
            last_update=datetime.utcnow()
        )
        
        self.state[engine_id] = new_state
        
        if engine_id not in self.history:
            self.history[engine_id] = []
        self.history[engine_id].append(new_state)
        
        return new_state
        
    def get_state(self, engine_id: str):
        return self.state.get(engine_id)
        
    def get_history(self, engine_id: str):
        return self.history.get(engine_id, [])
        
    def get_explanation(self, engine_id: str):
        return self.explanations.get(engine_id)

twin_engine = DigitalTwinEngine()
