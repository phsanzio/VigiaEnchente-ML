# Guia de Coleta de Dados - VigiaEnchente ML

## Arquitetura Final do Dataset

```
┌─────────────────────────────────────────────────────────────────┐
│                        FEATURES (dia D)                         │
├─────────────────────────────────────────────────────────────────┤
│  ANA (Chuva)           │  INMET (Meteorologia)                  │
│  ├─ precipitação       │  ├─ temperatura_media                  │
│  ├─ acum_3d/7d/14d/30d │  ├─ temperatura_max                    │
│  └─ lags (d-1..d-7)    │  ├─ temperatura_min                    │
│                        │  ├─ umidade_relativa                   │
│                        │  ├─ vento_velocidade                   │
│                        │  └─ pressao_atmosferica                │
└─────────────────────────────────────────────────────────────────┘
                              ↓ Modelo ML ↓
┌─────────────────────────────────────────────────────────────────┐
│                        TARGET (dia D+1)                         │
├─────────────────────────────────────────────────────────────────┤
│  GloFAS (Vazão Simulada)                                        │
│  └─ river_discharge (m³/s)                                      │
└─────────────────────────────────────────────────────────────────┘
```

**Período:** 1997-2025 (cobertura conjunta de todas as fontes)

---

## 1. Dados de Chuva (ANA) ✅ Já temos

- **Estação:** 1943006 (Sabará)
- **Período:** 1941-2025 (vamos usar 1997-2025)
- **Arquivo:** `dados-defesa-civil/csv/chuvas.csv`
- **Status:** Já extraído do .mdb

---

## 2. Dados Meteorológicos (INMET) 🆕

### Estação a usar

- **Código WMO:** 83587
- **Nome:** Belo Horizonte
- **Distância de Sabará:** ~15km (mesma região climática)
- **Tipo:** Estação convencional (dados desde 1961)

### Variáveis disponíveis

| Variável | Unidade | Uso no modelo |
|----------|---------|---------------|
| Precipitação | mm | Comparar com ANA (validação) |
| Temperatura média | °C | Feature |
| Temperatura máxima | °C | Feature |
| Temperatura mínima | °C | Feature |
| Umidade relativa | % | Feature |
| Velocidade do vento | m/s | Feature |
| Direção do vento | graus | Opcional |
| Pressão atmosférica | hPa | Feature |
| Insolação | horas | Opcional |
| Evaporação | mm | Opcional (proxy saturação) |

### Como baixar os dados

#### Opção A: Ferramenta automatizada (RECOMENDADO)

```bash
# Instalar o fetcher
pip install git+https://github.com/Quantilica/inmet-fetcher.git

# Baixar todos os anos de MG
cd vigiaenchente-ml
mkdir -p data/inmet
inmet-fetcher sync 1997:2025 -o ./data/inmet --workers 4

# Listar estações disponíveis
inmet-fetcher stations -o ./data/inmet --save-as data/inmet/estacoes.csv

# Filtrar só MG e exportar
inmet-fetcher read -o ./data/inmet --uf MG --save-as data/inmet/mg_completo.parquet
```

#### Opção B: Download manual

1. Acessar: https://portal.inmet.gov.br/dadoshistoricos
2. Baixar ZIP de cada ano (1997-2025)
3. Descompactar e filtrar pela estação 83587

#### Opção C: API BDMEP (menos recomendado)

- Portal: https://bdmep.inmet.gov.br/
- Requer cadastro e aprovação
- Interface web para seleção de estação/período

### Código Python para processar

```python
import pandas as pd

# Após baixar com inmet-fetcher
df_inmet = pd.read_parquet('data/inmet/mg_completo.parquet')

# Filtrar estação Belo Horizonte (código WMO 83587)
df_bh = df_inmet[df_inmet['codigo_wmo'] == 'A501']  # Ou buscar por nome
# NOTA: Verificar se é A501 (automática) ou 83587 (convencional)

# Converter para diário se necessário (dados podem ser horários)
df_diario = df_bh.resample('D', on='data_hora').agg({
    'temperatura_ar': 'mean',
    'temperatura_maxima': 'max',
    'temperatura_minima': 'min',
    'umidade_relativa': 'mean',
    'vento_velocidade': 'mean',
    'precipitacao': 'sum',
    'pressao_atmosferica': 'mean'
})
```

---

## 3. Dados de Vazão/Target (GloFAS via Open-Meteo)

### Coordenadas de Sabará

```
Latitude: -19.8867
Longitude: -43.8067
```

### API Open-Meteo Flood

```python
import requests
import pandas as pd

# Coordenadas de Sabará
lat, lon = -19.8867, -43.8067

# API Open-Meteo Flood (GloFAS)
url = "https://flood-api.open-meteo.com/v1/flood"
params = {
    "latitude": lat,
    "longitude": lon,
    "daily": "river_discharge",
    "start_date": "1997-01-01",
    "end_date": "2025-12-31"
}

response = requests.get(url, params=params)
data = response.json()

# Converter para DataFrame
df_glofas = pd.DataFrame({
    'data': pd.to_datetime(data['daily']['time']),
    'vazao_glofas': data['daily']['river_discharge']
})
df_glofas.set_index('data', inplace=True)

# Salvar
df_glofas.to_csv('data/glofas_sabara.csv')
```

### Sobre a resolução (~5km)

**Realidade:** A resolução de ~5km do GloFAS é a melhor disponível gratuitamente para dados de vazão estimada. Não existe forma de "melhorar" essa resolução sem:

1. **Dados reais locais** (que não existem após 1965)
2. **Modelos hidrológicos próprios** (requer expertise e dados de entrada detalhados)
3. **Downscaling estatístico** (complexo e fora do escopo do TCC)

**Argumento para o TCC:**
> "A resolução de ~5km do GloFAS, embora não ideal, representa a melhor referência disponível para regiões sem monitoramento fluviométrico ativo. O modelo desenvolvido neste trabalho visa justamente superar essa limitação, criando estimativas locais a partir de dados pluviométricos medidos in loco."

---

## 4. Montando o Dataset Final

```python
import pandas as pd

# Carregar cada fonte
df_chuva = pd.read_csv('data/chuvas_diario.csv', parse_dates=['data'], index_col='data')
df_inmet = pd.read_csv('data/inmet_diario.csv', parse_dates=['data'], index_col='data')
df_glofas = pd.read_csv('data/glofas_sabara.csv', parse_dates=['data'], index_col='data')

# Juntar tudo
df = df_chuva.join(df_inmet, how='inner').join(df_glofas, how='inner')

# Criar features de lag e acumulado
for lag in range(1, 8):
    df[f'chuva_lag{lag}'] = df['precipitacao'].shift(lag)

for janela in [3, 7, 14, 30]:
    df[f'chuva_acum{janela}d'] = df['precipitacao'].rolling(janela).sum()

# Criar target D+1 (vazão do dia seguinte)
df['target_vazao_d1'] = df['vazao_glofas'].shift(-1)

# Remover linhas com NaN
df_final = df.dropna()

# Salvar
df_final.to_csv('data/dataset_completo.csv')
print(f"Dataset: {len(df_final)} registros, {df_final.shape[1]} colunas")
```

---

## Checklist de Execução

- [ ] Baixar dados INMET (1997-2025) com inmet-fetcher
- [ ] Identificar código correto da estação BH (83587 ou A501)
- [ ] Processar dados INMET para formato diário
- [ ] Baixar dados GloFAS via API Open-Meteo
- [ ] Processar chuvas ANA (já feito parcialmente)
- [ ] Juntar todas as fontes em dataset único
- [ ] Criar features (lags, acumulados)
- [ ] Criar target D+1
- [ ] Split temporal (treino < 2020, teste >= 2020)
- [ ] Validar contra 5 eventos confirmados

---

## Referências

- INMET BDMEP: https://portal.inmet.gov.br/dadoshistoricos
- Open-Meteo Flood API: https://open-meteo.com/en/docs/flood-api
- GloFAS (ECMWF): https://www.globalfloods.eu/
- inmet-fetcher: https://github.com/Quantilica/inmet-fetcher
