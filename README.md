# Modelo de Estimativa de Emissões de CO₂ na RMSP (2017 vs. 2023)

## Visão Geral do Projeto e Estrutura do Repositório

Este repositório contém a pipeline de dados e modelagem espacial desenvolvida para estimar e comparar as emissões de dióxido de carbono ($\text{CO}_2$) decorrentes do sistema de transporte de passageiros na Região Metropolitana de São Paulo (RMSP) entre 2017 e 2023.

A análise fundamenta-se nos microdados e matrizes de viagens das edições de 2017 e 2023 da Pesquisa Origem e Destino (OD) do Metrô de São Paulo, estruturados em um banco de dados analítico relacional de alta performance no DuckDB (`pesquisa_od_sp.duckdb`).

### Objetivos Principais:
1. **Compatibilização Territorial:** Mapear e padronizar as alterações de zoneamento do Metrô entre 2017 e 2023 através de uma tabela oficial de correspondência (*De-Para*).
2. **Carga e Modelagem de Dados:** Construir matrizes de viagens consolidadas por modal (Coletivo, Individual, A Pé e Bicicleta) e dados socioeconômicos.
3. **Cálculo Espacial e Emissões:** Calcular distâncias interzonais (entre centroides) e intrazonais (estimadas pela área territorial) para mensurar as emissões em nível de Macrozona.

---

### Estrutura do Projeto

Para garantir a organização, rastreabilidade e reprodutibilidade do projeto, os arquivos estão distribuídos na seguinte estrutura:

```text
.
├── data/                        # Planilhas brutas do Metrô (não versionadas no Git)
│   ├── Corresp2017_2023_190225.xlsx
│   └── Tabelas_Site_OD2023_REV_190225.xlsx
├── scripts/                     # Scripts de automação e ETL em Python
│   ├── ingestao_depara.py       # Carga e tratamento da tabela de correspondência (2017 <-> 2023)
│   └── ingestao_co2_base.py     # Ingestão das matrizes e indicadores
├── .gitignore                   # Arquivo de exclusão para git (ignora .venv/ e .duckdb)
└── README.md                    # Documentação do repositório

# Clone o repositório e acesse a pasta do projeto
git clone [https://github.com/vieiraAnaCarolina/Pesquisa_OrigemDestino.git](https://github.com/vieiraAnaCarolina/Pesquisa_OrigemDestino.git)
cd Pesquisa_OrigemDestino

# Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Atualize o pip e instale as dependências
pip install --upgrade pip
pip install -r requirements.txt

# Execução da pipeline de dados no DuckDB:
# 1. Cria a tabela de correspondência geográfica (de_para_zonas)
python scripts/ingestao_depara.py

# 2. Insere os dados de viagens e indicadores
python scripts/ingestao_co2_base.py
