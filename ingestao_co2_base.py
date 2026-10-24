"""

DESCRIÇÃO GERAL:
----------------
Este script realiza o processo de Extração, Transformação e Carga (ETL) dos dados
públicos da Pesquisa Origem e Destino (OD) 2023 realizada pelo Metrô de São Paulo.
O objetivo é transformar planilhas brutas em formato matricial (.xlsx) em um banco
de dados relacional e vetorial utilizando o DuckDB.


ESTRUTURA DAS TABELAS GERADAS NO DUCKDB:
----------------------------------------
1. tabela 'indicadores_zonas':
   - Contém os atributos socioeconômicos e territoriais das 527 Zonas de Pesquisa (Tab1).
   - Colunas: zona_id, nome_zona, domicilios, familias, populacao, matriculas_escolares,
              empregos, automoveis, viagens_produzidas, viagens_atraidas, area_ha,
              area_km2, ano.

2. tabela 'viagens_matriz_od':
   - Contém a matriz Origem-Destino unificada dos 4 modais principais de transporte,
     despivotada (unpivoted) e filtrada apenas para pares OD com viagens ativas (>0).
   - Colunas: zona_origem, zona_destino, viagens (estimativa por dia útil), ano, modo_transporte.
   - Modais incluídos:
       * Tab24 -> Coletivo (Ônibus, Metrô, Trem)
       * Tab25 -> Individual (Automóvel, Moto, Táxi, App)
       * Tab27 -> A_Pe
       * Tab28 -> Bicicleta


INSTRUÇÕES PARA REPRODUÇÃO EM OUTROS COMPUTADORES:
---------------------------------------------------
1. Pré-requisitos do Sistema:
   - Python 3.9+ instalado.
   - Dependências necessárias no ambiente Python:
     pip install duckdb pandas openpyxl

2. Arquivo Fonte Necessário:
   - A planilha original do Metrô 'Tabelas_Site_OD2023_REV_190225.xlsx' deve estar
     armazenada no mesmo diretório/pasta deste script Python.

3. Execução:
   - Execute o script via terminal: python ingestao_co2_base.py
   - O arquivo 'pesquisa_od_sp.duckdb' será gerado/atualizado automaticamente no diretório.

4. Visualização dos Dados:
   - Abra o programa DBeaver (ou extensão DuckDB no VS Code).
   - Crie uma conexão do tipo 'DuckDB' apontando para o arquivo 'pesquisa_od_sp.duckdb'.
================================================================================
"""

import duckdb
import pandas as pd

# ------------------------------------------------------------------------------
# CONFIGURAÇÃO DE CAMINHOS E CONEXÃO AO BANCO DE DADOS
# ------------------------------------------------------------------------------
# Nome do arquivo de planilha fornecido pelo Metrô de São Paulo
excel_path = "Tabelas_Site_OD2023_REV_190225.xlsx"

# Inicializa o leitor de abas do pandas para evitar reabrir o arquivo pesado várias vezes
xls = pd.ExcelFile(excel_path)

# Conecta ao banco de dados DuckDB (Cria o arquivo no disco se ele não existir)
conn = duckdb.connect("pesquisa_od_sp.duckdb")

# ==============================================================================
# 1. PROCESSAMENTO DA TABELA 01 (INDICADORES SOCIOECONÔMICOS E ZONAIS)
# ==============================================================================
print("=== 1. PROCESSANDO A TABELA 01 (INDICADORES ZONAIS) ===")

# Lê a aba Tab1 sem assumir cabeçalhos fixos, pois o arquivo possui metadados no topo
df_tab1_raw = pd.read_excel(xls, sheet_name="Tab1", header=None)

# Busca dinamicamente a linha onde começam os dados numéricos da Zona de Pesquisa 1
tab1_start_idx = None
for idx in range(df_tab1_raw.shape[0]):
    val0 = df_tab1_raw.iloc[idx, 0]
    if pd.notna(val0):
        try:
            if int(val0) == 1:
                tab1_start_idx = idx
                break
        except (ValueError, TypeError):
            continue

# Seleciona as linhas a partir da Zona 1 e as primeiras 11 colunas de indicadores
df_tab1 = df_tab1_raw.iloc[tab1_start_idx:, :11].copy()
df_tab1[0] = pd.to_numeric(df_tab1[0], errors="coerce")
df_tab1 = df_tab1.dropna(subset=[0]).reset_index(drop=True)

# Mapeia e limpa as colunas alinhando perfeitamente com os nomes oficiais dos indicadores
df_tab01_clean = pd.DataFrame(
    {
        "zona_id": df_tab1[0].astype(int),
        "nome_zona": df_tab1[1].astype(str),
        "domicilios": pd.to_numeric(df_tab1[2], errors="coerce").fillna(0),
        "familias": pd.to_numeric(df_tab1[3], errors="coerce").fillna(0),
        "populacao": pd.to_numeric(df_tab1[4], errors="coerce").fillna(0),
        "matriculas_escolares": pd.to_numeric(
            df_tab1[5], errors="coerce"
        ).fillna(0),
        "empregos": pd.to_numeric(df_tab1[6], errors="coerce").fillna(0),
        "automoveis": pd.to_numeric(df_tab1[7], errors="coerce").fillna(0),
        "viagens_produzidas": pd.to_numeric(
            df_tab1[8], errors="coerce"
        ).fillna(0),
        "viagens_atraidas": pd.to_numeric(df_tab1[9], errors="coerce").fillna(
            0
        ),
        "area_ha": pd.to_numeric(df_tab1[10], errors="coerce").fillna(0),
    }
)

# Converte a área de Hectares (ha) para Quilômetros Quadrados (km²) [1 km² = 100 ha]
df_tab01_clean["area_km2"] = df_tab01_clean["area_ha"] / 100.0
df_tab01_clean["ano"] = 2023

# Cria a tabela de indicadores no DuckDB (substitui caso já exista)
conn.execute("DROP TABLE IF EXISTS indicadores_zonas")
conn.execute(
    "CREATE TABLE indicadores_zonas AS SELECT * FROM df_tab01_clean"
)
print(
    f"✓ Tabela 'indicadores_zonas' criada com sucesso! Zonas carregadas: {len(df_tab01_clean)}"
)

# ==============================================================================
# 2. PROCESSAMENTO DAS MATRIZES ORIGEM-DESTINO (TABELAS 24, 25, 27 E 28)
# ==============================================================================
print("\n=== 2. PROCESSANDO AS MATRIZES OD (TAB 24, 25, 27, 28) ===")

# Mapeamento entre o nome das abas na planilha Excel e a nomenclatura padronizada dos modais
matrizes_foco = {
    "Tab24": "Coletivo",
    "Tab25": "Individual",
    "Tab27": "A_Pe",
    "Tab28": "Bicicleta",
}

# Cria a tabela unificada no DuckDB que armazenará todas as viagens despivotadas
conn.execute("DROP TABLE IF EXISTS viagens_matriz_od")
conn.execute("""
    CREATE TABLE viagens_matriz_od (
        zona_origem INTEGER,
        zona_destino INTEGER,
        viagens DOUBLE,
        ano INTEGER,
        modo_transporte VARCHAR
    )
""")


def extrair_matriz_od(sheet_name):
    """Lê uma aba matricial da Pesquisa OD, identifica o cabeçalho das zonas de destino,

    despivota a matriz 527x527 para o formato relacional longo (long-format) e
    remove pares zerados para otimização de espaço.
    """
    df_raw = pd.read_excel(xls, sheet_name=sheet_name, header=None)

    # Localiza dinamicamente a linha que contém o sequencial das Zonas de Destino (1, 2, 3...)
    header_idx = None
    for idx in range(df_raw.shape[0]):
        v1, v2 = df_raw.iloc[idx, 1], df_raw.iloc[idx, 2]
        if pd.notna(v1) and pd.notna(v2):
            try:
                if int(v1) == 1 and int(v2) == 2:
                    header_idx = idx
                    break
            except (ValueError, TypeError):
                continue

    # Extrai as 527 zonas de destino das colunas (garante conversão limpa para números inteiros)
    dest_zones_raw = df_raw.iloc[header_idx, 1:528].values
    dest_zones = [int(pd.to_numeric(z)) for z in dest_zones_raw]

    # Localiza dinamicamente a linha onde começam os dados de viagem da Zona de Origem = 1
    data_start_idx = None
    for idx in range(header_idx + 1, df_raw.shape[0]):
        v0 = df_raw.iloc[idx, 0]
        if pd.notna(v0):
            try:
                if int(v0) == 1:
                    data_start_idx = idx
                    break
            except (ValueError, TypeError):
                continue

    # Isola o bloco numérico de dados da matriz Origem x Destino
    df_data = df_raw.iloc[data_start_idx:, :528].copy()
    df_data[0] = pd.to_numeric(df_data[0], errors="coerce")
    df_data = df_data.dropna(subset=[0])
    df_data[0] = df_data[0].astype(int)

    # Atribui os nomes das colunas: 'zona_origem' + os IDs das 527 zonas de destino
    df_data.columns = ["zona_origem"] + dest_zones

    # Transformação de Despivotamento (Melt/Unpivot): Transforma colunas de destino em linhas
    df_long = df_data.melt(
        id_vars=["zona_origem"], var_name="zona_destino", value_name="viagens"
    )
    df_long["zona_destino"] = df_long["zona_destino"].astype(int)
    df_long["viagens"] = pd.to_numeric(
        df_long["viagens"], errors="coerce"
    ).fillna(0)

    # Filtra apenas os pares Origem-Destino ativos (onde o volume diário estimado de viagens é > 0)
    df_long = df_long[df_long["viagens"] > 0].reset_index(drop=True)
    return df_long


# Processa cada aba de modo de transporte e insere sequencialmente na tabela do DuckDB
for sheet, modo in matrizes_foco.items():
    print(f"  -> Processando {sheet} ({modo})...")
    df_long = extrair_matriz_od(sheet)
    df_long["ano"] = 2023
    df_long["modo_transporte"] = modo

    # Inserção direta do DataFrame do pandas no DuckDB
    conn.execute("INSERT INTO viagens_matriz_od SELECT * FROM df_long")

print("\n✓ Matrizes OD unificadas com sucesso na tabela 'viagens_matriz_od'!")

# ==============================================================================
# 3. VALIDAÇÃO E SUMÁRIO DE CONTROLE DOS DADOS
# ==============================================================================
print("\n=== RESUMO DAS MATRIZES CARREGADAS NO DUCKDB ===")

# Executa consulta SQL de verificação agrupando os totais de linhas e viagens por modal
res_matrizes = conn.execute("""
    SELECT 
        modo_transporte, 
        COUNT(*) as pares_od_ativos, 
        ROUND(SUM(viagens), 2) as total_viagens_dia_util
    FROM viagens_matriz_od
    GROUP BY modo_transporte
    ORDER BY total_viagens_dia_util DESC
""").df()

print(res_matrizes)

# Fecha a conexão com o banco de dados
conn.close()
print("\nProcessamento concluído com sucesso!")