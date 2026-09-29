import os
import json
import pandas as pd
import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

def evaluate_models():
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    data_dir = os.path.join(base_dir, 'backend', 'data')
    models_dir = os.path.join(base_dir, 'backend', 'trained_models')
    results_dir = os.path.join(base_dir, 'backend', 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    test_file = os.path.join(data_dir, 'test_preprocessed.csv')
    meta_file = os.path.join(models_dir, 'meta.pkl')
    rul_model_file = os.path.join(models_dir, 'rul_model.pkl')
    
    print("Loading test data and models...")
    df = pd.read_csv(test_file)
    meta = joblib.load(meta_file)
    features = meta['features']
    
    rul_model = joblib.load(rul_model_file)
    
    # We evaluate RUL model on the LAST cycle of each unit in the test set
    # because the provided true RUL is for the last recorded cycle
    last_cycle_df = df.groupby('unit_number').last().reset_index()
    X_test = last_cycle_df[features]
    y_true = last_cycle_df['RUL']
    
    print("Evaluating RUL model...")
    y_pred = rul_model.predict(X_test)
    
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    metrics = {
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "R2": round(r2, 4)
    }
    
    print(f"RUL Model Metrics: {metrics}")
    
    with open(os.path.join(results_dir, 'metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=4)
        
    print("Evaluation complete.")

if __name__ == "__main__":
    evaluate_models()
