# Próximos Passos - Pós KGE 0.679

Agora que já alcançamos KGE de 0.679 com o XGBoost, o ganho de desempenho via feature engineering tabular tende a estabilizar. Para enriquecer o TCC e garantir aprovação no congresso, os próximos passos ideais são:

---

## 1. Explicabilidade com SHAP (SHapley Additive exPlanations)

Gerar um gráfico de **SHAP Summary Plot** para o XGBoost.

O SHAP mostra não apenas qual variável é importante, mas **como** cada variável afeta a vazão. Por exemplo: "quando o `api_30d` é alto e o `vpd` é baixo, a previsão de vazão aumenta em X m³/s".

**Benefício:** Comprova para a banca que o aprendizado de máquina não é uma "caixa preta", mas sim um modelo coerente com a física hidrológica.

```python
import shap

explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(X_test)
shap.summary_plot(shap_values, X_test, feature_names=FEATURE_COLS)
```

---

## 2. Análise dos Hidrogramas nos Picos de 2022

Plotar o gráfico de linha da **vazão real do GloFAS** versus a **vazão prevista pelo XGBoost** para o período crítico de janeiro de 2022.

**Objetivo:** Discutir como o modelo se comportou no pico da cheia em Sabará.

```python
import matplotlib.pyplot as plt

# Filtrar período crítico
jan_2022 = test_df[test_df['data'].between('2022-01-01', '2022-01-31')]

plt.figure(figsize=(12, 5))
plt.plot(jan_2022['data'], jan_2022['target'], label='GloFAS (Real)', linewidth=2)
plt.plot(jan_2022['data'], y_pred_test[:len(jan_2022)], label='XGBoost (Previsto)', linewidth=2, linestyle='--')
plt.xlabel('Data')
plt.ylabel('Vazão (m³/s)')
plt.title('Hidrograma - Pico de Cheia Janeiro 2022')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('hidrograma_jan_2022.png', dpi=300)
```

---

## Status

- [ ] Implementar SHAP Summary Plot
- [ ] Gerar hidrograma janeiro 2022
- [ ] Incluir figuras no TCC
