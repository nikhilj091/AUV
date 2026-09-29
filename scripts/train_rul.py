import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor

def train_rul():
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    data_dir = os.path.join(base_dir, 'backend', 'data')
    models_dir = os.path.join(base_dir, 'backend', 'trained_models')
    
    train_file = os.path.join(data_dir, 'train_preprocessed.csv')
    meta_file = os.path.join(models_dir, 'meta.pkl')
    
    print("Loading data for RUL prediction training...")
    df = pd.read_csv(train_file)
    meta = joblib.load(meta_file)
    features = meta['features']
    
    X_train = df[features]
    y_train = df['RUL']
    
    print("Training Random Forest Regressor for RUL...")
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    
    model_path = os.path.join(models_dir, 'rul_model.pkl')
    joblib.dump(rf_model, model_path)
    
    print("RUL model trained and saved successfully.")

if __name__ == "__main__":
    train_rul()
