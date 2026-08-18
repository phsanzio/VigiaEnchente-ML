# Plano de Execução - VigiaEnchente ML

> **Data:** 18/08/2026  
> **Status:** Pronto para executar  
> **Última atualização:** 18/08/2026 - Validação via API INMET

---

## Resumo do Projeto

**Objetivo:** Criar um modelo de ML que preveja vazão D+1 do Rio das Velhas em Sabará usando apenas dados locais (chuva + meteorologia), permitindo que a Defesa Civil faça previsões sem depender de estações fluviométricas (inexistentes desde 1965) ou APIs externas em produção.

### Contribuição Principal do TCC

> **"Diante da inexistência de dados fluviométricos públicos para Sabará desde 1965, este trabalho propõe a criação de uma base de dados local de referência de vazão, utilizando o sistema GloFAS (Global Flood Awareness System) do ECMWF/Copernicus como proxy inicial. O modelo de ML treinado permitirá gerar previsões de vazão baseadas exclusivamente em dados pluviométricos e meteorológicos medidos localmente, estabelecendo uma metodologia replicável para municípios brasileiros sem infraestrutura de monitoramento fluviométrico."**

Esta abordagem é inovadora porque:
1. **Preenche um gap de 60 anos** de dados de vazão inexistentes
2. **Utiliza dados medidos locais** (não reanálise/simulados)
3. **Cria capacidade local** de previsão sem dependência de APIs externas
4. **Replicável** para outros municípios sem monitoramento

**Arquitetura:**
```
FEATURES (dia D)                          TARGET (dia D+1)
┌─────────────────────────────────┐       ┌─────────────────┐
│  Chuva ANA (1943006)            │       │                 │
│  ├─ precipitação                │       │  Vazão GloFAS   │
│  ├─ acumulados (3d,7d,14d,30d)  │       │  (m³/s)         │
│  └─ lags (d-1 a d-7)            │  ───► │                 │
│                                 │       │  Resolução ~5km │
│  Meteorologia INMET (A521)      │       │                 │
│  ├─ temperatura (max/min/média) │       └─────────────────┘
│  ├─ umidade relativa            │
│  ├─ velocidade do vento         │
│  └─ pressão atmosférica         │
└─────────────────────────────────┘
```

---

## Fontes de Dados

### 1. Chuva (ANA/HidroWeb) ✅ Já temos
- **Estação:** 1943006 (Sabará)
- **Período:** 1941-2025 (usaremos 2006-2025 para coincidir com INMET)
- **Arquivo:** `dados-defesa-civil/csv/chuvas.csv`
- **Granularidade:** Diária

### 2. Meteorologia (INMET) 🆕 A coletar
- **Estação:** A521 (Belo Horizonte - Pampulha)
- **Coordenadas:** -19.88388888, -43.96944443
- **Distância de Sabará:** **17.0 km** (calculado via Haversine)
- **Período disponível:** 2006-10-09 até hoje (estação automática)
- **Variáveis:** temp_max, temp_min, temp_media, umidade, vento, pressão

#### Pesquisa de Estações INMET (via API oficial)

Consulta realizada em 18/08/2026 via `https://apitempo.inmet.gov.br/estacoes/T`:

| # | Estação | Código | Distância | Status | Início Operação |
|---|---------|--------|-----------|--------|-----------------|
| 1 | BH - Santo Agostinho | A572 | 16.1 km | ✅ Operante | **2025-08-27** (muito recente!) |
| 2 | **BH - Pampulha** | **A521** | **17.0 km** | ✅ Operante | **2006-10-09** |
| 3 | BH - Cercadinho | F501 | 19.0 km | ✅ Operante | 2013-12-26 |
| 4 | Ibirité (Rola Moça) | A555 | 26.7 km | ❌ Pane | 2008-06-05 |
| 5 | Sete Lagoas | A569 | 61.4 km | ✅ Operante | 2016-06-09 |

**Conclusão: NÃO EXISTE estação INMET em Sabará, Caeté ou Santa Luzia.**

**Escolha: A521 (Pampulha)** - melhor combinação de proximidade (17km) e série histórica longa (desde 2006).

**Justificativa acadêmica:**
> "O município de Sabará não possui estação meteorológica do INMET (verificado via API oficial em 18/08/2026). Utilizou-se a estação automática A521 (Belo Horizonte - Pampulha), situada a 17 km do ponto de interesse. Esta proximidade é meteorologicamente aceitável considerando que: (1) sistemas frontais e eventos de precipitação intensa tipicamente apresentam escala espacial superior a 20 km; (2) ambas as localidades pertencem à mesma região climática da bacia do Rio das Velhas; (3) a altitude é similar (~800m); (4) não há barreiras geográficas significativas entre os pontos."

### 3. Vazão/Target (GloFAS via Open-Meteo) ✅ JÁ COLETADO
- **Coordenadas:** -19.8867, -43.8067 (Sabará)
- **Período coletado:** 2006-01-01 a 2025-12-31 (7.305 registros)
- **Arquivo:** `data/glofas/glofas_sabara_diario.csv`
- **Variável:** river_discharge (m³/s)
- **Resolução:** ~5km (limitação inerente do GloFAS)

**Estatísticas da vazão GloFAS (2006-2025):**
| Métrica | Valor |
|---------|-------|
| Média | 2.16 m³/s |
| Mediana (P50) | 0.97 m³/s |
| P75 | 1.78 m³/s |
| P90 | 5.08 m³/s |
| P95 | 8.35 m³/s |
| P99 | 19.08 m³/s |
| Máximo | 48.55 m³/s (jan/2022) |

**Top 5 eventos de maior vazão:**
1. 10/01/2022: 48.55 m³/s
2. 11/01/2022: 46.86 m³/s
3. 09/01/2022: 43.57 m³/s
4. 10/01/2012: 40.30 m³/s
5. 09/01/2023: 32.34 m³/s

#### Por que NÃO usar dados de vazão da ANA (1939-1965)?

Os dados existentes são **muito antigos e não representativos**:

| Problema | Explicação |
|----------|------------|
| **Gap de 60 anos** | Última medição em 1965 - a bacia mudou completamente |
| **Urbanização** | Sabará e RMBH cresceram exponencialmente, alterando escoamento superficial |
| **Uso do solo** | Desmatamento, pavimentação, ocupação de várzeas |
| **Alterações no rio** | Canalizações, barragens, extração de areia |
| **Clima diferente** | Padrões de precipitação mudaram em 60 anos |

> "Utilizar dados de vazão de 1939-1965 para treinar um modelo atual seria metodologicamente inadequado. A relação chuva-vazão de 60 anos atrás não representa a dinâmica hidrológica atual da bacia. O modelo aprenderia padrões obsoletos."

#### Por que GloFAS como target é a solução

O GloFAS (Global Flood Awareness System) do ECMWF/Copernicus fornece:
- Estimativas de vazão **atuais** (1984-presente)
- Cobertura **global** (incluindo regiões sem monitoramento)
- Dados **gratuitos** e publicamente acessíveis
- Validação internacional para sistemas de alerta de cheias

**Limitação assumida:** Resolução de ~5km. O TCC argumenta que:
> "O modelo de ML calibrado com dados pluviométricos locais (estação 1943006 em Sabará) efetivamente realiza um downscaling implícito, ajustando as previsões de vazão à realidade local. Isso supera parcialmente a limitação de resolução do GloFAS."

#### Contribuição: Criando dados de vazão para Sabará

Este trabalho estabelece uma metodologia para municípios sem dados de vazão:

```
┌─────────────────────────────────────────────────────────────────┐
│  SITUAÇÃO ATUAL: Sabará não tem dados de vazão desde 1965       │
│                                                                 │
│  PROBLEMA: Como prever enchentes sem medição fluviométrica?     │
│                                                                 │
│  SOLUÇÃO PROPOSTA:                                              │
│  1. Usar GloFAS como REFERÊNCIA INICIAL de vazão                │
│  2. Treinar modelo ML: chuva_local + meteo → vazão_GloFAS       │
│  3. Modelo treinado gera "vazão local estimada"                 │
│  4. Sistema passa a funcionar SEM depender de API externa       │
│                                                                 │
│  RESULTADO: Sabará terá capacidade de previsão de vazão D+1     │
│             usando apenas dados de chuva e meteorologia locais  │
└─────────────────────────────────────────────────────────────────┘
```

**Trabalhos futuros:** Com dados gerados pelo modelo, validar contra eventos reais e calibrar limiares de alerta específicos para Sabará.

---

## Período de Estudo

- **Período completo:** 2006-2025 (19 anos - coincide com disponibilidade INMET A521)
- **Split temporal:**
  - Treino: 2006-2019 (~5.000 dias)
  - Teste: 2020-2025 (~2.000 dias)
- **Validação:** 5 eventos confirmados pela Defesa Civil (todos após 2020)

**Por que 2006-2025 (e não 1997-2025):**
- INMET A521 começou apenas em outubro/2006
- Usar período mais curto mas com TODOS os dados disponíveis
- Mantém consistência entre features (não há buraco nos dados INMET)

**Experimento alternativo:** Treinar modelo SEM dados INMET (apenas chuva ANA) para período 1997-2025, comparando performance.

---

## Sobre Vazamento de Dados (Data Leakage)

**NÃO HÁ VAZAMENTO.** A arquitetura evita isso:

1. **Features temporalmente corretas:**
   - Todas as features são do dia D (ou anteriores)
   - chuva_3d = soma dos dias D-2, D-1, D
   - lags = valores de dias anteriores (D-1, D-2, etc.)
   
2. **Target é futuro:**
   - target = vazão GloFAS do dia D+1
   - Nunca usamos vazão D+1 como feature
   
3. **Split temporal rigoroso:**
   - Treino ANTES de 2020
   - Teste A PARTIR de 2020
   - Nenhuma mistura de anos

**Sobre overfitting:**
- Mitigado por validação temporal (TimeSeriesSplit)
- Regularização no modelo (class_weight='balanced')
- Conjunto de teste de 5+ anos nunca visto

---

## Checklist de Execução

### Fase 1: Coleta de Dados (Hoje)

- [ ] **1.1 Processar chuva ANA**
  ```python
  # Já temos o arquivo, só precisa despivotar
  # dados-defesa-civil/csv/chuvas.csv → formato diário
  ```

- [ ] **1.2 Baixar dados INMET**
  
  **Opção A: Via portal INMET (RECOMENDADO)**
  1. Acessar https://portal.inmet.gov.br/dadoshistoricos
  2. Baixar ZIPs de 2006-2025
  3. Filtrar estação A521 (Pampulha)
  4. Processar com script `scripts/processar_inmet.py`
  
  **Opção B: Via API (pode ter instabilidade)**
  ```bash
  python scripts/coleta_inmet_api.py
  ```
  
  **Opção C: Via inmet-fetcher (automatizado)**
  ```bash
  pip install git+https://github.com/Quantilica/inmet-fetcher.git
  mkdir -p data/inmet
  inmet-fetcher sync 2006:2025 -o ./data/inmet --workers 4
  ```
  
  **Variáveis necessárias:**
  - TEMP_MIN, TEMP_MAX, TEMP_MED (temperatura)
  - UMID_MIN, UMID_MAX, UMID_MED (umidade relativa)
  - CHUVA (precipitação - complementar à ANA)
  - VEL_VENTO_MED (velocidade do vento)
  - PRESS_ATM_MED (pressão atmosférica)

- [ ] **1.3 Baixar dados GloFAS** ✅ **FEITO**
  ```
  Arquivo: data/glofas/glofas_sabara_diario.csv
  Período: 2006-01-01 a 2025-12-31
  Registros: 7.305 dias
  ```

### Fase 2: Pré-processamento

- [ ] **2.1 Despivotar chuvas**
  - Formato original: 1 linha/mês, colunas Chuva01-Chuva31
  - Formato final: 1 linha/dia, coluna precipitacao
  
- [ ] **2.2 Processar INMET**
  - Agregar dados horários → diários
  - Extrair: temp_max, temp_min, temp_media, umidade, vento, pressao

- [ ] **2.3 Juntar datasets**
  ```python
  df = df_chuva.merge(df_inmet, on='data', how='inner')
  df = df.merge(df_glofas, on='data', how='inner')
  ```

### Fase 3: Feature Engineering

- [ ] **3.1 Criar acumulados de chuva**
  ```python
  for janela in [3, 7, 14, 30]:
      df[f'chuva_acum{janela}d'] = df['precipitacao'].rolling(janela).sum()
  ```

- [ ] **3.2 Criar lags**
  ```python
  for lag in range(1, 8):
      df[f'chuva_lag{lag}'] = df['precipitacao'].shift(lag)
      df[f'vazao_lag{lag}'] = df['vazao_glofas'].shift(lag)
  ```

- [ ] **3.3 Criar target D+1**
  ```python
  df['target'] = df['vazao_glofas'].shift(-1)
  ```

- [ ] **3.4 Adicionar sazonalidade**
  ```python
  df['mes'] = df['data'].dt.month
  df['estacao_chuvosa'] = df['mes'].isin([10,11,12,1,2,3]).astype(int)
  ```

### Fase 4: Treinamento

- [ ] **4.1 Split temporal**
  ```python
  treino = df[df['data'] < '2020-01-01']
  teste = df[df['data'] >= '2020-01-01']
  ```

- [ ] **4.2 Treinar modelos**
  - Logistic Regression (baseline)
  - Random Forest
  - XGBoost
  - SVM

- [ ] **4.3 Avaliar com baseline operacional**
  ```python
  # Regra PLANCON: chuva >= 100mm em 72h
  y_baseline = (teste['chuva_acum3d'] >= 100).astype(int)
  ```

### Fase 5: Avaliação

- [ ] **5.1 Métricas**
  - F1-Score
  - Precision / Recall
  - Confusion Matrix

- [ ] **5.2 Validar eventos reais**
  
  **Análise dos dados GloFAS vs eventos históricos:**
  
  | Evento | Tipo | Data | Vazão GloFAS | Percentil | Capturado? |
  |--------|------|------|--------------|-----------|------------|
  | Enchente jan/2020 | Fluvial | 27/01/2020 | 20.18 m³/s | P99.1 | ✅ SIM |
  | Enchente jan/2022 | Fluvial | 09/01/2022 | 48.55 m³/s | P100 | ✅ SIM |
  | Alagamento out/2023 | Urbano | 26/10/2023 | 0.64 m³/s | P24 | ❌ NÃO |
  | Alagamento nov/2024 | Urbano | 13/11/2024 | 0.83 m³/s | P39 | ❌ NÃO |
  
  **Conclusão importante:** O modelo de vazão (GloFAS/ML) captura bem eventos FLUVIAIS (subida do rio), mas NÃO captura eventos de ALAGAMENTO URBANO (chuva intensa localizada). Isso é esperado e deve ser documentado como limitação do modelo.
  
  **Limiares sugeridos (baseados em P95/P99):**
  - Normal: < 5.08 m³/s (P90)
  - Atenção: 5.08-8.35 m³/s (P90-P95)
  - Alerta: 8.35-19.08 m³/s (P95-P99)
  - Emergência: > 19.08 m³/s (P99)

- [ ] **5.3 Feature importance**
  - Identificar variáveis mais relevantes

---

## Cronograma

| Atividade | Prazo | Status |
|-----------|-------|--------|
| Coleta INMET + GloFAS | 19-21/08 | ⏳ |
| Pré-processamento | 22-23/08 | ⏳ |
| Feature Engineering | 24-25/08 | ⏳ |
| Survey ML/enchentes | 25/08 | ⏳ |
| Treino + validação | 01-03/09 | ⏳ |
| Resultados + texto | 17-30/09 | ⏳ |
| Revisão + slides | Out/2026 | ⏳ |
| Defesa | Nov/2026 | ⏳ |

---

## Argumentação para o TCC

### 1. Por que NÃO usar vazão real da ANA (1939-1965)?

> "Os dados de vazão da ANA para Sabará terminam em 1965, representando um **gap de 60 anos**. Neste período, a bacia hidrográfica sofreu transformações profundas:
> - Urbanização acelerada de Sabará e RMBH (população multiplicou por 10x)
> - Mudanças drásticas no uso do solo (desmatamento, pavimentação, ocupação irregular)
> - Alterações físicas no rio (canalizações, barragens, extração de areia)
> - Mudanças climáticas documentadas nas últimas décadas
>
> Utilizar dados de vazão de 60 anos atrás para treinar um modelo atual seria metodologicamente inadequado. A relação chuva-vazão de 1965 não representa a dinâmica hidrológica atual. **É melhor usar uma referência internacional atual (GloFAS) do que dados locais obsoletos.**"

### 2. Por que usar GloFAS como referência de vazão?

> "O GloFAS (Global Flood Awareness System) do ECMWF/Copernicus é o sistema de previsão de cheias mais utilizado mundialmente. Fornece estimativas de vazão para qualquer ponto do planeta, incluindo regiões sem monitoramento fluviométrico como Sabará.
>
> **Vantagens:**
> - Dados atuais (1984-presente)
> - Validação internacional
> - Gratuito e publicamente acessível
>
> **Limitação reconhecida:** Resolução de ~5km pode não capturar detalhes locais.
>
> **Mitigação:** O modelo de ML, ao ser treinado com dados pluviométricos locais (estação 1943006 em Sabará), realiza implicitamente um ajuste local das previsões de vazão."

### 3. Por que usar INMET de BH para Sabará?

> "Consulta à API oficial do INMET (18/08/2026) confirmou que **não existe estação meteorológica em Sabará, Caeté ou Santa Luzia**. A estação A521 (BH-Pampulha), a 17 km de distância, é a mais próxima com série histórica adequada (desde 2006).
>
> Esta distância é meteorologicamente aceitável:
> - Sistemas de precipitação intensa têm escala > 20km
> - Mesma região climática e altitude (~800m)
> - Sem barreiras geográficas significativas
> - Prática comum em estudos hidrológicos brasileiros"

### 4. Qual a contribuição do trabalho?

> "Este trabalho estabelece uma **metodologia para gerar capacidade de previsão de vazão em municípios sem infraestrutura de monitoramento fluviométrico**:
>
> 1. Identifica fontes de dados locais disponíveis (ANA, INMET)
> 2. Usa GloFAS como referência inicial de vazão
> 3. Treina modelo ML: dados_locais → vazão_estimada
> 4. Modelo treinado funciona independente de APIs externas
>
> Resultado: Sabará ganha capacidade de previsão D+1 usando apenas dados locais. Metodologia replicável para outros 5.000+ municípios brasileiros sem monitoramento fluviométrico."

### 5. O que o modelo permite em produção?

> "Após treinamento, a Defesa Civil de Sabará poderá:
> - Receber previsão de vazão D+1 usando apenas dados de chuva e meteorologia
> - Operar sem depender de estação fluviométrica (inexistente)
> - Operar sem depender de APIs externas (offline-capable)
> - Calibrar limiares de alerta específicos para a realidade local
>
> Isso representa uma solução de **baixo custo** para municípios sem infraestrutura."

---

## Trabalhos Futuros

1. **Validação com dados reais:** Contatar COPASA/CBH Rio das Velhas para obter dados de vazão medida (posto de Rio Acima) e validar o modelo
2. **Expansão:** Adaptar metodologia para outros municípios da bacia do Rio das Velhas
3. **Integração:** Conectar modelo a sistema de alertas em tempo real
4. **Modelos avançados:** Testar redes neurais recorrentes (LSTM) para capturar dependências temporais mais complexas
