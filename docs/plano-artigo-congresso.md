# Plano Completo - Artigo Científico e TCC Final

Este é o plano completo e estruturado para reescrever o pré-projeto e transformá-lo em um **artigo científico de alto nível e TCC final**, pronto para submissão em congressos (como a ABRHidro ou eventos da SBC) e aprovação com nota máxima na banca examinadora.

---

## 1. MUDANÇAS ESTRATÉGICAS NA NARRATIVA DO TRABALHO

A principal evolução do projeto em relação ao pré-projeto original foi a transição de um modelo de **classificação binária simples** para um **framework de modelagem chuva-vazão contínua com módulo de alerta quantílico**:

```
 [ ABORDAGEM ANTIGA (Pré-Projeto) ]
 Precipitação → Modelo de Classificação Binária → Risco / Não Risco (Rótulo fixo PLANCON)

 [ NOVA ABORDAGEM (Versão Final Otimizada) ]
 Precipitação + Meteorologia + Features Físicas (VPD, Sazonalidade, Lag) 
   │
   ▼
 XGBoost / Random Forest (Previsão Contínua de Vazão D+1, Target GloFAS)
   │
   ▼
 Mapeamento Quantílico (Q90, Q95, Q99) → Níveis Operacionais de Alerta (POD, FAR, CSI)
```

### Por que essa mudança convence os revisores do congresso?

1. **Evita o Vazamento de Informação do PLANCON:** No pré-projeto, usar a regra do PLANCON para criar o rótulo e depois tentar prever esse mesmo rótulo criava uma redundância circular.

2. **Resolve o Problema da Bacia Não-Monitorada (PUB):** O modelo é apresentado como um **Modelo Emulador (Surrogate Model)** que aprende a resposta da bacia sem depender de estações fluviométricas locais in-situ.

3. **Demonstra um Estudo de Ablação Causal:** O artigo prova, passo a passo, como a inclusão de variáveis físicas ($VPD$, $P_{60d}$, $P_{90d}$, $\sin/\cos\text{DOY}$) fez o modelo saltar de $KGE = 0,583$ para **$KGE = 0,693$ (+18,9%)** no conjunto de teste.

---

## 2. ESTRUTURA DETALHADA E CONTEÚDO DE CADA SEÇÃO

### TÍTULO SUGERIDO

> **Modelagem Chuva-Vazão Sem Informação Fluviométrica Antecedente via Aprendizado de Máquina: Sistema de Alerta para o Município de Sabará-MG**

---

### RESUMO / ABSTRACT

**O que escrever:**

- Contextualizar a escassez de dados fluviométricos *in-situ* em bacias tropicais urbanas.
- Definir o objetivo: estimar a vazão contínua em $D+1$ usando **apenas** variáveis meteorológicas e pluviométricas (modelo puro) via Random Forest e XGBoost.
- Mencionar a estratégia de validação: treino em 1997–2016 com `TimeSeriesSplit` (5 folds), validação em 2017–2021 e teste em 2022–2026 (incluindo as cheias históricas de 2022).
- **Destacar os resultados numéricos finais:** O XGBoost atingiu $KGE = 0,693$ e $R^2 = 0,643$ após a engenharia de atributos físico-hidrológicos, representando um ganho de 18,9% sobre a baseline básica.
- Concluir mencionando a conversão das vazões previstas em níveis operacionais de alerta ($Q_{90}, Q_{95}, Q_{99}$).

---

### SEÇÃO 1: INTRODUÇÃO

#### 1.1 Contextualização e Problema do Estudo de Caso

- Descrever a vulnerabilidade de Sabará-MG a enchentes decorrentes da calha do Rio das Velhas e do Ribeirão Sabará.
- Explicar a limitação operacional: a ausência/desativação de postos fluviométricos telemétricos *in-situ* em tempo real.

#### 1.2 O Paradigma da Modelagem Chuva-Vazão Pura

- Explicar explicitamente a premissa fundamental: o modelo **não** utiliza a vazão do dia anterior ($Q_t$) como atributo de entrada.
- Justificar: modelos que usam $Q_t$ funcionam apenas como operadores de persistência e falham em bacias não-monitoradas. O modelo chuva-vazão puro força o algoritmo a aprender os processos físicos de retenção e infiltração no solo.

#### 1.3 Reanálise GloFAS como Target (Surrogate Modeling)

- Apresentar o uso da reanálise hidrológica global GloFAS-ERA5 como *ground truth* para treinamento.
- Posicionar o modelo como um **Emulador de Alta Eficiência** alimentado por dados observados de superfície (estações da ANA e INMET).

#### 1.4 Contribuições Principais do Trabalho

1. Criação de uma base integrada diária de 29 anos (1997–2026) unindo ANA, INMET e GloFAS.
2. Framework de engenharia de atributos físicos que elevou o desempenho preditivo para $KGE = 0,693$.
3. Validação temporal rigorosa em evento extremo fora da distribuição (cheia de janeiro de 2022).
4. Mapeamento das saídas contínuas em limiares operacionais de alerta para a Defesa Civil.

---

### SEÇÃO 2: TRABALHOS RELACIONADOS

**Como estruturar para convencer a banca:**

- **Grupo 1: Modelagem Chuva-Vazão com ML e Redes Neurais:** Discutir trabalhos que aplicam XGBoost, Random Forest e LSTM em bacias brasileiras.

- **Grupo 2: O Problema das Bacias Não-Monitoradas (PUB):** Citar publicações internacionais mostrando a transição de modelos conceituais para modelos de aprendizado de máquina puros.

- **Grupo 3: Uso de Reanálise Hidrológica como Proxy:** Citar iniciativas globais (como a plataforma de previsão de inundações do Google e o ECMWF GloFAS) que utilizam reanálise para treinar modelos em regiões sem sensores fluviométricos.

- **Diferencial do seu trabalho:** Enfatizar que, ao contrário dos trabalhos citados na literatura local que dependem de medições fluviométricas contínuas em tempo real, a sua abordagem é 100% operacional para locais desprovidos de sensores no rio.

---

### SEÇÃO 3: METODOLOGIA

#### 3.1 Área de Estudo e Fontes de Dados

Apresentar a tabela consolidada das fontes utilizadas:

| Fonte | Variáveis Coletadas | Período Utilizado | Função no Projeto |
|-------|---------------------|-------------------|-------------------|
| **ANA (Estação 1943006)** | Precipitação Diária (mm) | 1997 – 2026 | Feature de Entrada |
| **INMET (Estação BH 83587)** | Temp. ($T_{med}, T_{max}, T_{min}$), Umidade ($RH$) | 1997 – 2026 | Feature de Entrada |
| **GloFAS / Copernicus** | Vazão Diária de Reanálise (m³/s) | 1997 – 2026 | Target do Modelo ($Y$) |

#### 3.2 Engenharia de Atributos Físico-Hidrológicos (Feature Engineering)

Apresentar o conjunto final de atributos e a **justificativa física** de cada um:

- **Sazonalidade Cíclica ($\sin\_doy, \cos\_doy$):** Codificação do dia do ano para informar o estado estacional da bacia (estação seca vs. chuvosa).

- **Atmosfera e Evaporação ($VPD$):** Calculado via $T_{med}$ e $RH$, mede o déficit de pressão de vapor e a taxa de secagem do solo.

- **Retenção de Longo Prazo e Aquíferos ($P_{60d}, P_{90d}, API_{30d}$):** Representam a memória profunda e o estado de saturação prévia dos lençóis freáticos.

- **Tempo de Concentração e Deslocamento ($P_{t-3}, P_{t-4}$):** Representam o tempo de viagem da água do alto curso do Rio das Velhas até Sabará.

#### 3.3 Divisão dos Dados e Estratégia de Validação Temporal

Detalhar o arranjo cronológico que evita vazamento de dados (*data leakage*):

- **Treinamento (1997–2016):** Usado para ajuste dos pesos dos modelos.
- **Tuning com `TimeSeriesSplit(n_splits=5)`:** Validação cruzada temporal expansiva aplicada **estritamente dentro do conjunto de treino**.
- **Validação (2017–2021):** Utilizada para confirmação dos hiperparâmetros e *early stopping*.
- **Teste Final Holdout (2022–2026):** Conjunto "cego" preservado exclusivamente para a avaliação final.

#### 3.4 Algoritmos e Otimização

- Descrever os modelos testados: **Random Forest Regressor** e **XGBoost Regressor**.
- Detalhar o processo de busca em grade (`GridSearchCV`) otimizando diretamente a métrica $KGE$ via `make_scorer(calculate_kge, greater_is_better=True)`.

#### 3.5 Métricas de Avaliação Hidrológica

- Apresentar as equações matemáticas do $KGE$ (Eficiência de Kling-Gupta), $NSE$, $R^2$, $RMSE$ e $MAE$.
- Explicar por que a baseline de comparação da média climatológica possui $KGE = -0,41$, demonstrando que qualquer $KGE > 0,50$ indica capacidade preditiva satisfatória.

#### 3.6 Módulo de Alerta Operacional Categórico

- Detalhar o mapeamento das previsões contínuas em três limiares quantílicos da série histórica ($Q_{90}, Q_{95}, Q_{99}$).
- Apresentar as métricas categóricas de avaliação do alerta: Probabilidade de Detecção ($POD$), Taxa de Falsos Alarmes ($FAR$) e Índice de Sucesso Crítico ($CSI$).

---

### SEÇÃO 4: RESULTADOS E DISCUSSÃO

#### 4.1 Estudo de Ablação: A Evolução da Engenharia de Features

Apresentar a tabela comparativa que comprova o ganho metodológico:

| Etapa do Experimento | Atributos Utilizados | XGBoost Test $KGE$ | XGBoost Test $R^2$ | Impacto Relativo |
|----------------------|----------------------|--------------------|--------------------|------------------|
| **1. Modelo Básico** | 13 atributos (Chuva diária, $API$, meteorologia simples) | 0,583 | 0,550 | Baseline |
| **2. + Física e Sazonalidade** | 19 atributos (+ $\sin/\cos\text{DOY}$, $VPD$, $P_{60d}$, lags 3d/4d) | 0,679 | 0,620 | +16,5% |
| **3. Modelo Final Otimizado** | Atributos selecionados (+ $P_{90d}$ e poda de variáveis fracas) | **0,693** | **0,643** | **+18,9%** |

#### 4.2 Importância dos Atributos e Interpretabilidade Física (SHAP Analysis)

Discutir o ranking de importância das variáveis do modelo campeão (XGBoost):

- Destacar que o $API_{30d}$, a umidade média, o $VPD$ e os acumulados de longo prazo ($P_{60d}, P_{90d}$) dominaram a capacidade preditiva.
- Discutir como o SHAP confirma a física do modelo: valores elevados de $API_{30d}$ combinados com baixo $VPD$ aumentam a previsão de vazão em $D+1$.

#### 4.3 Desempenho no Período de Teste e Eventos Extremos de 2022

- Apresentar o gráfico de linhas (hidrograma) comparando a vazão real do GloFAS com a previsão do XGBoost durante o evento catastrófico de janeiro de 2022 em Sabará.
- Discutir a limitação das árvores de decisão na extrapolação de picos inéditos, explicando como o modelo ainda assim conseguiu capturar a curva de ascensão do hidrograma com antecedência de 24 horas.

#### 4.4 Avaliação do Módulo de Alerta da Defesa Civil

Apresentar a matriz de confusão e a tabela de métricas categóricas para o limiar de emergência ($Q_{99}$):

- Reportar os valores de $POD$, $FAR$ e $CSI$.
- Demonstrar que o modelo minimiza falsos negativos, atendendo ao objetivo operacional de proteção de vidas.

---

### SEÇÃO 5: CONCLUSÃO E TRABALHOS FUTUROS

#### Conclusões

- Reafirmar que foi possível construir um modelo chuva-vazão puro com $KGE = 0,693$ sem depender de medições de vazão em tempo real.
- Validar o uso de reanálises globais (GloFAS) combinadas com aprendizado de máquina como solução viável para a gestão de riscos em municípios desprovidos de dados telemétricos.

#### Trabalhos Futuros

1. Testar redes neurais profundas do tipo **LSTM (Long Short-Term Memory)** para avaliar se a memória celular supera as árvores na extrapolação de picos de cheia.
2. Expandir a previsão para múltiplos horizontes ($D+2$ e $D+3$) integrando previsões numéricas de tempo (NWP).
3. Desenvolver uma interface/dashboard para a Defesa Civil de Sabará operar o modelo em tempo real.

---

## 3. CHECKLIST FINAL DE APROVAÇÃO E SUBMISSÃO

### Gráficos essenciais a incluir na versão final:

- [ ] Mapa de localização da bacia do Rio das Velhas e do município de Sabará.
- [ ] Diagrama do fluxo metodológico (Coleta → Feature Engineering → TimeSeriesSplit → XGBoost → Quantis de Alerta).
- [ ] Gráfico de *SHAP Summary Plot* mostrando a importância e o impacto físico das variáveis.
- [ ] Hidrograma do período de teste (2022–2026) destacando o evento de janeiro de 2022.

### Citações e Referências bibliográficas:

- Garantir que artigos clássicos de $KGE$ (Gupta et al., 2009; Kling et al., 2012) e de modelagem chuva-vazão pura via ML estejam devidamente referenciados no texto.

---

## 4. RESUMO DOS RESULTADOS FINAIS

### Métricas do Modelo Final (XGBoost)

| Conjunto | KGE | R² | RMSE (m³/s) | MAE (m³/s) |
|----------|-----|-----|-------------|------------|
| Validação (2017-2021) | 0.706 | 0.559 | 1.64 | 0.90 |
| **Teste (2022+)** | **0.693** | **0.643** | **2.86** | **1.36** |

### Evolução do Projeto (Estudo de Ablação)

| Etapa | Features | XGB Test KGE | Ganho |
|-------|----------|--------------|-------|
| 1. Original | 13 | 0.583 | Baseline |
| 2. + Física | 19 | 0.679 | +16.5% |
| 3. + Memória | 20 | **0.693** | **+18.9%** |

### Features Finais (20 atributos)

```python
FEATURE_COLS = [
    'chuva_mm', 'temp_media', 'temp_max', 'temp_min', 'umidade_media',
    'chuva_3d', 'chuva_7d', 'chuva_14d', 'chuva_30d', 'chuva_60d', 'chuva_90d',
    'api_7d', 'api_30d',
    'chuva_ontem', 'chuva_anteontem', 'chuva_3d_atras', 'chuva_4d_atras',
    'sin_doy', 'cos_doy', 'vpd'
]
```
