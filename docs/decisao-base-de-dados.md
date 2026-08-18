# Decisão: Base de Dados para o Modelo de ML

## O que já temos

| Fonte | Variável | Período | Observações |
|-------|----------|---------|-------------|
| ANA/Defesa Civil (estação 1943006) | Chuva diária (mm) | 1941-2025 | 84 anos, dados reais, nível 1 e 2 |
| ANA (estações 41205000, 41220000, 41230000) | Vazão (m³/s) | 1939-1965 | 26 anos, dados reais, nível 2 |
| ANA (estações 41205000, 41220000, 41230000, 41242500) | Cota/nível (cm) | 1938-1965 | 27 anos, dados reais |
| Defesa Civil (Plano Municipal) | Eventos de enchente | 1997, 2020, 2022, 2023, 2024 | 5 eventos confirmados oficialmente |
| Defesa Civil (Plano Municipal) | Thresholds oficiais | - | Nível > 2.0m, Chuva > 100mm/72h |

## O problema

- Temos chuva por 84 anos, mas vazão/nível só até 1965
- Os eventos confirmados (target) são de 1997-2024
- Nos anos em que temos eventos, NÃO temos vazão real
- Precisamos complementar pra ter um dataset completo no período dos eventos

---

## Alternativas de complemento

### Opção 1: Open-Meteo Historical Weather API (clima)

**O que oferece:** precipitação, temperatura, umidade, vento, pressão, evapotranspiração. Desde 1940 até hoje. Resolução diária. Grátis.

**Positivo:**
- Cobre o período inteiro (1940-2026), alinha com nossos dados de chuva
- Grátis, sem cadastro, API aberta
- Dados já tratados (reanálise ERA5), sem lacunas
- Adiciona variáveis que não temos (temperatura, umidade, vento, pressão)
- Pode validar contra nossos dados reais de chuva (comparar Open-Meteo vs estação 1943006)

**Negativo:**
- São dados modelados/reanálise, não medições reais in loco
- Resolução espacial de ~25km (ERA5), pode não captar chuvas muito localizadas
- Não tem vazão/nível do rio

### Opção 2: Open-Meteo Flood API (GloFAS)

**O que oferece:** vazão simulada desde 1984. Resolução diária. Grátis.

**Positivo:**
- Única fonte de "vazão" para o período 1984-2026 (preenche o gap de 60 anos)
- Grátis, sem cadastro
- Já temos integrado no backend Spring Boot
- Cobre os anos dos eventos confirmados (2020-2024)

**Negativo:**
- Resolução grosseira (5x5 km), valores absolutos não batem com a realidade (picos de ~17 m³/s vs 1350 m³/s reais na estação ANA)
- Mede um "quadrado" genérico, não o Rio das Velhas especificamente
- Serve como indicador de tendência, não como valor absoluto
- Precisa normalizar pra usar junto com dados reais

### Opção 3: Estação Raposos (41200430) - HidroWeb/Telemetria

**O que oferece:** vazão e nível em tempo real do Rio das Velhas, em Raposos (cidade vizinha, rio acima).

**Positivo:**
- Dados REAIS do Rio das Velhas (não simulados)
- Está a montante de Sabará (o nível lá antecipa o que vai chegar em Sabará)
- Pode ter série histórica convencional no HidroWeb
- Alta correlação esperada com enchentes em Sabará

**Negativo:**
- Não verificamos o período disponível (pode ser curto)
- Precisa acessar e baixar (pode ter burocracia)
- É de outra cidade, precisa justificar relevância hidrológica
- Se for só telemétrica recente (2020+), período curto

### Opção 4: CEMADEN (pluviométricas automáticas em Sabará)

**O que oferece:** 4 estações em Sabará (1943141-1943144), chuva desde ~2014.

**Positivo:**
- Dados de chuva reais, de dentro de Sabará
- Resolução horária ou sub-horária
- Cobre os eventos recentes (2020-2024)
- Múltiplas estações = visão espacial da chuva no município

**Negativo:**
- Período curto (~10 anos)
- Não tem vazão/nível
- Pode ter lacunas (como vimos na 1943146 com sensor defeituoso)

### Opção 5: Transformação precipitação-vazão (modelagem)

**O que oferece:** usar um modelo pra estimar vazão a partir da chuva nos anos em que não temos vazão real.

**Positivo:**
- Usa os 26 anos de dados pareados (chuva + vazão, 1939-1965) pra treinar
- Aplica nos 84 anos de chuva pra gerar vazão estimada pra todo o período
- Abordagem cientificamente válida (Sperb fez isso, podemos citar)
- Não depende de fonte externa

**Negativo:**
- Introduz erro/incerteza (modelo sobre modelo)
- A relação chuva-vazão de 1939-1965 pode não valer pra 2020 (urbanização mudou a bacia)
- Mais complexo de implementar e justificar
- Pode ser questionado pela banca

### Opção 6: Usar só chuva + features derivadas (sem vazão)

**O que oferece:** modelo baseado apenas em precipitação (84 anos) + features temporais.

**Positivo:**
- Simples, dados completos sem lacuna
- 84 anos ininterruptos
- Target claro: > 100mm/72h = risco (threshold oficial)
- Fácil de justificar e explicar

**Negativo:**
- Perde informação (vazão é indicador mais direto de enchente)
- Modelo pode ser menos preciso
- Pode ser "simples demais" pro TCC
- Ignora a dinâmica do rio

---

## Decisão: Combinação pragmática

### Composição da base de dados final

```
DADOS REAIS (espinha dorsal):
├── Chuva diária real (ANA, 1941-2025, 84 anos)
│
COMPLEMENTO MODELADO (preencher lacunas e adicionar variáveis):
├── Open-Meteo Historical Weather (1940-2026)
│   ├── temperature_2m_max / min
│   ├── precipitation_sum (pra comparar com dado real)
│   ├── relative_humidity_2m_max
│   ├── wind_speed_10m_max
│   └── et0_fao_evapotranspiration
│
├── Open-Meteo Flood API / GloFAS (1984-2026)
│   └── river_discharge (vazão simulada, normalizada)
│
TARGET (variável alvo):
├── Abordagem dupla (testar ambas e comparar):
│
│   Opção A — Regressão (target contínuo 0 a 1):
│   ├── 0.0 = dia normal
│   ├── 0.55 = alagamento localizado
│   ├── 0.75-0.80 = alagamento com danos
│   ├── 0.90-0.95 = inundação Rio das Velhas
│   ├── 1.0 = evento extremo citywide
│   ├── Para dias confirmados: usar severidade da tabela ground truth
│   ├── Para dias não confirmados: 0.0 (assumir sem evento)
│   └── Vantagem: depois pode prever severidade em dias futuros
│
│   Opção B — Classificação binária (0 ou 1):
│   ├── 1 = enchente (chuva acumulada > 100mm/72h OU evento confirmado)
│   ├── 0 = sem enchente
│   └── Vantagem: mais simples, métricas claras (F1, precision, recall)
│
│   Validação (ambas as opções):
│   ├── Cruzar com os 5 eventos confirmados pela Defesa Civil
│   └── Comparar qual abordagem performa melhor nas métricas
```

### Por que essa combinação

1. **Usa dados reais como base** - chuva de 84 anos é a espinha dorsal, é oficial e inquestionável
2. **Complementa com Open-Meteo pra ter cobertura completa** - especialmente no período 1984-2025 onde temos os eventos
3. **Não depende de acesso a dados que não temos** - tudo é API aberta ou já está em mãos
4. **Permite validação cruzada** - nos 26 anos sobrepostos (1941-1965) podemos comparar chuva real vs Open-Meteo pra medir confiabilidade
5. **É implementável agora** - sem burocracia, sem esperar resposta de ninguém
6. **É defensável no TCC** - combina fontes oficiais com dados modelados reconhecidos internacionalmente (ERA5, GloFAS)

### Como implementar (passo a passo)

#### Etapa 1: Montar o "tabelão" base (1 linha por dia)

```python
# Carregar chuva real (já temos no CSV, despivotar)
df_chuva = carregar_e_despivotar('chuvas.csv')  # 1941-2025, ~30.000 dias

# Resultado: DataFrame com colunas [data, chuva_mm]
```

#### Etapa 2: Buscar Open-Meteo Historical Weather

```python
# API: https://archive-api.open-meteo.com/v1/archive
# Parâmetros: latitude=-19.88, longitude=-43.80 (Sabará)
# Variáveis: temperature_2m_max, temperature_2m_min, precipitation_sum,
#            relative_humidity_2m_max, wind_speed_10m_max, et0_fao_evapotranspiration
# Período: 1940-01-01 a 2026-06-11

# Resultado: DataFrame com [data, temp_max, temp_min, precip_om, umidade, vento, et0]
```

#### Etapa 3: Buscar Open-Meteo Flood API (GloFAS)

```python
# API: https://flood-api.open-meteo.com/v1/flood
# Parâmetros: latitude=-19.88, longitude=-43.80
# Variáveis: river_discharge
# Período: 1984-01-01 a 2026-06-11

# Resultado: DataFrame com [data, vazao_glofas]
```

#### Etapa 4: Juntar tudo por data

```python
df = df_chuva.merge(df_weather, on='data', how='left')
df = df.merge(df_flood, on='data', how='left')

# Resultado: tabelão com 1 linha por dia, todas as variáveis
```

#### Etapa 5: Feature engineering

```python
# Chuva acumulada
df['chuva_3d'] = df['chuva_mm'].rolling(3).sum()
df['chuva_7d'] = df['chuva_mm'].rolling(7).sum()
df['chuva_14d'] = df['chuva_mm'].rolling(14).sum()

# Sazonalidade
df['mes'] = df['data'].dt.month
df['dia_ano'] = df['data'].dt.dayofyear

# Taxa de variação da vazão (se disponível)
df['vazao_diff'] = df['vazao_glofas'].diff()
df['vazao_media_7d'] = df['vazao_glofas'].rolling(7).mean()

# Lag features (valores de dias anteriores)
df['chuva_lag1'] = df['chuva_mm'].shift(1)
df['chuva_lag3'] = df['chuva_mm'].shift(3)
df['vazao_lag1'] = df['vazao_glofas'].shift(1)
```

#### Etapa 6: Definir target

```python
# Critério oficial: chuva acumulada > 100mm em 72h
df['target'] = (df['chuva_3d'] > 100).astype(int)

# Validação: verificar se os 5 eventos confirmados estão marcados como 1
eventos = ['1997-12-15', '2020-01-27', '2022-01-09', '2023-10-26', '2024-11-13']
# Ajustar datas exatas quando soubermos
```

#### Etapa 7: Validação dos dados Open-Meteo

```python
# Comparar chuva real (ANA) vs chuva Open-Meteo no período 1941-2025
# Calcular correlação, RMSE, bias
# Isso vira um argumento no TCC: "a fonte complementar foi validada contra dados reais"
```

#### Etapa 8: Split temporal e treinamento

```python
# Split temporal (NÃO aleatório)
# Treino: 1984-2019 (período com GloFAS disponível)
# Teste: 2020-2025 (período com eventos confirmados)

# Modelos candidatos:
# - Random Forest
# - Gradient Boosting (XGBoost ou LightGBM)
# - Logistic Regression (baseline)
```

---

## Alternativas futuras (trabalhos futuros no TCC)

- Integrar estação de Raposos (41200430) quando dados estiverem acessíveis
- Testar transformação precipitação-vazão com os 26 anos pareados
- Incorporar dados CEMADEN (resolução horária) pra modelo de curto prazo
- Classificação multiclasse (SEM_RISCO, BAIXO, MEDIO, ALTO) em vez de binária

---

## Resumo da decisão

| Aspecto | Escolha |
|---------|---------|
| Modelos | Regressão Logística (baseline), Random Forest, XGBoost, SVM |
| Janelas temporais | 3d, 7d, 14d, 30d |
| Fontes de vazão | Open-Meteo GloFAS, Modelo precipitação-vazão local |
| Target principal | Classificação binária (enchente sim/não, threshold PLANCON) |
| Target complementar | Regressão (severidade 0-1) |
| Total de combinações | 32 (4 modelos x 4 janelas x 2 fontes) |
| Tempo estimado de execução | < 1 minuto |
| Features fixas em todas | chuva, acumulados, lags, sazonalidade, temp, umidade, vento |
| Variável que muda entre cenários | Apenas a fonte de vazão |
| Métrica principal | F1-Score |
| Validação extra | 5 eventos confirmados Defesa Civil |
| Após os 32 testes | GridSearch no modelo vencedor + regressão de severidade |
