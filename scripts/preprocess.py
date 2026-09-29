import os
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler

def load_cmapss_data(file_path):
    # Columns for C-MAPSS dataset
    columns = ['unit_number', 'time_cycles', 'op_setting_1', 'op_setting_2', 'op_setting_3']
    columns += [f'sensor_{i}' for i in range(1, 22)]
    
    df = pd.read_csv(file_path, sep=r'\s+', header=None, names=columns)
    return df

def generate_rul(df):
    # Group by unit_number and find max time_cycles
    max_cycles = df.groupby('unit_number')['time_cycles'].max().reset_index()
    max_cycles.rename(columns={'time_cycles': 'max_time'}, inplace=True)
    
    # Merge back to original dataframe
    df = df.merge(max_cycles, on='unit_number', how='left')
    
    # Calculate RUL
    df['RUL'] = df['max_time'] - df['time_cycles']
    df.drop('max_time', axis=1, inplace=True)
    
    # Piecewise linear degradation model for RUL
    # (clip maximum RUL to 130 to improve prediction of end-of-life)
    df['RUL'] = df['RUL'].clip(upper=130)
    return df

def preprocess_data():
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    data_dir = os.path.join(base_dir, 'backend', 'data')
    models_dir = os.path.join(base_dir, 'backend', 'trained_models')
    os.makedirs(models_dir, exist_ok=True)
    
    train_file = os.path.join(data_dir, 'train_FD001.txt')
    test_file = os.path.join(data_dir, 'test_FD001.txt')
    rul_file = os.path.join(data_dir, 'RUL_FD001.txt')
    
    print("Loading raw data...")
    train_df = load_cmapss_data(train_file)
    test_df = load_cmapss_data(test_file)
    
    print("Generating RUL for training data...")
    train_df = generate_rul(train_df)
    
    # Generate RUL for test data
    truth_df = pd.read_csv(rul_file, sep=r'\s+', header=None, names=['RUL'])
    truth_df['unit_number'] = truth_df.index + 1
    
    test_max_cycles = test_df.groupby('unit_number')['time_cycles'].max().reset_index()
    test_max_cycles = test_max_cycles.merge(truth_df, on='unit_number')
    test_max_cycles['max_time'] = test_max_cycles['time_cycles'] + test_max_cycles['RUL']
    
    test_df = test_df.merge(test_max_cycles[['unit_number', 'max_time']], on='unit_number', how='left')
    test_df['RUL'] = test_df['max_time'] - test_df['time_cycles']
    test_df.drop('max_time', axis=1, inplace=True)
    test_df['RUL'] = test_df['RUL'].clip(upper=130)
    
    # Features to use (drop constant sensors and some settings)
    # Usually sensors 1, 5, 6, 10, 16, 18, 19 are constant in FD001
    drop_sensors = ['sensor_1', 'sensor_5', 'sensor_6', 'sensor_10', 'sensor_16', 'sensor_18', 'sensor_19']
    drop_cols = ['unit_number', 'time_cycles', 'op_setting_1', 'op_setting_2', 'op_setting_3'] + drop_sensors + ['RUL']
    
    features = [c for c in train_df.columns if c not in drop_cols]
    
    print("Fitting scaler on training data...")
    scaler = MinMaxScaler()
    train_df[features] = scaler.fit_transform(train_df[features])
    test_df[features] = scaler.transform(test_df[features])
    
    scaler_path = os.path.join(models_dir, 'scaler.pkl')
    joblib.dump(scaler, scaler_path)
    
    # Save preprocessed metadata
    meta = {
        'features': features,
        'drop_sensors': drop_sensors,
        'version': '1.0'
    }
    joblib.dump(meta, os.path.join(models_dir, 'meta.pkl'))
    
    print("Saving preprocessed datasets...")
    train_df.to_csv(os.path.join(data_dir, 'train_preprocessed.csv'), index=False)
    test_df.to_csv(os.path.join(data_dir, 'test_preprocessed.csv'), index=False)
    
    print("Preprocessing complete.")

if __name__ == "__main__":
    preprocess_data()
