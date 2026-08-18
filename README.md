# VigiaEnchente-ML

Modelo de Machine Learning para previsão de enchentes no município de Sabará/MG, focado no Rio das Velhas.

## Sobre o Projeto

Este repositório contém a implementação do modelo de ML desenvolvido como parte do TCC no Instituto Federal de Minas Gerais (IFMG), Campus Sabará.

### Problema

Sabará sofre historicamente com enchentes do Rio das Velhas, especialmente no período chuvoso (outubro a março). Os métodos tradicionais de previsão dependem de:
- Interpretação manual de cada variável hidrológica
- Experiência individual de especialistas
- Monitoramento visual do nível do rio (régua)

**Desafio adicional:** As estações fluviométricas da ANA em Sabará foram desativadas em 1965, resultando em um gap de 60 anos sem dados de vazão locais.

### Solução Proposta

Um modelo de ML que aprende a prever vazão D+1 usando apenas dados locais disponíveis:

```
FEATURES (dia D)                          TARGET (dia D+1)
┌─────────────────────────────────┐       ┌─────────────────┐
│  Chuva ANA (estação 1943006)    │       │                 │
│  ├─ precipitação diária         │       │  Vazão GloFAS   │
│  ├─ acumulados (3d,7d,14d,30d)  │       │  (m³/s)         │
│  └─ lags (d-1 a d-7)            │  ───► │                 │
│                                 │       │  (referência    │
│  Meteorologia INMET (A521)      │       │   internacional)│
│  ├─ temperatura (max/min/média) │       │                 │
│  └─ umidade, vento, pressão     │       └─────────────────┘
└─────────────────────────────────┘
```

**Após treinado, o modelo funciona offline**, sem dependência de APIs externas.

## Contribuição Principal

> "Diante da inexistência de dados fluviométricos públicos para Sabará desde 1965, este trabalho propõe a criação de uma base de dados local de referência de vazão, utilizando o sistema GloFAS (Global Flood Awareness System) do ECMWF/Copernicus como proxy inicial. O modelo de ML treinado permitirá gerar previsões de vazão baseadas exclusivamente em dados pluviométricos e meteorológicos medidos localmente."

Esta abordagem é **replicável para outros 5.000+ municípios brasileiros** sem infraestrutura de monitoramento fluviométrico.

## Arquitetura do Dataset

| Fonte | Variável | Período | Tipo |
|-------|----------|---------|------|
| ANA (estação 1943006) | Precipitação diária | 1941-2025 | Medido in loco |
| INMET (estação A521) | Temp, umidade, vento, pressão | 2006-2025 | Medido (BH, 17km) |
| GloFAS/Open-Meteo | Vazão simulada (target) | 1984-2025 | Modelado (~5km) |
| Defesa Civil Sabará | Eventos confirmados | 1997-2024 | Ground truth |

**Período de estudo:** 2006-2025 (coincidência de todas as fontes)

## Modelos Avaliados

| Modelo | Tipo | Justificativa |
|--------|------|---------------|
| Regressão Logística | Baseline | Referência mínima de performance |
| Random Forest | Ensemble (bagging) | Robusto, interpretável, feature importance |
| XGBoost | Ensemble (boosting) | Melhor performance em trabalhos correlatos |
| SVM | Kernel-based | Diversidade (não baseado em árvores) |

## Métricas de Avaliação

- **F1-Score** (principal) - equilíbrio entre precisão e recall
- **Recall** - prioridade para detectar eventos reais
- **Precision** - evitar alarmes falsos
- **Validação contra eventos reais** - 5 enchentes confirmadas pela Defesa Civil

## Baseline Operacional

Regra PLANCON (Defesa Civil de Sabará):
- Precipitação acumulada > 100mm em 72h **OU**
- Nível do Rio das Velhas > 2.0m na Régua da Ponte do Paciência

## Estrutura do Repositório

```
vigiaenchente-ml/
├── README.md                           # Este arquivo
├── LICENSE                             # MIT License
├── requirements.txt                    # Dependências Python
├── .gitignore                          # Arquivos ignorados
│
├── data/                               # Dados (não versionados)
│   ├── raw/                            # Dados brutos
│   ├── processed/                      # Dados processados
│   └── glofas/                         # Dados GloFAS
│
├── src/                                # Código fonte
│   ├── coleta/                         # Scripts de coleta
│   ├── preprocessamento/               # Pré-processamento
│   ├── features/                       # Feature engineering
│   ├── modelos/                        # Treinamento e avaliação
│   └── utils/                          # Utilitários
│
├── docs/                               # Documentação
│   ├── decisao-base-de-dados.md        # Decisões sobre dados
│   ├── decisao-modelos-e-experimentos.md
│   ├── guia-coleta-dados.md
│   ├── plano-de-acao.md
│   └── plano-execucao-tcc.md
│
└── outputs/                            # Resultados (não versionados)
    ├── modelos/                        # Modelos salvos
    ├── figuras/                        # Gráficos gerados
    └── metricas/                       # Métricas de avaliação
```

## Instalação

```bash
# Clonar repositório
git clone https://github.com/phsanzio/VigiaEnchente-ML.git
cd VigiaEnchente-ML

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt
```

## Execução

```bash
# 1. Coletar dados
python src/coleta/coletar_glofas.py
python src/coleta/coletar_inmet.py

# 2. Pré-processar
python src/preprocessamento/processar_chuvas.py
python src/preprocessamento/juntar_datasets.py

# 3. Criar features
python src/features/criar_features.py

# 4. Treinar modelos
python src/modelos/treinar.py

# 5. Avaliar
python src/modelos/avaliar.py
```

## Eventos de Referência (Ground Truth)

| Data | Tipo | Vazão GloFAS | Capturado? |
|------|------|--------------|------------|
| Dez/1997 | Fluvial | - | ✅ |
| 27/01/2020 | Fluvial | 20.18 m³/s | ✅ |
| 09/01/2022 | Fluvial | 48.55 m³/s | ✅ |
| 26/10/2023 | Urbano | 0.64 m³/s | ❌ (drenagem) |
| 13/11/2024 | Urbano | 0.83 m³/s | ❌ (drenagem) |

**Limitação conhecida:** O modelo captura eventos fluviais (subida do rio) mas não alagamentos urbanos por falha de drenagem.

## Justificativas Técnicas

### Por que não usar vazão real da ANA (1939-1965)?

Os dados têm **60 anos de defasagem**. Neste período:
- Urbanização mudou completamente o escoamento superficial
- Uso do solo foi alterado (desmatamento, pavimentação)
- Alterações físicas no rio (canalizações, barragens)
- Padrões climáticos mudaram

Usar dados obsoletos criaria um modelo que aprende relações que não existem mais.

### Por que GloFAS como referência?

O GloFAS (Global Flood Awareness System) do ECMWF/Copernicus:
- Fornece dados atuais (1984-presente)
- Validação internacional para sistemas de alerta
- Único disponível gratuitamente para Sabará
- Resolução de ~5km é uma limitação, mas o modelo de ML ajusta localmente

### Por que INMET de BH para Sabará?

Consulta à API oficial do INMET confirmou: **não existe estação em Sabará**.
A estação A521 (Pampulha, 17km de distância) é a mais próxima com série histórica adequada.
Esta distância é meteorologicamente aceitável para eventos de precipitação intensa.

## Equipe

- **Pedro Henrique Sanzio Fernandes Xavier** - Autor
- **Carlos Alexandre Silva** - Orientador
- **Carlos Alberto Severiano Junior** - Coorientador

## Referências

- [Open-Meteo Flood API](https://open-meteo.com/en/docs/flood-api)
- [GloFAS - ECMWF](https://www.globalfloods.eu/)
- [INMET - Dados Históricos](https://portal.inmet.gov.br/dadoshistoricos)
- [ANA - HidroWeb](https://www.snirh.gov.br/hidroweb/)
- [Defesa Civil de Sabará - PLANCON](https://www.sabara.mg.gov.br/defesa-civil)

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**IFMG - Campus Sabará | 2026**
