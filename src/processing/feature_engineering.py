import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)


def sum_rain(df):
    df["chuva_3d"] = df["chuva_mm"].rolling(window=3, min_periods=1).sum()
    df["chuva_7d"] = df["chuva_mm"].rolling(window=7, min_periods=1).sum()
    df["chuva_14d"] = df["chuva_mm"].rolling(window=14, min_periods=1).sum()
    df["chuva_30d"] = df["chuva_mm"].rolling(window=30, min_periods=1).sum()
    df["chuva_60d"] = df["chuva_mm"].rolling(window=60, min_periods=1).sum()
    df["chuva_90d"] = df["chuva_mm"].rolling(window=90, min_periods=1).sum()
    return df


def recursive_api(chuva, alpha):
    api = np.zeros(len(chuva))
    for t in range(1, len(chuva)):
        c = chuva[t-1] if not np.isnan(chuva[t-1]) else 0
        api[t] = alpha * (api[t-1] + c)
    return api


def calculate_api(df):
    chuva = df["chuva_mm"].to_numpy()
    df["api_7d"] = recursive_api(chuva, alpha=0.85)
    df["api_30d"] = recursive_api(chuva, alpha=0.90)
    return df


def calculate_lags(df):
    df["chuva_ontem"] = df["chuva_mm"].shift(1)
    df["chuva_anteontem"] = df["chuva_mm"].shift(2)
    df["chuva_3d_atras"] = df["chuva_mm"].shift(3)
    df["chuva_4d_atras"] = df["chuva_mm"].shift(4)
    return df


def calculate_si(df):
    doy = df['data'].dt.dayofyear
    df['sin_doy'] = np.sin(2 * np.pi * doy / 365.25)
    df['cos_doy'] = np.cos(2 * np.pi * doy / 365.25)
    return df


def calculate_vpd(df):
    es = 0.61078 * np.exp((17.27 * df['temp_media']) / (df['temp_media'] + 237.3))
    ea = es * (df['umidade_media'] / 100.0)
    df['vpd'] = es - ea
    return df


def create_target(df):
    df["target"] = df["vazao"].shift(-1)
    return df


def create_features():
    df = pd.read_csv(PROCESSED / "unified_database.csv", parse_dates=['data'])
    df = df.sort_values("data").reset_index(drop=True)
    
    df = sum_rain(df)
    df = calculate_api(df)
    df = calculate_lags(df)
    df = calculate_si(df)
    df = calculate_vpd(df)
    df = create_target(df)
    df = df.dropna().reset_index(drop=True)
    df = df.round(2)
    df.to_csv(PROCESSED / "final_database.csv", index=False)
