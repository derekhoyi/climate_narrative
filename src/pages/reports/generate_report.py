import dash
from dash import html, callback, Output, Input, State, ctx, dcc
import dash_bootstrap_components as dbc
from src.utils import data_loader
import pandas as pd
from urllib.parse import parse_qs
import time

dash.register_page(__name__, path='/reports/generate-report')

def layout(report_type=None, institution_type=None, **kwargs):
	layout = html.Div([
		dcc.Location(id='generate-report-url'),
		html.Div(id='report-content'),
	], className="container")
	return layout

@callback(
	Output("generate-report-url", "href", allow_duplicate=True),
	Input("all-user-selection-store", "data"),
	Input("generate-report-url", "pathname"),
	State("generate-report-url", "search"),
	State("report-type-store", "data"),
	State("institution-type-store", "data"),
	prevent_initial_call=True
)
def update_url(all_stored_data, url_path, url_search, report_type, institution_type):
	query = parse_qs(url_search.lstrip('?'))
	start_page = len(query) == 0

	if start_page:
		return f"/reports/generate-report?report-type={report_type}&institution-type={institution_type}"
	return dash.no_update

@callback(
	Output("report-content", "children"),
	Input("all-user-selection-store", "data"),
	State("output-structure-mapping-store", "data"),
	State("exposure-product-mapping-store", "data"),
	State("scenario-mapping-store", "data"),
	State("report-type-store", "data"),
)
def generate_all_reports(all_stored_data, output_structure_mapping_dict, exposure_product_mapping_dict, scenario_mapping_dict, report_type):
	all_user_selection_df = pd.DataFrame()
	for k, v in all_stored_data.items():
		user_selection_df = pd.DataFrame(all_stored_data[k])
		all_user_selection_df = pd.concat([all_user_selection_df, user_selection_df])

	# Extract scenario list if any
	scenario_list = list(all_user_selection_df[all_user_selection_df['exposure'] == 'Scenario']['label'].unique())
	scenario_mapping_df = pd.DataFrame(scenario_mapping_dict)

	# Prepare output structure mapping
	output_structure_mapping_df = pd.DataFrame(output_structure_mapping_dict)
	output_structure_mapping_df = pd.melt(
		output_structure_mapping_df,
		id_vars=['report_type', 'output_structure', 'materiality'],
		var_name='section', value_name='content_id'
	)
	output_structure_mapping_df.dropna(subset=['content_id'], inplace=True)
	output_structure_mapping_df = output_structure_mapping_df.map(lambda x: x.lower() if isinstance(x, str) else x)
	output_structure_mapping_df = output_structure_mapping_df[output_structure_mapping_df['report_type'] == report_type]

	# Executive Summary
	executive_summary_mapping_df = output_structure_mapping_df[
		output_structure_mapping_df['output_structure'] == 'executive summary'
	]
	output_structure_layout = []
	for section in executive_summary_mapping_df['section'].unique():
		section_mapping_df = executive_summary_mapping_df[executive_summary_mapping_df['section'] == section]
		if section == 'summary_input_table_flag':
			summary_input_table_flag = True if section_mapping_df['content_id'].iloc[0] == 'Yes' else False
			if summary_input_table_flag:
				section_layout = html.Div([
					html.H2('Summary of inputs'),
					dbc.Table.from_dataframe(
						all_user_selection_df, striped=True, bordered=True, hover=True, responsive=True,
						className="border border-1 text-center align-middle w-auto",
						style={"minWidth": "100%", "tableLayout": "fixed", "overflow-x": "auto"}
					)
				])
			else:
				section_layout = html.Div([])
		elif section == 'scenario_content_id':
			scenario_content_id = section_mapping_df['content_id'].iloc[0]
			section_layout = html.Div([
				html.H2('Summary of Scenarios'),
				html.Div([get_scenario_content(scenario_mapping_df, scenario, scenario_content_id) for scenario in scenario_list])
			])
		elif section == 'exposure_scenario_content_id':
			section_layout = []
		else:
			section_layout = []
		output_structure_layout.append(section_layout)
	executive_summary_layout = html.Div([
		html.H1('Executive Summary', className='text-success fw-bold'),
	] + output_structure_layout)

	exposure_product_mapping_df = pd.DataFrame(exposure_product_mapping_dict)
	return executive_summary_layout

def get_scenario_content(scenario_mapping_df, scenario, content_id):
	scenario_mapping_df = scenario_mapping_df[scenario_mapping_df['scenario_name'] == scenario]
	scenario_yml_file = scenario_mapping_df['scenario_yml_file'].iloc[0]
	scenario_yml = data_loader.load_yml_file('scenario', f'{scenario_yml_file}.yml')
	desc_title = dcc.Markdown(scenario, link_target="_blank", className='h3 fw-bolder')
	desc_yml = dcc.Markdown(scenario_yml[content_id], link_target="_blank", className='display-12', style={'textTransform': 'none'})
	desc = html.Div([desc_title, desc_yml])
	return desc

# def get_exposure_information(exposure_product_mapping_df, report, institution, exposure, portfolio, ptype):
# 	if report == 'institutional':
# 		mask = (
# 			(exposure_product_mapping_df['institution'] == institution)
# 			& (exposure_product_mapping_df['exposure'] == exposure)
# 			& (exposure_product_mapping_df['portfolio'] == portfolio)
# 			& (exposure_product_mapping_df['type'] == ptype)
# 		)
# 	elif report == 'sector':
# 		mask = (exposure_product_mapping_df['portfolio'] == portfolio)
# 	else:
# 		mask = ()
#
# 	exposure_mapping_df = exposure_product_mapping_df[mask]
# 	exposure_yml_file = exposure_mapping_df['exposure_yml_file'].iloc[0]
# 	exposure_yml = data_loader.load_yml_file('exposure_class', f'{exposure_yml_file}.yml')
# 	product_yml_file = exposure_mapping_df['product_yml_file'].iloc[0]
# 	product_yml = data_loader.load_yml_file('product', f'{product_yml_file}.yml')
#
# 	return exposure_type, product
