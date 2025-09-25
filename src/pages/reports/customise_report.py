import dash
from dash import html, callback, Output, Input, State, ctx, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from urllib.parse import parse_qs
import pandas as pd
import numpy as np
from utils import data_loader

dash.register_page(__name__, path='/reports/customise-report')
value_bg_color_mapping = {
	"N/A": "white",
	"Low": "#BFEBCE",
	"Medium": "#61CD85",
	"High": "#00B050"
}

def layout(report_type=None, institution_type=None, **kwargs):
	# page layout
	layout = html.Div([
		dcc.Location(id="customise-report-url"),
		# Creating placeholder divs for generate_report
		html.Div([
			html.Div(id='generate-report-url'),
			html.Div(id='generate-report-previous-btn'),
			html.Div(id='report-sidebar'),
			html.Div(id='report-content'),
			], className="d-none"
		),
		html.H2(f'{kwargs['report-type']} Report'),
		html.Div(id="institution-type-radio"),
		html.Div(id="stepper-content", children=[html.Div(id="stepper")]),
		html.Div(id="selection-content"),
		html.Div(id="no-customisation-error-message"),
		html.Div(id="review-summary-content"),
		html.Div(id="report-navigation-buttons", children=[
			html.Div(id="report-restart-btn"),
			html.Div(id="report-previous-btn"),
			html.Div(id="report-next-btn"),
			html.Div(id="report-generate-btn"),
		]),
	], className="mx-auto py-3 container")
	return layout

@callback(
	Output("customise-report-url", "href", allow_duplicate=True),
	Input('user-selection-completed-store', 'data'),
	Input("report-previous-btn", "n_clicks"),
	Input("report-next-btn", "n_clicks"),
	Input("report-restart-btn", "n_clicks"),
	Input("report-generate-btn", "n_clicks"),
	State("report-type-store", "data"),
	State("institution-type-store", "data"),
	State("customise-report-url", "search"),
	State("all-user-selection-store", "data"),
	prevent_initial_call=True
)
def update_url(user_selection_completed, back, _next, restart, generate_report, report_type, institution_type,
			   url_search, all_stored_data):
	query = parse_qs(url_search.lstrip('?'))
	institutional_start_page = report_type == 'Institutional' and len(query) == 1
	institution_type = query.get("institution-type", [None])[0] if institution_type is None else institution_type
	review_summary = query.get("review", [None])[0]
	triggered_id = ctx.triggered_id
	error_flag = data_loader.create_error_flag(all_stored_data, report_type)

	if institutional_start_page or (review_summary and back) or (generate_report and error_flag):
		user_selection_completed = None

	if generate_report and error_flag:
		raise dash.exceptions.PreventUpdate

	if report_type == 'Institutional':
		if (institutional_start_page and _next and not user_selection_completed) or (review_summary and back) or (generate_report and error_flag):
			return f"/reports/customise-report?report-type={report_type}&institution-type={institution_type}"
		elif institutional_start_page and restart:
			return f"/reports"
		elif not institutional_start_page and restart:
			return f"/reports/customise-report?report-type={report_type}"
		elif user_selection_completed and not review_summary:
			return f"/reports/customise-report?report-type={report_type}&institution-type={institution_type}&review=summary"
		elif generate_report and all_stored_data:
			return f"/reports/generate-report"
		else:
			raise dash.exceptions.PreventUpdate
	else:
		if ((triggered_id == "report-previous-btn" and back and review_summary)
				or (triggered_id == "report-generate-btn" and generate_report and error_flag)):
			return f"/reports/customise-report?report-type={report_type}"
		elif triggered_id == "report-restart-btn" and restart:
			return "/reports"
		elif user_selection_completed and not review_summary:
			return f"/reports/customise-report?report-type={report_type}&review=summary"
		elif triggered_id == "report-generate-btn" and generate_report and all_stored_data:
			return "/reports/generate-report"
		else:
			raise dash.exceptions.PreventUpdate

@callback(
	Output("institution-type-radio", "children"),
	Input("exposure-sector-product-mapping-store", "data"),
	State("customise-report-url", "search"),
)
def institution_type_radio(exposure_sector_product_mapping_dict, url_search):
	query = parse_qs(url_search.lstrip('?'))
	report_type = query.get("report-type", [None])[0]
	institutional_start_page = report_type == 'Institutional' and len(query) == 1

	if institutional_start_page:
		exposure_sector_product_mapping_df = pd.DataFrame(exposure_sector_product_mapping_dict)
		unique_institution_types = [x for x in exposure_sector_product_mapping_df['institution'].unique() if x.upper() != 'ALL']
		institution_selection = html.Div([
			dbc.Label("Select one type of institution: "),
			dbc.RadioItems(
				options=[{"label": x, "value": x} for x in unique_institution_types],
				value=unique_institution_types[0] if unique_institution_types else None,
				id="institution-type-value",
				persistence=True,
				persistence_type='memory'
			),
		])
	else:
		institution_selection = html.Div(className='d-none')
	return institution_selection

@callback(
	Output("institution-type-store", "data"),
	Input("institution-type-value", "value"),
	prevent_initial_call=True
)
def store_institution_type(value):
	return value

@callback(
	Output("stepper-content", "children"),
	Output("exposure-type-store", "data", allow_duplicate=True),
	Input("customise-report-url", "search"),
	State("exposure-sector-product-mapping-store", "data"),
	State('user-selection-completed-store', 'data'),
	prevent_initial_call=True
)
def initiate_stepper(url_search, exposure_sector_product_mapping_dict, user_selection_completed):
	query = parse_qs(url_search.lstrip('?'))
	report_type = query.get("report-type", [None])[0]
	institution_type = query.get("institution-type", [None])[0]
	institutional_start_page = report_type == 'Institutional' and len(query) == 1

	# Only run this callback if not on start page
	if institutional_start_page or user_selection_completed:
		raise dash.exceptions.PreventUpdate

	# stepper children
	stepper_children_styling = {"minWidth": "180px", "maxWidth": "220px", "overflow": "auto"}
	if report_type == 'Institutional':
		exposure_sector_product_mapping_df = data_loader.get_selected_institution_type_mapping(
			exposure_sector_product_mapping_dict, institution_type
		)
		exposures = exposure_sector_product_mapping_df['exposure'].unique()
		exposure_type = exposures[0] if len(exposures) > 0 else None
		stepper_children = [
			dmc.StepperStep(label=f"Step {i + 1}", description=f"{exposure}", style=stepper_children_styling)
			for i, exposure in enumerate(exposures)
		] + [
			dmc.StepperStep(label=f"Step {len(exposures) + 1}", description=f"Scenarios", style=stepper_children_styling)
		]
	elif report_type == 'Sector':
		stepper_children = [
			dmc.StepperStep(label="Step 1", description="Sectors", style=stepper_children_styling),
			dmc.StepperStep(label="Step 2", description="Scenarios", style=stepper_children_styling),
		]
		exposure_type = 'Sectors'
	elif report_type == 'Scenario':
		stepper_children = [dmc.StepperStep(label="Step 1", description="Scenarios", style=stepper_children_styling)]
		exposure_type = 'Scenarios'
	else:
		stepper_children = []
		exposure_type = None

	# stepper
	stepper = html.Div([dmc.MantineProvider(html.Div([
		dmc.Stepper(
			id="stepper",
			active=0,
			color="green",
			children=stepper_children + [dmc.StepperCompleted()],
			className="m-0 p-2 pt-4 g-4 align-items-stretch"
		)], className="rounded-4 p-3 border border-1 border-gray-4"
	)), html.Br()])
	return stepper, exposure_type

@callback(
	Output("stepper", "active", allow_duplicate=True),
	Output("exposure-type-store", "data", allow_duplicate=True),
	Input("exposure-sector-product-mapping-store", "data"),
	Input("report-previous-btn", "n_clicks"),
	Input("report-next-btn", "n_clicks"),
	State('user-selection-completed-store', 'data'),
	Input("stepper", "active"),
	State("stepper", "children"),
	State("customise-report-url", "search"),
	prevent_initial_call=True
)
def update_stepper(exposure_sector_product_mapping_dict, back, _next, user_selection_completed, stepper_active, stepper_children, url_search):
	query = parse_qs(url_search.lstrip('?'))
	report_type = query.get("report-type", [None])[0]
	institutional_start_page = report_type == 'Institutional' and len(query) == 1

	# Only run this callback if not on start page
	if institutional_start_page or user_selection_completed:
		raise dash.exceptions.PreventUpdate

	# Get max_step (according to python indexing convention)
	max_step = len(stepper_children) - 2 if stepper_children else 0

	# Initialize current step
	stepper_active = stepper_active or 0
	button_id = ctx.triggered_id
	step = stepper_active

	# Update step based on button clicked or direct stepper click
	if button_id == "report-previous-btn" and back:
		step = step - 1 if step > 0 else step
	elif button_id == "report-next-btn" and _next:
		step = step + 1 if step < max_step else step
	elif button_id == "stepper":
		step = stepper_active

	# Get exposure type for current step
	exposure_type = stepper_children[step]['props']['description'] if stepper_children else None
	return step, exposure_type

@callback(
	Output("exposure-selection-dropdown", "children"),
	Input("exposure-sector-product-mapping-store", "data"),
	Input("exposure-type-store", "data"),
	Input('user-selection-completed-store', 'data'),
	Input("all-user-selection-store", "data"),
	Input("customise-report-url", "search"),
)
def initiate_exposure_selection_dropdown(exposure_sector_product_mapping_dict, exposure_type, user_selection_completed, stored_data, url_search):
	query = parse_qs(url_search.lstrip('?'))
	report_type = query.get("report-type", [None])[0]
	institution_type = query.get("institution-type", [None])[0]
	institutional_start_page = report_type == 'Institutional' and len(query) == 1

	# Only run this callback if not on start page
	if exposure_type == "Scenarios" or report_type != 'Institutional' or institutional_start_page or user_selection_completed:
		raise dash.exceptions.PreventUpdate

	stored_data = stored_data or {}
	filtered_stored_data = stored_data.get(exposure_type, [])

	exposure_sector_product_mapping_df = data_loader.get_selected_institution_type_mapping(exposure_sector_product_mapping_dict, institution_type)
	exposure_sector_product_mapping_df = exposure_sector_product_mapping_df[exposure_sector_product_mapping_df['exposure'] == exposure_type]
	sectors = exposure_sector_product_mapping_df['sector'].unique()
	ptypes = exposure_sector_product_mapping_df['type'].unique()
	combinations_to_keep_list = [(p, t) for p, t in exposure_sector_product_mapping_df[['sector', 'type']].drop_duplicates().values]

	table_styling = {
		"margin": 8, "padding": 8, "align-items": "center", "verticalAlign": "middle", "width": "100%", "height": "100%",
		"minWidth": 150, "maxWidth": 200,
	}
	header = html.Tr(
		[html.Th("Type", style=table_styling | {"maxWidth": 300})] +
		[html.Th(t, style=table_styling | {"textAlign": "center"}) for t in ptypes]
	)
	rows = []
	for s in sectors:
		row = [html.Td(s, style=table_styling)]
		for t in ptypes:
			options_list = [{"label": l, "value": f"{institution_type}|{exposure_type}|{s}|{t}|{l}"} for l in
							value_bg_color_mapping.keys()]
			default_items = [x for x in filtered_stored_data if x['sector'] == s and x['ptype'] == t]
			default_value = default_items[0]['value'] if default_items else options_list[0]['value']
			background_color = value_bg_color_mapping.get(default_value.split('|')[-1], "white")
			row.append(html.Td(
				dcc.Dropdown(
					options=options_list,
					value=default_value,
					id={"type": 'exposure-selection-store', "exposure": exposure_type, "sector": s, "ptype": t},
					clearable=False,
					style=({'visibility': 'hidden', "opacity": 0} if (s, t) not in combinations_to_keep_list else {})
						  | {"background-color": background_color},
				),
				style=table_styling | {"textAlign": "center"}
			))
		rows.append(html.Tr(row))
	return html.Div(
		html.Table([html.Thead(header)] + [html.Tbody(rows)], className="table",
		style={"width": "100%", "tableLayout": "fixed", "overflow-x": "auto"})
	)

@callback(
	Output({"type": "exposure-selection-store", "exposure": dash.ALL, "sector": dash.ALL, "ptype": dash.ALL}, "style"),
	State('user-selection-completed-store', 'data'),
	Input({"type": "exposure-selection-store", "exposure": dash.ALL, "sector": dash.ALL, "ptype": dash.ALL}, "value"),
	State({"type": "exposure-selection-store", "exposure": dash.ALL, "sector": dash.ALL, "ptype": dash.ALL}, "style"),
	State("customise-report-url", "search"),
	State("exposure-type-store", "data"),
	prevent_initial_call=True
)
def update_dropdown_color(user_selection_completed, values, current_styles, url_search, exposure_type):
	query = parse_qs(url_search.lstrip('?'))
	report_type = query.get("report-type", [None])[0]
	institutional_start_page = report_type == 'Institutional' and len(query) == 1

	# Only run this callback if not on start page
	if exposure_type == "Scenarios" or report_type != 'Institutional' or institutional_start_page or user_selection_completed:
		raise dash.exceptions.PreventUpdate

	# Merge color with existing style
	updated_style = [
		{**{k: v for k, v in current_styles[idx].items() if k != "background-color"},
		 "background-color": value_bg_color_mapping.get(val.split('|')[-1], "white")}
		for idx, val in enumerate(values)
	]
	return updated_style

@callback(
	Output("sector-selection-checklist", "children"),
	Input("exposure-sector-product-mapping-store", "data"),
	Input("exposure-type-store", "data"),
	State('user-selection-completed-store', 'data'),
	State("customise-report-url", "search"),
	State("all-user-selection-store", "data")
)
def initiate_sectors_checklist(exposure_sector_product_mapping_dict, exposure_type, user_selection_completed, url_search, stored_data):
	query = parse_qs(url_search.lstrip('?'))
	report_type = query.get("report-type", [None])[0]

	# Only run this callback if not on start page
	if exposure_type != "Sectors" or report_type != 'Sector' or user_selection_completed:
		raise dash.exceptions.PreventUpdate

	if exposure_type == "Sectors":
		stored_data = stored_data or {}
		filtered_stored_data = stored_data.get("Sectors", [])

		exposure_sector_product_mapping_df = pd.DataFrame(exposure_sector_product_mapping_dict)
		exposure_sector_product_mapping_df['sector'] = [
			next(iter(data_loader.load_yml_file('exposure_class', f'{sector_yml_file}.yml').values()))['name']
			for sector_yml_file in exposure_sector_product_mapping_df['sector_yml_file']
		]
		exposure_sector_product_mapping_df['sector_group'] = exposure_sector_product_mapping_df['sector_yml_file'].str.split('/', expand=True)[0]
		conditions_list = [
			exposure_sector_product_mapping_df['sector_group'] == 'sector',
			exposure_sector_product_mapping_df['sector_group'] == 'underwriting',
			exposure_sector_product_mapping_df['sector_group'] == 'sovereigns'
		]
		choices_list = ['Sectors', 'Underwriting Classes', 'Sovereigns']
		exposure_sector_product_mapping_df['sector_group'] = np.select(conditions_list, choices_list, default='Other')
		exposure_sector_product_mapping_df['sector_group'] = pd.Categorical(
			exposure_sector_product_mapping_df['sector_group'], categories=choices_list, ordered=True
		)
		unique_sector_groups_and_sectors_df = exposure_sector_product_mapping_df[['sector_group', 'sector']].drop_duplicates()

		sectors_selection_checklists = []
		for sector_group in unique_sector_groups_and_sectors_df['sector_group'].unique():
			sectors_df = unique_sector_groups_and_sectors_df[unique_sector_groups_and_sectors_df['sector_group'] == sector_group]
			sectors_selection_checklists.append(
				dbc.Col(
					html.Div([
						html.P(sector_group, className='fw-bold'),
						dbc.Checklist(
							options=[{"label": x, "value": f'{sector_group}|{x}'} for x in sectors_df['sector'].unique()],
							value=[x['value'] for x in filtered_stored_data if x['value'].split('|')[0] == sector_group],
							id={"type": 'sector-selection-store', "sector_group": sector_group},
							persistence=True,
							persistence_type='memory'
						)
					])
				)
			)

		sectors_selection_layout = html.Div([
			dbc.Label("Select the sectors applicable: "),
			html.Br(),
			html.Div(dbc.Row(sectors_selection_checklists)),
			html.Br(),
			dbc.ButtonGroup([
				dbc.Button(
					"Select All",
					id="sector-selection-select-all",
					color="success",
					outline=True,
					className="flex-fill"
				),
				dbc.Button(
					"Clear All",
					id="sector-selection-clear-all",
					color="success",
					outline=True,
					className="flex-fill"
				)
			], className="gap-2"),
		])
	else:
		sectors_selection_layout = html.Div([])
	return sectors_selection_layout

@callback(
	Output({"type": 'sector-selection-store', "sector_group": dash.ALL}, "value"),
	Input("sector-selection-select-all", "n_clicks"),
	Input("sector-selection-clear-all", "n_clicks"),
	State({"type": 'sector-selection-store', "sector_group": dash.ALL}, "options"),
)
def sectors_checklist_select_or_clear_all(select_all, clear_all, options):
	trigger = ctx.triggered_id
	if trigger == "sector-selection-select-all" and select_all:
		option_list = options[0] if options else []
		selection = [opt["value"] for opt in option_list]
	elif trigger == "sector-selection-clear-all" and clear_all:
		selection = []
	else:
		raise dash.exceptions.PreventUpdate
	return [selection]

@callback(
	Output("scenario-selection-checklist", "children"),
	Input("scenario-mapping-store", "data"),
	Input("exposure-type-store", "data"),
	State('user-selection-completed-store', 'data'),
	State("customise-report-url", "search"),
	State("all-user-selection-store", "data")
)
def initiate_scenarios_checklist(scenario_mapping_dict, exposure_type, user_selection_completed, url_search, stored_data):
	query = parse_qs(url_search.lstrip('?'))
	report_type = query.get("report-type", [None])[0]
	institutional_start_page = report_type == 'Institutional' and len(query) == 1

	# Only run this callback if not on start page
	if exposure_type != "Scenarios" or institutional_start_page or user_selection_completed:
		raise dash.exceptions.PreventUpdate

	if exposure_type == "Scenarios":
		stored_data = stored_data or {}
		filtered_stored_data = stored_data.get("Scenarios", [])

		scenario_mapping_df = pd.DataFrame(scenario_mapping_dict)
		scenarios = scenario_mapping_df['scenario_name'].unique()

		default_value = [x['value'] for x in filtered_stored_data] if filtered_stored_data else []
		scenario_selection_layout = html.Div([
			dbc.Label("Select the scenarios applicable: "),
			html.Br(),
			dbc.Checklist(
				options=[{"label": x, "value": x} for x in scenarios],
				value=default_value,
				id={"type": 'scenario-selection-store', "scenario": ""},
				persistence=True,
				persistence_type='memory'
			),
			html.Br(),
			dbc.ButtonGroup([
				dbc.Button(
					"Select All",
					id="scenario-selection-select-all",
					color="success",
					outline=True,
					className="flex-fill"
				),
				dbc.Button(
					"Clear All",
					id="scenario-selection-clear-all",
					color="success",
					outline=True,
					className="flex-fill"
				)
			], className="gap-2"),
		])
	else:
		scenario_selection_layout = html.Div([])
	return scenario_selection_layout

@callback(
	Output({"type": 'scenario-selection-store', "scenario": dash.ALL}, "value"),
	Input("scenario-selection-select-all", "n_clicks"),
	Input("scenario-selection-clear-all", "n_clicks"),
	State({"type": 'scenario-selection-store', "scenario": dash.ALL}, "options"),
)
def scenarios_checklist_select_or_clear_all(select_all, clear_all, options):
	trigger = ctx.triggered_id
	if trigger == "scenario-selection-select-all" and select_all:
		option_list = options[0] if options else []
		selection = [opt["value"] for opt in option_list]
	elif trigger == "scenario-selection-clear-all" and clear_all:
		selection = []
	else:
		raise dash.exceptions.PreventUpdate
	return [selection]

@callback(
	Output("selection-content", "children"),
	Input("exposure-type-store", "data"),
	State('user-selection-completed-store', 'data'),
	State("customise-report-url", "search"),
)
def selection_layout(exposure_type, user_selection_completed, url_search):
	query = parse_qs(url_search.lstrip('?'))
	report_type = query.get("report-type", [None])[0]
	institution_type = query.get("institution-type", [None])[0]
	institutional_start_page = report_type == 'Institutional' and len(query) == 1

	# Only run this callback if not on start page or not created stepper yet
	if institutional_start_page or user_selection_completed:
		raise dash.exceptions.PreventUpdate

	# title
	if institution_type:
		title_text = f"{institution_type}: {exposure_type}" + (" Exposures" if exposure_type != "Scenarios" else "")
	else:
		title_text = exposure_type
	title = html.H4(title_text, className="ms-1 mb-3")

	# description
	description = html.Div([
		dcc.Markdown("""
		Enter your firm's exposures by asset class and sector using the following definitions:
		- High: One of your top 5 exposures or more than 10% of total assets
		- Medium: 5% - 10% of total assets
		- Low: Below than 5% of total assets
		- N/A: Immaterial or no exposure
		"""),
	], className="rounded-4 p-3 border border-1 border-gray-4 bg-light text-transform-none")

	# layout
	if exposure_type == "Scenarios":
		layout = html.Div([
			html.Div([
				title,
				html.Div(id='scenario-selection-checklist'),
			], className="rounded-4 p-4 border border-1 border-gray-4"),
		])
	elif exposure_type == "Sectors":
		layout = html.Div([
			html.Div([
				title,
				dcc.Loading(html.Div(id='sector-selection-checklist'), color='#00B050'),
			], className="rounded-4 p-4 border border-1 border-gray-4"),
		])
	else:
		layout = html.Div([
			html.Div([
				title,
				description,
				html.Br(),
				html.Div(id='exposure-selection-dropdown'),
			], className="rounded-4 p-4 border border-1 border-gray-4"),
		])
	return layout

@callback(
	Output("report-navigation-buttons", "children"),
	Input("stepper", "active"),
	State('user-selection-completed-store', 'data'),
	State("customise-report-url", "search"),
)
def navigation_buttons(stepper_active, user_selection_completed, url_search):
	# Parse from URL
	query = parse_qs(url_search.lstrip('?'))
	report_type = query.get("report-type", [None])[0]
	institutional_start_page = report_type == 'Institutional' and len(query) == 1

	# Define buttons and their visibility
	button_styling = 'w-100 h-100 d-flex align-items-center justify-content-center text-center'
	button_map = {
		"restart": dbc.Button("Restart Selection", id='report-restart-btn', color="light", className=button_styling),
		"previous": dbc.Button("Previous", id='report-previous-btn', className=button_styling),
		"next": dbc.Button("Next", id='report-next-btn', className=button_styling),
		"generate_report": dbc.Button("Generate Report", id='report-generate-btn', color="success", className=button_styling),
	}

	# Update button styles based on step
	if institutional_start_page:
		buttons = ['restart', 'previous', 'generate_report', 'next']
		visibility = [False, True, True, False]
	elif user_selection_completed:
		buttons = ['restart', 'previous', 'next', 'generate_report']
		visibility = [False, False, True, False]
	elif stepper_active == 0:
		buttons = ['restart', 'previous', 'next', 'generate_report']
		visibility = [False, True, False, True]
	else:
		buttons = ["restart", "previous", "next", "generate_report"]
		visibility = [False, False, False, True]

	button_bar = html.Div([
		dbc.Container(
			dbc.Row(
				[dbc.Col(button_map[b], className="p-0 invisible opacity-0" if v else "p-0") for b, v in zip(buttons, visibility)],
				class_name="d-flex align-items-stretch w-100 h-100 p-3",
				style={'gap': "100px"}
			), fluid=True, className="p-0"
		),
	])
	return button_bar

@callback(
	Output("no-customisation-error-message", "children"),
	Input("report-generate-btn", "n_clicks"),
	State("all-user-selection-store", "data"),
	State("report-type-store", "data"),
	prevent_initial_call=True
)
def no_customisation_error_message(generate_report, all_stored_data, report_type):
	if report_type == 'Scenario':
		error_message = "one scenario"
	else:
		error_message = "one exposure's materiality and scenario"
	error_flag = data_loader.create_error_flag(all_stored_data, report_type)

	if generate_report and error_flag:
		error_message = f"Please select at least {error_message} before generating the report " \
						f"and ensure you click the Next/Previous button to register your selection. "
		msg = dbc.Modal(
			[
				dbc.ModalHeader(dbc.Col(dbc.ModalTitle("Error", class_name="text-danger"), className="text-center"), close_button=False),
				dbc.ModalBody([html.P(error_message)], className="text-center text-danger"),
				dbc.ModalFooter([dbc.Button("Close", id="no-customisation-error-message-close", className="mx-auto d-flex justify-content-center", color="danger")]
				),
			],
			id="no-customisation-error-message-modal",
			size="lg",
			is_open=True,
			centered=True,
		)
		return msg
	else:
		raise dash.exceptions.PreventUpdate

@callback(
	Output("no-customisation-error-message-modal", "is_open"),
	Output('user-selection-completed-store', 'data', allow_duplicate=True),
	Output("customise-report-url", "href", allow_duplicate=True),
	Input("no-customisation-error-message-close", "n_clicks"),
	State("no-customisation-error-message-modal", "is_open"),
	State("customise-report-url", "search"),
	prevent_initial_call=True
)
def toggle_modal(n_click, is_open, url_search):
	if n_click:
		query = parse_qs(url_search.lstrip('?'))
		report_type = query.get("report-type", [None])[0]
		institution_type = query.get("institution-type", [None])[0]
		if institution_type:
			url_pathname = f"/reports/customise-report?report-type={report_type}&institution-type={institution_type}"
		else:
			url_pathname = f"/reports/customise-report?report-type={report_type}"
		return not is_open, None, url_pathname
	return is_open, dash.no_update, dash.no_update

@callback(
	Output("all-user-selection-store", "data", allow_duplicate=True),
	Input("report-previous-btn", "n_clicks"),
	Input("report-next-btn", "n_clicks"),
	Input("report-restart-btn", "n_clicks"),
	Input("report-generate-btn", "n_clicks"),
	State('user-selection-completed-store', 'data'),
	State("exposure-type-store", "data"),
	State("all-user-selection-store", "data"),
	Input("customise-report-url", "search"),
	State({"type": "exposure-selection-store", "exposure": dash.ALL, "sector": dash.ALL, "ptype": dash.ALL}, "value"),
	State({"type": 'scenario-selection-store', "scenario": dash.ALL}, "value"),
	State({"type": 'sector-selection-store', "sector_group": dash.ALL}, "value"),
	prevent_initial_call=True
)
def store_user_selection(
		back, _next, restart, generate_report, user_selection_completed, exposure_type, all_stored_data, url_search,
		exposure_selection_values, scenario_selection_values, sector_selection_values):
	query = parse_qs(url_search.lstrip('?'))
	report_type = query.get("report-type", [None])[0]
	institution_type = query.get("institution-type", [None])[0]
	institutional_start_page = report_type == 'Institutional' and len(query) == 1

	button_id = ctx.triggered_id
	updated = False

	# Create empty dictionary if empty or restart triggered
	if (all_stored_data is None) or (button_id == "report-restart-btn" and restart) or institutional_start_page:
		return {}

	# Allow update on review summary arrival both on the Next click and the subsequent URL change
	if institutional_start_page or button_id is None or user_selection_completed:
		raise dash.exceptions.PreventUpdate

	# Only act on navigation / generate buttons
	if button_id in ["report-previous-btn", "report-next-btn", "report-generate-btn"]:
		if exposure_type == "Scenarios":
			if scenario_selection_values[0]:
				stored_data = [{
					'report': report_type,
					'id': s,
					'institution': institution_type if institution_type else "N/A",
					'exposure': exposure_type,
					'sector': "N/A",
					'ptype': "N/A",
					'label': s,
					'value': s,
				} for s in scenario_selection_values[0]]
				all_stored_data = all_stored_data or {}
				all_stored_data[exposure_type] = stored_data
				updated = True
		elif exposure_type == "Sectors":
			if any([len(x) > 0 for x in sector_selection_values]):
				stored_data = [{
					'report': report_type,
					'id': f'{sector}',
					'institution': institution_type if institution_type else "N/A",
					'exposure': exposure_type,
					'sector': sector.split('|')[1],
					'ptype': "N/A",
					'label': 'High',
					'value': f'{sector}',
					} for sector_group in sector_selection_values for sector in sector_group
				]
				all_stored_data = all_stored_data or {}
				all_stored_data[exposure_type] = stored_data
				updated = True
		else:
			if exposure_selection_values:
				stored_data = []
				for x in exposure_selection_values:
					parts = x.split('|')
					stored_data.append({
						'report': report_type,
						'id': '|'.join(parts[:4]),
						'institution': institution_type,
						'exposure': parts[1],
						'sector': parts[2],
						'ptype': parts[3],
						'label': parts[4],
						'value': x,
					})
				all_stored_data = all_stored_data or {}
				all_stored_data[exposure_type] = stored_data
				updated = True

	if not updated:
		raise dash.exceptions.PreventUpdate
	return all_stored_data

@callback(
	Output('user-selection-completed-store', 'data', allow_duplicate=True),
	Input("report-next-btn", "n_clicks"),
	Input("report-previous-btn", "n_clicks"),
	State("customise-report-url", "search"),
	State("stepper", "children"),
	State("stepper", "active"),
	prevent_initial_call=True
)
def store_user_selection_completed(_next, back, url_search, stepper_children, stepper_active):
	query = parse_qs(url_search.lstrip('?'))
	report_type = query.get("report-type", [None])[0]
	institutional_start_page = report_type == 'Institutional' and len(query) == 1
	review_summary = query.get("review", [None])[0]

	# Return None only when genuinely outside selection flow (start page or backing out of review)
	if institutional_start_page or (back and review_summary):
		return None

	# While on non-Institutional flows before any Next click, do not overwrite (keep existing state)
	if report_type != 'Institutional' and not _next:
		raise dash.exceptions.PreventUpdate

	if not _next:
		raise dash.exceptions.PreventUpdate

	max_step = len(stepper_children) - 2 if stepper_children else 0
	if max_step == stepper_active:
		return True

	raise dash.exceptions.PreventUpdate

@callback(
	Output("review-summary-content", "children"),
	Input("report-next-btn", "n_clicks"),
	Input("all-user-selection-store", "data"),
	Input('user-selection-completed-store', 'data'),
	State("customise-report-url", "search"),
	State("exposure-sector-product-mapping-store", "data"),
	prevent_initial_call=True
)
def review_summary_page(_next, all_stored_data, user_selection_completed, url_search, exposure_sector_product_mapping_dict):
	query = parse_qs(url_search.lstrip('?'))
	report_type = query.get("report-type", [None])[0]
	institution_type = query.get("institution-type", [None])[0]
	review_summary = query.get("review", [None])[0]

	if not (user_selection_completed and review_summary):
		raise dash.exceptions.PreventUpdate

	# Only keep user selections that are not 'N/A'
	all_user_selection_df = data_loader.get_user_selection_from_store(all_stored_data, report_type)
	all_user_selection_df = all_user_selection_df[all_user_selection_df['label'] != 'N/A']

	# Reorder rows
	if report_type == 'Institutional':
		scenario_user_selection_df = all_user_selection_df[all_user_selection_df['exposure'] == 'Scenarios']
		exposure_sector_product_mapping_df = pd.DataFrame(exposure_sector_product_mapping_dict)
		exposure_sector_product_mapping_df = exposure_sector_product_mapping_df[
			exposure_sector_product_mapping_df['institution'].isin([institution_type, 'All'])
		]
		sort_order_df = exposure_sector_product_mapping_df[['exposure', 'sector', 'type']].drop_duplicates().rename(columns={'type': 'ptype'})
		all_user_selection_df = pd.merge(sort_order_df, all_user_selection_df, on=['exposure', 'sector', 'ptype'], how='left')
		all_user_selection_df = all_user_selection_df.dropna(subset='label')
		all_user_selection_df = pd.concat([all_user_selection_df, scenario_user_selection_df], ignore_index=True)
	elif report_type == 'Scenario':
		all_user_selection_df = all_user_selection_df[['label']].rename(columns={'label': 'scenario'})
	elif report_type == 'Sector':
		all_user_selection_df['label'] = np.where(
			all_user_selection_df['exposure'] == 'Sectors', all_user_selection_df['sector'], all_user_selection_df['label']
		)
		all_user_selection_df = all_user_selection_df[['exposure', 'label']]


	# Rename columns for better presentation
	all_user_selection_df = data_loader.rename_user_selection_data_columns(all_user_selection_df)

	# title
	if institution_type:
		title_text = f"{institution_type}: Review your selections"
	else:
		title_text = "Review your selections"
	title = html.H4(title_text, className="ms-1 mb-3")

	review_summary_layout = html.Div([
		title,
		html.Div(
			"Please review your selections below. You can go back to previous steps to make any changes if needed before generating the report.",
			className="rounded-4 p-3 border border-1 border-gray-4 bg-light text-transform-none"
		),
		data_loader.create_data_table(all_user_selection_df)
	], className="rounded-4 p-4 border border-1 border-gray-4")
	return review_summary_layout
