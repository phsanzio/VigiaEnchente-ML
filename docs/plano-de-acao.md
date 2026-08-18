# Plano de Ação - Implementação do Modelo ML (POSI II)

> **Última atualização:** 18/08/2026  
> **Status:** MVP apresentado em IA, aguardando definição final do target para TCC

## Visão Geral

- 4 modelos: Logistic Regression (baseline), Random Forest, XGBoost, SVM
- 4 janelas temporais: 3, 7, 14, 30 dias
- 1 fonte de vazão principal: GloFAS (modelo precipitação-vazão como experimento secundário)
- Baseline operacional: Regra de Chuva 100mm/72h (derivada do PLANCON)
- Período: 1997-2025 (28 anos, cobertura conjunta de todas as fontes)
- Horizonte de previsão: D+1 (24 horas)

---

## Decisões Metodológicas Consolidadas

### Dados descartados do modelo principal
- **Vazão real ANA (1939-1965):** 60 anos de defasagem, não representa a bacia atual (urbanização, mudanças no uso do solo, modificações no curso do rio)
- Permanece como possibilidade de experimento secundário

### Fontes de dados utilizadas (1997-2025)
1. **Precipitação medida (ANA/HidroWeb):** estação 1943006
2. **Descarga simulada (GloFAS):** API Open-Meteo, resolução ~5km
3. **Variáveis meteorológicas (ERA5):** temperatura, umidade, vento via Open-Meteo

### Definição do target
- **PLANCON usa "OU":** precipitação >100mm/72h OU nível >2m
- **TCC usa descarga D+1 apenas:** evita circularidade com baseline de chuva
- **Threshold:** vazão GloFAS D+1 > 7.5 m³/s (mínimo dos eventos fluviais confirmados)
- **Evento não capturado:** nov/2024 (alagamento urbano, drenagem) — GloFAS não reflete

### Eventos confirmados (ground truth)
| Data | Tipo | Capturado GloFAS? |
|------|------|-------------------|
| 12/1997 | Fluvial | ✅ Sim |
| 27/01/2020 | Fluvial | ✅ Sim |
| 09/01/2022 | Fluvial | ✅ Sim |
| 26/10/2023 | Urbano (drenagem) | ⚠️ Parcial |
| 13-14/11/2024 | Urbano | ❌ Não |

---

## Etapa 1: Buscar Survey Recente (Prazo: 25/08/2026)

### O que fazer:
1. Buscar 1-2 revisões/surveys recentes sobre ML para previsão de enchentes
2. Identificar como outros trabalhos definiram a variável-alvo
3. Adicionar ao .bib e à seção de Trabalhos Relacionados

### Resultado esperado:
- Novas referências que fundamentem a definição do target
- Seção 2 atualizada

---

## Etapa 2: Definir Target Final (Prazo: 01/09/2026)

### O que fazer:
1. Validar threshold de vazão GloFAS com orientador
2. Decidir se inclui evento de nov/2024 (não capturado) ou documenta como limitação
3. Formalizar critério no documento de decisões

### Resultado esperado:
- Target bem definido e justificado
- Documento com justificativa técnica

---

## Etapa 3: Gerar Base Final (Prazo: 03/09/2026)

### O que fazer:
1. Carregar chuvas.csv, despivotar de mensal pra diário
2. Priorizar nível 2 (consistido) sobre nível 1 (bruto)
3. Buscar Open-Meteo Historical Weather API (temperatura, umidade, vento)
4. Buscar Open-Meteo Flood API / GloFAS (vazão simulada 1997-2025)
5. Juntar tudo por data num único DataFrame
6. Aplicar target definido na Etapa 2: vazão D+1 > threshold

### Resultado esperado:
- DataFrame com ~10.000 linhas (1997-2025, diário)
- Colunas: data, chuva_mm, vazao_glofas, vazao_amanha, temp_max, temp_min, umidade, vento, target
- Features todas do dia D, target do dia D+1

---

## Etapa 4: Feature Engineering (Prazo: 03/09/2026)

### O que fazer:
1. Calcular acumulados: chuva_3d, chuva_7d, chuva_14d, chuva_30d (dias D-2 a D-N)
2. Calcular lags: chuva_lag1, chuva_lag2, chuva_lag3, vazao_lag1, vazao_lag2
3. Adicionar sazonalidade: mês (1-12), is_wet_season (nov-mar = 1)
4. Normalizar variáveis contínuas (MinMaxScaler)
5. Remover linhas com NaN (primeiros 30 dias terão NaN nos acumulados)

### IMPORTANTE: Todas as features são do dia D, target é do dia D+1
- chuva_3d = chuva dos dias D-2, D-1, D (disponível no dia D)
- vazao_amanha = vazão do dia D+1 (o que queremos prever)
- NÃO usar chuva ou vazão do dia D+1 como feature

### Resultado esperado:
- DataFrame pronto com ~15 colunas de features + 1 coluna target
- Sem NaN, sem vazamento de informação

---

## Etapa 5: Treinamento dos Modelos (Prazo: 17/09/2026)

### O que fazer:
```python
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score

modelos = {
    'LogReg': LogisticRegression(),
    'RF': RandomForestClassifier(n_estimators=100, random_state=42),
    'XGBoost': XGBClassifier(n_estimators=100, random_state=42),
    'SVM': SVC(kernel='rbf')
}

janelas = [3, 7, 14, 30]

resultados = []
for nome_modelo, modelo in modelos.items():
    for janela in janelas:
        # Montar features com a janela específica
        X_train, X_test, y_train, y_test = preparar_dados(janela)
        modelo.fit(X_train, y_train)
        y_pred = modelo.predict(X_test)
        resultados.append({
            'modelo': nome_modelo,
            'janela': janela,
            'f1': f1_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'accuracy': accuracy_score(y_test, y_pred)
        })

df_resultados = pd.DataFrame(resultados)
```

### Baseline operacional (Regra de Chuva)
```python
# Baseline PLANCON: se chuva acumulada 3d (D-2, D-1, D) >= 100mm, prevê risco
y_pred_baseline = (df_test['acumulado_3d'] >= 100).astype(int)
```

### Split temporal
- Treino: 1997-2019 (~8.000 dias)
- Teste: 2020-2025 (~2.000 dias, inclui 4 dos 5 eventos)

### Resultado esperado:
- Tabela com 16 linhas (4 modelos x 4 janelas) + 1 linha baseline
- Métricas: F1, Precision, Recall, Accuracy
- Identificar o vencedor (melhor F1 ou Recall, dado o contexto)

---

## Etapa 6: Ajuste de Hiperparâmetros (Prazo: 17/09/2026)

### O que fazer:
1. Pegar o melhor modelo + janela da Etapa 5
2. Rodar GridSearchCV com parâmetros candidatos
3. Testar técnicas de balanceamento se necessário

```python
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit

# Exemplo pra RF:
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 20, None],
    'min_samples_split': [2, 5, 10],
    'class_weight': ['balanced', None]  # Ajuda no desbalanceamento
}

grid = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid,
    cv=TimeSeriesSplit(n_splits=5),
    scoring='f1'  # ou 'recall' se priorizar detectar eventos
)
grid.fit(X_train, y_train)
print(grid.best_params_)
```

### Resultado esperado:
- Melhor configuração de hiperparâmetros pro modelo vencedor
- F1/Recall final otimizado

---

## Etapa 7: Avaliação Final e Resultados (Prazo: 30/09/2026)

### O que fazer:
1. Feature importance do modelo final
2. Confusion matrix (visualizar FP vs FN)
3. Validar contra os 5 eventos confirmados da Defesa Civil
4. Comparar ML vs baseline Regra de Chuva
5. Gerar gráficos e tabelas pro TCC
6. Redigir seção de Resultados

### Validação contra eventos reais:
```python
eventos_confirmados = ['1997-12-14', '2020-01-24', '2020-01-25', 
                       '2022-01-08', '2022-01-09', '2022-01-10',
                       '2024-11-13', '2024-11-14']

# Quantos o modelo detectou?
acertos = df_test[df_test['data'].isin(eventos_confirmados)]['predicao'].sum()
print(f"Modelo detectou {acertos}/{len(eventos_confirmados)} eventos reais")
```

### Discussão dos tipos de erro:
- **Falso Negativo (FN):** modelo não previu enchente que aconteceu → crítico, pode custar vidas
- **Falso Positivo (FP):** modelo previu enchente que não aconteceu → menos grave, mas afeta credibilidade
- Priorizar Recall para minimizar FN

### Resultado esperado:
- Seção de Resultados completa
- Gráficos prontos pra colar no TCC
- Resposta: "o modelo acertou X dos 5 eventos reais"
- Comparação quantitativa: ML vs baseline

---

## Etapa 8: Revisão Final e Defesa (Prazo: 31/10/2026)

### O que fazer:
1. Revisar texto completo (Conclusão, Abstract, ajustes)
2. Incorporar correções do orientador
3. Preparar slides da apresentação (15-20 min)

### Resultado esperado:
- PDF final do TCC
- Slides prontos
- Defesa em novembro/2026

---

## Cronograma Resumido (POSI II)

| Atividade | Prazo | Status |
|-----------|-------|--------|
| 1. Survey ML/enchentes | 25/08/2026 | ⏳ Pendente |
| 2. Definir target | 01/09/2026 | ⏳ Pendente |
| 3. Base final + features | 03/09/2026 | ⏳ Pendente |
| 4. Treinar modelos | 17/09/2026 | ⏳ Pendente |
| 5. Resultados + texto | 30/09/2026 | ⏳ Pendente |
| 6. Revisão + slides | 31/10/2026 | ⏳ Pendente |
| 7. Defesa | Novembro/2026 | ⏳ Pendente |

---

## Risco Principal

**Desempenho insatisfatório** dos modelos devido ao desbalanceamento extremo (5 eventos em 28 anos de dados).

**Mitigações:**
- `class_weight='balanced'` no treinamento
- SMOTE para oversampling da classe minoritária
- Ajustar threshold de decisão priorizando Recall
- Documentar limitações se resultados não forem ideais
