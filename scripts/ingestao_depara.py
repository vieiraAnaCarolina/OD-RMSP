"""
================================================================================
PROJETO: Modelo de Estimativa de Emissões de CO2 na RMSP (Pesquisa OD 2023 / 2017)
MÓDULO: Ingestão do Mapeamento Territorial e Tabela de Correspondência (De-Para)
BANCO DE DADOS FINAL: pesquisa_od_sp.duckdb
================================================================================

DESCRIÇÃO GERAL:
----------------
Este script é responsável pela ingestão da Tabela de Correspondência Oficial (De-Para)
publicada pelo Metrô de São Paulo. Ele mapeia a equivalência territorial e de numeração
entre as 527 Zonas de Pesquisa do zoneamento de 2023 e as Zonas da Pesquisa OD 2017.

A criação desta tabela no DuckDB é fundamental para viabilizar análises comparativas
históricas e espaciais sem distorções, permitindo agregar dados de emissões de CO2 e
fluxos de viagens de ambos os anos sob as mesmas unidades territoriais (Macrozonas).

ESTRUTURA DA TABELA GERADA NO DUCKDB:
--------------------------------------
Tabela 'de_para_zonas':
  - Mapeia o de-para entre o zoneamento de 2023 e 2017, relacionando cada zona com seus
    respectivos recortes administrativos (Município e Distrito) e área territorial.
  - Colunas:
      * zona_2023       : ID numérico da zona de pesquisa em 2023.
      * zona_2017       : ID numérico da zona equivalente no zoneamento de 2017.
      * nome_zona_2023  : Nome oficial da zona em 2023.
      * municipio_id    : Código numérico do município.
      * nome_municipio  : Nome do município (ex: São Paulo, Guarulhos, etc.).
      * distrito_id     : Código numérico do distrito.
      * nome_distrito   : Nome do distrito (ex: Sé, República, Santo Amaro).
      * area_ha         : Área da zona em Hectares (ha).
      * area_km2        : Área da zona convertida para Quilômetros Quadrados (km²).

INSTRUÇÕES PARA REPRODUÇÃO EM OUTROS COMPUTADORES:
---------------------------------------------------
1. Pré-requisitos do Sistema:
   - Python 3.9+ instalado no ambiente (.venv).
   - Pacotes necessários: duckdb, pandas, openpyxl.

2. Arquivos Necessários no Diretório:
   - 'Corresp2017_2023_190225.xlsx' (Planilha oficial de correspondência do Metrô).
   - 'pesquisa_od_sp.duckdb' (Banco de dados DuckDB previamente inicializado).

3. Atenção Importante antes da Execução:
   - O DBeaver (ou qualquer outro cliente SQL) deve estar DESCONECTADO do arquivo
     'pesquisa_od_sp.duckdb' para evitar erros de bloqueio de arquivo (file lock).

4. Execução:
   - Execute no terminal: python ingestao_depara.py
================================================================================
"""

import duckdb
import pandas as pd

# ------------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DOS CAMINHOS DE ARQUIVO E BANCO DE DADOS
# ------------------------------------------------------------------------------
# Nome da planilha oficial fornecida pelo Metrô com a correspondência 2017/2023
excel_corresp = "Corresp2017_2023_190225.xlsx"

# Caminho do banco de dados relacional DuckDB do projeto
db_path = "pesquisa_od_sp.duckdb"

# ------------------------------------------------------------------------------
# 2. LEITURA E TRATAMENTO BRUTO DA PLANILHA EXCEL
# ------------------------------------------------------------------------------
# Leitura da aba 'Correspondência' sem cabeçalho fixo para lidar com metadados do topo
df_raw = pd.read_excel(
    excel_corresp, sheet_name="Correspondência", header=None
)

# Isola as linhas a partir do índice 5, onde começam os dados numéricos das zonas
df_data = df_raw.iloc[5:].copy()

# ------------------------------------------------------------------------------
# 3. ESTRUTURAÇÃO DOS DADOS E TRATAMENTO DE VALORES NULOS/SENSÍVEIS
# ------------------------------------------------------------------------------
# Mapeia as colunas extraídas, aplicando coerção numérica para prevenir exceções
df_depara = pd.DataFrame(
    {
        "zona_2023": pd.to_numeric(df_data[1], errors="coerce"),
        "zona_2017": pd.to_numeric(df_data[0], errors="coerce"),
        "nome_zona_2023": df_data[2].astype(str),
        "municipio_id": pd.to_numeric(df_data[3], errors="coerce"),
        "nome_municipio": df_data[4].astype(str),
        "distrito_id": pd.to_numeric(df_data[5], errors="coerce"),
        "nome_distrito": df_data[6].astype(str),
        "area_ha": pd.to_numeric(df_data[7], errors="coerce").fillna(0),
    }
)

# Remove linhas de cabeçalho secundário ou linhas vazias no rodapé
df_depara = df_depara.dropna(subset=["zona_2023", "zona_2017"]).reset_index(
    drop=True
)

# Converte os identificadores para o tipo inteiro nativo com segurança
df_depara["zona_2023"] = df_depara["zona_2023"].astype(int)
df_depara["zona_2017"] = df_depara["zona_2017"].astype(int)
df_depara["municipio_id"] = df_depara["municipio_id"].astype(int)
df_depara["distrito_id"] = df_depara["distrito_id"].astype(int)

# Realiza a conversão da área territorial de Hectares (ha) para Quilômetros Quadrados (km²)
df_depara["area_km2"] = df_depara["area_ha"] / 100.0

# ------------------------------------------------------------------------------
# 4. CARGA E CONSOLIDAÇÃO NO BANCO DE DADOS DUCKDB
# ------------------------------------------------------------------------------
# Conecta ao arquivo do banco de dados (garanta que o DBeaver esteja desconectado)
conn = duckdb.connect(db_path)

# Substitui/Cria a tabela 'de_para_zonas' com os dados devidamente higienizados
conn.execute("DROP TABLE IF EXISTS de_para_zonas")
conn.execute("CREATE TABLE de_para_zonas AS SELECT * FROM df_depara")

print(
    f"✓ Tabela 'de_para_zonas' criada com sucesso no DuckDB com {len(df_depara)} registros!"
)

# Encerra a conexão liberando o arquivo do banco de dados
conn.close()