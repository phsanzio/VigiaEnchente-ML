# Metodologia - Coleta e Pré-processamento de Dados

## Período de Estudo

O estudo abrange o período de **01 de janeiro de 1997 a 30 de abril de 2026**, totalizando aproximadamente 29 anos de dados diários.

## Fontes de Dados

### Dados Pluviométricos

Os dados de precipitação foram obtidos do Sistema Hidroweb da Agência Nacional de Águas (ANA), utilizando a estação **SABARÁ (código 1943006)**, localizada no município de Sabará-MG (latitude -19.8931°, longitude -43.815°, altitude 720m).

Para preenchimento de uma lacuna de dados entre 02 e 08 de novembro de 2024, foram utilizados dados da estação **CGH MARZAGÃO BARRAMENTO (código 1943146)**, também localizada em Sabará-MG (latitude -19.8997°, longitude -43.8742°), distante aproximadamente 5.6 km da estação principal. Os dados horários dessa estação foram agregados em totais diários.

### Dados Meteorológicos

Os dados de temperatura e umidade relativa do ar foram obtidos do Banco de Dados Meteorológicos do INMET (BDMEP), utilizando a estação convencional de **Belo Horizonte (código OMM 83587)**, distante aproximadamente 17 km de Sabará. A utilização dessa estação é justificada pela alta correlação espacial de variáveis meteorológicas de mesoescala em distâncias de até 30-50 km.

Variáveis utilizadas:
- Temperatura média compensada diária (°C)
- Temperatura máxima diária (°C)
- Temperatura mínima diária (°C)
- Umidade relativa do ar média diária (%)

A variável velocidade do vento foi descartada devido ao elevado número de dados faltantes e baixa relevância para previsão de vazão.

### Dados de Vazão

Os dados de vazão foram obtidos do sistema **GloFAS (Global Flood Awareness System)** do Copernicus Climate Data Store (ECMWF). O GloFAS fornece dados de reanálise de descarga fluvial com resolução espacial de 0.05° (~5 km) e resolução temporal diária. Foi utilizado o ponto de grade mais próximo de Sabará (latitude -19.89°, longitude -43.82°).

## Pré-processamento

### Unificação das Bases

As três fontes de dados (precipitação, meteorologia e vazão) foram unificadas através de junção (inner join) pela coluna de data, resultando em **10.712 registros diários**.

### Tratamento de Dados Faltantes

- **Precipitação**: Lacuna de 7 dias (02-08/nov/2024) preenchida com dados de estação auxiliar
- **Meteorologia**: Registros com dados faltantes de temperatura ou umidade foram removidos (~21 dias)
- **Vento**: Variável removida do estudo devido a 180 dias de dados faltantes

### Engenharia de Features

A partir dos dados unificados, foram calculadas as seguintes variáveis derivadas:

**Acumulados de Precipitação:**
- Precipitação acumulada 3 dias (chuva_3d)
- Precipitação acumulada 7 dias (chuva_7d)
- Precipitação acumulada 14 dias (chuva_14d)
- Precipitação acumulada 30 dias (chuva_30d)

**Índice de Precipitação Antecedente (API):**

O API foi calculado de forma recursiva segundo a equação:

```
API(t) = α × (API(t-1) + P(t-1))
```

Onde P(t-1) é a precipitação do dia anterior e α é o fator de decaimento. Foram calculados dois APIs:
- API de curto prazo (α = 0.85): representa umidade do solo superficial
- API de longo prazo (α = 0.90): representa contribuição de aquíferos

**Variáveis Defasadas (Lags):**
- Vazão do dia anterior (vazao_lag1)
- Vazão de 2 dias atrás (vazao_lag2)
- Precipitação do dia anterior (chuva_lag1)
- Precipitação de 2 dias atrás (chuva_lag2)

**Variável Alvo:**
- Vazão do dia seguinte (target): deslocamento de -1 dia da série de vazão

### Remoção de Registros Incompletos

Após a criação das features, foram removidos registros com valores ausentes:
- 2 primeiros dias da série (impossibilidade de calcular lags de 2 dias)
- Último dia da série (ausência de valor alvo)
- Dias com dados meteorológicos faltantes

## Base Final

A base de dados final para modelagem contém:
- **10.688 registros** (99.78% dos dados originais)
- **Período**: 03/01/1997 a 29/04/2026
- **18 variáveis preditoras** + 1 variável alvo
- **0 valores ausentes**

### Variáveis do Dataset Final

| Variável | Descrição | Unidade |
|----------|-----------|---------|
| data | Data do registro | - |
| chuva_mm | Precipitação diária | mm |
| vazao | Vazão observada | m³/s |
| temp_media | Temperatura média | °C |
| temp_max | Temperatura máxima | °C |
| temp_min | Temperatura mínima | °C |
| umidade_media | Umidade relativa média | % |
| chuva_3d | Precipitação acumulada 3 dias | mm |
| chuva_7d | Precipitação acumulada 7 dias | mm |
| chuva_14d | Precipitação acumulada 14 dias | mm |
| chuva_30d | Precipitação acumulada 30 dias | mm |
| api_7d | API curto prazo (α=0.85) | mm |
| api_30d | API longo prazo (α=0.90) | mm |
| vazao_lag1 | Vazão dia anterior | m³/s |
| vazao_lag2 | Vazão 2 dias atrás | m³/s |
| chuva_lag1 | Precipitação dia anterior | mm |
| chuva_lag2 | Precipitação 2 dias atrás | mm |
| target | Vazão dia seguinte (D+1) | m³/s |
