import pandas as pd
from datetime import datetime
import json
from pathlib import Path
import yaml
from dash import dcc, dash_table, html
import dash_bootstrap_components as dbc

FILE_PATH = Path(__file__).parent.parent
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
	converted_json = {'sheets': {}}
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
		yml = yaml.load(f, Loader=getattr(yaml, 'CLoader', yaml.SafeLoader))
	return yml

def load_config_json_and_store():
	"""
	Load the configuration JSON file and return its contents as a dictionary and dcc.Store.
	"""
	config_json = convert_config_excel_to_json()

	# Create stores
	stores = [
		dcc.Store(id='report-section-index-store', storage_type='session', data=2),
		dcc.Store(id='report-type-store', storage_type='session'),
		dcc.Store(id='institution-type-store', storage_type='session'),
		dcc.Store(id='exposure-type-store', storage_type='session'),
		dcc.Store(id='all-user-selection-store', storage_type='session'),
		dcc.Store(id='user-selection-completed-store', storage_type='session', data=False),
		dcc.Store(id='trigger-error-store', storage_type='memory', data=False),
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

def get_user_selection_from_store(all_stored_data, report_type):
	all_user_selection_df = pd.DataFrame()
	for k, v in all_stored_data.items():
		user_selection_df = pd.DataFrame(all_stored_data[k])
		all_user_selection_df = pd.concat([all_user_selection_df, user_selection_df])

	if len(all_user_selection_df) == 0:
		all_user_selection_df = pd.DataFrame([], columns=[
			'report', 'id', 'institution', 'exposure', 'sector', 'ptype', 'label', 'value'
		])
	return all_user_selection_df

def rename_user_selection_data_columns(all_user_selection_df):
	output_df = all_user_selection_df.copy()
	columns_to_keep_and_rename_dict = {
		'institution': 'Institution Type',
		'exposure': 'Exposure',
		'sector': 'Sector',
		'product': 'Product',
		'ptype': 'Type',
		'type': 'Type',
		'label': 'Materiality / Scenario',
		'materiality': 'Materiality',
		'scenario': 'Scenario',
		'sector_group': 'Sector Group',
		'sector_scenario': 'Sector / Scenario',
		'description': 'Description'
	}
	columns_to_keep_and_rename_dict = {k: v for k, v in columns_to_keep_and_rename_dict.items() if k in output_df.columns}
	output_df = output_df[columns_to_keep_and_rename_dict.keys()]
	output_df = output_df.rename(columns=columns_to_keep_and_rename_dict)
	return output_df

def create_data_table(df, bullet_point_columns_list=None, left_align_columns_list=None):
	updated_columns_presentation_list = [
		{"name": col, "id": col, "presentation": "markdown" if col in bullet_point_columns_list else "input"}
		for col in df.columns
	] if bullet_point_columns_list else [{"name": i, "id": i} for i in df.columns]
	table_styling = {
		"textAlign": "center",
        "verticalAlign": "middle",
        "width": "auto",
        "whiteSpace": "normal",
        "wordWrap": "break-word"
    }
	left_aligned_styling = [{
        'if': {'column_id': c},
        'textAlign': 'left'
        } for c in left_align_columns_list
    ] if left_align_columns_list else []
	return html.Div([dash_table.DataTable(
        data=df.to_dict('records'),
        columns=updated_columns_presentation_list,
		style_data=table_styling,
		style_header=table_styling,
		style_data_conditional=left_aligned_styling
	)], className="table")

def plural_add_s(plural_flag):
	return "s" if plural_flag else ""

def create_error_flag(all_stored_data, report_type):
	all_user_selection_df = get_user_selection_from_store(all_stored_data, report_type)
	all_user_selection_df = all_user_selection_df[all_user_selection_df['label'] != 'N/A']
	if report_type == 'Scenario':
		error_flag = len(all_user_selection_df) == 0
	else:
		scenario_user_selection_df = all_user_selection_df[all_user_selection_df['exposure'] == 'Scenarios']
		exposure_user_selection_df = all_user_selection_df[all_user_selection_df['exposure'] != 'Scenarios']
		error_flag = len(scenario_user_selection_df) == 0 or len(exposure_user_selection_df) == 0
	return error_flag
