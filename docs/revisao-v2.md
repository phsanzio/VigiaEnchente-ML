# Fundamentação Teórica e Metodológica para Previsão Hidrológica com ML

## Bacia do Alto Rio das Velhas (Sabará - MG)

> **Revisão de Literatura v2** - Gemini Deep Research (Agosto 2026)

---

## 1. Tratamento de Dados Faltantes: Pressão Atmosférica, VPD e Extensão Temporal

### 1.1 Importância Relativa da Pressão Atmosférica

A pressão atmosférica de superfície atua primariamente como uma variável de estado termodinâmico de escala sinótica que sinaliza a aproximação de frentes ou centros de baixa pressão. Em modelos hidrológicos orientados a dados (data-driven) em escala diária, **a inclusão da pressão atmosférica apresenta ganho marginal ou desprezível** quando as séries temporais já contêm variáveis como precipitação, temperatura, umidade relativa e vento.

A resposta hidrológica da bacia decorre da conversão do volume pluviométrico em escoamento superficial e subterrâneo, regulada pelo estado de umidade antecedente do solo e pela taxa de evapotranspiração real. Como o pluviômetro já registra a precipitação efetiva que atinge a superfície, o sinal físico que a queda de pressão atmosférica indicaria no tempo presente já se encontra explicitado no volume de chuva registrado.

**Citações:**

> **Zubelzu et al. (2024)** - "A combined data-driven and physical approach for predicting runoff occurrence and volume at catchment scale", Journal of Environmental Management. DOI: 10.1016/j.jenvman.2024.120404
> 
> Demonstraram que a umidade relativa e a precipitação dominam a capacidade preditiva, enquanto a pressão atmosférica apresenta contribuição marginal na redução do erro quadrático.

> **Papacharalampous et al. (2019)** - "Predictability of monthly streamflow using data-driven models and meteorological inputs", Hydrological Sciences Journal. DOI: 10.1080/02626667.2019.1661414
> 
> Constataram que modelos parcimoniosos baseados unicamente em temperatura, umidade e histórico pluviométrico alcançam eficiências hidrológicas equivalentes ou superiores a modelos que incorporam pressão de superfície.

### 1.2 Déficit de Pressão de Vapor (VPD)

O VPD define a diferença entre a pressão de vapor de saturação ($e_s$) e a pressão real de vapor do ar ($e_a$):

$$VPD = e_s - e_a$$

O VPD constitui uma das principais forças motrizes da evapotranspiração. Em modelos de balanço hídrico contínuo, taxas elevadas de VPD aceleram a secagem do perfil do solo durante períodos de estiagem.

**Importante:** A ausência de sensores de pressão atmosférica **não inviabiliza** o cálculo do VPD. Conforme a formulação FAO-56, a pressão de vapor de saturação é determinada pela temperatura através da equação de Tetens:

$$e^0(T) = 0.61078 \exp\left( \frac{17.27 \, T}{T + 237.3} \right)$$

Para resolução diária:

$$e_s = \frac{e^0(T_{max}) + e^0(T_{min})}{2}$$

A pressão real de vapor ($e_a$) é computada a partir da umidade relativa média ($UR$, em %):

$$e_a = e_s \times \frac{UR}{100}$$

O VPD diário (em kPa):

$$VPD = e_s \times \left(1 - \frac{UR}{100}\right)$$

**Citação:**

> **Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998)** - "Crop Evapotranspiration: Guidelines for Computing Crop Water Requirements", FAO Irrigation and Drainage Paper 56. ISBN: 92-5-104219-5
> 
> Padroniza os procedimentos matemáticos para cálculo do VPD e evapotranspiração a partir de temperatura máxima, mínima e umidade relativa.

### 1.3 Estação Convencional vs. Automática

| Critério | Estação Convencional 83587 | Estação Automática (pós-2006) |
|----------|---------------------------|------------------------------|
| Janela Temporal | 1997-2026 (~10.700 registros) | 2006-2026 (~7.300 registros) |
| Eventos Extremos | Registra 1997, 2003, 2008, 2020, 2022, 2023, 2024 | Perde 1997 e início dos anos 2000 |
| Variáveis | T_med, T_max, T_min, UR_med, Vento_med | T, UR, Vento, Radiação, **Pressão** |
| Impacto | Ampla cobertura estatística | Redução amostral de ~32% |

**Recomendação:** Preservar a série longa da estação convencional 83587 (1997-2026). Trocar 30 anos por 20 anos apenas para incorporar pressão atmosférica **degradaria a distribuição amostral das vazões máximas, com ganho preditivo mínimo**.

---

## 2. Representatividade Espacial e Dinâmica Climatológica Regional

### 2.1 Uso de Estações Meteorológicas a 15-20 km de Distância

O aproveitamento de dados meteorológicos da estação 83587 (Belo Horizonte), situada a aproximadamente 17 km de Sabará, fundamenta-se na escala espacial das variáveis termodinâmicas continentais. Grandezas como temperatura, umidade relativa e velocidade do vento apresentam **raios de correlação espacial de 30 a 50 km** em relevos de planalto.

A precipitação, que apresenta maior variabilidade espacial, está sendo aferida diretamente no município pelo pluviômetro local (ANA 1943006). Consequentemente, o forçamento hídrico principal é local, enquanto a estação de BH fornece a demanda evaporativa regional.

**Citações:**

> **Blöschl, G., et al. (2019)** - "Twenty-three unsolved problems in hydrology (UPH)", Hydrological Sciences Journal, 64(10), 1141-1158. DOI: 10.1080/02626667.2019.1620507
> 
> Discute os limites de representatividade espacial e transferência de dados meteorológicos entre pontos vizinhos.

> **Ly, S., Charles, C., & Degré, A. (2013)** - "Different methods for spatial interpolation of rainfall analysis for daily hydrological modelling in data-scarce regions", Water Resources Management, 27(6), 1829-1843. DOI: 10.1007/s11269-012-0248-2
> 
> Demonstra que modelos **toleram distâncias superiores a 20 km para preditores de demanda evaporativa** (temperatura e umidade) sem perda estatística de desempenho.

### 2.2 Escala dos Sistemas Meteorológicos

| Fenômeno | Escala Espacial | Duração | Resposta Hidrológica |
|----------|-----------------|---------|---------------------|
| **ZCAS** | 1.000-3.000 km | 3-10 dias | Cheias volumétricas graduais |
| **Frentes Frias** | 500-1.500 km | 1-3 dias | Elevação generalizada |
| **Convecção Local** | 5-30 km | 30min-3h | Flash floods em córregos |

Como os episódios de cheia decorrem da ZCAS, o campo de precipitação cobre simultaneamente BH e Sabará. A distância de 17 km insere-se na mesma macroestrutura atmosférica.

**Citações:**

> **Carvalho, L. M. V., Jones, C., & Liebmann, B. (2004)** - "The South Atlantic Convergence Zone: Intensity, form, persistence, and relationships with intraseasonal to interannual activity and extreme rainfall", Journal of Climate, 17(1), 88-108. DOI: 10.1175/1520-0442(2004)017<0088:TSACZI>2.0.CO;2

> **Nobre, C. A., et al. (2016)** - "Characteristics of extreme rainfall events in the southeastern region of Brazil", Natural Hazards, 83(2), 1079-1094. DOI: 10.1007/s11069-016-2415-3

---

## 3. Utilização do GloFAS como Variável Alvo e Preditor Autorregressivo

### 3.1 Validação do GloFAS em Bacias Tropicais

O GloFAS (Global Flood Awareness System), operacionalizado pelo Copernicus/ECMWF, gera estimativas diárias de vazão fluvial global mediante acoplamento da reanálise ERA5 ao modelo hidrológico LISFLOOD.

**Citações:**

> **Harrigan, S. et al. (2020)** - "GloFAS-ERA5 operational global river discharge reanalysis 1979-present", Earth System Science Data, 12, 2043-2060. DOI: 10.5194/essd-12-2043-2020
> 
> Avaliou globalmente a reanálise de vazão do GloFAS frente a 1.801 estações. **O estudo constatou que a reanálise superou o referencial de escoamento médio em 86% das bacias** (medido pelo KGE).

> **Mendoza, M. A., et al. (2021)** - "Evaluating the Potential of GloFAS-ERA5 River Discharge Reanalysis Data for Calibrating Hydrological Models in Ungauged Basins", Remote Sensing, 13(16), 3299. DOI: 10.3390/rs13163299
> 
> Comprovou que o GloFAS apresenta correlação > 0,80 e KGE > 0,74 para calibração hidrológica em regiões tropicais com déficit de monitoramento.

### 3.2 Limitações do GloFAS

1. **Vieses Volumétricos:** Resolução de ~5 km pode gerar vieses sistemáticos em bacias de cabeceira
2. **Atenuação de Picos:** A grade global tende a suavizar picos instantâneos em microbacias
3. **Incertezas de Forçamento:** Tempestades orográficas localizadas podem ser atenuadas

**Estratégia de Mitigação:** O modelo de ML atua como um corretor empírico de viés (bias correction), aprendendo a dinâmica de propagação a partir de variáveis locais (chuva ANA + meteorologia INMET).

### 3.3 Vazão como Target E Feature - É Válido!

A inclusão da vazão histórica ($Q_t$, $Q_{t-1}$) para prever $Q_{t+1}$ é **plenamente aceitável e recomendada**. Essa estruturação configura um modelo **NARX** (autorregressivo não-linear com entradas exógenas).

**Não é Data Leakage** porque:
- No instante $t$, a vazão $Q_t$ já foi observada (pertence ao passado)
- O alvo é exclusivamente $Q_{t+1}$ (futuro)
- Todos os preditores pertencem ao intervalo temporal $(-\infty, t]$

**Citações:**

> **Kratzert, F. et al. (2018)** - "Rainfall-runoff modelling using Long Short-Term Memory (LSTM) networks", Hydrology and Earth System Sciences, 22(11), 6005-6022. DOI: 10.5194/hess-22-6005-2018
> 
> Define a estrutura formal de causalidade temporal para modelos de ML em escala diária.

> **Rozos, E., & Dimitriadis, P. (2021)** - "Autoregressive and Machine Learning Models for Streamflow Forecasting", Water, 13(11), 1585. DOI: 10.3390/w13111585
> 
> Demonstra o ganho de acurácia proporcionado por componentes autorregressivos em horizonte D+1.

---

## 4. Índice de Precipitação Antecedente (API)

### 4.1 Origem e Fundamentação

O API é uma métrica hidrológica formulada por **Kohler & Linsley (1951)** no US Weather Bureau para estimar as condições de umidade inicial do solo.

A formulação contínua diária fundamenta-se na premissa de que a umidade acumulada decai exponencialmente:

$$API_t = \sum_{i=1}^{k} \alpha^i P_{t-i}$$

Onde:
- $P_{t-i}$ = precipitação no dia $t-i$ (mm)
- $\alpha$ = coeficiente de decaimento (0 < α < 1)
- $k$ = extensão da janela (dias)

**Citações:**

> **Kohler, M. A., & Linsley, R. K. (1951)** - "Predicting Runoff from Storm Rainfall", Research Paper No. 34, U.S. Weather Bureau. Washington, D.C.
> 
> Documento seminal que estabeleceu as bases matemáticas da modelagem de umidade antecedente por decaimento exponencial.

> **Heggen, R. J. (2001)** - "Normalized Antecedent Precipitation Index", Journal of Hydrologic Engineering, 6(5), 377-381. DOI: 10.1061/(ASCE)1084-0699(2001)6:5(377)
> 
> Demonstra superioridade teórica do API frente a métodos discretizados (AMC do SCS-CN).

### 4.2 Justificativa de α = 0.90

Em escala diária, a literatura estabelece a faixa de 0,80 a 0,98:

| Região | α |
|--------|---|
| Semiáridas / solos arenosos | 0,80-0,85 |
| **Tropicais úmidas / latossolos** | **0,88-0,92** |
| Temperadas frias / solos orgânicos | 0,93-0,98 |

A adoção de **α = 0.90 com k = 30 dias** é compatível com o Alto Rio das Velhas. Sob essa parametrização:
- Chuva de 1 dia atrás: peso 90%
- Chuva de 7 dias atrás: peso 47,8%
- Chuva de 30 dias atrás: peso 4,2%

### 4.3 API vs Acumulados Simples

| Aspecto | Acumulados Simples (Σ) | API |
|---------|------------------------|-----|
| Ponderação | Uniforme (todos os dias iguais) | Decaimento exponencial |
| Física | 50mm há 29 dias = 50mm ontem | 50mm há 29 dias ≈ 2mm equivalentes |
| Sinal | Descontinuidades abruptas | Variável suave e contínua |

**A coexistência de acumulados (3d, 7d, 14d, 30d) e API é vantajosa** em algoritmos de árvores, fornecendo múltiplos recortes temporais.

> **Brocca, L., Melone, F., & Moramarco, T. (2008)** - "On the estimation of antecedent wetness conditions in rainfall-runoff modelling", Hydrological Processes, 22(5), 629-642. DOI: 10.1002/hyp.6629
> 
> Evidenciou que formulações com decaimento exponencial superam acumulações simples de janela fixa.

---

## 5. Estrutura Autorregressiva e Data Leakage

### 5.1 A Prática Autorregressiva

A utilização de $Q_t$ e $Q_{t-1}$ para prever $Q_{t+1}$ constitui o **padrão consolidado** na hidrologia preditiva. A vazão instantânea reflete o volume d'água em trânsito e o nível freático. Integrar termos autorregressivos confere inércia hidrodinâmica ao modelo, permitindo captar curvas de recessão do hidrograma.

### 5.2 O Que Configuraria Data Leakage (Evitar!)

- Usar médias móveis centradas que empreguem observações futuras ($t+1$, $t+2$)
- Calcular normalização (StandardScaler) em toda a base ANTES de particionar
- Alocar variáveis do dia $t+1$ no vetor de entrada

---

## 6. Seleção de Modelos e Protocolo de Otimização

### 6.1 Portfólio Comparativo (4 modelos)

| Categoria | Modelo | Justificativa |
|-----------|--------|---------------|
| **Baseline Ingênuo** | Persistência ($\hat{Q}_{t+1} = Q_t$) | Referência mínima obrigatória |
| **Baseline Linear** | Regressão Ridge/Lasso | Limite explicativo linear |
| **Bagging** | Random Forest | Reduz variância, não-linearidades |
| **Boosting** | XGBoost | Estado da arte para dados tabulares |

**4 modelos são suficientes** para um TCC/CONIC, cobrindo desde persistência até ensembles avançados.

### 6.2 Protocolo de Hiperparâmetros

1. **Triagem Inicial:** Todos os modelos com parâmetros default
2. **Otimização:** Grid/Random Search no conjunto de validação
3. **Avaliação Final:** Reajuste no conjunto Treino+Validação, teste definitivo

**Citação:**

> **Probst, P., Bischl, B., & Boulesteix, A. L. (2019)** - "Tunability: Importance of hyperparameters of machine learning algorithms", Journal of Machine Learning Research, 20(53), 1-32.
> 
> Demonstra que algoritmos de gradient boosting exigem sintonia fina para desempenho superior.

> **Chen, T., & Guestrin, C. (2016)** - "XGBoost: A Scalable Tree Boosting System", KDD 2016, 785-794. DOI: 10.1145/2939672.2939785

---

## 7. Métricas de Avaliação em Regressão Hidrológica

### 7.1 KGE vs NSE

O **NSE** (Nash-Sutcliffe, 1970) tem uma deficiência estrutural: sua maximização força o modelo a **subestimar a variância**, achatando picos de cheia.

O **KGE** (Kling-Gupta Efficiency) projeta os componentes em espaço euclidiano ortogonal:

$$KGE = 1 - \sqrt{(r - 1)^2 + (\gamma - 1)^2 + (\beta - 1)^2}$$

Onde:
- $r$ = correlação linear (sincronismo)
- $\gamma$ = razão de variabilidade (preserva picos)
- $\beta$ = razão de viés volumétrico

**Citação:**

> **Gupta, H. V., Kling, H., Yilmaz, K. K., & Martinez, G. F. (2009)** - "Decomposition of the mean squared error and NSE performance criteria", Journal of Hydrology, 377(1-2), 80-91. DOI: 10.1016/j.jhydrol.2009.08.003
> 
> Artigo clássico que introduz o KGE para evitar amortecimento sistemático de vazões de pico.

### 7.2 Métricas para o TCC

- **KGE** - Avaliação integrada (sincronia, volume, amplitude)
- **RMSE** - Sensível a desvios em picos
- **MAE** - Erro médio absoluto
- **R²** - Variância explicada
- NSE (opcional, comparativo)

---

## 8. Partição Temporal e Validação

### 8.1 Divisão Cronológica (70/15/15)

| Conjunto | Período | Registros | Finalidade |
|----------|---------|-----------|------------|
| **Treino** | 1997-2016 | ~7.305 (70%) | Calibração. Contém evento 1997 |
| **Validação** | 2017-2021 | ~1.826 (15%) | Ajuste hiperparâmetros. Contém 2020 |
| **Teste** | 2022-2026 | ~1.580 (15%) | Avaliação final. Contém 2022, 2023, 2024 |

### 8.2 Por Que NÃO Usar K-Fold com Shuffle

- **Autocorrelação:** Pontos adjacentes ($t-1$, $t$, $t+1$) são estatisticamente dependentes
- **Vazamento Temporal:** Embaralhamento aloca dias intermediários de uma onda de cheia no teste e adjacentes no treino, inflacionando métricas artificialmente

**Citações:**

> **Bergmeir, C., & Benítez, J. M. (2012)** - "On the use of cross-validation for time series predictor evaluation", Information Sciences, 191, 192-213. DOI: 10.1016/j.ins.2011.12.028

> **Roberts, D. R., et al. (2017)** - "Cross-validation strategies for data with temporal, spatial, hierarchical or phylogenetic structure", Ecography, 40(8), 913-929. DOI: 10.1111/ecog.02881

### 8.3 Walk-Forward vs Partição Fixa

Walk-Forward simula operação em tempo real, mas exige retreinamento contínuo. **Para TCC/CONIC com prazo curto, partição cronológica fixa atende plenamente** aos requisitos de rigor científico.

---

## 9. Matriz de Priorização (TCC / CONIC)

### ESSENCIAL E OBRIGATÓRIO

1. **Partição Temporal Cronológica** - Treino/Validação/Teste contíguos
2. **Prevenção de Data Leakage** - Preditores em $t$ → alvo em $t+1$
3. **Modelos Baseline** - Persistência + Regressão Linear
4. **Modelos de ML** - Random Forest + XGBoost
5. **Avaliação Completa** - KGE, RMSE, MAE, R²

### DIFERENCIAL DE ALTO IMPACTO

6. **Tabela de Contingência** - Discretização em percentis (Q75, Q90, Q95) + POD, FAR, CSI
7. **Feature Importance** - Gráfico de importância relativa

### TRABALHOS FUTUROS / LIMITAÇÕES

8. Modelos Recorrentes (LSTM)
9. Previsão Multietapas (D+2, D+3, D+7)
10. Modelagem Hidráulica 2D (HEC-RAS)

---

## 10. Validação com Eventos Históricos

### 10.1 Conversão de Regressão em Limiares

Embora o modelo seja regressão contínua (m³/s), a utilidade para defesa civil depende da detecção de limiares de transbordamento. Usa-se a curva de permanência calculada **exclusivamente sobre o treino (1997-2016)**:

| Percentil | Nível | Significado |
|-----------|-------|-------------|
| Q75 | Atenção | Cheia intermediária |
| Q90 | Alerta | Extravasamento em pontos baixos |
| Q95/Q98 | Emergência | Transbordamento generalizado |

### 10.2 Métricas Categóricas

- **POD** (Probability of Detection) = H / (H + M)
- **FAR** (False Alarm Ratio) = FA / (H + FA)
- **CSI** (Critical Success Index) = H / (H + FA + M)

### 10.3 Enquadramento dos Eventos

| Evento | Conjunto | Uso |
|--------|----------|-----|
| Janeiro/1997 | Treino | Assinatura de enchente centenária |
| Janeiro/2020 | Validação | Ajuste de hiperparâmetros |
| Janeiro/2022, 2023, 2024 | **Teste** | Generalização final |

Os eventos de 2022-2024 no teste demonstram se o modelo treinado até 2016 consegue **antecipar com 24h os picos de vazão recentes**.

---

## Referências Principais

1. Allen et al. (1998) - FAO-56 (VPD)
2. Bergmeir & Benítez (2012) - Validação temporal
3. Brocca et al. (2008) - API
4. Chen & Guestrin (2016) - XGBoost
5. Gupta et al. (2009) - KGE
6. Harrigan et al. (2020) - GloFAS
7. Kohler & Linsley (1951) - API original
8. Kratzert et al. (2018) - Causalidade temporal
9. Ly et al. (2013) - Representatividade espacial
10. Zubelzu et al. (2024) - Pressão atmosférica dispensável
