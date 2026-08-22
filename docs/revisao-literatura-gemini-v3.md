# Modelagem Chuva-Vazão Sem Informação Fluviométrica Antecedente via Aprendizado de Máquina

## Framework para Previsão de Inundações em Bacias Tropicais Não-Monitoradas

---

## 1. O Paradigma da Modelagem Chuva-Vazão Pura em Bacias Não-Monitoradas

A modelagem de vazão fluvial por meio de algoritmos de aprendizado de máquina subdivide-se em dois paradigmas metodológicos distintos: a **modelagem autorregressiva hidrometeorológica** e a **modelagem chuva-vazão pura**.

### Modelagem Autorregressiva Hidrometeorológica

Na modelagem autorregressiva, a vazão histórica observada nos passos de tempo anteriores ($Q_{t}, Q_{t-1}, \dots, Q_{t-k}$) é incluída como variável explicativa de entrada para prever a vazão futura ($Q_{t+1}$). 

Embora essa abordagem apresente métricas de desempenho estatístico frequentemente elevadas, com coeficientes de determinação ($R^2$) ultrapassando $0,95$, a inclusão da vazão defasada introduz uma **dependência temporal persistente** que mascara a capacidade real do algoritmo de aprender os processos físicos de transformação da precipitação em escoamento.

Nesses casos, o algoritmo atua primariamente como um **operador de persistência**, falhando em momentos críticos como:
- Ascensão súbita de hidrogramas de cheia
- Interrupções na transmissão de dados telemétricos

### Modelagem Chuva-Vazão Pura

A modelagem chuva-vazão pura restringe estritamente as variáveis de entrada aos **forçantes meteorológicos atmosféricos**:
- Precipitação
- Temperatura
- Umidade
- Evapotranspiração

Omitindo qualquer dado de vazão como feature.

Sob a ótica da literatura acadêmica e das iniciativas globais de hidrologia computacional, a modelagem chuva-vazão pura possui **valor científico e aplicabilidade prática superiores** quando o objetivo é a previsão em bacias não-monitoradas (**Prediction in Ungauged Basins - PUB**).

A ausência de medições de vazão antecedente força o modelo a aprender as relações não-lineares complexas que regem:
- O retardamento do escoamento
- A taxa de infiltração
- A saturação do solo
- A evapotranspiração da bacia

### Contexto de Sabará-MG

No contexto do município de Sabará-MG, inserido na bacia do Rio das Velhas, a adoção do modelo chuva-vazão puro é fundamental. A maioria das sub-bacias afluentes e áreas de risco de inundação urbana **não conta com estações fluviométricas telemétricas em tempo real**.

Ao demonstrar que o modelo treinado é capaz de estimar a vazão $D+1$ utilizando exclusivamente dados pluviométricos e meteorológicos de superfície, valida-se uma metodologia aplicável a qualquer trecho da bacia hidrográfica desprovido de monitoramento hidráulico direto, alinhando o trabalho às fronteiras da pesquisa internacional em hidrologia e inteligência artificial.

---

## 2. Linhas de Base (Baselines) Apropriadas para Modelos Sem Persistência

A avaliação rigorosa de um modelo de aprendizado de máquina exige a comparação contra modelos de referência (baselines) adequados à formulação do problema.

Quando a vazão histórica não é disponibilizada como variável de entrada, a linha de base tradicional baseada na **persistência simples** ($Q_{t+1} = Q_t$) torna-se inviável, exigindo a seleção de alternativas estatísticas e hidrológicas que representem o nível mínimo de conhecimento do sistema.

### 2.1 Baselines Estatísticas e Climatológicas

| Baseline | Descrição |
|----------|-----------|
| **Média Climatológica Diária** | Estima a vazão do dia $d$ como a média histórica de todos os dias $d$ registrados no conjunto de treinamento. Constitui o **limite inferior** de desempenho preditivo. |
| **Regressão Ridge ou Lasso com API** | Modelo linear regularizado que utiliza apenas a chuva do dia e os acumulados ponderados anteriores. Quantifica o ganho marginal obtido ao migrar de algoritmos lineares para arquiteturas não-lineares de ML. |

### 2.2 Baselines Hidrológicas Conceituais

| Baseline | Descrição |
|----------|-----------|
| **Modelo GR4J** | Modelo conceitual parsimonioso (Génie Rural à 4 parâmetros Journalier) amplamente utilizado na literatura como benchmark hidrológico. Utiliza dados diários de precipitação e evapotranspiração potencial para simular dois reservatórios conceituais (solo e roteamento). |
| **SCS-CN (Número da Curva)** | Modelo empírico clássico do Soil Conservation Service que estima o escoamento superficial direto com base na precipitação acumulada e na retenção potencial do solo. |

### 2.3 Síntese das Baselines

| Categoria | Modelo | Função no Estudo Comparativo |
|-----------|--------|------------------------------|
| Estatística Simples | Média Climatológica Diária | Estabelece o limite inferior de habilidade preditiva |
| Linear Regularizada | Regressão Ridge/Lasso com API | Quantifica o ganho trazido por não-linearidades de ML |
| Conceitual Hidrológica | Modelo GR4J (4 parâmetros) | Prova a superioridade de ML sobre modelos conceituais |
| Empírica de Engenharia | SCS-CN (Número da Curva) | Avalia a estimativa do escoamento superficial direto |

### 2.4 Interpretação do KGE como Referência

A interpretação das métricas contra as baselines deve fundamentar-se no estudo de **Knoben et al. (2019)**, o qual demonstrou analiticamente que a utilização da média observada como preditor contínuo resulta em um valor de Eficiência de Kling-Gupta ($KGE$) igual a **$-0,41$**.

Dessa forma:
- Qualquer modelo chuva-vazão puro que apresente $KGE > -0,41$ demonstra habilidade preditiva superior à média climatológica
- Valores de $KGE \ge 0,60$ são exigidos para conferir **utilidade operacional** ao modelo em sistemas de alerta

---

## 3. Reanálise Hidrológica (GloFAS) como Ground Truth

### 3.1 Validade Acadêmica

A ausência de postos fluviométricos in-situ com séries históricas contínuas e sem falhas é um desafio recorrente no desenvolvimento de sistemas de alerta em países em desenvolvimento.

A utilização do produto de reanálise hidrológica global **Global Flood Awareness System (GloFAS-ERA5)**, mantido pelo Serviço de Mudanças Climáticas Copernicus (CEMS) e pelo ECMWF, como variável-alvo (ground truth) para o treinamento de modelos locais de aprendizado de máquina é uma **abordagem validada na literatura internacional moderna**.

### 3.2 Referências de Uso

Projetos de grande escala utilizam dados de reanálise hidrológica:
- **Google Flood Hub**: Plataforma global de previsão de inundações
- **Arquitetura AIFL**: Artificial Intelligence for Floods

Esses projetos utilizam dados de reanálise hidrológica gerados por modelos físicos globais (LISFLOOD, HTESSEL) combinados com dados meteorológicos para treinar redes neurais profundas em milhares de bacias não-monitoradas.

O dataset **GloFAS-ERA5** fornece séries temporais diárias em resolução espacial de $0,1°$ (~10 km) cobrindo o período de 1979 até o presente.

### 3.3 Fluxo de Dados GloFAS

```
ECMWF ERA5 (Reanálise Atmosférica)
         │
         ▼
Modelo HTESSEL (Balanço de Água na Superfície)
         │
         ▼
Modelo LISFLOOD (Roteamento Hidráulico em Grade de 0.1°)
         │
         ▼
Série Temporal GloFAS-ERA5 (Target do Treinamento)
         │
         ▼
Modelo Local de Machine Learning
(Treinado com Dados de Superfície da ANA e INMET)
```

### 3.4 Modelo Emulador (Surrogate Model)

Ao utilizar os dados do GloFAS como variável de saída, o modelo de aprendizado de máquina desenvolvido **não deve ser interpretado** como um estimador direto da vazão fluviométrica real do rio, mas sim como um **Modelo Emulador de Alta Eficiência (Surrogate Model)**.

A proposta científica consiste em treinar o algoritmo para aprender a resposta física do modelo global GloFAS, porém alimentando-o com dados meteorológicos de superfície observados localmente (estação ANA 1943006 e INMET BH 83587), refinando assim a capacidade de resposta a eventos pluviométricos locais.

### 3.5 Limitações do GloFAS-ERA5

As limitações devem ser **explicitamente relatadas** no TCC e no artigo acadêmico:

| Limitação | Descrição |
|-----------|-----------|
| **Suavização de Picos de Cheia** | Devido à resolução espacial de $0,1°$, o GloFAS tende a atenuações na magnitude dos picos de vazão gerados por tempestades convectivas de pequena escala espacial |
| **Vieses Sistemáticos Regionais** | Em bacias tropicais brasileiras de médio porte, o modelo LISFLOOD sem calibração local pode apresentar viés volumétrico ($PBIAS$) e pequenos desfasamentos temporais no tempo de pico |
| **Erros no Roteamento em Calhas Urbanas** | O produto de reanálise não contempla modificações antropogênicas locais na calha do rio, como canalizações urbanas ou diques no município de Sabará |

---

## 4. Engenharia de Features e Representação de Processos Hidrológicos Tropicais

Em modelos chuva-vazão puros, a engenharia de atributos (feature engineering) desempenha o papel de fornecer ao algoritmo os **estados de umidade da bacia** e as **taxas de evapotranspiração** que determinam se uma tempestade resultará em escoamento superficial direto ou em infiltração.

### 4.1 Conjunto de Atributos Recomendados

| Categoria | Variável/Feature | Formulação/Fonte | Significado Hidrológico |
|-----------|------------------|------------------|-------------------------|
| **Chuva Defasada** | $P_t, P_{t-1}, \dots, P_{t-7}$ | Medição diária ANA | Captura a resposta rápida e a forma do hidrograma |
| **Acumulados** | $P_{3d}, P_{7d}, P_{14d}, P_{30d}, P_{60d}$ | Soma móvel de precipitação | Simula a retenção em reservatórios de solo e aquíferos |
| **Saturação** | Índice API | $API_t = \sum P_{t-i} \cdot \gamma^i$ ($\gamma=0,90$) | Proxy do decaimento exponencial da umidade do solo |
| **Evapotranspiração** | ETP Hargreaves-Samani | $0,0023 \cdot R_a \cdot (T_{med}+17,8) \cdot \sqrt{T_{max}-T_{min}}$ | Quantifica a demanda evaporativa da atmosfera |
| **Atmosfera** | Déficit de Pressão de Vapor (VPD) | Calculado a partir de $T_{med}$ e $RH$ (INMET) | Reflete a taxa de secagem do solo entre eventos de chuva |
| **Sazonalidade** | Componentes Cíclicas | $\sin(2\pi \cdot DOY/365,25)$, $\cos(...)$ | Informa o período do ano (estação seca vs. chuvosa) |
| **Sensoriamento** | NDVI/EVI Móvel | MODIS/Sentinel-2 | Captura a variabilidade da cobertura vegetal e transpiração |

### 4.2 Evapotranspiração de Hargreaves-Samani

A inclusão da **Evapotranspiração Potencial (PET)** via equação de Hargreaves-Samani é especialmente recomendada quando estão disponíveis apenas dados de temperatura (mínima, máxima e média), dispensando dados de radiação solar direta.

### 4.3 Variáveis de Sazonalidade

A inclusão das variáveis trigonométricas do dia do ano ($DOY$) permite que o algoritmo diferencie o impacto de:
- Uma chuva de 50 mm em **novembro** (início da estação chuvosa, solo seco)
- Uma chuva de mesma magnitude em **janeiro** (solo já saturado pelos acumulados de dezembro)

---

## 5. Arquiteturas de Aprendizado de Máquina: Modelos Tabulares vs. Sequenciais

A escolha do algoritmo ideal para previsão de vazão $D+1$ deve considerar:
- Capacidade de lidar com séries temporais
- Não-linearidades intensas
- Preservação do estado do sistema

### 5.1 Evolução das Arquiteturas

```
                        EVOLUÇÃO DAS ARQUITETURAS
                                   │
   ┌───────────────────────────────┼───────────────────────────────┐
   │                               │                               │
   ▼                               ▼                               ▼
Regressão Ridge/Lasso    Tree Ensembles (RF/XGBoost)    Deep Learning (LSTM/GRU)
- Mínima complexidade    - Excelente para tabulares     - Padrão-ouro em hidrologia
- Linearidade estrita    - Requer featurização manual   - Memória de longo/curto prazo
- Atua como baseline     - Falha na extrapolação        - Preserva estados de umidade
```

### 5.2 Regressão Ridge e Modelos Lineares Regularizados

Modelos lineares servem como **referência baseline**. Embora apresentem alta interpretabilidade e baixo risco de overfitting, são **incapazes de capturar os limiares físicos não-lineares**, como a transição súbita do escoamento quando o solo atinge a capacidade de campo.

### 5.3 Ensembles de Árvores de Decisão (Random Forest e XGBoost)

Algoritmos de Gradient Boosting (XGBoost, LightGBM) e Random Forest exibem excelente desempenho quando alimentados com uma matriz de atributos bem estruturada contendo:
- Lags defasados ($P_{t-1} \dots P_{t-k}$)
- Médias móveis

**Limitação Matemática Intrínseca**: Incapacidade de extrapolar valores fora do intervalo observado no conjunto de treinamento.

Durante cheias históricas sem precedentes (como as ocorridas em Minas Gerais em 2020 e 2022), esses modelos tendem a **subestimar severamente os picos de vazão**, truncando a previsão no valor máximo visto na fase de treino.

### 5.4 Redes Neurais Recorrentes e LSTM

A arquitetura **LSTM** tornou-se o **padrão-ouro** na literatura hidrológica internacional.

**Características**:
- Células de memória interna
- Mecanismos de portões (gates)
- Mantém estado de memória contínuo que simula o armazenamento de água no solo e aquíferos

As LSTMs superam modelos tabulares e até modelos hidrológicos conceituais tradicionais em testes regionais e de bacias não-monitoradas (demonstrado nos conjuntos de dados CAMELS e CARAVAN).

---

## 6. Seleção e Interpretação de Métricas Hidrológicas Padrão

A avaliação de modelos hidrológicos **não deve basear-se** em métricas estatísticas genéricas ($RMSE$, $R^2$), pois estas:
- Não capturam diferentes componentes do hidrograma
- São desproporcionalmente influenciadas por vazões extremas

### 6.1 Métricas Hidrológicas Específicas

| Métrica | Formulação | Componentes Avaliados | Interpretação |
|---------|------------|----------------------|---------------|
| **KGE** | $1 - \sqrt{(r-1)^2 + (\alpha-1)^2 + (\beta-1)^2}$ | Correlação ($r$), Variabilidade ($\alpha$), Viés ($\beta$) | Avaliação integrada da forma, amplitude e volume do hidrograma |
| **NSE** | $1 - \frac{\sum (Q_{obs} - Q_{sim})^2}{\sum (Q_{obs} - \bar{Q}_{obs})^2}$ | Erro quadrático relativo à variância histórica | Precisão geral com foco na magnitude dos picos |
| **PBIAS** | $\frac{\sum (Q_{obs} - Q_{sim})}{\sum Q_{obs}} \times 100\%$ | Erro acumulado de volume | Tendência de subestimar ($>0$) ou superestimar ($<0$) |
| **KGE_log** | $KGE(\ln(Q_{obs}), \ln(Q_{sim}))$ | Erro em escala logarítmica | Reduz influência dos picos, avalia vazões de estiagem |
| **MAE** | $\frac{1}{n}\sum |Q_{obs} - Q_{sim}|$ | Erro linear em m³/s | Magnitude média do erro sem penalização quadrática |

### 6.2 Decomposição do KGE

A decomposição do KGE (Gupta et al., 2009; Kling et al., 2012) fornece diagnósticos claros:

| Componente | Diagnóstico |
|------------|-------------|
| Se $r$ for baixo | O modelo falha em capturar o tempo de resposta da chuva e a dinâmica da bacia |
| Se $\alpha = \sigma_{sim}/\sigma_{obs} < 1$ | O modelo está amortecendo excessivamente a variabilidade, subestimando picos de cheia |
| Se $\beta = \mu_{sim}/\mu_{obs} \neq 1$ | Há falha no balanço hídrico total (super ou subestimação de volume) |

---

## 7. Estratégias de Validação Temporal e Mudanças Climáticas

A validação de modelos sobre séries temporais exige cuidados rigorosos para:
- Evitar vazamento de dados (data leakage)
- Garantir avaliação da capacidade de lidar com variações climáticas prolongadas

### 7.1 Divisão Temporal (Holdout Chronological Split)

A divisão configurada no projeto é **conceitualmente correta**:
- **Treinamento**: 1997-2016
- **Validação**: 2017-2021
- **Teste**: 2022-2026

Respeita a ordenação cronológica dos eventos, prevenindo contaminações do futuro no passado.

### 7.2 Validação Cruzada com Janela Expansiva (TimeSeriesSplit)

Para maior robustez estatística em séries longas (~29 anos), recomenda-se complementar com validação cruzada por janela expansiva:

| Bloco | Treino | Validação |
|-------|--------|-----------|
| 1 | 1997–2010 | 2011–2014 |
| 2 | 1997–2014 | 2015–2018 |
| 3 | 1997–2018 | 2019–2022 |
| 4 | 1997–2022 | 2023–2026 (Teste Final) |

### 7.3 Desafio da Não-Estacionariedade Climática

O período de teste final (2022–2026) inclui eventos pluviométricos e de inundação históricos na bacia do Rio das Velhas e RMBH, como a **grande cheia de janeiro de 2022**.

A ocorrência desses eventos representa um **teste severo de resiliência fora da distribuição (Out-of-Distribution - OOD)**.

**Recomendações**:
1. Aplicar **normalização robusta** aos atributos (RobustScaler baseado no intervalo interquartil)
2. Incluir **atributos de longo prazo** (acumulados de 30d e 60d) para fornecer escala prévia da umidade regional

---

## 8. Previsão Multietapa (Multi-Step Ahead) e Integração Numérica

### 8.1 Necessidade Operacional

Embora a previsão $D+1$ seja o ponto de partida metodológico, a operação real de um sistema de alerta para Sabará necessita de **horizontes estendidos**: $D+1$, $D+2$ e $D+3$.

Esse tempo antecedente é necessário para que a Defesa Civil municipal possa:
- Emitir avisos populacionais
- Organizar plano de evacuação nas áreas de risco

### 8.2 Estratégias de Previsão Multietapa

#### Estratégia Direta (Modelos Tabulares)

```
ESTRATÉGIA DIRETA (XGBoost / Random Forest):
├── Modelo 1: Inputs(t) ──────► Previsão Q(t+1)
├── Modelo 2: Inputs(t) ──────► Previsão Q(t+2)
└── Modelo 3: Inputs(t) ──────► Previsão Q(t+3)
```

**Recomendada para modelos de árvores de decisão**. Consiste em treinar $H$ modelos independentes, onde cada modelo $f_h$ é otimizado exclusivamente para prever a vazão no horizonte $t+h$:

$$\hat{Q}_{t+h} = f_h(P_t, P_{t-1}, \dots, MET_t)$$

Evita a propagação e amplificação de erros da estratégia recursiva.

#### Estratégia Multi-Output (Redes Neurais)

```
ESTRATÉGIA MULTI-OUTPUT (LSTM):
└── Modelo Único: Inputs(t) ──────► Vetor [Q(t+1), Q(t+2), Q(t+3)]
```

Nativa de redes neurais profundas e LSTMs. Mantém a **coerência temporal** entre as previsões dos dias subsequentes, reduzindo o custo computacional.

### 8.3 Integração com Previsões Meteorológicas Numéricas (NWP)

Para horizontes $D+2$ e $D+3$, a acurácia depende do conhecimento da chuva que ocorrerá nesses dias.

**Implementação operacional**: Alimentar o modelo com Previsão Numérica do Tempo (NWP) de modelos atmosféricos operacionais (GFS/NOAA ou INMET/CPTEC).

**No âmbito do TCC**: A validação de $D+2$ e $D+3$ pode ser realizada utilizando a **chuva real observada** (Perfect Forecast Experiment), explicitando na metodologia que essa premissa simula o **limite superior de desempenho** do sistema.

---

## 9. Definição de Limiares para Sistemas de Alerta Operacional

A saída de um modelo de regressão chuva-vazão é uma série contínua de vazões estimadas ($\hat{Q}_t$ em m³/s). Para transformar em ferramenta operacional, é necessário mapear a variável contínua em **níveis discretos de alerta**.

### 9.1 Abordagem Estatística por Quantis

Utiliza a curva de permanência da série histórica do GloFAS:

| Nível | Critério | Cor |
|-------|----------|-----|
| **Atenção** | $Q_{pred} \ge Q_{90}$ (superada em 10% do tempo) | 🟡 Amarelo |
| **Alerta** | $Q_{pred} \ge Q_{95}$ (superada em 5% do tempo) | 🟠 Laranja |
| **Emergência** | $Q_{pred} \ge Q_{99}$ (eventos raros de cheia) | 🔴 Vermelho |

### 9.2 Abordagem Hidráulica por Cotas (SACE/CPRM)

Caso haja dados telemétricos históricos de nível d'água, converte-se a vazão prevista em cota de nível ($H$) por meio de uma **curva-chave calibrada** ($Q \times H$). Os limiares são definidos a partir das cotas físicas reais de extravasamento.

### 9.3 Significado Operacional dos Estágios em Sabará-MG

| Estágio | Critério | Significado Operacional |
|---------|----------|------------------------|
| **Atenção** | $Q_{pred} \ge Q_{90}$ | Elevação do nível do rio; monitoramento contínuo pelas equipes locais |
| **Alerta** | $Q_{pred} \ge Q_{95}$ | Risco moderado de alagamentos pontuais nas margens do Rio Sabará e Velhas |
| **Emergência** | $Q_{pred} \ge Q_{99}$ | Transbordamento iminente; evacuação preventiva de áreas vulneráveis |

### 9.4 Métricas Categóricas para Avaliação do Sistema de Alerta

A eficiência da conversão de vazão contínua em alertas discretos deve ser avaliada transformando o problema em **classificação binária** (Ocorrência ou Não-Ocorrência de Evento Extremo).

**Métricas recomendadas**:

$$POD = \frac{\text{Acertos de Cheia}}{\text{Acertos de Cheia} + \text{Omissões}}$$

$$FAR = \frac{\text{Falsos Alarmes}}{\text{Acertos de Cheia} + \text{Falsos Alarmes}}$$

$$CSI = \frac{\text{Acertos de Cheia}}{\text{Acertos de Cheia} + \text{Falsos Alarmes} + \text{Omissões}}$$

A apresentação das **curvas ROC-AUC** e da **Matriz de Confusão** para o quantil de emergência ($Q_{99}$) demonstra a aplicabilidade direta do trabalho para gestão de riscos.

---

## 10. Contribuições Científicas, Lacunas na Literatura e Estruturação do Trabalho

Para garantir aprovação do TCC e maximizar chances de aceitação em congressos (ex: Simpósio Brasileiro de Recursos Hídricos - ABRHidro), o trabalho precisa explicitar suas **contribuições metodológicas** e o **preenchimento de lacunas**.

### 10.1 Lacunas da Literatura Preenchidas

| Lacuna | Contribuição |
|--------|-------------|
| **Mitigação do Vazio Telemétrico** | Framework preditivo puro para Sabará, operando sem estações fluviométricas operacionais |
| **Transferência de Aprendizado via GloFAS** | Demonstração de como produtos globais de reanálise podem ser desacoplados e ajustados localmente por modelos de ML |
| **Análise de Extrapolação de Extremos** | Avaliação sistemática de como XGBoost/RF e LSTM lidam com eventos fora da distribuição (como 2022 em MG) |

### 10.2 Estrutura Recomendada para o TCC

1. **Introdução e Justificativa**
   - Vulnerabilidade histórica de Sabará a enchentes
   - Importância da modelagem chuva-vazão pura em bacias não-monitoradas (PUB)

2. **Referencial Teórico**
   - Evolução da modelagem hidrológica
   - Fundamentos do GloFAS-ERA5
   - Transição de modelos conceituais para deep learning (LSTM) e gradient boosting

3. **Engenharia de Features e Modelagem**
   - Construção dos acumulados de chuva, índice API, evapotranspiração de Hargreaves
   - Variáveis de sazonalidade
   - Formulação das baselines ($KGE = -0,41$)

4. **Resultados e Discussão**
   - Tabelas comparativas usando $KGE$, $NSE$, $PBIAS$, $KGE_{log}$, $MAE$
   - Gráficos dos hidrogramas simulados vs. observados (período 2022–2026)

5. **Explicabilidade do Modelo (XAI)**
   - Aplicar técnica **SHAP** (SHapley Additive exPlanations)
   - Quantificar contribuição de cada variável na previsão de picos
   - Comprovar coerência física do algoritmo

6. **Módulo de Alerta de Cheias**
   - Matriz de confusão e métricas categóricas ($POD$, $FAR$, $CSI$)
   - Limiares baseados nos quantis teóricos ($Q_{90}$, $Q_{95}$, $Q_{99}$)

---

## 11. Síntese e Diretrizes Operacionais

A condução da pesquisa sob as diretrizes consolidadas neste relatório garante um arcabouço metodológico robusto e alinhado aos padrões da hidrologia computacional moderna.

### 11.1 Principais Diretrizes

1. **Remoção da dependência da vazão histórica antecedente** converte o modelo em solução aplicável para regiões com escassez de dados telemétricos

2. **Transição de modelos tabulares para LSTM**, combinada à engenharia de atributos hidrológicos (API, evapotranspiração de Hargreaves, variáveis de sazonalidade), permite capturar a dinâmica do solo e variabilidade climática extrema

3. **Validação por métricas específicas** ($KGE$) somada à conversão em **limiares operacionais** avaliados por métricas categóricas ($CSI$, $POD$, $FAR$) consolida o trabalho como contribuição científica de alto impacto aplicado

### 11.2 Impacto Final

O framework proposto contribui diretamente para o **gerenciamento de riscos de desastres naturais em Minas Gerais**, especificamente para o município de Sabará e a bacia do Rio das Velhas.

---

## Referências Bibliográficas Citadas

- Gupta, H. V., Kling, H., Yilmaz, K. K., & Martinez, G. F. (2009). Decomposition of the mean squared error and NSE performance criteria: Implications for improving hydrological modelling.
- Kling, H., Fuchs, M., & Paulin, M. (2012). Runoff conditions in the upper Danube basin under an ensemble of climate change scenarios.
- Knoben, W. J. M., Freer, J. E., & Woods, R. A. (2019). Technical note: Inherent benchmark or not? Comparing Nash–Sutcliffe and Kling–Gupta efficiency scores.
- Kratzert, F., et al. (2019). Towards learning universal, regional, and local hydrological behaviors via machine learning applied to large-sample datasets.
- Nearing, G. S., et al. (2021). What Role Does Hydrological Science Play in the Age of Machine Learning?

---

*Documento gerado a partir de pesquisa profunda sobre modelagem chuva-vazão com Machine Learning para aplicação em sistemas de alerta de inundações.*
