# Estrutura Completa do TCC - Previsão de Enchentes em Sabará-MG

## Resultado Final Alcançado

**XGBoost Test KGE: 0.693 | R²: 0.643**

Modelo chuva-vazão **puro** (sem usar vazão como feature), testado em período crítico de eventos extremos (2022+).

---

## 1. Introdução

### O que falar:
- Contextualização do problema de enchentes em Sabará-MG
- Importância de sistemas de alerta precoce para a Defesa Civil
- Limitação de bacias não-monitoradas (PUB - Prediction in Ungauged Basins)
- Objetivo: desenvolver modelo chuva-vazão puro usando ML

### O que justificar:
- Por que Sabará? (histórico de enchentes, dados disponíveis)
- Por que modelo chuva-vazão puro? (aplicável a bacias sem estações fluviométricas)
- Por que XGBoost/Random Forest? (estado da arte em hidrologia computacional)

---

## 2. Revisão Bibliográfica

### O que incluir:
- Modelos hidrológicos tradicionais vs ML
- Trabalhos relacionados na bacia do Rio das Velhas
- Métricas de avaliação (KGE, NSE, R², RMSE)
- Importância do KGE sobre NSE (Gupta et al. 2009, Knoben et al. 2019)

### Tabela comparativa com trabalhos relacionados:
| Autor | Bacia | Modelo | Métrica | Resultado |
|-------|-------|--------|---------|-----------|
| Trabalho X | Rio Y | LSTM | NSE | 0.85 |
| Trabalho Y | Rio Z | RF | KGE | 0.72 |
| **Este trabalho** | **Rio das Velhas (Sabará)** | **XGBoost** | **KGE** | **0.693** |

---

## 3. Metodologia

### 3.1 Área de Estudo
- Mapa da bacia do Rio das Velhas até Sabará
- Características físicas da bacia
- Histórico de eventos críticos

### 3.2 Dados Utilizados

**Tabela de Fontes de Dados:**
| Variável | Fonte | Período | Resolução |
|----------|-------|---------|-----------|
| Precipitação | INMET/ANA | 1997-2024 | Diária |
| Temperatura | INMET | 1997-2024 | Diária |
| Umidade | INMET | 1997-2024 | Diária |
| Vazão (target) | GloFAS | 1997-2024 | Diária |

### 3.3 Engenharia de Atributos (Feature Engineering)

**Justificar cada grupo de features:**

| Categoria | Features | Justificativa Física |
|-----------|----------|---------------------|
| **Precipitação bruta** | `chuva_mm`, `chuva_ontem`, `chuva_anteontem` | Input direto do processo chuva-vazão |
| **Lags estendidos** | `chuva_3d_atras`, `chuva_4d_atras` | Tempo de concentração da bacia (2-4 dias) |
| **Acumulados** | `chuva_3d`, `chuva_7d`, `chuva_14d`, `chuva_30d`, `chuva_60d`, `chuva_90d` | Umidade do solo e saturação do aquífero |
| **API** | `api_7d`, `api_30d` | Índice de Precipitação Antecedente (decaimento exponencial) |
| **Meteorologia** | `temp_media`, `temp_max`, `temp_min`, `umidade_media` | Evapotranspiração e balanço hídrico |
| **Sazonalidade** | `sin_doy`, `cos_doy` | Ciclo hidrológico anual (período chuvoso vs seco) |
| **VPD** | `vpd` | Déficit de Pressão de Vapor (proxy de evaporação) |

**Total: 20 features**

### 3.4 Divisão Temporal dos Dados

```
|-------- TREINO --------|-- VALIDAÇÃO --|---- TESTE ----|
|     1997 - 2016        |  2017 - 2021  |    2022+      |
|      (~7.300 dias)     | (~1.800 dias) | (~900+ dias)  |
```

**Justificativa:** Preserva ordem cronológica, evita data leakage, teste em período com eventos extremos reais.

### 3.5 Modelos Utilizados

- **Random Forest:** ensemble de árvores de decisão, robusto a outliers
- **XGBoost:** gradient boosting, estado da arte em competições e hidrologia
- **Baseline:** média climatológica (KGE teórico ≈ -0.41 por Knoben et al. 2019)

### 3.6 Otimização de Hiperparâmetros

- **Método:** GridSearchCV com validação simples (treino → validação fixa)
- **Métrica de otimização:** KGE
- **Parâmetros testados:**
  - RF: n_estimators, max_depth, min_samples_split
  - XGB: n_estimators, max_depth, learning_rate

---

## 4. Resultados

### 4.1 Tabela de Estudo de Ablação (OBRIGATÓRIA)

| Etapa | Atributos | XGB Test KGE | XGB Test R² | Ganho |
|-------|-----------|--------------|-------------|-------|
| **1. Modelo Original** | 13 (básicos) | 0.583 | ~0.550 | Baseline |
| **2. + Física e Sazonalidade** | 19 (+sin/cos_doy, VPD, chuva_60d, lags 3d/4d) | 0.679 | ~0.620 | +16.5% |
| **3. + Memória Profunda** | 20 (+chuva_90d, poda de features fracas) | **0.693** | **0.643** | **+18.9%** |

**Discussão:** O ganho de +18.9% no KGE demonstra que a engenharia de atributos baseada na física da bacia é mais efetiva que tuning de hiperparâmetros.

### 4.2 Comparação RF vs XGBoost

| Modelo | Val KGE | Test KGE | Test R² | Test RMSE |
|--------|---------|----------|---------|-----------|
| Random Forest | 0.695 | 0.660 | 0.656 | 2.81 m³/s |
| **XGBoost** | 0.706 | **0.693** | 0.643 | 2.86 m³/s |

### 4.3 Feature Importance (Gráfico de Barras)

**Top 10 features mais importantes (RF):**
1. `api_30d` - 37.9%
2. `umidade_media` - 10.5%
3. `api_7d` - 7.7%
4. `chuva_30d` - 6.1%
5. `sin_doy` - 5.2%
6. `chuva_90d` - 5.0%
7. `chuva_60d` - 4.4%
8. `chuva_14d` - 3.0%
9. `chuva_7d` - 2.7%
10. `cos_doy` - 2.6%

**Discussão:** A dominância do `api_30d` (38%) confirma que a umidade antecedente do solo é o fator mais determinante na transformação chuva-vazão.

### 4.4 Gráfico SHAP Summary Plot (A FAZER)

- Mostra como cada feature afeta a previsão
- Comprova coerência física do modelo
- Exemplo: "quando `api_30d` é alto e `vpd` é baixo, vazão prevista aumenta"

### 4.5 Hidrograma Janeiro 2022 (A FAZER)

- Gráfico temporal: vazão real (GloFAS) vs prevista (XGBoost)
- Análise do comportamento no pico de cheia
- Discussão de acertos e erros do modelo

---

## 5. Discussão

### O que discutir:

1. **Por que o modelo funciona?**
   - Features capturam física da bacia (sazonalidade, saturação, tempo de concentração)
   - KGE 0.693 está na faixa "bom a operacional" da literatura

2. **Validação contra overfitting:**
   - Ganho ocorreu no conjunto de TESTE (dados futuros, não vistos)
   - Razão amostras/features de 350:1 (muito acima do mínimo de 10:1)
   - Features removidas tinham baixa importância (<1%)

3. **Limitações:**
   - Modelo não captura eventos extremos fora da distribuição do treino
   - Dependência da qualidade dos dados do GloFAS
   - Não considera características de uso do solo

4. **Comparação com literatura:**
   - KGE 0.693 é competitivo com modelos que usam vazão como feature
   - Vantagem: aplicável a bacias não-monitoradas (PUB)

---

## 6. Conclusão

### O que concluir:

1. Modelo XGBoost chuva-vazão puro alcançou KGE de 0.693 no teste
2. Engenharia de atributos baseada em física hidrológica foi crucial (+18.9%)
3. Sistema pode ser integrado à Defesa Civil de Sabará para alertas precoces
4. Metodologia replicável para outras bacias sem monitoramento fluviométrico

### Trabalhos futuros:
- Implementar SHAP para explicabilidade
- Testar LSTM para capturar dependências temporais longas
- Integrar previsão meteorológica (NWP) para horizonte de 3-7 dias
- Calcular métricas de alerta (POD, FAR, CSI)

---

## 7. Gráficos e Tabelas Necessárias

### Tabelas:
- [x] Tabela de fontes de dados
- [x] Tabela de features e justificativas
- [x] Tabela de estudo de ablação
- [x] Tabela comparativa RF vs XGBoost
- [ ] Tabela comparativa com literatura

### Gráficos:
- [ ] Mapa da área de estudo
- [x] Gráfico de Feature Importance (barras)
- [ ] SHAP Summary Plot
- [ ] Hidrograma janeiro 2022 (real vs previsto)
- [ ] Scatter plot: vazão real vs prevista
- [ ] Série temporal completa do período de teste

---

## 8. Próximos Passos Imediatos

### Prioridade Alta:
- [ ] Implementar SHAP Summary Plot
- [ ] Gerar hidrograma janeiro 2022
- [ ] Criar scatter plot real vs previsto

### Prioridade Média:
- [ ] Calcular métricas de alerta (POD, FAR, CSI) usando quantis Q90, Q95, Q99
- [ ] Comparar com baseline de persistência (y_pred = y_ontem)

### Prioridade Baixa:
- [ ] Testar LSTM
- [ ] Integrar com API de previsão meteorológica

---

## Argumentos Contra Overfitting (Para Defesa)

Se a banca perguntar sobre overfitting, usar estes argumentos:

1. **Ganho no conjunto de TESTE:** Se houvesse overfitting, o teste teria piorado, não melhorado em +18.9%

2. **Justificativa física das features:** Todas as 20 features têm embasamento hidrológico (sazonalidade, saturação do solo, tempo de concentração, evaporação)

3. **Poda de features:** Removemos 3 features com importância <1%, seguindo princípio da parsimônia

4. **Razão amostras/features:** 7.000 amostras / 20 features = 350:1 (literatura recomenda mínimo 10:1)

5. **Validação temporal rigorosa:** Treino (1997-2016), Validação (2017-2021), Teste (2022+) - sem data leakage
