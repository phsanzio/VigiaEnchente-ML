# Diário da Sessão - 21 de Agosto de 2026

## Resumo do Dia
Otimização completa do pipeline ML chuva-vazão para TCC sobre previsão de enchentes em Sabará-MG.

---

## 1. Mudança para Modelo Chuva-Vazão PURO

**Decisão:** Remover vazão das features (eram `vazao_ontem`, `vazao_anteontem`)

**Motivo:** 
- Modelo chuva-vazão puro não depende de dados de vazão em tempo real
- Aplicável a bacias não-monitoradas (PUB - Prediction in Ungauged Basins)
- A vazão é o TARGET (GloFAS), não deve ser feature

**Resultado:** Modelo passou a usar apenas precipitação e meteorologia como entrada.

---

## 2. Nova Baseline: Média Climatológica

**Antes:** Baseline de persistência (y_pred = y_ontem) - usava vazão!

**Depois:** Média climatológica (y_pred = média do treino)

**Justificativa:** Conforme Knoben et al. (2019), a baseline climatológica tem KGE ≈ -0.41, sendo o padrão para comparação em hidrologia.

---

## 3. Novas Features Físico-Hidrológicas

### Features Adicionadas (com justificativa física):

| Feature | Justificativa |
|---------|---------------|
| `sin_doy`, `cos_doy` | Sazonalidade cíclica (período chuvoso vs seco) |
| `vpd` | Déficit de Pressão de Vapor (proxy de evaporação) |
| `chuva_3d_atras`, `chuva_4d_atras` | Tempo de concentração da bacia (2-4 dias) |
| `chuva_60d` | Saturação do solo profundo |
| `chuva_90d` | Memória do aquífero / escoamento de base |

### Features Testadas e Removidas (importância <1%):
- `temp_amplitude` (temp_max - temp_min)
- `chuva_max_3d` (pico de intensidade)
- `delta_chuva` (variação dia a dia)

### Estudo de Ablação:

| Etapa | Features | XGB Test KGE | Ganho |
|-------|----------|--------------|-------|
| 1. Original | 13 | 0.583 | Baseline |
| 2. + Física | 19 | 0.679 | +16.5% |
| 3. + Memória | 20 | 0.693 | +18.9% |

---

## 4. Hyperparameter Tuning com TimeSeriesSplit

**Método:** GridSearchCV com TimeSeriesSplit (5 folds) no conjunto de treino (1997-2016)

**Divisão dos Folds:**
```
Fold 1: Treina [1997-2000] → Valida [2000-2003]
Fold 2: Treina [1997-2003] → Valida [2003-2007]
Fold 3: Treina [1997-2007] → Valida [2007-2010]
Fold 4: Treina [1997-2010] → Valida [2010-2013]
Fold 5: Treina [1997-2013] → Valida [2013-2016]
```

**Justificativa:** 5 folds garante ~3.3 anos por janela de validação, cobrindo ciclos climáticos completos.

### Parâmetros Encontrados:

| Modelo | Parâmetros | KGE (CV) |
|--------|------------|----------|
| RF | max_depth=10, min_samples_split=2, n_estimators=200 | 0.626 |
| XGB | learning_rate=0.2, max_depth=5, n_estimators=100 | 0.650 |

---

## 5. Resultados Finais (com tuning)

### Validação (2017-2021):

| Modelo | KGE | R² |
|--------|-----|-----|
| RF | 0.700 | 0.630 |
| **XGB** | **0.723** | 0.616 |

### Teste (2022+):

| Modelo | KGE | R² | RMSE |
|--------|-----|-----|------|
| RF | 0.655 | 0.651 | 2.83 |
| **XGB** | **0.703** | 0.663 | 2.78 |

---

## 6. Features Finais (20 atributos)

```python
FEATURE_COLS = [
    'chuva_mm', 'temp_media', 'temp_max', 'temp_min', 'umidade_media',
    'chuva_3d', 'chuva_7d', 'chuva_14d', 'chuva_30d', 'chuva_60d', 'chuva_90d',
    'api_7d', 'api_30d',
    'chuva_ontem', 'chuva_anteontem', 'chuva_3d_atras', 'chuva_4d_atras',
    'sin_doy', 'cos_doy', 'vpd'
]
```

---

## 7. Estrutura de Arquivos

```
vigiaenchente-ml/src/
├── main.py                      # Orquestra pipeline
├── processing/
│   ├── database_processor.py    # Carrega dados brutos
│   └── feature_engineering.py   # Cria 20 features
├── training/
│   ├── models_training.py       # RF, XGB, Ridge (params tunados)
│   └── hyperparameter_tuning.py # TimeSeriesSplit 5 folds
└── metrics/
    └── metrics.py               # KGE, R², RMSE, MAE
```

---

## 8. Próximos Passos (A FAZER)

### Prioridade Alta:
- [ ] SHAP Summary Plot para explicabilidade
- [ ] Hidrograma janeiro 2022 (real vs previsto)
- [ ] Scatter plot real vs previsto

### Prioridade Média:
- [ ] Métricas de alerta (POD, FAR, CSI) com quantis Q90, Q95, Q99
- [ ] Limpar código e adicionar docstrings

---

## 9. Documentos Criados Hoje

1. `docs/proximos-passos.md` - Tarefas pendentes (SHAP, hidrogramas)
2. `docs/estrutura-tcc-completa.md` - Estrutura completa do TCC
3. `docs/plano-artigo-congresso.md` - Plano detalhado pro artigo
4. `docs/diario-sessao-2024-08-21.md` - Este documento

---

## 10. Decisões Importantes para o TCC

1. **Modelo chuva-vazão PURO** - não usa vazão como feature, só como target
2. **Baseline climatológica** - padrão da literatura (KGE ≈ -0.41)
3. **TimeSeriesSplit 5 folds** - validação cruzada temporal no treino
4. **Features com justificativa física** - cada uma tem embasamento hidrológico
5. **XGB é o melhor modelo** - KGE 0.703 no teste

---

## Resumo Executivo

> Desenvolvemos um modelo chuva-vazão puro (sem usar vazão como feature) usando XGBoost que alcançou **KGE = 0.703** no conjunto de teste (2022+). A engenharia de features baseada em física hidrológica (sazonalidade, VPD, acumulados de longo prazo) foi responsável por um ganho de **+18.9%** sobre o modelo baseline. O tuning com TimeSeriesSplit (5 folds) encontrou parâmetros que melhoraram ainda mais o resultado final.
