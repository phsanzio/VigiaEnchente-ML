import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import make_scorer
from xgboost import XGBRegressor
from src.metrics.metrics import calculate_kge


ROOT = Path(__file__).parent.parent.parent
PROCESSED = ROOT / "data" / "processed"

FEATURE_COLS = [
    'chuva_mm', 'temp_media', 'temp_max', 'temp_min', 'umidade_media',
    'chuva_3d', 'chuva_7d', 'chuva_14d', 'chuva_30d', 'chuva_60d', 'chuva_90d',
    'api_7d', 'api_30d',
    'chuva_ontem', 'chuva_anteontem', 'chuva_3d_atras', 'chuva_4d_atras',
    'sin_doy', 'cos_doy', 'vpd'
]


def tune_rf(X, y, tscv):
    print("Tuning Random Forest...")
    params = {
        'n_estimators': [100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5],
    }
    grid = GridSearchCV(
        RandomForestRegressor(random_state=42, n_jobs=-1),
        params,
        scoring=make_scorer(calculate_kge, greater_is_better=True),
        cv=tscv,
        verbose=1,
        n_jobs=-1
    )
    grid.fit(X, y)
    print(f"Best KGE: {grid.best_score_:.4f}")
    print(f"Best RF Params: {grid.best_params_}")
    return grid.best_params_, grid.best_score_


def tune_xgb(X, y, tscv):
    print("\nTuning XGBoost...")
    params = {
        'n_estimators': [100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.05, 0.1, 0.2],
    }
    grid = GridSearchCV(
        XGBRegressor(random_state=42, n_jobs=-1),
        params,
        scoring=make_scorer(calculate_kge, greater_is_better=True),
        cv=tscv,
        verbose=1,
        n_jobs=-1
    )
    grid.fit(X, y)
    print(f"Best KGE: {grid.best_score_:.4f}")
    print(f"Best XGB Params: {grid.best_params_}")
    return grid.best_params_, grid.best_score_


def run_tuning():
    df = pd.read_csv(PROCESSED / "final_database.csv", parse_dates=['data'])
    df = df.sort_values('data').reset_index(drop=True)
    train = df[df["data"].between("1997-01-01", "2016-12-31")].copy()
    X, y = train[FEATURE_COLS], train['target']
    
    print(f"Dados de treino: {len(X)} amostras (1997-2016)")
    print(f"Features: {len(FEATURE_COLS)}")
    
    time_series = TimeSeriesSplit(n_splits=5)
    
    rf_params, rf_score = tune_rf(X, y, time_series)
    xgb_params, xgb_score = tune_xgb(X, y, time_series)
    
    print("\n" + "="*50)
    print("RESULTADO FINAL DO TUNING")
    print("="*50)
    print(f"RF:  KGE={rf_score:.4f} | {rf_params}")
    print(f"XGB: KGE={xgb_score:.4f} | {xgb_params}")
    
    return rf_params, xgb_params

if __name__ == "__main__":
    run_tuning()