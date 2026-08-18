"""
Script para coleta de dados de vazão do GloFAS via API Open-Meteo.

O GloFAS (Global Flood Awareness System) é um sistema do ECMWF/Copernicus
que fornece estimativas de vazão para qualquer ponto do planeta.

Fonte: https://open-meteo.com/en/docs/flood-api

Autor: Pedro Henrique Sanzio Fernandes Xavier
Data: Agosto/2026
"""

import json
import subprocess
import pandas as pd
from pathlib import Path


# Configurações
LATITUDE = -19.8867   # Sabará, MG
LONGITUDE = -43.8067  # Sabará, MG
DATA_INICIO = "1997-01-01"  # GloFAS só tem dados a partir de 1997 pra essa região
DATA_FIM = "2026-04-30"

# Diretórios
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data" / "raw"


def coletar_vazao_glofas(
    latitude: float,
    longitude: float,
    data_inicio: str,
    data_fim: str
) -> pd.DataFrame:
    """
    Coleta dados de vazão do GloFAS via API Open-Meteo usando curl.
    
    Args:
        latitude: Latitude do ponto de interesse
        longitude: Longitude do ponto de interesse
        data_inicio: Data inicial no formato YYYY-MM-DD
        data_fim: Data final no formato YYYY-MM-DD
    
    Returns:
        DataFrame com colunas [data, vazao_m3s]
    """
    url = (
        f"https://flood-api.open-meteo.com/v1/flood?"
        f"latitude={latitude}&longitude={longitude}"
        f"&daily=river_discharge"
        f"&start_date={data_inicio}&end_date={data_fim}"
    )
    
    print(f"Coletando dados GloFAS...")
    print(f"  Coordenadas: {latitude}, {longitude}")
    print(f"  Período: {data_inicio} a {data_fim}")
    
    # Usar curl para evitar problemas de SSL
    result = subprocess.run(
        ["curl", "-s", url],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Erro ao chamar API: {result.stderr}")
    
    data = json.loads(result.stdout)
    
    if "error" in data:
        raise RuntimeError(f"Erro da API: {data['error']}")
    
    df = pd.DataFrame({
        "data": pd.to_datetime(data["daily"]["time"]),
        "vazao_m3s": data["daily"]["river_discharge"]
    })
    
    print(f"  Registros coletados: {len(df)}")
    print(f"  Vazão média: {df['vazao_m3s'].mean():.2f} m³/s")
    print(f"  Vazão máxima: {df['vazao_m3s'].max():.2f} m³/s")
    
    return df


def main():
    """Função principal."""
    print("=" * 60)
    print("COLETA DE DADOS GLOFAS - VigiaEnchente ML")
    print("=" * 60)
    print()
    
    # Garantir que o diretório existe
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Coletar dados
    df = coletar_vazao_glofas(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        data_inicio=DATA_INICIO,
        data_fim=DATA_FIM
    )
    
    # Salvar
    arquivo_saida = DATA_DIR / "glofas_vazao_sabara.csv"
    df.to_csv(arquivo_saida, index=False)
    
    print()
    print(f"Arquivo salvo: {arquivo_saida}")
    print()
    print("Estatísticas:")
    print(f"  Primeiro registro: {df['data'].min().strftime('%Y-%m-%d')}")
    print(f"  Último registro: {df['data'].max().strftime('%Y-%m-%d')}")
    print(f"  Total de dias: {len(df)}")
    print(f"  Valores nulos: {df['vazao_m3s'].isna().sum()}")
    print()
    print("Concluído!")


if __name__ == "__main__":
    main()
