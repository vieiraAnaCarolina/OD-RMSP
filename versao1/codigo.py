# -*- coding: utf-8 -*-
"""
Spyder Editor, stated 07.08.2025
this py-file imports excel-sheets and converts it to .csv
files this _chg at end were changed from Excel Binary to normal worksheet for import
"""
# %% import modules
import pandas as pd
import os
import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import pearsonr, spearmanr
import numpy as np
import unicodedata
from pygam import LinearGAM, s
import statsmodels.api as sm

print('>>> All modules imported sucessfully <<<')
# %% set locations
os.chdir('C:\\Users\\eriki\\OneDrive\\Desktop\\Artigo_OD_SP_doc\\DATA_SP_1977-2017') # go to folder of dataset

# path to safe the converted csv-files
path_csv = 'C:\\Users\\eriki\\OneDrive\\Desktop\\Artigo_OD_SP_doc\\DATA_SP_CSV'

print('making path sucessful, you are here:',os.getcwd())
# %% import files and save as .CSV and panda Dataframe (only run if data has changed)

for year in [1977, 1987, 1997, 2007, 2017]: # change here to run all years
#for year in [2017]: # change here to skip loop

    print(f"Processing year {year}...")
    
    '''# Socioeconomic 2017 
    df = pd.read_excel('Dados_Socioeconomicos (1977-2017).xlsx',
                       sheet_name=str(year), usecols='A:I', header=0)
    df = df.dropna(how='all') #clean all NaN
    df = df.rename(columns={df.columns[0]: 'Zone',
                            'Região': 'Region',
                            'Área': 'Area',
                            'População': 'Population',
                            'Empregos': 'Jobs',
                            'Auto_part': 'Car_Share',
                            'Test_ExpRenda': 'Income_Exp_Test',
                            'RendMed': 'Avg_Income',
                            'PropRendMed': 'Income_Median_Share'})
    df['Area'] = df['Area']/100
    df.to_csv(os.path.join(path_csv,  f'Socioeco_{year}.csv'), index=False, encoding='utf-8')
    globals()[f"socio_eco_{year}"] = df.copy()
    
    # Mobility
    df = pd.read_excel('Imobilidade (1977-2017).xlsx',
                       sheet_name='TUDO', header=0).dropna(how='all').query('`Ano` == @year')
    df = df.rename(columns={'Ano': 'Year',
                            'Zona': 'Zone',
                            'Imobilidade': 'Immobility',
                            'Região': 'Region'})
    df.to_csv(os.path.join(path_csv, f'Mobility_{year}.csv'), index=False, encoding='utf-8')
    globals()[f"mobility_{year}"] = df.copy()
    
    # Modalsplit
    df = pd.read_excel('Produc_ordem_ZHT (1977-2017).xlsx',
                       sheet_name=str(year), usecols='B:N', header=0)
    df = df.dropna(how='all') #clean all NaN
    df = df.rename(columns={'Zona_2017': 'Zone_2017',
                            'Metrô': 'Metro',
                            'Trem': 'Train',
                            'Ônibus': 'Bus',
                            'Auto': 'Car',
                            'Moto': 'Motorcycle',
                            'Não Motorizado': 'Non_Motorized',
                            'Metrô.1': 'Metro_Share',
                            'Trem.1': 'Train_Share',
                            'Ônibus.1': 'Bus_Share',
                            'Auto.1': 'Car_Share',
                            'Moto.1': 'Motorcycle_Share',
                            'Não Motorizado.1': 'Non_Motorized_Share'})
    df.to_csv(os.path.join(path_csv, f'ModalSplit_{year}.csv'), index=False, encoding='utf-8')
    globals()[f"modalsplit_{year}"] = df.copy()
    
    # TravelInfo
    df = pd.read_excel('Tempo andando_1MODO (1977-2017)_chg.xlsx',
                       sheet_name=str(year), usecols='F:N', header=0)
    df = df.dropna(how='all')
    df = df.rename(columns={'ZONA_O':'Origin_Zone',
                            'MODO1':'Mode1',
                            'FE_VIA':'Trip_End',
                            'RG':'Region',
                            'MODO1.1':'Mode2',
                            'ANDA_O':'Walk_Origin',
                            'ANDA_D':'Walk_Destination',
                            'Dur Exp O':'Expected_Duration_Origin',
                            'Dur Exp D':'Expected_Duration_Destination'})
    df[df.columns[df.columns.str.strip() ==
                  'Mode2'][0]] = df[df.columns[df.columns.str.strip() ==
                                               'Mode2'][0]].replace({'Trilhos': 'Rail',
                                                                     'Ônibus': 'Bus',
                                                                     'Individual': 'Individual',
                                                                     'Não Motorizado': 'Non-motorized',
                                                                     'Excluído': 'Excluded'})
    df.to_csv(os.path.join(path_csv, f'TravelInfo_{year}.csv'), index=False, encoding='utf-8')
    globals()[f"travel_info_{year}"] = df.copy()

    # TravelDuration
    units = ['Zone_ID', 'Region', 'Code', 'Type', 'Code', 'Type', 'Concat', '', 'min', 'min', 'km', 'km']

    df = pd.read_excel('Duracao_deslocamentos (1977-2017)_chg.xlsx',
                       sheet_name=str(year), usecols='G:R', header=0)
    #df = df.dropna(subset=[df.columns[0]])
    df = df.rename(columns={df.columns[0]:'Origin_Zone',
                            'RG_O':'Region',
                            'MODO1':'Mode1',
                            'MODO1.1':'Mode1_type',
                            'MODO2':'Mode2',
                            'MODO2.1':'Mode2_type',
                            'CONCAT':'Concat',
                            'Motorizado.1':'Motorized',
                            'FE_VIA':'Expansion factor',
                            'DURACAO':'Duration',
                            'DUR_EXP':'Expected_Duration',
                            'DISTANCIA':'Distance',
                            'DIST_EXP':'Expected_Distance'
                            }).applymap(lambda x: unicodedata.normalize('NFKD',
                            str(x)).encode('ascii', 'ignore').decode('utf-8')
                                 if isinstance(x, str)
                                 else x).replace({'Mode1_type': {'Nao Motorizado': 'Non_Motorized',
                                                                 'Trilhos': 'Rail',
                                                                 'Onibus': 'Bus',
                                                                 'Individual': 'Individual'},
                                                 'Mode2_type': {'Nao Motorizado': 'Non_Motorized',
                                                                'Trilhos': 'Rail',
                                                                'Onibus': 'Bus',
                                                                'Individual': 'Individual'},
                                                 'Motorized': {'Sim': 'Yes',
                                                               'Nao': 'No'}})
    df = df.replace({'Mode1_type': {'Não Motorizado': 'Non_Motorized',
                                    'Trilhos': 'Rail',
                                    'Ônibus': 'Bus',
                                    'Individual': 'Individual'},
                     'Mode2_type': {'Não Motorizado': 'Non_Motorized',
                                    'Trilhos': 'Rail', 'Ônibus': 'Bus',
                                    'Individual': 'Individual'},
                     'Motorized': {'Sim': 'Yes',
                                   'Não': 'No'}})
    df = pd.concat([pd.DataFrame([units], columns=df.columns), df], ignore_index=True)
    df.to_csv(os.path.join(path_csv, f'TravelDuration_{year}.csv'), index=False, encoding='utf-8')
    globals()[f"travel_dur_{year}"] = df.copy()

    # TravelDuration_table
    df = pd.read_excel('Duracao_deslocamentos (1977-2017)_chg.xlsx',
                       sheet_name=str(year), usecols='C:F', header=0)
    df = df.dropna(how='all')
    df = df.rename(columns={"Banco de dados": "Database",
                            "Class": "Class",
                            "Novo Modo": "New_Mode",
                            "Motorizado": "Motorized"})
    df['Database'] = df['Database'].astype(str).str.strip().replace({
    '01 - Metrô':'Metro','Metrô':'Metro',
    '02 - Trem':'Train','Trem':'Train',
    '03 - Monotrilho':'Monorail','Monotrilho':'Monorail',
    '04 - Ônibus/micro-ônibus/perua do município de São Paulo':'Bus/Microbus/Van (São Paulo municipality)',
    '05 - Ônibus/micro-ônibus/perua de outros municípios':'Bus/Microbus/Van (other municipalities)',
    '06 - Ônibus/micro-ônibus/perua metropolitano':'Bus/Microbus/Van (metropolitan)',
    '07 - Transporte Fretado':'Chartered Transport','Transporte Fretado':'Chartered Transport',
    '08 - Transporte Escolar':'School Transport','Transporte Escolar':'School Transport',
    '09 - Dirigindo Automóvel':'Driving Car','Dirigindo Automóvel':'Driving Car',
    '10 - Passageiro de Automóvel':'Car Passenger','Passageiro de Automóvel':'Car Passenger',
    '11 - Táxi Convencional':'Conventional Taxi','Táxi Convencional':'Conventional Taxi',
    '12 - Táxi não Convencional':'Non-conventional Taxi','Táxi não Convencional':'Non-conventional Taxi',
    '13 - Dirigindo Moto':'Driving Motorcycle','Dirigindo Moto':'Driving Motorcycle',
    '14 - Passageiro de Moto':'Motorcycle Passenger','Passageiro de Moto':'Motorcycle Passenger',
    '15 - Bicicleta':'Bicycle','Bicicleta':'Bicycle',
    '16 - A Pé':'Walking','A Pé':'Walking','APé':'Walking','A Pe':'Walking',
    '17 - Outros':'Other','Outros':'Other'})
    df = df.replace({'New_Mode': {'Trilhos': 'Rail',
                                  'Ônibus': 'Bus',
                                  'Individual': 'Individual',
                                  'Não Motorizado': 'Non_Motorized',
                                  'Excluído': 'Excluded'},
                     'Motorized': {'Sim': 'Yes',
                                   'Não': 'No',
                                   'Excluído': 'Excluded'}})
    df.to_csv(os.path.join(path_csv, f'TravelDuration_table{year}.csv'), index=False, encoding='utf-8')
    globals()[f"travel_dur_table_{year}"] = df.copy()
    
    #end of loop
    print('for year [', year, '] import data and safe as .CSV and dataframe sucessful')

print(">>> All CSV-files safed successfully <<<")

del df
del year
'''
# %% import csv and make DataFrame (safes time)

datasets = {"socio_eco": "Socioeco_{year}.csv",
            "mobility": "Mobility_{year}.csv",
            "modalsplit": "ModalSplit_{year}.csv",
            "travel_info": "TravelInfo_{year}.csv",
            "travel_dur": "TravelDuration_{year}.csv",
            "travel_dur_table": "TravelDuration_table{year}.csv"}

for year in [1977, 1987, 1997, 2007, 2017]:
    for var_prefix, file_pattern in datasets.items():
        file_path = os.path.join(path_csv, file_pattern.format(year=year))
        if os.path.exists(file_path):
            globals()[f"{var_prefix}_{year}"] = pd.read_csv(file_path)
            print(f"Loaded {var_prefix}_{year} from {file_path}")
        else:
            print(f"⚠ File not found: {file_path}")

print(">>> All DataFrames loaded successfully <<<")

del datasets
del file_path
del file_pattern
del var_prefix
# %% make Dataframe for 517 zones with parameters 
# population desnity, income per capita, retail\non r jobs per km2, motorization rates, immobility, population

zones_per_year = {2017:517, 2007:460, 1997:389, 1987:254, 1977:243} # Fixed number of zones per year

# Units dictionary
units = {
    "Zone": "ID",
    "Area": "km²",
    "Population": "persons",
    "Population_Density": "persons/km²",
    "Income_per_Capita": "US$/year",
    "Jobs_per_km2": "jobs/km²",
    "Retail_Jobs_per_km2": "jobs/km²",
    "Non_Retail_Jobs_per_km2": "jobs/km²",
    "Immobility": "%",
    "Motorization_Rate": "vehicles per 1000 citizen",
    "Metro": "trips/day",
    "Train": "trips/day",
    "Bus": "trips/day",
    "Car": "trips/day",
    "Motorcycle": "trips/day",
    "Non_Motorized": "trips/day",
    "Metro_Share": "%",
    "Train_Share": "%",
    "Bus_Share": "%",
    "Car_Share": "%",
    "Motorcycle_Share": "%",
    "Non_Motorized_Share": "%"
}

for year in [1977, 1987, 1997, 2007, 2017]:
    print(f"Processing year {year}...")

    # Get socio_eco DataFrame from memory
    socio = globals()[f"socio_eco_{year}"].copy()

    # Remove fully empty rows and limit to zone count
    socio = socio.dropna(how="all").head(zones_per_year[year]).reset_index(drop=True)

    # Base DataFrame with Zone 1..N
    df_params = pd.DataFrame({"Zone": range(1, zones_per_year[year] + 1)})

    # Area
    df_params["Area"] = socio["Area"]

    # Population
    if "Population" in socio.columns:
        df_params["Population"] = socio["Population"].values
    else:
        df_params["Population"] = None
        
    # Drop rows where Population == 0
    df_params = df_params[df_params["Population"] != 0].reset_index(drop=True)

    # Population density
    if "Population" in socio.columns and "Area" in socio.columns:
        df_params["Population_Density"] = socio["Population"] / socio["Area"]
    else:
        df_params["Population_Density"] = None

    # Income per capita
    if "Avg_Income" in socio.columns:
        df_params["Income_per_Capita"] = socio["Avg_Income"]
    else:
        df_params["Income_per_Capita"] = None

    # Jobs per km²
    if "Jobs" in socio.columns and "Area" in socio.columns:
        df_params["Jobs_per_km2"] = socio["Jobs"] / socio["Area"]
    else:
        df_params["Jobs_per_km2"] = None
        
    # Mobility
    mobility=globals()[f"mobility_{year}"].copy().dropna(how="all").head(zones_per_year[year]).reset_index(drop=True)
    if "Immobility" in mobility.columns:
        df_params["Immobility"] = mobility["Immobility"]
    else:
        df_params["Immobility"] = None

    # Motorization rate
    if "Car_Share" in socio.columns:
        df_params["Motorization_Rate"] = socio["Car_Share"]
    else:
        df_params["Motorization_Rate"] = None
    
    # Drop rows where Motorizatiuion == 0
    df_params = df_params[df_params["Motorization_Rate"] != 0].reset_index(drop=True)
        
    '''# Modal Split
    modal = globals()[f"modalsplit_{year}"].dropna(how="all").head(zones_per_year[year]).reset_index(drop=True)
    df_params["Metro"] = modal["Metro"]
    df_params["Train"] = modal["Train"]
    df_params["Bus"] = modal["Bus"]
    df_params["Car"] = modal["Car"]
    df_params["Motorcycle"] = modal["Motorcycle"]
    df_params["Non_Motorized"] = modal["Non_Motorized"]
    df_params["Metro_Share"] = modal["Metro_Share"]
    df_params["Train_Share"] = modal["Train_Share"]
    df_params["Bus_Share"] = modal["Bus_Share"]
    df_params["Car_Share"] = modal["Car_Share"]
    df_params["Motorcycle_Share"] = modal["Motorcycle_Share"]
    df_params["Non_Motorized_Share"] = modal["Non_Motorized_Share"]'''

    # Add units as second header row
    unit_row = [units.get(col, "") for col in df_params.columns]
    df_params.columns = pd.MultiIndex.from_tuples(zip(df_params.columns, unit_row))
    
    # Save result in memory, end of loop
    globals()[f"parameters_{year}"] = df_params.copy()
    print(f"Parameters_{year} created with {len(df_params)} zones")

print(">>> All parameter DataFrames created successfully <<<")
del socio
del mobility
del df_params
del zones_per_year
#del modal
del unit_row
del units
del year
# %% calculate CO2-emissions per zone with data from Travel duration, mode and emissionfactor

co2_factor = pd.DataFrame({
    'mode': ['Individual', 'Rail', 'Bus', 'Non-Motorized'],
    'factor': [110.0, 6.0, 75.0, 18.6]  # gCO2 per km alterar o fator de
})

# Mapping from Mode1_type to CO2 factor names
mode_map = {
    'Non_Motorized': 'Non-Motorized',
    'Non-motorized': 'Non-Motorized',
    'Rail': 'Rail',
    'Bus': 'Bus',
    'Car': 'Individual',
    'Individual': 'Individual'
}

# Function to calculate CO2 emissions per zone for a given year dataframe
def calc_co2_per_zone(df, year):
    df = df.copy()

    # Normalize mode names
    df['mode_clean'] = df['Mode1_type'].map(mode_map)

    # Merge emission factors
    df = df.merge(co2_factor, how='left', left_on='mode_clean', right_on='mode')

    # Ensure numeric values
    df['Expected_Distance'] = pd.to_numeric(df['Expected_Distance'], errors='coerce')
    df['Origin_Zone'] = pd.to_numeric(df['Origin_Zone'], errors='coerce')

    # Calculate CO2 emissions per row in grams
    df['CO2_g'] = df['Expected_Distance'] * df['factor']

    # Sum CO2 emissions by Origin_Zone
    co2_by_zone = df.groupby('Origin_Zone', as_index=False)['CO2_g'].sum()

    # Add CO2 in tonnes and teragrams
    co2_by_zone[f'CO2_t_{year}'] = co2_by_zone['CO2_g'] / 1_000_000           # tonnes
    co2_by_zone[f'CO2_Tg_{year}'] = co2_by_zone['CO2_g'] / 1_000_000_000_000  # teragrams

    # Rename CO2_g column for clarity
    co2_by_zone.rename(columns={'CO2_g': f'CO2_g_{year}'}, inplace=True)

    # Sort numerically by Origin_Zone
    co2_by_zone = co2_by_zone.sort_values(by='Origin_Zone').reset_index(drop=True)

    return co2_by_zone

# --- List of yearly dataframes ---
year_dfs = {
    1977: travel_dur_1977,
    1987: travel_dur_1987,
    1997: travel_dur_1997,
    2007: travel_dur_2007,
    2017: travel_dur_2017
}

# Calculate one dataframe per year
co2_yearly = {}
for year, df in year_dfs.items():
    co2_yearly[year] = calc_co2_per_zone(df, year)

# Access individual year results directly
co2_1977 = co2_yearly[1977]
co2_1987 = co2_yearly[1987]
co2_1997 = co2_yearly[1997]
co2_2007 = co2_yearly[2007]
co2_2017 = co2_yearly[2017]

# %% GAM Model

#make Dataframe for GAM for each year
years = [1977, 1987, 1997, 2007, 2017]

for year in years:
    params_df = globals()[f'parameters_{year}'].copy()
    co2_df = globals()[f'co2_{year}'].copy()
    
    # Flatten MultiIndex columns if they exist
    if isinstance(params_df.columns, pd.MultiIndex):
        params_df.columns = ['_'.join(map(str, col)).strip() for col in params_df.columns.values]
    if isinstance(co2_df.columns, pd.MultiIndex):
        co2_df.columns = ['_'.join(map(str, col)).strip() for col in co2_df.columns.values]
    
    # Rename 'Zone' to 'Zone_ID' for consistency
    if 'Zone' in params_df.columns:
        params_df.rename(columns={'Zone': 'Zone_ID'}, inplace=True)
    
    # CO2 dataframe: ensure the zone column is 'Origin_Zone'
    if 'Origin_Zone' not in co2_df.columns and 'Zone' in co2_df.columns:
        co2_df.rename(columns={'Zone': 'Origin_Zone'}, inplace=True)
    
    # Merge only if CO2 columns exist
    if any(col.startswith('CO2') for col in co2_df.columns):
        merged_df = pd.merge(params_df, co2_df, left_on='Zone_ID', right_on='Origin_Zone', how='inner')
        
        # Rename CO2 columns to uniform names
        for suffix in ['g','t','Tg']:
            col_name = f'CO2_{suffix}_{year}'
            if col_name in merged_df.columns:
                merged_df.rename(columns={col_name: f'CO2_{suffix}'}, inplace=True)
    else:
        merged_df = params_df  # no CO2 columns, just keep parameters
    
    # Store as GAM_parameters_YEAR
    globals()[f'GAM_parameters_{year}'] = merged_df

# Years with CO2 data
years_with_co2 = [2007, 2017]

# Store models
gam_models = {}

for year in years_with_co2:
    df_current = globals()[f'GAM_parameters_{year}'].copy()
    
    # Determine previous year to get lagged predictors
    if year == 2007:
        prev_year = 1997
    elif year == 2017:
        prev_year = 2007
    
    # Get previous year's dataframe for lagged socioeconomic data
    df_prev = globals()[f'GAM_parameters_{prev_year}'].copy()
    
    # Select relevant lagged columns
    lag_cols = [
        'Population_Density_persons/km²',
        'Income_per_Capita_US$/year',
        'Jobs_per_km2_jobs/km²',
        'Motorization_Rate_vehicles per 1000 citizen',
        'Immobility_%',
        'Population_persons'
    ]
    
    # Rename previous year columns
    df_prev = df_prev[['Zone_ID'] + lag_cols].rename(
        columns={col: f'{col}_prev' for col in lag_cols}
    )
    
    # Merge lagged values into current year
    df_current = df_current.merge(df_prev, on='Zone_ID', how='left')
    
    # Calculate population change
    df_current['Population_change'] = df_current['Population_persons'] - df_current['Population_persons_prev']
    
    # Define predictors and target
    predictors = [
        'Population_Density_persons/km²_prev',
        'Income_per_Capita_US$/year_prev',
        'Jobs_per_km2_jobs/km²_prev',
        'Motorization_Rate_vehicles per 1000 citizen_prev',
        'Immobility_%_prev',
        'Population_change'
    ]
    
    # Remove rows with missing predictors or target
    df_model = df_current.dropna(subset=predictors + ['CO2_Tg'])
    
    X = df_model[predictors].values
    y = df_model['CO2_Tg'].values
    
    # Fit GAM
    gam = LinearGAM(s(0) + s(1) + s(2) + s(3) + s(4) + s(5)).fit(X, y)
    
    gam_models[year] = gam
    globals()[f'GAM_models_{year}'] = gam
    print(f'GAM model fitted for {year}')

# %% Plots GAM Model
years_to_plot = [2007, 2017]

for year in years_to_plot:
    gam = gam_models[year]
    
    fig, axs = plt.subplots(2, 3, figsize=(18,10))
    fig.suptitle(f"Partial Dependence of Predictors on CO2, calculated for each Zone using GAM, Sao Paulo in Year {year}", fontsize=16, y=1.05)

    for i, ax in enumerate(axs.flatten()):
        # Generate grid for this term
        XX = gam.generate_X_grid(term=i)
        pd_values = gam.partial_dependence(term=i, X=XX)
        
        # Plot
        ax.plot(XX[:, i], pd_values, color='blue', lw=2)
        ax.set_xlabel(predictors[i], fontsize=12)
        ax.set_ylabel('Partial effect on CO2_Tg', fontsize=12)
        ax.set_title(f'Effect of {predictors[i]}', fontsize=14)
        ax.grid(True)
    
    plt.tight_layout()
    plt.show()


#2 in one
raw_cols = {
    'Population_Density_persons/km²': 'Population Density',
    'Income_per_Capita_US$/year': 'Income per Capita',
    'Jobs_per_km2_jobs/km²': 'Jobs per km²',
    'Motorization_Rate_vehicles per 1000 citizen': 'Motorization Rate',
    'Immobility_%': 'Immobility',
    'Population_persons': 'Population'
}

# --- TRECHO CORRIGIDO NO BLOCO "#2 in one" ---
#2 in one
raw_cols = {
    'Population_Density_persons/km²': 'Population Density',
    'Income_per_Capita_US$/year': 'Income per Capita',
    'Jobs_per_km2_jobs/km²': 'Jobs per km²',
    'Motorization_Rate_vehicles per 1000 citizen': 'Motorization Rate',
    'Immobility_%': 'Immobility',
    'Population_persons': 'Population'
}

num_predictors = len(predictors)
fig, axs = plt.subplots(num_predictors, 1, figsize=(10, 4*num_predictors))

for i, predictor in enumerate(predictors):
    ax = axs[i]
    
    for year, color in zip(years_to_plot, ['blue', 'red']):
        gam = gam_models[year]
        df_current = globals()[f'GAM_parameters_{year}'].copy()
        
        # Merge previous year's predictors for lagged values
        prev_year = 1997 if year == 2007 else 2007
        df_prev = globals()[f'GAM_parameters_{prev_year}'].copy()
        lag_cols = [
            'Population_Density_persons/km%',
            'Income_per_Capita_US$/year',
            'Jobs_per_km2_jobs/km%',
            'Motorization_Rate_vehicles per 1000 citizen',
            'Immobility_%',
            'Population_persons'
        ]
        # Ajuste fino para capturar variações de colunas com strings parciais
        lag_cols = [c for c in df_prev.columns if any(p in c for p in ['Population_Density', 'Income_per_Capita', 'Jobs_per_km2', 'Motorization_Rate', 'Immobility', 'Population']) and 'CO2' not in c and 'Zone' not in c]
        
        df_prev = df_prev[['Zone_ID'] + lag_cols].rename(columns={col: f'{col}_prev' for col in lag_cols})
        df_current = df_current.merge(df_prev, on='Zone_ID', how='left')
        
        # Encontra dinamicamente a coluna de população atual e anterior para a subtração
        pop_col_curr = [c for c in df_current.columns if 'Population' in c and '_prev' not in c and 'Density' not in c and 'change' not in c][0]
        pop_col_prev = [c for c in df_current.columns if 'Population' in c and '_prev' in c and 'Density' not in c][0]
        df_current['Population_change'] = df_current[pop_col_curr] - df_current[pop_col_prev]

        # Prepare X for GAM
        X = df_current[predictors].values
        XX = gam.generate_X_grid(term=i)
        pd_values = gam.partial_dependence(term=i, X=XX)
        
        # Plot partial dependence
        ax.plot(XX[:, i], pd_values*1e6, color=color, lw=2, label=f'{year}')
        
        # --- SOLUÇÃO ROBUSTA PARA EVITAR KEYERROR ---
        params_df = globals()[f'parameters_{year}'].copy()
        if isinstance(params_df.columns, pd.MultiIndex):
            params_df.columns = ['_'.join(map(str, col)).strip() for col in params_df.columns.values]
            
        if predictor in raw_cols or predictor.replace('_prev', '') in raw_cols or predictor == "Population_change":
            if predictor == "Population_change":
                # Busca dinâmica baseada em texto parcial
                col_name_list = [c for c in params_df.columns if 'Population' in c and 'Density' not in c]
            else:
                # Remove o '_prev' e limpa caracteres especiais para buscar por aproximação
                base_name = predictor.replace('_prev', '').split('_')[0] # Pega 'Population' ou 'Income', etc.
                col_name_list = [c for c in params_df.columns if base_name in c]
            
            if col_name_list:
                col_name = col_name_list[0]
                mean_val = params_df[col_name].mean()
                
                # vertical line with legend label
                ax.axvline(mean_val, color=color, linestyle='--', lw=1.5, 
                           label=f'{year} mean')
    
    ax.set_xlabel(predictor, fontsize=12)
    ax.set_ylabel('Partial effect on CO2 (tonnes)', fontsize=12)
    ax.set_title(f'Effect of {predictor} on CO2', fontsize=14)
    ax.grid(True)
    ax.legend()

plt.tight_layout()
plt.show()

# For 2007
gam_models[2007].summary()

# For 2017
gam_models[2017].summary()
# %% Plots Data

years = [1977, 1987, 1997, 2007, 2017]
colors = ['red', 'blue', 'green', 'orange', 'purple']

plt.figure(figsize=(8,5))

for year, color in zip(years, colors):
    df = globals()[f"parameters_{year}"].copy()
    
    # Flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(map(str, col)).strip() for col in df.columns.values]
    
    # Pick columns containing 'Zone' and 'Population'
    zone_col = [c for c in df.columns if 'Zone_ID' in c][0]
    pop_col = [c for c in df.columns if 'Population' in c][0]
    
    # Convert to numeric and drop missing
    zone = pd.to_numeric(df[zone_col], errors='coerce')
    pop = pd.to_numeric(df[pop_col], errors='coerce')
    mask = zone.notna() & pop.notna()
    zone, pop = zone[mask], pop[mask]
    
    plt.scatter(zone, pop, color=color, alpha=0.6, label=str(year), s=30)

plt.xlabel("Zone ID")
plt.ylabel("persons")
plt.title("Population per zone across years")
plt.legend(title="Year")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()
# %% Plots CO₂ per person vs Population Density across Years in São Paulo

years = [1977, 1987, 1997, 2007, 2017]
colors = ['red', 'blue', 'green', 'orange', 'purple']

plt.figure(figsize=(8, 5))

for year, color in zip(years, colors):
    parameters = globals()[f'parameters_{year}']
    
    # Flatten column names if needed
    parameters.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col 
                           for col in parameters.columns]
    
    # Extract population and density
    df_pop = parameters[['Zone_ID', 'Population_persons', 'Population_Density_persons/km²']].rename(
        columns={'Zone_ID':'Origin_Zone'}
    )
    
    # CO2 for this year
    df_co2 = globals()[f'co2_{year}'][['Origin_Zone', f'CO2_Tg_{year}']]
    
    # Merge
    df = pd.merge(df_pop, df_co2, on='Origin_Zone')
    
    # Calculate CO2 per person
    df['CO2_per_person'] = df[f'CO2_Tg_{year}'] / df['Population_persons'] * 1000000000
    
    # Filter meaningful points
    mask = (df['Population_Density_persons/km²'] > 0) & (df['CO2_per_person'] > 0)
    df_plot = df[mask]
    
    # Scatter plot
    plt.scatter(df_plot['Population_Density_persons/km²'], df_plot['CO2_per_person'], 
                color=color, label=str(year), alpha=0.7)

plt.xlabel('Population Density (persons/km²)')
plt.ylabel('CO₂ per Person and Zone (kg/person)')
plt.title('CO₂ per Person vs Population Density across Years in São Paulo')
plt.legend()
plt.grid(True)
plt.show()

#cumulativ
years = [2007, 2017]
colors = ['red', 'blue', 'green', 'orange', 'purple']

plt.figure(figsize=(8, 5))

for year, color in zip(years, colors):
    parameters = globals()[f'parameters_{year}']
    
    # Flatten column names if needed
    parameters.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col 
                           for col in parameters.columns]
    
    # Extract population and density
    df_pop = parameters[['Zone_ID', 'Population_persons', 'Population_Density_persons/km²']].rename(
        columns={'Zone_ID':'Origin_Zone'}
    )
    
    # CO2 for this year
    df_co2 = globals()[f'co2_{year}'][['Origin_Zone', f'CO2_Tg_{year}']]
    
    # Merge
    df = pd.merge(df_pop, df_co2, on='Origin_Zone')
    
    # Calculate CO2 per person
    df['CO2_per_person'] = df[f'CO2_Tg_{year}'] / df['Population_persons'] * 1e9
    
    # Filter meaningful points
    mask = (df['Population_Density_persons/km²'] > 0) & (df['CO2_per_person'] > 0)
    df_plot = df[mask].copy()
    
    # --- Scatter plot (original) ---
    plt.scatter(df_plot['Population_Density_persons/km²'], 
                df_plot['CO2_per_person'], 
                color=color, label=f'{year} (Data Density)', alpha=0.5)
    
    # --- Cumulative line ---
    df_plot = df_plot.sort_values('Population_Density_persons/km²')
    df_plot['Cumulative_CO2_per_person'] = df_plot['CO2_per_person'].cumsum()
    
    plt.plot(df_plot['Population_Density_persons/km²'], 
             df_plot['Cumulative_CO2_per_person'], 
             color=color, linestyle='-', linewidth=2, label=f'{year} (cumulative)')
        


plt.xlabel('Population Density (persons/km²)')
plt.ylabel('CO₂ per Person and Zone (kg/person)')
plt.title('CO₂ per Person Cumulative vs Population Density (incl. Data Density) in São Paulo')
plt.legend()
plt.grid(True)
plt.show()

# %% Plots CO₂ vs Population per Zone across Years in São Paulo

years = [ 2007, 2017]
#years = [2017]
colors = ['red', 'blue', 'green', 'orange', 'purple']

plt.figure(figsize=(8, 5))

for year, color in zip(years, colors):
    
    parameters =  globals()[f'parameters_{year}']
    
    parameters.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in parameters.columns]
    df_pop = parameters[['Zone_ID', 'Population_persons']].rename(columns={'Zone_ID':'Origin_Zone'})

    df_co2 = globals()[f'co2_{year}'][['Origin_Zone', f'CO2_Tg_{year}']]
    df = pd.merge(df_pop, df_co2, on='Origin_Zone')
    
    mask = (df['Population_persons'] > 0) & (df[f'CO2_Tg_{year}'] > 0)
    df_plot = df[mask]
    
    plt.scatter(df_plot['Population_persons'], df_plot[f'CO2_Tg_{year}'], 
                color=color, label=str(year), alpha=0.5)

plt.xlabel('Population (Persons per Zone)')
plt.ylabel('CO₂ (Tg) per Zone')
plt.title('CO₂ vs Population per Zone across Years in São Paulo')
plt.legend()
plt.grid(True)
plt.show()
# %% statistics - Correlation: Population Density vs CO₂ (Tg) by Year
years = [1977, 1987, 1997, 2007, 2017]

pearsons = []
spearmans = []
counts = []

for year in years:
    # Get parameters for this year and flatten columns if needed
    parameters = globals()[f'parameters_{year}'].copy()
    parameters.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col
                          for col in parameters.columns]
    
    # Extract population density + align zone id
    df_pop = parameters[['Zone_ID', 'Population_Density_persons/km²']].rename(
        columns={'Zone_ID': 'Origin_Zone'}
    )
    
    # CO2 Tg for this year
    df_co2 = globals()[f'co2_{year}'][['Origin_Zone', f'CO2_Tg_{year}']]
    
    # Merge
    df = pd.merge(df_pop, df_co2, on='Origin_Zone', how='inner')
    
    # Keep meaningful rows only
    xcol = 'Population_Density_persons/km²'
    ycol = f'CO2_Tg_{year}'
    df_clean = df[(df[xcol] > 0) & (df[ycol] > 0)].copy()
    
    # If too few points, set NaN correlations
    if len(df_clean) < 3:
        pearsons.append(np.nan)
        spearmans.append(np.nan)
        counts.append(len(df_clean))
        continue
    
    # Correlations via pandas (no SciPy needed)
    pear = df_clean[xcol].corr(df_clean[ycol], method='pearson')
    spear = df_clean[xcol].corr(df_clean[ycol], method='spearman')
    
    pearsons.append(pear)
    spearmans.append(spear)
    counts.append(len(df_clean))

# Show table
df_corr = pd.DataFrame({
    'Year': years,
    'N_pairs': counts,
    'Pearson': pearsons,
    'Spearman': spearmans
})
print("\nCorrelation between Population Density and CO₂ (Tg) by Year")
print(df_corr.to_string(index=False))

# Plot correlations (Matplotlib only)
plt.figure(figsize=(8, 5))
plt.plot(years, pearsons, marker='o', label='Pearson', color='r')
plt.plot(years, spearmans, marker='s', label='Spearman')
plt.axhline(0, linewidth=1)
plt.ylim(-1, 1)
plt.xlabel('Year')
plt.ylabel('Correlation')
plt.title('Correlation: Population Density vs CO₂ (Tg) per Zone by Year')
plt.grid(True)
plt.legend()
plt.xticks(years)
plt.tight_layout()
plt.show()
# %% statistics - Correlation Population per Zone vs CO₂ (Tg) by Year
years = [1977, 1987, 1997, 2007, 2017]

pearsons = []
spearmans = []
counts = []

for year in years:
    # Get parameters for this year and flatten columns if needed
    parameters = globals()[f'parameters_{year}'].copy()
    parameters.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col
                          for col in parameters.columns]
    
    # Extract population density + align zone id
    df_pop = parameters[['Zone_ID', 'Population_persons']].rename(
        columns={'Zone_ID': 'Origin_Zone'}
    )
    
    # CO2 Tg for this year
    df_co2 = globals()[f'co2_{year}'][['Origin_Zone', f'CO2_Tg_{year}']]
    
    # Merge
    df = pd.merge(df_pop, df_co2, on='Origin_Zone', how='inner')
    
    # Keep meaningful rows only
    xcol = 'Population_persons'
    ycol = f'CO2_Tg_{year}'
    df_clean = df[(df[xcol] > 0) & (df[ycol] > 0)].copy()
    
    # If too few points, set NaN correlations
    if len(df_clean) < 3:
        pearsons.append(np.nan)
        spearmans.append(np.nan)
        counts.append(len(df_clean))
        continue
    
    # Correlations via pandas (no SciPy needed)
    pear = df_clean[xcol].corr(df_clean[ycol], method='pearson')
    spear = df_clean[xcol].corr(df_clean[ycol], method='spearman')
    
    pearsons.append(pear)
    spearmans.append(spear)
    counts.append(len(df_clean))

# Show table
df_corr = pd.DataFrame({
    'Year': years,
    'N_pairs': counts,
    'Pearson': pearsons,
    'Spearman': spearmans
})
print("\nCorrelation between Population per Zone and CO₂ (Tg) by Year")
print(df_corr.to_string(index=False))

# Plot correlations (Matplotlib only)
plt.figure(figsize=(8, 5))
plt.plot(years, pearsons, marker='o', label='Pearson', color='r')
plt.plot(years, spearmans, marker='s', label='Spearman')
plt.axhline(0, linewidth=1)
plt.ylim(-1, 1)
plt.xlabel('Year')
plt.ylabel('Correlation')
plt.title('Correlation: Population per Zone vs CO₂ (Tg) per Zone by Year')
plt.grid(True)
plt.legend()
plt.xticks(years)

plt.tight_layout()
plt.show()
# %% statistics - Correlation Population Density (persons/km²) per Zone and CO₂ per Person by Year

years = [1977, 1987, 1997, 2007, 2017]

pearsons = []
spearmans = []
counts = []

for year in years:
    # Get parameters for this year and flatten columns if needed
    parameters = globals()[f'parameters_{year}'].copy()
    parameters.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col
                          for col in parameters.columns]
    
    # Extract population density + align zone id
    df_pop = parameters[['Zone_ID', 'Population_Density_persons/km²']].rename(
        columns={'Zone_ID': 'Origin_Zone'}
    )
    
    # CO2 Tg for this year
    df_co2 = globals()[f'co2_{year}'][['Origin_Zone', f'CO2_Tg_{year}']]
    
    # Merge
    df = pd.merge(df_pop, df_co2, on='Origin_Zone', how='inner')
    
    
    # Extract population and density
    df_pop = parameters[['Zone_ID', 'Population_persons', 'Population_Density_persons/km²']].rename(
        columns={'Zone_ID':'Origin_Zone'}
    )
    
    # CO2 for this year
    df_co2 = globals()[f'co2_{year}'][['Origin_Zone', f'CO2_Tg_{year}']]
    
    # Merge
    df = pd.merge(df_pop, df_co2, on='Origin_Zone')
    
    # Calculate CO2 per person
    df['CO2_per_person'] = df[f'CO2_Tg_{year}'] / df['Population_persons']
    
    
    
    # Keep meaningful rows only
    xcol = 'Population_Density_persons/km²'
    ycol = 'CO2_per_person'
    df_clean = df[(df[xcol] > 0) & (df[ycol] > 0)].copy()
    
    # If too few points, set NaN correlations
    if len(df_clean) < 3:
        pearsons.append(np.nan)
        spearmans.append(np.nan)
        counts.append(len(df_clean))
        continue
    
    # Correlations via pandas (no SciPy needed)
    pear = df_clean[xcol].corr(df_clean[ycol], method='pearson')
    spear = df_clean[xcol].corr(df_clean[ycol], method='spearman')
    
    pearsons.append(pear)
    spearmans.append(spear)
    counts.append(len(df_clean))


# Show table
df_corr = pd.DataFrame({
    'Year': years,
    'N_pairs': counts,
    'Pearson': pearsons,
    'Spearman': spearmans
})
print("\nCorrelation between Population Density (persons/km²) per Zone and CO₂ per Person by Year")
print(df_corr.to_string(index=False))

# Plot correlations (Matplotlib only)
plt.figure(figsize=(10, 6))
plt.plot(years, pearsons, marker='o', label='Pearson', color='r')
plt.plot(years, spearmans, marker='s', label='Spearman')
plt.axhline(0, linewidth=1)
plt.ylim(-1, 1)
plt.xlabel('Year')
plt.ylabel('Correlation')
plt.title('Correlation: Population Density (persons/km²) per Zone and CO₂ per Person and Zone by Year')
plt.grid(True)
plt.legend()
plt.xticks(years)
plt.tight_layout()
plt.show()
# %%Code end

total_co2 = co2_2017['CO2_t_2017'].sum()
total_co2_mio = total_co2 / 1000000
print("\nTotal CO2 2017:\n", total_co2_mio, "million tons:")

print("\n>>> Code finished sucessfully <<<")
