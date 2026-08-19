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


def calcular_api(df, k_dias=30, alpha=0.90, nome_coluna="api_30d"):
    pesos = np.array([alpha ** i for i in range(1, k_dias + 1)])
    api_valores = np.zeros(len(df))
    chuva = df["chuva_mm"].to_numpy()
    
    for t in range(1, len(df)):
        inicio = max(0, t - k_dias)
        chuvas_passadas = chuva[inicio:t][::-1]
        w = pesos[:len(chuvas_passadas)]
        api_valores[t] = np.sum(chuvas_passadas * w)
    
    df[nome_coluna] = api_valores
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
    df = calcular_api(df, k_dias=7, alpha=0.85, nome_coluna="api_7d")
    df = calcular_api(df, k_dias=30, alpha=0.90, nome_coluna="api_30d")
    df = calcular_lags(df)
    df = criar_target(df)
    return df


if __name__ == "__main__":
    df = pd.read_csv(PROCESSED / "unified_database.csv")
    df["data"] = pd.to_datetime(df["data"])
    
    df = criar_features(df)
    
    df = df.dropna().reset_index(drop=True)
    
    df.to_csv(PROCESSED / "features_database.csv", index=False)
    
    print(f"Registros: {len(df)}")
    print(f"Colunas: {list(df.columns)}")
    print(df.head(10))
