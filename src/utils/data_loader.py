import pandas as pd
from datetime import datetime
import json
from pathlib import Path
import yaml
from dash import dcc

FILE_PATH = Path(__file__).parent.parent.parent
CONFIG_PATH = FILE_PATH.joinpath("./assets/config").resolve()
PAGE_CONTENTS_PATH = FILE_PATH.joinpath("./assets/page_contents").resolve()


def clean_string(s):
    """
    Clean a string by stripping whitespace, converting to lowercase, replacing hyphens and spaces with underscores.
    """
    return s.strip().lower().replace('-', '_').replace(' ', '_')

def clean_df_columns(input_df):
    """
    Clean DataFrame column names.
    """
    output_df = input_df.copy()
    output_df.columns = [clean_string(col) for col in output_df.columns]
    return output_df

def convert_config_excel_to_json():
    """
    Convert an Excel file with multiple sheets to a versioned JSON file.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    input_file_path = CONFIG_PATH.joinpath('./config.xlsx').resolve()
    output_file_path = CONFIG_PATH.joinpath('./config.json').resolve()

    xls = pd.ExcelFile(input_file_path)
    converted_json = {'exported_at': timestamp, 'sheets': {}}
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(input_file_path, sheet_name=sheet_name)
        cleaned_df = clean_df_columns(df)
        converted_json['sheets'][clean_string(sheet_name)] = cleaned_df.to_dict(orient='records')

    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(converted_json, f, indent=2)
    return converted_json

def load_yml_file(yml_folder_path, yml_file_name):
    """
    Load a YAML file and return its contents as a dictionary.
    """
    yml_file_path = PAGE_CONTENTS_PATH.joinpath(yml_folder_path).joinpath(yml_file_name).resolve()
    with open(yml_file_path, encoding="utf-8") as f:
        yml = yaml.safe_load(f)
    return yml

def load_config_json_and_store():
    """
    Load the configuration JSON file and return its contents as a dictionary and dcc.Store.
    """
    config_json = convert_config_excel_to_json()

    # Create stores
    stores = [
        dcc.Store(id='report-type-store', storage_type='session'),
        dcc.Store(id='institution-type-store', storage_type='session'),
        dcc.Store(id='all-user-selection-store', storage_type='session'),
        dcc.Store(id='user-selection-completed-store', storage_type='session', data=False)
    ] + [
        dcc.Store(
            id=f'{sheet_name.replace("_", "-")}-store',
            data=sheet_data,
            storage_type='session',
        ) for sheet_name, sheet_data in config_json['sheets'].items()
    ]
    return config_json, stores

def get_selected_institution_type_mapping(exposure_product_mapping_dict, institution_type):
    exposure_product_mapping_df = pd.DataFrame(exposure_product_mapping_dict)
    exposure_product_mapping_df = exposure_product_mapping_df[exposure_product_mapping_df['institution'].isin([institution_type, 'All'])]
    return exposure_product_mapping_df

def get_user_selection_from_store(all_stored_data):
    all_user_selection_df = pd.DataFrame()
    for k, v in all_stored_data.items():
        user_selection_df = pd.DataFrame(all_stored_data[k])
        all_user_selection_df = pd.concat([all_user_selection_df, user_selection_df])
    return all_user_selection_df
