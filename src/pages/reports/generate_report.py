import dash
from dash import html, callback, Output, Input, State, ctx, dcc
from src.utils import data_loader
import pandas as pd
from urllib.parse import parse_qs

dash.register_page(__name__, path='/reports/generate-report')

def layout(report_type=None, institution_type=None, **kwargs):
	layout = html.Div([
		dcc.Location(id='generate-report-url'),
		html.Div(id='report-content'),
	], className="container")
	return layout

@callback(
	Output("generate-report-url", "href"),
	Input("user-selection-completed-store", "data"),
	Input("generate-report-url", "search"),
	State("report-type-store", "data"),
	State("institution-type-store", "data"),
)
def update_url(user_selection_completed, url_search, report_type, institution_type):
	query = parse_qs(url_search.lstrip('?'))
	start_page = len(query) == 0
	report_page = query.get('report_type', [None])[0]

	if start_page and user_selection_completed and not report_page:
		return f"/reports/generate-report?report-type={report_type}&institution-type={institution_type}"
	return dash.no_update

@callback(
	Output("report-content", "children"),
	Input("generate-report-url", "search"),
	Input("all-user-selection-store", "data"),
	State("output-structure-mapping-store", "data"),
	State("exposure-sector-product-mapping-store", "data"),
	State("scenario-mapping-store", "data"),
	State("report-type-store", "data"),
	prevent_initial_call=True
)
def generate_all_reports(url_search, all_stored_data, output_structure_mapping_dict, sector_sector_product_mapping_dict, scenario_mapping_dict, report_type):
	query = parse_qs(url_search.lstrip('?'))
	start_page = len(query) == 0
	report_page = query.get('report_type', [None])[0]

	if start_page:
		raise dash.exceptions.PreventUpdate

	# Initialise all dataframes
	all_user_selection_df = pd.DataFrame()
	for k, v in all_stored_data.items():
		user_selection_df = pd.DataFrame(all_stored_data[k])
		all_user_selection_df = pd.concat([all_user_selection_df, user_selection_df])

	scenario_mapping_df = pd.DataFrame(scenario_mapping_dict)
	exposure_sector_product_mapping_df = pd.DataFrame(sector_sector_product_mapping_dict)
	output_structure_mapping_df = pd.DataFrame(output_structure_mapping_dict)

	# Extract scenario list if any
	scenario_list = list(all_user_selection_df[all_user_selection_df['exposure'] == 'Scenario']['label'].unique())

	# Prepare output structure mapping
	sorted_output_structure_mapping_df = prepare_output_structure_mapping(output_structure_mapping_df, report_type)

	# Get user selection with sector and product yml file path
	user_selection_with_yml_file_path_df = get_sector_and_product_yml_file_path(
		all_user_selection_df, sorted_output_structure_mapping_df, exposure_sector_product_mapping_df
	)

	# Output structure
	output_structure_layout = []
	for section in sorted_output_structure_mapping_df['output_structure'].unique():
		section_layout = []
		section_mapping_df = sorted_output_structure_mapping_df[
			sorted_output_structure_mapping_df['output_structure'] == section
		]
		for sub_section in section_mapping_df['sub_section'].unique():
			sub_section_mapping_df = section_mapping_df[section_mapping_df['sub_section'] == sub_section]
			if sub_section == 'summary_input_table_flag':
				sub_section_layout = get_summary_input_table_layout(all_user_selection_df)
			elif sub_section == 'scenario_content_id':
				sub_section_layout = get_scenario_layout(sub_section_mapping_df, scenario_mapping_df, scenario_list)
			elif sub_section == 'sector_description_content_id':
				filtered_user_selection_with_yml_file_path_df = _filter_user_selection_by_section(
					user_selection_with_yml_file_path_df, section, sub_section
				)
				sub_section_layout = []
			elif sub_section == 'sector_scenario_content_id':
				filtered_user_selection_with_yml_file_path_df = _filter_user_selection_by_section(
					user_selection_with_yml_file_path_df, section, sub_section
				)
				sub_section_layout = get_sector_scenario_layout(
					filtered_user_selection_with_yml_file_path_df, scenario_mapping_df, scenario_list
				)
			elif sub_section == 'product_content_id':
				sub_section_layout = []
			else:
				sub_section_layout = []
			section_layout.append(sub_section_layout)
		section_layout = html.Div([
			html.H1(section, className='text-success fw-bold'),
		] + section_layout)
		output_structure_layout.append(section_layout)
	return html.Div(output_structure_layout)

def prepare_output_structure_mapping(output_structure_mapping_df, report_type):
	exploded_output_structure_mapping_df = output_structure_mapping_df.copy()
	exploded_output_structure_mapping_df['materiality'] = [
		['Low', 'Medium', 'High'] if x == 'All' else [x] for x in exploded_output_structure_mapping_df['materiality']
	]
	exploded_output_structure_mapping_df = exploded_output_structure_mapping_df.explode(['materiality'])
	exploded_output_structure_mapping_df['materiality'] = pd.Categorical(
		exploded_output_structure_mapping_df['materiality'],
		categories=['Low', 'Medium', 'High'],
		ordered=True
	)
	output_structure_order_df = exploded_output_structure_mapping_df[['report_type', 'output_structure', 'materiality']].drop_duplicates()

	melted_output_structure_mapping_df = pd.melt(
		exploded_output_structure_mapping_df,
		id_vars=['report_type', 'output_structure', 'materiality'],
		var_name='sub_section', value_name='content_id'
	)
	melted_output_structure_mapping_df = melted_output_structure_mapping_df[
		~(melted_output_structure_mapping_df['content_id'].isnull())
		& (melted_output_structure_mapping_df['report_type'] == report_type)
	]
	sorted_output_structure_mapping_df = pd.merge(
		output_structure_order_df, melted_output_structure_mapping_df,
		on=['report_type', 'output_structure', 'materiality'], how='left'
	)
	return sorted_output_structure_mapping_df

def get_sector_and_product_yml_file_path(all_user_selection_df, output_structure_mapping_df, exposure_sector_product_mapping_df):
	user_selection_df = all_user_selection_df[all_user_selection_df['exposure'] != 'Scenario'].copy()
	user_selection_df = user_selection_df.rename(columns={
		'report': 'report_type',
		'label': 'materiality',
		'ptype': 'type',
	})
	user_selection_df = user_selection_df.drop(columns=['id', 'value'])

	# Merge in exposure-sector-product mapping to get yml file
	sovereign_user_selection_df = user_selection_df[user_selection_df['exposure'] == 'Sovereign']
	sovereign_user_selection_with_mapping_df = pd.merge(
		sovereign_user_selection_df, exposure_sector_product_mapping_df.drop(columns=['institution', 'type']),
		on=['exposure', 'sector'], how='left'
	)
	other_user_selection_df = user_selection_df[user_selection_df['exposure'] != 'Sovereign']
	other_user_selection_with_mapping_df = pd.merge(
		other_user_selection_df, exposure_sector_product_mapping_df, on=['institution', 'exposure', 'sector', 'type'], how='left'
	)
	user_selection_with_mapping_df = pd.concat([sovereign_user_selection_with_mapping_df, other_user_selection_with_mapping_df])

	# Merge in output structure mapping to get content_id
	user_selection_with_mapping_df = pd.merge(
		user_selection_with_mapping_df, output_structure_mapping_df, on=['report_type', 'materiality'], how='left'
	)
	return user_selection_with_mapping_df

def get_summary_input_table_layout(all_user_selection_df):
	summary_input_table = all_user_selection_df.copy()
	summary_input_table = data_loader.rename_user_selection_data_columns(summary_input_table)
	summary_input_table_layout = html.Div([
		html.H2('Summary of inputs'),
		data_loader.create_data_table(summary_input_table)
	])
	return summary_input_table_layout

def get_scenario_layout(sub_section_mapping_df, scenario_mapping_df, scenario_list):
	section = sub_section_mapping_df['output_structure'].iloc[0]
	content_id = sub_section_mapping_df['content_id'].iloc[0]
	all_desc = []
	if len(scenario_list) == 0:
		scenario_layout = html.Div(className='d-none')
	else:
		for scenario in scenario_list:
			filtered_scenario_mapping_df = scenario_mapping_df[scenario_mapping_df['scenario_name'] == scenario]
			scenario_yml_file = filtered_scenario_mapping_df['scenario_yml_file'].iloc[0]
			scenario_yml = data_loader.load_yml_file('scenario', f'{scenario_yml_file}.yml')
			content_value = scenario_yml.get(content_id, "")
			desc_container = html.Div([
				dcc.Markdown(scenario, link_target="_blank", className='h3 fw-bolder'),
				dcc.Markdown(content_value, link_target="_blank", className='display-12', style={'textTransform': 'none'})
			], className='mb-3')
			all_desc.append(desc_container)

		if section == 'Executive Summary':
			header_layout = html.Div([
				html.H2(f'Summary of Scenario{data_loader.plural_add_s(len(scenario_list) > 0)}'),
				html.P(f'This report considers the following scenario'
					   f'{data_loader.plural_add_s(len(scenario_list) > 0)}:'),
			])
		else:
			header_layout = html.Div(className='d-none')

		scenario_layout = html.Div([
			header_layout,
			*all_desc
		])
	return scenario_layout

def get_sector_scenario_layout(user_selection_with_yml_file_path_df, scenario_mapping_df, scenario_list):
	section = user_selection_with_yml_file_path_df['output_structure'].iloc[0]

	# Split by materiality
	high_materiality_df = user_selection_with_yml_file_path_df[user_selection_with_yml_file_path_df['materiality'] == 'High'].copy()
	high_materiality_df = high_materiality_df[['sector_yml_file', 'content_id', 'materiality']].drop_duplicates()
	low_medium_materiality_df = user_selection_with_yml_file_path_df[user_selection_with_yml_file_path_df['materiality'].isin(['Low', 'Medium'])].copy()
	low_medium_materiality_df = low_medium_materiality_df[['sector_yml_file', 'content_id', 'materiality']].drop_duplicates()

	if len(scenario_list) == 0:
		sector_scenario_layout = html.Div(className='d-none')
	else:
		# High materiality section
		if len(high_materiality_df) == 0:
			high_materiality_layout = html.Div(className='d-none')
		else:
			high_materiality_sovereign_desc = []
			high_materiality_other_desc = []
			for sector_yml_file in high_materiality_df['sector_yml_file'].unique():
				sector_selection_df = high_materiality_df[high_materiality_df['sector_yml_file'] == sector_yml_file]
				sector_yml_file = sector_selection_df['sector_yml_file'].iloc[0]
				sector_yml = data_loader.load_yml_file('exposure_class', f'{sector_yml_file}.yml')
				sector_yml = next(iter(sector_yml.values()))
				content_id_list = list(sector_selection_df['content_id'].unique())
				scenario_desc = [
					html.Div([
						dcc.Markdown(scenario, link_target="_blank", className='h5 fw-bold'),
						*[
							dcc.Markdown(
								_filter_yml_by_scenario(sector_yml, scenario, scenario_mapping_df)[content_id],
								link_target="_blank", className='display-12', style={'textTransform': 'none'}
							) for content_id in content_id_list
						]
					]) for scenario in scenario_list
				]
				sector_name = sector_yml['name']
				sector_div = html.Div([
					dcc.Markdown(sector_name, link_target="_blank", className='h4 fw-bold'),
					*scenario_desc
				])
				if 'sovereign' in sector_name.lower():
					new_children = [dcc.Markdown(sector_name, link_target="_blank", className='h5 fw-bold')] + sector_div.children[1:]
					high_materiality_sovereign_desc.append(html.Div(new_children))
				else:
					high_materiality_other_desc.append(sector_div)
			high_materiality_layout = html.Div([
				html.H3('High materiality exposures') if section == 'Executive Summary' else html.Div([], className='d-none'),
				html.Div([
					html.H4('Sovereign', className='fw-bold'),
					*high_materiality_sovereign_desc
				]),
				*high_materiality_other_desc
			])

		# Low and Medium materiality section
		if len(low_medium_materiality_df) == 0:
			low_medium_materiality_layout = html.Div([], className='d-none')
		else:
			if section == 'Executive Summary':
				# Combine materiality
				groupby_variables_list = [x for x in low_medium_materiality_df if x != 'materiality']
				low_medium_materiality_df = low_medium_materiality_df.sort_values('materiality')
				low_medium_materiality_df = low_medium_materiality_df.groupby(
					groupby_variables_list, as_index=False).agg({'materiality': ', '.join})

				# Add scenarios
				low_medium_materiality_df['scenario'] = [scenario_list for x in low_medium_materiality_df['sector_yml_file']]
				low_medium_materiality_df = low_medium_materiality_df.explode('scenario')

				# Add sector yml
				low_medium_materiality_df['sector_yml'] = [
					next(iter(data_loader.load_yml_file('exposure_class', f'{sector_yml_file}.yml').values()))
					for sector_yml_file in low_medium_materiality_df['sector_yml_file']
				]
				low_medium_materiality_df['sector'] = [
					sector_yml['name'] for sector_yml in low_medium_materiality_df['sector_yml']
				]

				# Add description
				low_medium_materiality_df['description'] = [
					_filter_yml_by_scenario(sector_yml, scenario, scenario_mapping_df)[content_id]
					for sector_yml, scenario, content_id in low_medium_materiality_df[['sector_yml', 'scenario', 'content_id']].to_numpy()
				]

				# Create datatable
				low_medium_materiality_table = data_loader.rename_user_selection_data_columns(low_medium_materiality_df)
				low_medium_materiality_table = data_loader.create_data_table(low_medium_materiality_table)

				low_medium_materiality_layout = html.Div([
					html.H3('Other exposures'),
					html.Div(low_medium_materiality_table)
				])
			elif section == 'Sector Detail':
				low_medium_materiality_sovereign_desc = []
				low_medium_materiality_other_desc = []
				for sector_yml_file in low_medium_materiality_df['sector_yml_file'].unique():
					sector_selection_df = low_medium_materiality_df[low_medium_materiality_df['sector_yml_file'] == sector_yml_file]
					sector_yml_file = sector_selection_df['sector_yml_file'].iloc[0]
					sector_yml = data_loader.load_yml_file('exposure_class', f'{sector_yml_file}.yml')
					sector_yml = next(iter(sector_yml.values()))
					content_id = sector_selection_df['content_id'].iloc[0]
					scenario_desc = [
						html.Div([
							dcc.Markdown(scenario, link_target="_blank", className='h5 fw-bold'),
							dcc.Markdown(
								_filter_yml_by_scenario(sector_yml, scenario, scenario_mapping_df)[content_id],
								link_target="_blank", className='display-12', style={'textTransform': 'none'}
							)
						]) for scenario in scenario_list
					]
					sector_name = sector_yml['name']
					sector_div = html.Div([
						dcc.Markdown(sector_name, link_target="_blank", className='h4 fw-bold'),
						*scenario_desc
					])

					if 'sovereign' in sector_name.lower():
						new_children = [dcc.Markdown(sector_name, link_target="_blank", className='h5 fw-bold')] + sector_div.children[1:]
						low_medium_materiality_sovereign_desc.append(html.Div(new_children))
					else:
						low_medium_materiality_other_desc.append(sector_div)
				low_medium_materiality_layout = html.Div([
					*low_medium_materiality_other_desc,
					html.Div([
						html.H4('Sovereign', className='fw-bold'),
						*low_medium_materiality_sovereign_desc
					]),
				])
			else:
				low_medium_materiality_layout = html.Div(className='d-none')

		if section == 'Executive Summary':
			sector_scenario_layout = html.Div([
				html.H2(f'Summary of exposure{data_loader.plural_add_s(len(user_selection_with_yml_file_path_df) > 0)}'),
				html.P(f'This report considers the following exposure'
					   f'{data_loader.plural_add_s(len(user_selection_with_yml_file_path_df) > 0)}:'),
				high_materiality_layout,
				low_medium_materiality_layout
			])
		elif section == 'Sector Detail':
			sector_list = []
			other_desc = []
			for desc in high_materiality_other_desc:
				if hasattr(desc, 'children'):
					sector_name = desc.children[0].children
					sector_list.append(sector_name)
					other_desc.append(desc)

			for desc in low_medium_materiality_other_desc:
				if hasattr(desc, 'children'):
					sector_name = desc.children[0].children
					if sector_name not in sector_list:
						sector_list.append(sector_name)
						other_desc.append(desc)

			sector_scenario_layout = html.Div([
				*other_desc,
				html.H4('Sovereign', className='fw-bold'),
				*high_materiality_sovereign_desc,
				*low_medium_materiality_sovereign_desc,
			])
		else:
			sector_scenario_layout = html.Div(className='d-none')
	return sector_scenario_layout

# def get_sector_description_layout(user_selection_with_yml_file_path_df):
	
def _filter_yml_by_scenario(yml, scenario, scenario_mapping_df):
	filtered_scenario_mapping_df = scenario_mapping_df[scenario_mapping_df['scenario_name'] == scenario]
	scenario_risk_type = filtered_scenario_mapping_df['risk_type'].iloc[0]
	scenario_risk_level = filtered_scenario_mapping_df['risk_level'].iloc[0]
	return yml[scenario_risk_type][scenario_risk_level]

def _filter_user_selection_by_section(user_selection_df, section, sub_section):
	filtered_user_selection_df = user_selection_df[
		(user_selection_df['output_structure'] == section)
		& (user_selection_df['sub_section'] == sub_section)
	]
	return filtered_user_selection_df

# 	if report == 'institutional':
# 		mask = (
# 			(exposure_sector_product_mapping_df['institution'] == institution)
# 			& (exposure_sector_product_mapping_df['sector'] == sector)
# 			& (exposure_sector_product_mapping_df['sector'] == sector)
# 			& (exposure_sector_product_mapping_df['type'] == ptype)
# 		)
# 	elif report == 'sector':
# 		mask = (exposure_sector_product_mapping_df['sector'] == sector)
# 	else:
# 		mask = ()
#
# 	sector_mapping_df = exposure_sector_product_mapping_df[mask]
# 	sector_yml_file = sector_mapping_df['sector_yml_file'].iloc[0]
# 	sector_yml = data_loader.load_yml_file('sector_class', f'{sector_yml_file}.yml')
# 	product_yml_file = sector_mapping_df['product_yml_file'].iloc[0]
# 	product_yml = data_loader.load_yml_file('product', f'{product_yml_file}.yml')
#
# 	return sector_type, product
