import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from metrics.metrics import calculate_metrics
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).parent.parent.parent
PROCESSED = ROOT / "data" / "processed"
MODELS = ROOT / "models"
MODELS.mkdir(parents=True, exist_ok=True)

FEATURE_COLS = [
    'chuva_mm', 'temp_media', 'temp_max', 'temp_min', 'umidade_media',
    'chuva_3d', 'chuva_7d', 'chuva_14d', 'chuva_30d', 'chuva_60d', 'chuva_90d',
    'api_7d', 'api_30d',
    'chuva_ontem', 'chuva_anteontem', 'chuva_3d_atras', 'chuva_4d_atras',
    'sin_doy', 'cos_doy', 'vpd'
]

def split_database(df):
    df = df.sort_values('data').reset_index(drop=True)
    train = df[df["data"].between("1997-01-01", "2016-12-31")].copy()
    validate = df[df["data"].between("2017-01-01", "2021-12-31")].copy()
    test = df[df["data"] >= "2022-01-01"].copy()
    X_train, y_train = train[FEATURE_COLS], train['target']
    X_val, y_val = validate[FEATURE_COLS], validate['target']
    X_test, y_test = test[FEATURE_COLS], test['target']
    return X_train, X_val, X_test, y_train, y_val, y_test

def train_rf(X_train, y_train, X_val, y_val):
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    y_pred_val = rf.predict(X_val)
    results_val = {'model': 'RandomForest (Validation)', 'metrics': calculate_metrics(y_val, y_pred_val)}
    print(results_val)
    
    joblib.dump(rf, MODELS / "random_forest.joblib")

def train_xgb(X_train, y_train, X_val, y_val):
    xgb = XGBRegressor(n_estimators=100, random_state=42)
    xgb.fit(X_train, y_train)
    
    y_pred_val = xgb.predict(X_val)
    results_val = {'model': 'XGBoost (Validation)', 'metrics': calculate_metrics(y_val, y_pred_val)}
    print(results_val)
    
    joblib.dump(xgb, MODELS / "xgboost.joblib")

def train_ridge(X_train, y_train, X_val, y_val):
    ridge = Ridge()
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    ridge.fit(X_train_scaled, y_train)
    y_pred_ridge = ridge.predict(X_val_scaled)
    results_ridge = {'model': 'Ridge (Validation)', 'metrics': calculate_metrics(y_val, y_pred_ridge)}
    print(results_ridge)
    joblib.dump(ridge, MODELS / "ridge.joblib")
    joblib.dump(scaler, MODELS / "ridge_scaler.joblib")

def baseline_climatologica(y_train, y_val):
    media_treino = y_train.mean()
    y_pred = np.full(len(y_val), media_treino)
    results_baseline = {'model': 'Baseline (Validation)', 'metrics': calculate_metrics(y_val, y_pred)}
    print(results_baseline)

def train_all_models():
    final_database = pd.read_csv(PROCESSED / "final_database.csv", parse_dates=['data'])
    X_train, X_val, y_train, y_val = split_database(final_database)
    train_rf(X_train, y_train, X_val, y_val)
    train_xgb(X_train, y_train, X_val, y_val)
    train_ridge(X_train, y_train, X_val, y_val)
    baseline_climatologica(y_train, y_val)
    print(f"\nModelos salvos em: {MODELS}")
