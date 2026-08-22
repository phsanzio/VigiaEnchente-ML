import json
import time
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from sklearn.metrics import make_scorer
from xgboost import XGBRegressor
from scipy.stats import randint, uniform, loguniform
from src.metrics.metrics import calculate_kge
from src.configuration.config import FEATURE_COLS, MODELS
from src.utils.data_utils import get_train_df
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def tune_rf(X, y, time_series, n_iter=60):
    print(f"Tuning Random Forest ({n_iter} iteracoes aleatorias continuas)...")
    
    params = {
        'n_estimators': randint(100, 1500),
        'max_depth': randint(10, 50),
        'min_samples_split': randint(2, 16),
        'min_samples_leaf': randint(1, 12),
        'max_features': ['sqrt', 'log2', 0.5, 0.8],
        'max_samples': uniform(0.5, 0.4)
    }
    
    random_search = RandomizedSearchCV(
        estimator=RandomForestRegressor(random_state=42, n_jobs=-1),
        param_distributions=params,
        n_iter=n_iter, 
        scoring=make_scorer(calculate_kge, greater_is_better=True),
        cv=time_series,
        verbose=1,
        n_jobs=-1,
        random_state=42
    )
    
    random_search.fit(X, y)
    print(f"Best RF KGE: {random_search.best_score_:.4f}")
    return random_search.best_params_, random_search.best_score_


def tune_xgb(X, y, time_series, n_iter=60):
    print(f"\nTuning XGBoost ({n_iter} iteracoes aleatorias continuas)...")
    
    params = {
        'n_estimators': randint(200, 3500),
        'learning_rate': loguniform(1e-3, 1e-1),
        'max_depth': randint(3, 16),
        'min_child_weight': uniform(1.0, 5.0),
        'subsample': uniform(0.4, 0.5),
        'colsample_bytree': uniform(0.4, 0.5),
        'gamma': uniform(0.0, 0.5),
        'reg_lambda': uniform(1.0, 59.0)
    }
    
    random_search = RandomizedSearchCV(
        estimator=XGBRegressor(random_state=42, n_jobs=-1),
        param_distributions=params,
        n_iter=n_iter,
        scoring=make_scorer(calculate_kge, greater_is_better=True),
        cv=time_series,
        verbose=1,
        n_jobs=-1,
        random_state=42
    )
    
    random_search.fit(X, y)
    print(f"Best XGB KGE: {random_search.best_score_:.4f}")
    return random_search.best_params_, random_search.best_score_


def run_tuning():
    start_time = time.time() 
    
    train_df = get_train_df()
    X, y = train_df[FEATURE_COLS], train_df['target']
    
    time_series = TimeSeriesSplit(n_splits=5)
    
    rf_params, rf_score = tune_rf(X, y, time_series, n_iter=60)
    xgb_params, xgb_score = tune_xgb(X, y, time_series, n_iter=60)
    
    end_time = time.time() 
    elapsed_minutes = (end_time - start_time) / 60
    
    print("\n" + "="*50)
    print("RESULTADO FINAL DO TUNING")
    print("="*50)
    print(f"Tempo total de execucao: {elapsed_minutes:.2f} minutos")
    print(f"RF:  KGE={rf_score:.4f} | {rf_params}")
    print(f"XGB: KGE={xgb_score:.4f} | {xgb_params}")
    
    best_params = {
        "random_forest": rf_params,
        "xgboost": xgb_params
    }
    
    MODELS.mkdir(parents=True, exist_ok=True)
    with open(MODELS / "best_params.json", "w") as f:
        json.dump(best_params, f, indent=4)
        
    print(f"\nParametros salvos em {MODELS / 'best_params.json'}")
    
    return best_params

if __name__ == "__main__":
    run_tuning()
