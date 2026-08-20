# Fontes de Dados

Documentação das estações e fontes utilizadas no TCC.

## Dados Pluviométricos (Chuva)

### Estação Principal: SABARÁ (1943006)

| Campo | Valor |
|-------|-------|
| Código | 1943006 |
| Nome | SABARÁ |
| Bacia | 4 - Rio São Francisco |
| SubBacia | 41 - Rios São Francisco, das Velhas |
| Estado | Minas Gerais |
| Município | Sabará |
| Responsável | ANA |
| Operadora | SGB-CPRM |
| Latitude | -19.8931 |
| Longitude | -43.815 |
| Altitude (m) | 720 |
| Período utilizado | 01/01/1997 a 30/04/2026 |

**Fonte**: Sistema Hidroweb da Agência Nacional de Águas (ANA)

### Estação Auxiliar: CGH MARZAGÃO BARRAMENTO (1943146)

Utilizada para preenchimento de lacuna de dados (02 a 08 de novembro de 2024).

| Campo | Valor |
|-------|-------|
| Código | 1943146 |
| Nome | CGH MARZAGÃO BARRAMENTO |
| Bacia | 4 - Rio São Francisco |
| SubBacia | 41 - Rios São Francisco, das Velhas |
| Estado | Minas Gerais |
| Município | Sabará |
| Responsável | FERTILIGAS |
| Operadora | FERTILIGAS |
| Latitude | -19.8997 |
| Longitude | -43.8742 |
| Altitude (m) | 706 |

**Fonte**: Sistema Hidro Telemetria da ANA

**Distância entre estações**: ~5.6 km

**Dados preenchidos** (agregados de medições horárias):

| Data | Chuva (mm) |
|------|------------|
| 02/11/2024 | 0.0 |
| 03/11/2024 | 0.0 |
| 04/11/2024 | 2.8 |
| 05/11/2024 | 37.8 |
| 06/11/2024 | 0.0 |
| 07/11/2024 | 1.6 |
| 08/11/2024 | 1.6 |

## Dados Meteorológicos (Temperatura, Umidade)

### Estação INMET: Belo Horizonte (83587)

| Campo | Valor |
|-------|-------|
| Código OMM | 83587 |
| Nome | BELO HORIZONTE |
| Estado | Minas Gerais |
| Tipo | Convencional |
| Período utilizado | 01/01/1997 a 30/04/2026 |

**Fonte**: Instituto Nacional de Meteorologia (INMET) - BDMEP

**Distância até Sabará**: ~17 km

**Variáveis utilizadas**:
- Temperatura média compensada diária (°C)
- Temperatura máxima diária (°C)
- Temperatura mínima diária (°C)
- Umidade relativa do ar média diária (%)

**Justificativa**: A estação de Belo Horizonte foi utilizada por ser a mais próxima com série histórica completa. A distância de 17 km é aceitável para variáveis meteorológicas de mesoescala como temperatura e umidade, que apresentam alta correlação espacial em distâncias de até 30-50 km.

## Dados de Vazão (Target)

### GloFAS - Global Flood Awareness System

| Campo | Valor |
|-------|-------|
| Fonte | Copernicus Climate Data Store |
| Produto | River discharge reanalysis |
| Resolução espacial | 0.05° (~5 km) |
| Resolução temporal | Diária |
| Período | 01/01/1997 a 30/04/2026 |
| Coordenadas | Lat -19.89, Lon -43.82 (ponto mais próximo de Sabará) |
| Unidade | m³/s |

**Fonte**: ECMWF Copernicus Climate Change Service

**Justificativa**: O GloFAS foi utilizado por fornecer série histórica consistente de vazão para o período de estudo. Embora seja um dado modelado (reanálise), apresenta boa correlação com dados observados em bacias de médio porte e é amplamente utilizado em estudos de previsão de cheias.

## Resumo das Fontes

| Variável | Fonte | Estação/Produto | Período |
|----------|-------|-----------------|---------|
| Chuva (mm) | ANA Hidroweb | 1943006 + 1943146 | 1997-2026 |
| Temperatura (°C) | INMET BDMEP | 83587 | 1997-2026 |
| Umidade (%) | INMET BDMEP | 83587 | 1997-2026 |
| Vazão (m³/s) | GloFAS/Copernicus | Reanálise | 1997-2026 |

## Localização das Estações

```
Estação SABARÁ (1943006):     -19.8931, -43.8150
Estação MARZAGÃO (1943146):   -19.8997, -43.8742
Estação INMET BH (83587):     -19.9317, -43.9350 (aprox.)
Ponto GloFAS:                 -19.89,   -43.82
```

Todas as estações estão localizadas na região metropolitana de Belo Horizonte, na bacia do Rio das Velhas (afluente do Rio São Francisco).
