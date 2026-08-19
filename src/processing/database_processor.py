import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"


def despivotar_chuvas(chuvas_raw):
    registros = []
    for _, row in chuvas_raw.iterrows():
        data_ref = pd.to_datetime(row["Data"], dayfirst=True)
        ano = data_ref.year
        mes = data_ref.month
        nivel = row["NivelConsistencia"]
        for dia in range(1, 32):
            col = f"Chuva{dia:02d}"
            if col not in row.index:
                continue
            valor = row[col]
            try:
                data = pd.Timestamp(year=ano, month=mes, day=dia)
            except ValueError:
                continue
            registros.append({
                "data": data, 
                "chuva_mm": valor if pd.notna(valor) else np.nan, 
                "nivel_consistencia": nivel
            })
    return pd.DataFrame(registros)


def processar_chuvas(chuvas_raw):
    daily_chuvas = despivotar_chuvas(chuvas_raw)
    daily_chuvas = daily_chuvas.sort_values("nivel_consistencia", ascending=False)
    daily_chuvas = daily_chuvas.drop_duplicates(subset="data", keep="first")
    daily_chuvas = daily_chuvas.sort_values("data").reset_index(drop=True)
    daily_chuvas["data"] = pd.to_datetime(daily_chuvas["data"])
    daily_chuvas = daily_chuvas[(daily_chuvas["data"] >= "1997-01-01") & (daily_chuvas["data"] <= "2026-04-30")].reset_index(drop=True)
    return daily_chuvas


def processar_vazao(vazao_raw):
    vazao = vazao_raw.rename(columns={"vazao_m3s": "vazao"})
    vazao["data"] = pd.to_datetime(vazao["data"])
    return vazao[["data", "vazao"]]


def processar_inmet(inmet_raw):
    inmet = inmet_raw.rename(columns={
        "Data Medicao": "data",
        "TEMPERATURA MEDIA COMPENSADA, DIARIA(Â°C)": "temp_media",
        "TEMPERATURA MAXIMA, DIARIA(Â°C)": "temp_max",
        "TEMPERATURA MINIMA, DIARIA(Â°C)": "temp_min",
        "UMIDADE RELATIVA DO AR, MEDIA DIARIA(%)": "umidade_media",
        "VENTO, VELOCIDADE MEDIA DIARIA(m/s)": "vento_medio"
    })
    inmet["data"] = pd.to_datetime(inmet["data"])
    inmet = inmet[["data", "temp_media", "temp_max", "temp_min", "umidade_media", "vento_medio"]]
    return inmet


def processar_bases(chuvas_raw, inmet_raw, vazao_raw):
    chuvas = processar_chuvas(chuvas_raw)
    vazao = processar_vazao(vazao_raw)
    inmet = processar_inmet(inmet_raw)
    
    unified_database = pd.merge(chuvas[["data", "chuva_mm"]], vazao, on="data", how="inner")
    unified_database = pd.merge(unified_database, inmet, on="data", how="inner")
    return unified_database


if __name__ == "__main__":
    chuvas_raw = pd.read_csv(RAW / "ana_chuva_sabara_1943006.csv", encoding="latin-1", sep=";", skiprows=12, decimal=",")
    inmet_raw = pd.read_csv(RAW / "inmet_meteo_bh_83587.csv", sep=";", skiprows=9, encoding="latin-1")
    vazao_raw = pd.read_csv(RAW / "glofas_vazao_sabara.csv")
    
    unified_database = processar_bases(chuvas_raw, inmet_raw, vazao_raw)
    unified_database.to_csv(PROCESSED / "unified_database.csv", index=False)
    
