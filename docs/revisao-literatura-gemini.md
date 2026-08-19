# Previsão de Enchentes com Aprendizado de Máquina e Inteligência Artificial na Bacia do Rio das Velhas

## Revisão Sistemática e Diretrizes Metodológicas para Sabará (MG)

> **Fonte:** Revisão gerada por IA (Gemini)  
> **Data:** Agosto 2026  
> **Escopo:** Estado da arte em ML/IA para previsão de cheias (2020-2026)

---

## Introdução

A modelagem preditiva de inundações em bacias hidrográficas urbanizadas constitui um dos temas mais críticos da hidrologia contemporânea e da gestão de riscos de desastres.

No contexto do município de **Sabará (Minas Gerais)**, situado na calha do Alto Rio das Velhas — sub-bacia estratégica do Rio São Francisco —, a estruturação de um sistema de alerta precoce com antecedência de 24 horas (D+1) exige uma formulação metodológica que integre:

- Dados pluviométricos pontuais
- Variáveis meteorológicas regionais
- Vazões simuladas por reanálises globais
- Registros históricos de desastres

Este relatório sintetiza o estado da arte na literatura científica internacional e nacional (2020–2026), abordando metodologias de aprendizado de máquina (Machine Learning - ML) e inteligência artificial aplicadas à previsão de cheias fluviais.

---

## 1. Metodologia e Boas Práticas em Modelagem Hidrológica com ML

### 1.1 Extensão Mínima de Séries Históricas

A literatura hidrológica internacional estabelece que o treinamento de modelos de ML para previsão de vazão e cheias requer **séries temporais com extensão de 15 a 30 anos**.

Essa duração se justifica pela necessidade física de capturar ciclos de variabilidade climática:
- El Niño-Oscilação Sul (ENOS)
- Oscilação Decadal do Pacífico (ODP)
- Zona de Convergência do Atlântico Sul (ZCAS)

Uma base de dados de **29 anos (~10.700 registros diários, 1997–2026)** apresenta representatividade climatológica robusta, contemplando:
- Períodos secos severos (crise hídrica 2014-2015)
- Eventos pluviométricos extremos (1997, 2020, 2022, 2023, 2024)

### 1.2 Tratamento do Desbalanceamento de Classes

O registro de apenas **5 episódios de inundação** em 10.700 dias estabelece um cenário de **desbalanceamento severo** (classe positiva < 0,05% da base total).

**Três vias principais de mitigação:**

1. **Cost-Sensitive Learning:** Ajuste de penalidades assimétricas na função de perda
   - Hiperparâmetro `scale_pos_weight` em GBDT
   - Focal Loss para modular gradientes

2. **Amostragem Sintética Temporal Controlada:**
   - SMOTE tradicional corrompe autocorrelação temporal
   - Usar Time-Series Block Oversampling

3. **Modelagem Contínua em Dois Estágios (RECOMENDADO):**
   - Estágio 1: Regressão contínua para vazão Q(t+1)
   - Estágio 2: Limiares de corte para alertas categóricos

### 1.3 Partição Temporal e Prevenção de Data Leakage

> **IMPORTANTE:** Validação cruzada k-fold com embaralhamento aleatório é **terminantemente inadequada** para dados hidrometeorológicos.

**Abordagens recomendadas:**

1. **Walk-Forward Cross-Validation:** Janela expansiva de treino

2. **Partição Cronológica em Blocos:**
   - **Treino (1997–2015):** ~19 anos, histórico básico + evento 1997
   - **Validação (2016–2019):** ~4 anos, ajuste de hiperparâmetros
   - **Teste (2020–2026):** ~6 anos, avaliação final com 4 dos 5 desastres

### 1.4 Métricas de Desempenho

> Acurácia global e ROC-AUC são **enganosas** em conjuntos desbalanceados.

| Métrica | Fórmula | Finalidade |
|---------|---------|------------|
| **Precision** | VP / (VP + FP) | Confiabilidade dos alertas |
| **Recall** | VP / (VP + FN) | Capacidade de detecção |
| **F1-Score** | 2 × (Prec × Rec) / (Prec + Rec) | Balanceamento |
| **PR-AUC** | Área sob curva Precisão-Recall | Seleção de modelos |
| **CSI** | VP / (VP + FP + FN) | Padrão-ouro em hidrologia |
| **KGE** | 1 - √[(r-1)² + (β-1)² + (γ-1)²] | Regressão de vazão |

### 1.5 Definição de Limiares de Alerta (sem Fluviometria Local)

Método da **Climatologia Consistente do Modelo:**

| Nível | Percentil | Significado |
|-------|-----------|-------------|
| **Atenção** | P95 | Elevação anômala, mobilização de equipes |
| **Alerta** | P98 | Período de retorno 1-2 anos |
| **Emergência** | P99.5 | Concentração dos picos de cheia históricos |

---

## 2. Features e Engenharia de Variáveis

### 2.1 Janelas Temporais de Precipitação

| Janela | Mecanismo Físico |
|--------|------------------|
| **P(1-3d)** | Escoamento superficial direto, cheias rápidas |
| **P(7-14d)** | Saturação do solo, redução de infiltração |
| **P(30d)** | Elevação do lençol freático e fluxo de base |

### 2.2 Índice de Precipitação Antecedente (API)

$$API_t = \sum_{i=1}^{k} \alpha^i P_{t-i}$$

Onde:
- $\alpha$ = 0,88 a 0,92 (fator de decaimento)
- $k$ = 30 dias (janela de memória)

### 2.3 Variáveis Meteorológicas (INMET)

| Variável | Mecanismo Físico |
|----------|------------------|
| **Pressão e ΔPress(24h)** | Aproximação de frentes e ZCAS |
| **Umidade Relativa / VPD** | Controle de evapotranspiração |
| **Temperatura** | Evapotranspiração potencial |
| **Vento** | Movimentação de massas de ar |

### 2.4 Estrutura de Lags

Incluir defasagens t, t-1, t-2 para:
- Todas as variáveis meteorológicas
- Série de vazão GloFAS

### 2.5 Normalização

| Modelo | Normalização |
|--------|--------------|
| **Random Forest, XGBoost** | Não necessária |
| **SVM, Regressão Logística, MLP** | **Obrigatória** (RobustScaler ou Z-Score) |

---

## 3. Fontes de Dados e Reanálises

### 3.1 GloFAS como Alvo Hidrológico

O GloFAS (Global Flood Awareness System) do ECMWF é amplamente utilizado para regiões sem dados fluviométricos, com KGE > 0 em 80% das bacias analisadas globalmente.

**Limitações:**
- Resolução espacial ~5-10 km (atenua picos de cheia súbitos)
- Viés volumétrico sistemático em terrenos tropicais

**Contorno:** Usar distribuição de quantis (Quantile Mapping) em vez de valores absolutos.

### 3.2 Por que Usar Medições Locais (ANA) em vez de Reanálise?

Produtos de reanálise (ERA5, CHIRPS) frequentemente **subestimam intensidades máximas** de chuva diária em bacias de cabeceira com relevo movimentado.

A metodologia com pluviômetro local ANA (1943006) preserva a assinatura física de tempestades intensas.

### 3.3 Justificativa para Estação INMET a 17 km

A distância de ~17 km entre a estação INMET e Sabará é justificável porque:

1. **Escala dos eventos:** Cheias em Sabará decorrem de ZCAS e frentes semi-estacionárias (escala de centenas de km)
2. **Integração multiescalar:** INMET representa termodinâmica regional; ANA ancora heterogeneidade pluviométrica local

---

## 4. Modelos e Algoritmos

### 4.1 Árvores vs Deep Learning

**Consenso na literatura:** Modelos baseados em árvores (XGBoost, Random Forest) **superam redes neurais profundas** em dados tabulares com < 50.000 amostras.

**Razões (Grinsztajn et al., NeurIPS 2022):**
- Árvores capturam funções não-lineares em degrau (limiares hidrológicos)
- Redes neurais impõem suavidade, achatando picos extremos
- LSTM/GRU sofrem com carência de dados para generalização de cauda

### 4.2 Comparativo de Algoritmos

| Algoritmo | Tratamento Desbalanc. | Vantagens | Limitações |
|-----------|----------------------|-----------|------------|
| **XGBoost** | Excelente | Alta generalização, regularização L1/L2 | Requer ajuste fino |
| **Random Forest** | Alta | Reduz variância, imune a overfitting | Não extrapola fora da faixa |
| **SVM (RBF)** | Moderada | Mapeamento não-linear eficiente | Custo O(N²), sensível a escala |
| **Regressão Logística** | Baixa | Transparência total | Incapaz de modelar não-linearidades |
| **LSTM/GRU** | Baixa (N<50k) | Dependências temporais longas | Instável em séries curtas |

### 4.3 Hiperparâmetros Críticos

**XGBoost:**
- `max_depth`: 3-6
- `learning_rate`: 0,01-0,05
- `scale_pos_weight`: N_neg/N_pos
- `subsample`, `colsample_bytree`: 0,7-0,9

**Random Forest:**
- `n_estimators`: 300-1000
- `min_samples_leaf`: 5-20
- `max_features`: sqrt ou log2

### 4.4 Ensemble (Stacking)

**Arquitetura recomendada:**
- **Nível 0:** XGBoost, Random Forest, SVM → probabilidades
- **Nível 1:** Regressão Logística regularizada → ponderação final

---

## 5. Contexto Regional: Bacia do Alto Rio das Velhas

### 5.1 Características

- Relevo acidentado do Quadrilátero Ferrífero
- Cabeceiras em Ouro Preto, passando por Itabirito, Rio Acima, Raposos, Sabará, Santa Luzia
- Sabará: ponto de estrangulamento vulnerável

### 5.2 Eventos Históricos

| Evento | Forçante | Impacto |
|--------|----------|---------|
| **Jan 1997** | ZCAS persistente | Enchente generalizada |
| **Jan 2020** | ZCAS + convecção extrema | Desabrigados em Sabará e Raposos |
| **Jan 2022** | ZCAS (15 dias contínuos) | Vazão pico 530 m³/s, calamidade regional |
| **Dez 2023** | Frentes sucessivas | Alagamentos e deslizamentos |
| **Jan 2024** | Convecção | Alertas preventivos acionados |

### 5.3 Efeito de Remanso (Ribeirão Arrudas)

O Ribeirão Arrudas (bacia 206 km², quase totalmente urbanizada) deságua no Rio das Velhas próximo a Sabará.

Em chuvas intensas na RMBH, quando o Rio das Velhas está alto, surge **barramento hidráulico** que eleva níveis a montante e causa transbordamento antecipado em Sabará.

→ Por isso é vital usar dados INMET de BH: antecipar o deflúvio do Arrudas.

---

## 6. Não-Estacionaridade e Urbanização

### 6.1 Por que NÃO Usar Dados Antigos (1939-1965)?

Nas últimas 6 décadas, a bacia sofreu transformações profundas:

- Impermeabilização: de < 10% para > 70% em sub-bacias metropolitanas
- Redução de tempo de concentração
- Alteração de batimetria por assoreamento

> **A função chuva-vazão de 1950 não é equivalente à de 2026.** Um mesmo volume de 80 mm/dia gerava elevação moderada nos anos 1950, mas produz vazões de pico muito mais altas hoje.

**Recomendação:**
- Série antiga: apenas para análise climatológica de período de retorno
- Treinamento ML: **usar base contemporânea (2006-2026)**

### 6.2 Inundação Fluvial vs Alagamento Urbano

| Tipo | Descrição | Capturado pelo Modelo? |
|------|-----------|------------------------|
| **Inundação Fluvial** | Transbordamento do rio por chuvas na bacia (12-48h de elevação) | **SIM** |
| **Alagamento Urbano** | Insuficiência de microdrenagem sob tempestades sub-diárias | **NÃO** |

> A validação deve ser filtrada para contemplar **exclusivamente eventos de transbordamento fluvial**.

---

## 7. Pipeline Operacional Proposto

```
[Dados Diários ANA 1943006 + INMET A521]
           │
           ▼
[Engenharia: Acumulados, API, Lags, ΔPressão]
           │
           ▼
[Série Contínua GloFAS (2006-2025)]
           │
           ▼
[Modelagem Contínua de Vazão D+1 (XGBoost/RF)]
           │
           ▼
[Mapeamento de Percentis: P90, P95, P99]
           │
           ▼
[Emissão de Alertas Categóricos]
```

---

## 8. Comunicação de Incertezas

Alertas operacionais **não devem ser binários** ("Sim/Não"), mas acompanhados de:
- Probabilidade calibrada de superação dos limiares
- Intervalos de confiança empíricos (IC 90%)

---

## 9. Consensos e Lacunas na Literatura

### Consensos

- Modelos de árvores > Deep Learning para N < 50k amostras
- Acurácia/ROC-AUC inadequadas para eventos raros
- Índice API e memória de 7-30 dias são indispensáveis

### Divergências

- SMOTE vs Cost-Sensitive Learning em séries temporais
- Uso direto de GloFAS vs necessidade de calibração local

### Lacunas (Oportunidades de Contribuição)

1. **Transferibilidade do GloFAS em escala municipal no Brasil**
2. **Metodologia de calibração com registros qualitativos de Defesa Civil**
3. **Quantificação do efeito de remanso em confluências urbanizadas**

---

## Referências Metodológicas

- Grinsztajn, L., Oyallon, E., & Varoquaux, G. (2022). Why do tree-based models still outperform deep learning on typical tabular data? NeurIPS.
- ECMWF/JRC. GloFAS-ERA5 Reanalysis v4 Documentation.
- Literatura hidrológica brasileira sobre SMAP, CEMADEN, SACE/CPRM.
