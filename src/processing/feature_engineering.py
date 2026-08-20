import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
PROCESSED = ROOT / "data" / "processed"


def calcular_acumulados(df):
    df["chuva_3d"] = df["chuva_mm"].rolling(window=3, min_periods=1).sum()
    df["chuva_7d"] = df["chuva_mm"].rolling(window=7, min_periods=1).sum()
    df["chuva_14d"] = df["chuva_mm"].rolling(window=14, min_periods=1).sum()
    df["chuva_30d"] = df["chuva_mm"].rolling(window=30, min_periods=1).sum()
    return df


def calcular_api_recursivo(chuva, alpha):
    api = np.zeros(len(chuva))
    for t in range(1, len(chuva)):
        c = chuva[t-1] if not np.isnan(chuva[t-1]) else 0
        api[t] = alpha * (api[t-1] + c)
    return api


def calcular_apis(df):
    chuva = df["chuva_mm"].to_numpy()
    df["api_7d"] = calcular_api_recursivo(chuva, alpha=0.85)
    df["api_30d"] = calcular_api_recursivo(chuva, alpha=0.90)
    return df


def calcular_lags(df):
    df["vazao_lag1"] = df["vazao"].shift(1)
    df["vazao_lag2"] = df["vazao"].shift(2)
    df["chuva_lag1"] = df["chuva_mm"].shift(1)
    df["chuva_lag2"] = df["chuva_mm"].shift(2)
    return df


def criar_target(df):
    df["target"] = df["vazao"].shift(-1)
    return df


def criar_features(df):
    df = calcular_acumulados(df)
    df = calcular_apis(df)
    df = calcular_lags(df)
    df = criar_target(df)
    return df


if __name__ == "__main__":
    df = pd.read_csv(PROCESSED / "unified_database.csv")
    df["data"] = pd.to_datetime(df["data"])
    
    df = criar_features(df)
    df = df.dropna().reset_index(drop=True)
    
    df = df.round(2)
    df.to_csv(PROCESSED / "final_database.csv", index=False)
    
