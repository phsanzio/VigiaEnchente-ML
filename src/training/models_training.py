import json
import numpy as np
import joblib
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from src.metrics.metrics import calculate_metrics
from src.utils.data_utils import get_train_df, get_val_df
from src.utils.results_utils import save_metrics
from src.configuration.config import MODELS, FEATURE_COLS


def train_rf(X_train, y_train, X_val, y_val, params=None):
    model_params = params if params else {'n_estimators': 100, 'random_state': 42}
    if 'random_state' not in model_params:
        model_params['random_state'] = 42
    
    rf = RandomForestRegressor(**model_params)
    rf.fit(X_train, y_train)
    
    y_pred_val = rf.predict(X_val)
    metrics = calculate_metrics(y_val, y_pred_val)
    
    print(f"RandomForest (Validation): {metrics}")
    save_metrics('RandomForest', metrics, 'validation', params=model_params)
    
    joblib.dump(rf, MODELS / "random_forest.joblib")
    return rf, metrics


def train_xgb(X_train, y_train, X_val, y_val, params=None):
    model_params = params if params else {'n_estimators': 100, 'random_state': 42}
    if 'random_state' not in model_params:
        model_params['random_state'] = 42
    
    xgb = XGBRegressor(**model_params)
    xgb.fit(X_train, y_train)
    
    y_pred_val = xgb.predict(X_val)
    metrics = calculate_metrics(y_val, y_pred_val)
    
    print(f"XGBoost (Validation): {metrics}")
    save_metrics('XGBoost', metrics, 'validation', params=model_params)
    
    joblib.dump(xgb, MODELS / "xgboost.joblib")
    return xgb, metrics


def train_ridge(X_train, y_train, X_val, y_val):
    ridge = Ridge()
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    ridge.fit(X_train_scaled, y_train)
    
    y_pred_val = ridge.predict(X_val_scaled)
    metrics = calculate_metrics(y_val, y_pred_val)
    
    print(f"Ridge (Validation): {metrics}")
    save_metrics('Ridge', metrics, 'validation')
    
    joblib.dump(ridge, MODELS / "ridge.joblib")
    joblib.dump(scaler, MODELS / "ridge_scaler.joblib")
    return ridge, metrics


def baseline_null_mean(y_train, y_val):
    mean_train = y_train.mean()
    y_pred = np.full(len(y_val), mean_train)
    metrics = calculate_metrics(y_val, y_pred)
    
    print(f"Baseline Null Mean (Validation): {metrics}")
    save_metrics('Baseline_NullMean', metrics, 'validation')
    
    return y_pred, metrics


def baseline_daily_climatology(train_df, val_df):
    doy_mean = train_df.groupby(train_df['data'].dt.dayofyear)['target'].mean()
    y_pred = val_df['data'].dt.dayofyear.map(doy_mean)
    y_pred = y_pred.fillna(train_df['target'].mean())
    metrics = calculate_metrics(val_df['target'], y_pred)
    
    print(f"Baseline Daily Climatology (Validation): {metrics}")
    save_metrics('Baseline_DailyClimatology', metrics, 'validation')
    
    return y_pred, metrics


def train_all_models():
    train_df = get_train_df()
    val_df = get_val_df()
    
    X_train, y_train = train_df[FEATURE_COLS], train_df['target']
    X_val, y_val = val_df[FEATURE_COLS], val_df['target']
    
    print("\n=== Treinamento inicial (parâmetros default) ===\n")
    
    train_rf(X_train, y_train, X_val, y_val)
    train_xgb(X_train, y_train, X_val, y_val)
    train_ridge(X_train, y_train, X_val, y_val)
    baseline_null_mean(y_train, y_val)
    baseline_daily_climatology(train_df, val_df)
    
    print(f"\nModelos salvos em: {MODELS}")


def retrain_best_models():
    params_path = MODELS / "best_params.json"
    
    if not params_path.exists():
        print("Arquivo best_params.json não encontrado. Rode o tuning primeiro!")
        return
    
    with open(params_path, 'r') as f:
        best_params = json.load(f)
    
    train_df = get_train_df()
    val_df = get_val_df()
    
    X_train, y_train = train_df[FEATURE_COLS], train_df['target']
    X_val, y_val = val_df[FEATURE_COLS], val_df['target']
    
    print("\n=== Retreinando com parâmetros otimizados ===\n")
    
    rf_params = best_params.get("random_forest")
    xgb_params = best_params.get("xgboost")
    
    if rf_params:
        train_rf(X_train, y_train, X_val, y_val, params=rf_params)
    
    if xgb_params:
        train_xgb(X_train, y_train, X_val, y_val, params=xgb_params)
    
    print(f"\nModelos otimizados salvos em: {MODELS}")


if __name__ == "__main__":
    train_all_models()
