# Decisão: Modelos e Experimentos

## Modelos candidatos

| Modelo | O que é | Por que testar |
|--------|---------|----------------|
| Regressão Logística | Modelo linear simples | Baseline. Se acerta bem, problema é simples. Se não, justifica modelos mais complexos. |
| Random Forest | Ensemble de árvores votando | Robusto, interpretável, feature importance, nosso favorito. |
| Gradient Boosting (XGBoost) | Árvores que aprendem com erros das anteriores | Geralmente melhor performance. Felipe (Mackenzie) usou e ganhou com ele. |
| SVM | Encontra melhor fronteira entre classes | Ramos (IFG) usou com bons resultados. Diferente dos baseados em árvore, dá diversidade. |

## O que diferencia nosso TCC dos demais (não é a comparação de modelos)

A comparação de modelos é prática padrão. Todo mundo faz. O que diferencia é:

1. **Os dados** - 84 anos oficiais da ANA/Defesa Civil + thresholds do PLANCON
2. **O target** - Definido por autoridade competente (não por notícia do G1)
3. **A colaboração** - Universidade + Defesa Civil (modelo de parceria)
4. **O local** - Sabará / Rio das Velhas (estudo de caso inédito)

## Experimentos originais (o que nenhum dos trabalhos relacionados fez)

### Experimento 1: Comparar fontes de dados

Mesmo modelo (RF por exemplo), mas treinar em cenários diferentes:

| Cenário | Dados usados | Pergunta que responde |
|---------|-------------|----------------------|
| A | Só chuva real (ANA, 84 anos) | Chuva sozinha já prevê? |
| B | Chuva real + Open-Meteo clima (temp, umidade, vento) | Variáveis extras ajudam? |
| C | Chuva real + Open-Meteo clima + vazão GloFAS | Vazão simulada agrega? |

Se B > A: variáveis climáticas melhoram o modelo.
Se C > B: vazão simulada contribui.
Se C = B: vazão GloFAS não ajuda (resolução grosseira demais).

Isso mostra pro TCC o impacto de cada fonte de dados na assertividade.

### Experimento 2: Comparar janelas temporais

Mesmo modelo, mesmos dados, mas variando a "memória" do modelo:

| Janela | Features usadas |
|--------|----------------|
| 3 dias | chuva_3d, vazao_lag1, vazao_lag3 |
| 7 dias | chuva_7d, media_movel_7d |
| 14 dias | chuva_14d, media_movel_14d |
| 30 dias | chuva_30d, media_movel_30d |

Pergunta: qual janela prevê melhor? Enchente depende mais dos últimos 3 dias ou do acumulado do mês?

Isso responde uma pergunta prática pra Defesa Civil: "quantos dias de chuva preciso monitorar?"

### Experimento 3: Target contínuo vs binário

| Abordagem | Target | Modelo | Métricas |
|-----------|--------|--------|----------|
| Regressão | Severidade 0 a 1 | RandomForestRegressor | RMSE, MAE, R² |
| Classificação | Enchente sim/não | RandomForestClassifier | F1, Precision, Recall, Accuracy |

Depois converte a regressão em classificação (threshold 0.5) e compara com a classificação direta.

Pergunta: o modelo que aprende intensidade generaliza melhor que o que só aprende sim/não?

### Experimento 4 (bônus): Validação nos eventos confirmados

Independente do experimento, validar manualmente:
- Dos 5 eventos confirmados, quantos o modelo acerta?
- O modelo prevê algum evento que não foi registrado? Se sim, corresponde a algum pico na telemétrica?

Isso é o argumento mais forte pro TCC: "o modelo acertou X dos 5 eventos reais".

## Métricas de avaliação

| Métrica | Pra que serve |
|---------|---------------|
| Accuracy | Acerto geral (cuidado: dataset desbalanceado mascara) |
| Precision | Quando previu enchente, quantas vezes acertou? (evita alarme falso) |
| Recall | Das enchentes reais, quantas detectou? (evita deixar passar) |
| F1-Score | Equilíbrio entre precision e recall (principal métrica) |
| RMSE / MAE | Erro médio (pra regressão) |
| ROC-AUC | Capacidade de distinguir classes |
| Feature Importance | Quais variáveis mais influenciam (gráfico pro TCC) |

## Ordem de execução

1. Treinar os 4 modelos com o cenário C completo (dados ANA + Open-Meteo + GloFAS)
2. Identificar o melhor modelo (maior F1-Score)
3. Com o melhor modelo, rodar Experimento 1 (comparar fontes)
4. Com o melhor modelo e melhor fonte, rodar Experimento 2 (janelas)
5. Rodar Experimento 3 (target contínuo vs binário)
6. Validar contra os 5 eventos confirmados
7. Documentar tudo com gráficos e tabelas

## Resultado esperado no TCC

Uma seção de Resultados que mostra:
- Tabela comparativa dos 4 modelos
- Gráfico de feature importance do vencedor
- Tabela mostrando impacto de cada fonte de dados
- Tabela mostrando melhor janela temporal
- Comparação regressão vs classificação
- Validação contra eventos reais ("acertou 4 de 5")
- Confusion matrix do melhor modelo

Isso é muito mais rico do que só "testei RF e XGBoost e XGBoost ganhou" que os outros fizeram.
