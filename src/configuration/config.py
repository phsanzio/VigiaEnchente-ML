from pathlib import Path

ROOT = Path(__file__).parent.parent.parent 
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
MODELS = ROOT / "models"
RESULTS = ROOT / "results"

RAW.mkdir(parents=True, exist_ok=True)
MODELS.mkdir(parents=True, exist_ok=True)
PROCESSED.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(parents=True, exist_ok=True)

TRAIN_START = '1997-01-01'
TRAIN_END = '2016-12-31'
VAL_START = '2017-01-01'
VAL_END = '2021-12-31'
TEST_START = '2022-01-01'

FEATURE_COLS = [
    'chuva_mm', 'temp_media', 'temp_max', 'temp_min', 'umidade_media',
    'chuva_3d', 'chuva_7d', 'chuva_14d', 'chuva_30d', 'chuva_60d', 'chuva_90d',
    'api_7d', 'api_30d',
    'chuva_ontem', 'chuva_anteontem', 'chuva_3d_atras', 'chuva_4d_atras',
    'sin_doy', 'cos_doy', 'vpd'
]