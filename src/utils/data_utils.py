import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
PROCESSED = ROOT / "data" / "processed"

FEATURE_COLS = [
    'chuva_mm', 'temp_media', 'temp_max', 'temp_min', 'umidade_media',
    'chuva_3d', 'chuva_7d', 'chuva_14d', 'chuva_30d', 'chuva_60d', 'chuva_90d',
    'api_7d', 'api_30d',
    'chuva_ontem', 'chuva_anteontem', 'chuva_3d_atras', 'chuva_4d_atras',
    'sin_doy', 'cos_doy', 'vpd'
]

def get_split_final_database():
  final_database = pd.read_csv(PROCESSED / "final_database.csv", parse_dates=['data'])
  return split_data(final_database)

def split_data(final_database):
    train = final_database[final_database['data'] < '2022-01-01']
    validate = final_database[(final_database['data'] >= '2022-01-01') & (final_database['data'] < '2023-01-01')]
    test = final_database[final_database['data'] >= '2023-01-01']
    
    X_train, y_train = train[FEATURE_COLS], train['target']
    X_val, y_val = validate[FEATURE_COLS], validate['target']
    X_test, y_test = test[FEATURE_COLS], test['target']
    
    return X_train, X_val, y_train, y_val, X_test, y_test

def get_raw_data():
   pass