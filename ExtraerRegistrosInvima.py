import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from gspread_dataframe import set_with_dataframe
import pdfplumber
import pandas as pd
import os
import re
from regex_patterns import (
    get_active_patterns, 
    enable_pattern, 
    disable_pattern, 
    disable_all_patterns,
    get_pattern_status
)

def Process_Registros_INVIMA(folder_path):
    # Configure patterns before processing
    print("Current pattern status:")
    get_pattern_status()
    
    # Allow user to configure patterns
    print("\nDisabling all patterns by default...")
    disable_all_patterns()
    
    print("\nEnter pattern names to enable (separated by commas), or 'all' for all patterns:")
    pattern_input = input().strip()
    
    if pattern_input.lower() == 'all':
        enable_all_patterns()
    else:
        patterns_to_enable = [p.strip() for p in pattern_input.split(',')]
        for pattern_name in patterns_to_enable:
            enable_pattern(pattern_name)
    
    print("\nProcessing with enabled patterns:")
    get_pattern_status()

    all_data = []

    # Iterate through each file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            
            try:
                with pdfplumber.open(file_path) as pdf:
                    # Assuming it's a one-page PDF
                    for page in pdf.pages:
                        tables = page.extract_tables()
                        
                        if not tables:
                            continue
                        
                        dataframes = [pd.DataFrame(table) for table in tables]

                        # Initialize empty DataFrames
                        Datos_producto = pd.DataFrame()
                        Datos_de_interés = pd.DataFrame()
                        Presentaciones_comerciales = pd.DataFrame()
                        Roles_por_producto = pd.DataFrame()

                        # Process Table 1
                        for df in dataframes:
                            if df.isin(['Expediente\nSanitario']).any().any():
                                table_one = pd.melt(df, var_name='Variable', value_name='Value')
                                table_one['Headers'] = table_one.apply(lambda row: row['Value'] if row['Variable'] in [0, 3, 5, 7] else None, axis=1)
                                table_one['Row_values'] = table_one.apply(lambda row: row['Value'] if row['Variable'] in [1, 2, 4, 6, 8] else None, axis=1)
                                table_one = table_one.drop(columns=['Variable', 'Value'])
                                data_headers = table_one['Headers'].dropna().tolist()
                                data_values = table_one['Row_values'].dropna().tolist()
                                if data_values:
                                    element = data_values.pop(0)
                                    data_values.insert(3, element)
                                Datos_producto = pd.DataFrame({'Variable': data_headers, 'Valor': data_values})
                                break

                        # Process Table 2
                        for df in dataframes:
                            if df.isin(['Vida Util']).any().any():
                                if df.shape[1] >= 4:
                                    new_column_1_3 = pd.concat([df[0], df[2]]).reset_index(drop=True)
                                    new_column_2_4 = pd.concat([df[1], df[3]]).reset_index(drop=True)
                                    Datos_de_interés = pd.DataFrame({'Variable': new_column_1_3, 'Valor': new_column_2_4})
                                break

                        # Process Table 3
                        for df in dataframes:
                            if df.isin(['Presentacion Comercial']).any().any():
                                df = df.drop(0).reset_index(drop=True)
                                concatenated_values = ' '.join(df.iloc[:, 0].dropna().astype(str).tolist())
                                Presentaciones_comerciales = pd.DataFrame({'Variable': ['Presentación Comercial'], 'Valor': [concatenated_values]})
                                break

                        # Process Table 4
                        for df in dataframes:
                            if df.isin(['FABRICANTE']).any().any():
                                if df.shape[1] >= 2:
                                    df = df.drop(index=0)
                                    df = df.drop(df.columns[2:7], axis=1)
                                    df = df.rename(columns={0: 'Variable', 1: 'Valor'})
                                    df = df.groupby('Variable', as_index=False).agg({'Valor': ' '.join})
                                    Roles_por_producto = df
                                break

                        # Concatenate all transformed tables
                        Registros_INVIMA = pd.concat([Datos_producto, Datos_de_interés, Presentaciones_comerciales, Roles_por_producto]).reset_index(drop=True)
                        all_data.append(Registros_INVIMA)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    return pd.concat(all_data).reset_index(drop=True) if all_data else pd.DataFrame()

# Example usage
folder_path = input("Please enter the folder path: ")
df = Process_Registros_INVIMA(folder_path)


def transform_df(df):
    """
    Transforms a DataFrame with 'Key' and 'Value' columns into a DataFrame with
    unique 'Key' values as headers and corresponding 'Value' entries.

    Args:
        df: Input DataFrame with 'Key' and 'Value' columns.

    Returns:
        Transformed DataFrame.
    """

    unique_keys = df['Variable'].unique()
    transformed_data = {}

    for key in unique_keys:
        transformed_data[key] = df[df['Variable'] == key]['Valor'].tolist()

    # Find the maximum length of lists to pad shorter lists with None
    max_length = max(len(v) for v in transformed_data.values())

    # Pad shorter lists with None
    for key in transformed_data:
        transformed_data[key] += [None] * (max_length - len(transformed_data[key]))

    transformed_df = pd.DataFrame(transformed_data)
    return transformed_df
transformed_df = transform_df(df)

for i in transformed_df['Observaciones']:
    text = i.strip()
    # re.sub(r'\W+', '', text)
    print(text)
    print(len(text))

text = i
patterns = list(get_active_patterns().values())
referencias = []
for pattern in patterns:
    matches = re.findall(pattern, text)
    for match in matches:
        referencias.append(match)

cleaned_list = []
for r in referencias:
    cleaned_string = r.replace('\n', '')
    cleaned_list.append(cleaned_string)

# Extend the DataFrame by repeating the first row
extended_df = pd.concat([transformed_df] * len(referencias), ignore_index=True)
# Add the new column to the extended DataFrame
extended_df.insert(3, "Referencias", cleaned_list)

extended_df['Descripcion'] = (
    'PRODUCTO: ' + extended_df.get('Nombre\nproducto', '') +
    '; REFERENCIA: ' + extended_df.get('Referencias', '') +
    '; REGISTRO SANITARIO: ' + extended_df.get('Registro\nSanitario', '') +
    '; VIGENCIA: ' + extended_df.get('Vencimiento', '') +
    '; EXPEDIENTE: ' + extended_df.get('Expediente\nSanitario', '') +
    '; FABRICANTE: ' + extended_df.get('FABRICANTE', '') +
    '; PAIS DE ORIGEN: ' + 'INSERTAR AQUI' +
    '; MARCA: ' + extended_df.get('Marcas', '') +
    '; PRESENTACIONES COMERCIALES: ' + extended_df.get('Presentación Comercial', '') +
    '; VIDA UTIL: ' + extended_df.get('Vida Util', '') +
    '; USO ESPECIFICO: ' + extended_df.get('Usos', '') +
    '; MERCANCIA NUEVA: ' + 'INSERTAR AQUI' +
    '; MES Y AÑO DE FABRICACION: ' + 'INSERTAR AQUI' + '.'
)

# Remove unwanted characters and make changes permanent
extended_df['Descripcion'] = extended_df['Descripcion'].apply(lambda x: x.strip().replace('\n', ''))

# Load your credentials
gc = gspread.service_account(filename="C:\\Users\\eabeltranm\\Documents\\Code\\Python_PDF_scripts\\gen-lang-client-0469262768-6cc744827056.json")
# Open the Google Sheet
sh = gc.open('Nuevo_Projecto')
# Name of the new sheet
new_sheet_name = 'exmaple_sheet_1'
# Create a new sheet
worksheet = sh.add_worksheet(title=new_sheet_name, rows="200", cols="50")
# Create a sample DataFrame
# Write the DataFrame to the Google Sheet
set_with_dataframe(worksheet, extended_df)