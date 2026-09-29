import os
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest

def train_anomaly():
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    data_dir = os.path.join(base_dir, 'backend', 'data')
    models_dir = os.path.join(base_dir, 'backend', 'trained_models')
    
    train_file = os.path.join(data_dir, 'train_preprocessed.csv')
    meta_file = os.path.join(models_dir, 'meta.pkl')
    
    print("Loading data for anomaly detection training...")
    df = pd.read_csv(train_file)
    meta = joblib.load(meta_file)
    features = meta['features']
    
    X_train = df[features]
    
    print("Training Isolation Forest...")
    # Assume 1% anomaly rate in training data for baseline
    iso_forest = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
    iso_forest.fit(X_train)
    
    model_path = os.path.join(models_dir, 'anomaly_model.pkl')
    joblib.dump(iso_forest, model_path)
    
    print("Anomaly model trained and saved successfully.")

if __name__ == "__main__":
    train_anomaly()
