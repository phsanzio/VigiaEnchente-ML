import numpy as np
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score

def calculate_kge(y_true, y_pred):
    """
    Calcula o Kling-Gupta Efficiency (KGE).
    
    Quando a previsão é constante (std_pred=0), aplica a convenção de
    Knoben et al. (2019): r=0 e alpha=0, resultando em KGE = 1 - sqrt(2) ≈ -0.414
    
    Referência: Knoben et al. (2019) - "Inherent benchmark or not? Comparing 
    Nash–Sutcliffe and Kling–Gupta efficiency scores" (HESS)
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    std_true = np.std(y_true)
    std_pred = np.std(y_pred)
    mean_true = np.mean(y_true)
    mean_pred = np.mean(y_pred)
    
    if std_pred == 0:
        r = 0.0
        alpha = 0.0
    else:
        r = np.corrcoef(y_true, y_pred)[0, 1]
        alpha = std_pred / std_true
    
    beta = mean_pred / mean_true
    
    kge = 1 - np.sqrt((r - 1)**2 + (alpha - 1)**2 + (beta - 1)**2)
    return float(kge)

def calculate_metrics(y_true, y_pred):
    rmse = root_mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    kge = calculate_kge(y_true, y_pred)
    
    return {
        'RMSE': rmse,
        'MAE': mae,
        'R2': r2,
        'KGE': kge
    }
