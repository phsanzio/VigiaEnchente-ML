# VigiaEnchente-ML

Modelo de Machine Learning para previsão de vazão fluvial D+1 no município de Sabará/MG, bacia do Alto Rio das Velhas.

## Sobre o Projeto

TCC desenvolvido no Instituto Federal de Minas Gerais (IFMG), Campus Sabará.

### Problema

Sabará sofre historicamente com enchentes do Rio das Velhas. As estações fluviométricas da ANA foram desativadas em 1965, resultando em 60 anos sem dados de vazão locais.

### Solução

Modelo de regressão precipitação-vazão que aprende a prever vazão D+1 usando dados locais:

```
FEATURES (dia D)                          TARGET (dia D+1)
┌─────────────────────────────────┐       ┌─────────────────┐
│  Chuva ANA (estação 1943006)    │       │                 │
│  ├─ precipitação diária         │       │  Vazão GloFAS   │
│  ├─ acumulados (3d,7d,14d,30d)  │  ───► │  (m³/s)         │
│  └─ API (α=0.90, k=30)          │       │                 │
│                                 │       └─────────────────┘
│  Meteorologia INMET (83587)     │
│  ├─ temperatura (max/min/média) │
│  ├─ umidade relativa            │
│  └─ velocidade do vento         │
│                                 │
│  Lags autorregressivos          │
│  ├─ vazao_lag1, vazao_lag2      │
│  └─ chuva_lag1, chuva_lag2      │
└─────────────────────────────────┘
```

## Dataset Unificado

**Período:** 1997-01-01 a 2026-04-30 (~10.700 registros diários)

| Fonte | Variáveis | Período Original |
|-------|-----------|------------------|
| ANA (1943006) | chuva_mm | 1941-2026 |
| GloFAS/ECMWF | vazao (m³/s) | 1997-2026 |
| INMET (83587) | temp_media, temp_max, temp_min, umidade_media, vento_medio | 1986-2026 |

**Arquivo processado:** `data/processed/unified_database.csv`

## Estrutura do Repositório

```
vigiaenchente-ml/
├── README.md
├── LICENSE
│
├── data/
│   ├── raw/                              # Dados brutos
│   │   ├── ana_chuva_sabara_1943006.csv  # Chuva ANA
│   │   ├── glofas_vazao_sabara.csv       # Vazão GloFAS
│   │   └── inmet_meteo_bh_83587.csv      # Meteorologia INMET
│   └── processed/
│       └── unified_database.csv          # Base unificada
│
├── src/
│   └── processing/
│       └── database_processor.py         # Processamento das bases
│
├── docs/
│   └── revisao-literatura-gemini.md      # Revisão sistemática
│
└── scripts/
    └── coleta_glofas.py                  # Coleta dados GloFAS
```

## Execução

```bash
# Processar bases e gerar unified_database.csv
python3 src/processing/database_processor.py
```

## Features Planejadas

| Feature | Descrição | Status |
|---------|-----------|--------|
| chuva_3d, 7d, 14d, 30d | Acumulados de precipitação | Pendente |
| api | Índice de Precipitação Antecedente (α=0.90, k=30) | Pendente |
| vazao_lag1, lag2 | Lags autorregressivos de vazão | Pendente |
| chuva_lag1, lag2 | Lags de precipitação | Pendente |
| target | vazao.shift(-1) - vazão D+1 | Pendente |

## Modelos Planejados

| Modelo | Justificativa |
|--------|---------------|
| XGBoost | Performance em dados tabulares, regularização |
| Random Forest | Robusto, interpretável, feature importance |
| Regressão Linear | Baseline |

## Métricas

- RMSE (Root Mean Square Error)
- MAE (Mean Absolute Error)
- R² (Coeficiente de determinação)
- KGE (Kling-Gupta Efficiency)

## Eventos de Referência

| Data | Vazão GloFAS | Tipo |
|------|--------------|------|
| Jan/1997 | - | Fluvial |
| 27/01/2020 | 20.18 m³/s | Fluvial |
| 09/01/2022 | 48.55 m³/s (máximo histórico) | Fluvial |
| Dez/2023 | - | Fluvial |
| Jan/2024 | - | Fluvial |

## Decisões Técnicas

### Por que estação INMET a 17km?
Não existe estação INMET em Sabará. A estação 83587 (BH) é a mais próxima com série longa. A distância é aceitável para eventos sinóticos (ZCAS, frentes).

### Por que GloFAS como target?
Única fonte de vazão disponível para Sabará desde 1965. Validado internacionalmente pelo ECMWF/Copernicus.

### Por que não usar pressão atmosférica?
A estação 83587 (convencional) não mede pressão. Estações automáticas com pressão têm série mais curta (~2007).

## Equipe

- **Pedro Henrique Sanzio Fernandes Xavier** - Autor
- **Carlos Alexandre Silva** - Orientador
- **Carlos Alberto Severiano Junior** - Coorientador

## Licença

MIT License

---

**IFMG - Campus Sabará | 2026**
