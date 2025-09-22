import dash
from dash import html, callback, Output, Input, State, ctx, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from urllib.parse import parse_qs
import pandas as pd
from utils import data_loader

dash.register_page(__name__, path='/reports/customise-report')
value_bg_color_mapping = {
	"N/A": "white",
	"Low": "#BFEBCE",
	"Medium": "#61CD85",
	"High": "#00B050"
}

def layout(institution_type=None, **kwargs):
	# page layout
	layout = html.Div([
		dcc.Location(id="customise-institutional-report-url"),
		dcc.Store(id='report-type-store', storage_type='session', data='Institutional'),
		html.H3('Institutional Report', className="text-success fw-bold"),
		html.Br(),
		html.Div(id="institution-type-radio"),
		html.Div(id="exposure-stepper-content", children=[html.Div(id="exposure-stepper")]),
		html.Div(id='exposure-type', className="d-none opacity-0 w-1"),
		html.Div(id="exposure-selection-content"),
		html.Div(id="no-customisation-error-message"),
		html.Div(id="review-summary-content"),
		html.Div(id="institutional-navigation-buttons", children=[
			html.Div(id="institutional-restart-btn"),
			html.Div(id="institutional-previous-btn"),
			html.Div(id="institutional-next-btn"),
			html.Div(id="generate-report-btn"),
		]),
	], className="mx-auto py-3 container")
	return layout

@callback(
	Output("customise-institutional-report-url", "href", allow_duplicate=True),
	Input('user-selection-completed-store', 'data'),
	Input("institutional-previous-btn", "n_clicks"),
	Input("institutional-next-btn", "n_clicks"),
	Input("institutional-restart-btn", "n_clicks"),
	Input("generate-report-btn", "n_clicks"),
	State("report-type-store", "data"),
	State("institution-type-store", "data"),
	State("customise-institutional-report-url", "search"),
	State("all-user-selection-store", "data"),
	prevent_initial_call=True
)
def update_url(user_selection_completed, back, _next, restart, generate_report, report_type, institution_type, current_search, all_stored_data):
	query = parse_qs(current_search.lstrip('?'))
	start_page = query.get("report-type", [None])[0] and len(query) == 1
	institution_type = query.get("institution-type", [None])[0] if institution_type is None else institution_type
	review_summary = query.get("review", [None])[0]

	if start_page or (review_summary and back):
		user_selection_completed = None
	if (start_page and _next and not user_selection_completed) or (review_summary and back):
		return f"/reports/customise-report?report-type={report_type}&institution-type={institution_type}"
	elif start_page and restart:
		return f"/reports"
	elif not start_page and restart:
		return f"/reports/customise-report?report-type={report_type}"
	elif user_selection_completed and not review_summary:
		return f"/reports/customise-report?report-type={report_type}&institution-type={institution_type}&review=summary"
	elif generate_report and all_stored_data:
		return f"/reports/generate-report"
	return dash.no_update

@callback(
	Output("institution-type-radio", "children"),
	Input("exposure-sector-product-mapping-store", "data"),
	State("customise-institutional-report-url", "search"),
)
def institution_type_radio(exposure_sector_product_mapping_dict, url_search):
	query = parse_qs(url_search.lstrip('?'))
	start_page = query.get("report-type", [None])[0] and len(query) == 1

	if start_page:
		exposure_sector_product_mapping_df = pd.DataFrame(exposure_sector_product_mapping_dict)
		unique_institution_types = [x for x in exposure_sector_product_mapping_df['institution'].unique() if x.upper() != 'ALL']
		institution_selection = html.Div([
			dbc.Label("Type of institution: "),
			dbc.RadioItems(
				options=[{"label": x, "value": x} for x in unique_institution_types],
				value=unique_institution_types[0] if unique_institution_types else None,
				id="institution-type-value",
				persistence=True,
				persistence_type='memory'
			),
		])
	else:
		institution_selection = html.Div([])
	return institution_selection

@callback(
	Output("institution-type-store", "data"),
	Input("institution-type-value", "value"),
	prevent_initial_call=True
)
def store_institution_type(value):
	return value

@callback(
	Output("exposure-stepper-content", "children"),
	Output("exposure-type", "children", allow_duplicate=True),
	Input("exposure-sector-product-mapping-store", "data"),
	State('user-selection-completed-store', 'data'),
	State("customise-institutional-report-url", "search"),
	prevent_initial_call='initial_duplicate'
)
def initiate_exposure_stepper(exposure_sector_product_mapping_dict, user_selection_completed, url_search):
	query = parse_qs(url_search.lstrip('?'))
	start_page = query.get("report-type", [None])[0] and len(query) == 1
	institution_type = query.get("institution-type", [None])[0]

	# Only run this callback if not on start page
	if start_page or user_selection_completed:
		raise dash.exceptions.PreventUpdate

	exposure_sector_product_mapping_df = data_loader.get_selected_institution_type_mapping(exposure_sector_product_mapping_dict, institution_type)
	exposures = exposure_sector_product_mapping_df['exposure'].unique()
	exposure_type = exposures[0] if len(exposures) > 0 else None

	# stepper
	stepper_children_styling = {"minWidth": "180px", "maxWidth": "220px", "overflow": "auto"}
	stepper = html.Div([dmc.MantineProvider(html.Div([
		dmc.Stepper(
			id="exposure-stepper",
			active=0,
			color="green",
			children=[
				dmc.StepperStep(label=f"Step {i + 1}", description=f"{exposure}", style=stepper_children_styling)
				for i, exposure in enumerate(exposures)
			] + [
				dmc.StepperStep(label=f"Step {len(exposures) + 1}", description=f"Scenario", style=stepper_children_styling),
				dmc.StepperCompleted()
			],
			className="m-0 p-2 pt-4 g-4 align-items-stretch"
		)], className="rounded-4 p-3 border border-1 border-gray-4"
	)), html.Br()])
	return stepper, exposure_type

@callback(
	Output("exposure-stepper", "active", allow_duplicate=True),
	Output("exposure-type", "children", allow_duplicate=True),
	Input("exposure-sector-product-mapping-store", "data"),
	Input("institutional-previous-btn", "n_clicks"),
	Input("institutional-next-btn", "n_clicks"),
	State('user-selection-completed-store', 'data'),
	Input("exposure-stepper", "active"),
	State("exposure-stepper", "children"),
	State("customise-institutional-report-url", "search"),
	prevent_initial_call=True
)
def update_stepper(exposure_sector_product_mapping_dict, back, _next, user_selection_completed, stepper_active, stepper_children, url_search):
	# Parse institution type from URL
	query = parse_qs(url_search.lstrip('?'))
	start_page = query.get("report-type", [None])[0] and len(query) == 1
	institution_type = query.get("institution-type", [None])[0]

	# Only run this callback if not on start page
	if start_page or user_selection_completed:
		raise dash.exceptions.PreventUpdate

	# Get selected institution type mapping and max_step (according to python indexing convention)
	exposure_sector_product_mapping_df = data_loader.get_selected_institution_type_mapping(exposure_sector_product_mapping_dict, institution_type)
	max_step = len(exposure_sector_product_mapping_df['exposure'].unique())

	# Initialize current step
	stepper_active = stepper_active or 0
	button_id = ctx.triggered_id
	step = stepper_active

	# Update step based on button clicked or direct stepper click
	if button_id == "institutional-previous-btn" and back:
		step = step - 1 if step > 0 else step
	elif button_id == "institutional-next-btn" and _next:
		step = step + 1 if step < max_step else step
	elif button_id == "exposure-stepper":
		step = stepper_active

	# Get exposure type for current step
	exposure_types = list(exposure_sector_product_mapping_df['exposure'].unique())
	if step < len(exposure_types):
		exposure_type = exposure_types[step]
	elif step == len(exposure_types):
		exposure_type = "Scenario"
	else:
		exposure_type = None
	return step, exposure_type

@callback(
	Output("exposure-selection-dropdown", "children"),
	Input("exposure-sector-product-mapping-store", "data"),
	Input("exposure-type", "children"),
	State('user-selection-completed-store', 'data'),
	Input("all-user-selection-store", "data"),
	State("customise-institutional-report-url", "search"),
)
def initiate_exposure_selection_dropdown(exposure_sector_product_mapping_dict, exposure_type, user_selection_completed, stored_data, url_search):
	query = parse_qs(url_search.lstrip('?'))
	start_page = query.get("report-type", [None])[0] and len(query) == 1
	institution_type = query.get("institution-type", [None])[0]

	# Only run this callback if not on start page
	if exposure_type == "Scenario" or start_page or user_selection_completed:
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
		html.Table([html.Thead(header)] + [html.Tbody(rows)], className="table table-responsive",
		style={"width": "100%", "tableLayout": "fixed", "overflow-x": "auto"})
	)

@callback(
	Output({"type": "exposure-selection-store", "exposure": dash.ALL, "sector": dash.ALL, "ptype": dash.ALL}, "style"),
	State('user-selection-completed-store', 'data'),
	Input({"type": "exposure-selection-store", "exposure": dash.ALL, "sector": dash.ALL, "ptype": dash.ALL}, "value"),
	State({"type": "exposure-selection-store", "exposure": dash.ALL, "sector": dash.ALL, "ptype": dash.ALL}, "style"),
	State("customise-institutional-report-url", "search"),
	State("exposure-type", "children"),
	prevent_initial_call=True
)
def update_dropdown_color(user_selection_completed, values, current_styles, url_search, exposure_type):
	query = parse_qs(url_search.lstrip('?'))
	start_page = query.get("report-type", [None])[0] and len(query) == 1

	# Only run this callback if not on start page
	if exposure_type == "Scenario" or start_page or user_selection_completed:
		raise dash.exceptions.PreventUpdate

	# Merge color with existing style
	updated_style = [
		{**{k: v for k, v in current_styles[idx].items() if k != "background-color"},
		 "background-color": value_bg_color_mapping.get(val.split('|')[-1], "white")}
		for idx, val in enumerate(values)
	]
	return updated_style

@callback(
	Output("scenario-selection-checklist", "children"),
	Input("scenario-mapping-store", "data"),
	Input("exposure-type", "children"),
	State('user-selection-completed-store', 'data'),
	State("customise-institutional-report-url", "search"),
	State("all-user-selection-store", "data")
)
def initiate_scenario_checklist(scenario_mapping_dict, exposure_type, user_selection_completed, url_search, stored_data):
	query = parse_qs(url_search.lstrip('?'))
	start_page = query.get("report-type", [None])[0] and len(query) == 1

	# Only run this callback if not on start page
	if exposure_type != "Scenario" or start_page or user_selection_completed:
		raise dash.exceptions.PreventUpdate

	if exposure_type == "Scenario":
		stored_data = stored_data or {}
		filtered_stored_data = stored_data.get("Scenario", [])

		scenario_mapping_df = pd.DataFrame(scenario_mapping_dict)
		scenarios = scenario_mapping_df['scenario_name'].unique()

		default_value = [x['value'] for x in filtered_stored_data] if filtered_stored_data else []
		scenario_selection = html.Div([
			dbc.Label("Select the scenarios applicable to your institution: "),
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
		scenario_selection = html.Div([])
	return scenario_selection

@callback(
	Output({"type": 'scenario-selection-store', "scenario": dash.ALL}, "value"),
	Input("scenario-selection-select-all", "n_clicks"),
	Input("scenario-selection-clear-all", "n_clicks"),
	State({"type": 'scenario-selection-store', "scenario": dash.ALL}, "options"),
)
def scenario_checklist_select_or_clear_all(select_all, clear_all, options):
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
	Output("all-user-selection-store", "data"),
	Input("institutional-previous-btn", "n_clicks"),
	Input("institutional-next-btn", "n_clicks"),
	Input("institutional-restart-btn", "n_clicks"),
	Input("generate-report-btn", "n_clicks"),
	State('user-selection-completed-store', 'data'),
	State("customise-institutional-report-url", "href"),
	State("exposure-type", "children"),
	State("all-user-selection-store", "data"),
	State({"type": "exposure-selection-store", "exposure": dash.ALL, "sector": dash.ALL, "ptype": dash.ALL}, "value"),
	State({"type": 'scenario-selection-store', "scenario": dash.ALL}, "value"),
	Input("customise-institutional-report-url", "search"),
)
def store_user_selection(back, _next, restart, generate_report, user_selection_completed, url_path, exposure_type,
					all_stored_data, exposure_selection_values, scenario_selection_values, url_search):
	query = parse_qs(url_search.lstrip('?'))
	start_page = query.get("report-type", [None])[0] and len(query) == 1
	institution_type = query.get("institution-type", [None])[0]
	button_id = ctx.triggered_id
	updated = False

	# Create empty dictionary if empty or restart triggered
	empty_flag = (all_stored_data is None) or (button_id == "institutional-restart-btn" and restart) or start_page
	if empty_flag:
		return {}

	# Allow update on review summary arrival both on the Next click and the subsequent URL change
	if start_page or button_id is None or user_selection_completed:
		raise dash.exceptions.PreventUpdate

	# Only act on navigation / generate buttons
	if button_id in ["institutional-previous-btn", "institutional-next-btn", "generate-report-btn", "customise-institutional-report-url"]:
		if exposure_type == "Scenario":
			stored_data = [{
				'report': 'Institutional',
				'id': s,
				'institution': institution_type,
				'exposure': 'Scenario',
				'sector': "N/A",
				'ptype': "N/A",
				'label': s,
				'value': s,
			} for s in scenario_selection_values[0]]
			if stored_data:
				all_stored_data = all_stored_data or {}
				all_stored_data[exposure_type] = stored_data
				updated = True
		else:
			if exposure_selection_values:
				stored_data = []
				for x in exposure_selection_values:
					parts = x.split('|')
					stored_data.append({
						'report': 'Institutional',
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
	Output("exposure-selection-content", "children"),
	State('user-selection-completed-store', 'data'),
	Input("exposure-stepper", "active"),
	State("exposure-stepper", "children"),
	State("customise-institutional-report-url", "search"),
)
def exposure_selection_layout(user_selection_completed, stepper_active, stepper_children, url_search):
	# Parse institution type from URL
	query = parse_qs(url_search.lstrip('?'))
	start_page = query.get("report-type", [None])[0] and len(query) == 1
	institution_type = query.get("institution-type", [None])[0]

	# Only run this callback if not on start page or not created stepper yet
	if start_page or user_selection_completed:
		raise dash.exceptions.PreventUpdate

	# title
	exposure_type = stepper_children[stepper_active]['props']['description'] if stepper_children else None
	title = html.H4(
		f"{institution_type}: {exposure_type}" + (" Exposures" if exposure_type != "Scenario" else "")
		, className="ms-1 mb-3"
	)

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
	if exposure_type == "Scenario":
		layout = html.Div([
			html.Div([
				title,
				html.Div(id='scenario-selection-checklist'),
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
	Output("institutional-navigation-buttons", "children"),
	Input("exposure-stepper", "active"),
	State('user-selection-completed-store', 'data'),
	State("customise-institutional-report-url", "search"),
)
def navigation_buttons(stepper_active, user_selection_completed, url_search):
	# Parse from URL
	query = parse_qs(url_search.lstrip('?'))
	start_page = query.get("report-type", [None])[0] and len(query) == 1

	# Define buttons and their visibility
	button_styling = 'w-100 h-100 d-flex align-items-center justify-content-center text-center'
	button_map = {
		"restart": dbc.Button("Restart Selection", id='institutional-restart-btn', color="light", className=button_styling),
		"previous": dbc.Button("Previous", id='institutional-previous-btn', className=button_styling),
		"next": dbc.Button("Next", id='institutional-next-btn', className=button_styling),
		"generate_report": dbc.Button("Generate Report", id='generate-report-btn', color="success", className=button_styling),
	}

	# Update button styles based on step
	if start_page:
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
		html.Br(),
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
	Input("generate-report-btn", "n_clicks"),
	State("all-user-selection-store", "data"),
	prevent_initial_call=True
)
def no_customisation_error_message(generate_report, all_stored_data):
	if generate_report and not all_stored_data:
		msg = dbc.Modal(
			[
				dbc.ModalHeader(dbc.Col(dbc.ModalTitle("Error", class_name="text-danger"), className="text-center"), close_button=False),
				dbc.ModalBody([html.P(
					"Please select at least one exposure's materiality or scenario before generating the report "
					"and ensure you click the Next button to register your selection. "
				)], className="text-center text-danger"),
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
	Output("customise-institutional-report-url", "href", allow_duplicate=True),
	Input("no-customisation-error-message-close", "n_clicks"),
	State("no-customisation-error-message-modal", "is_open"),
	State("customise-institutional-report-url", "search"),
	prevent_initial_call=True
)
def toggle_modal(n_click, is_open, url_search):
	if n_click:
		query = parse_qs(url_search.lstrip('?'))
		report_type = query['report_type'][0]
		institution_type = query.get("institution-type", [None])[0]
		return not is_open, f"/reports/customise-report?report-type={report_type}&institution-type={institution_type}"
	return is_open, dash.no_update

@callback(
	Output('user-selection-completed-store', 'data'),
	Input("institutional-next-btn", "n_clicks"),
	Input("institutional-previous-btn", "n_clicks"),
	State("customise-institutional-report-url", "search"),
	State("exposure-stepper", "children"),
	State("exposure-stepper", "active"),
	prevent_initial_call=True
)
def store_user_selection_completed(_next, back, url_search, stepper_children, stepper_active):
	query = parse_qs(url_search.lstrip('?'))
	start_page = query.get("report-type", [None])[0] and len(query) == 1
	review_summary = query.get("review", [None])[0]

	if start_page or (back and review_summary):
		return None

	if not _next:
		raise dash.exceptions.PreventUpdate

	exposure_type = stepper_children[stepper_active]['props']['description'] if stepper_children else None
	if exposure_type == "Scenario":
		return True

	raise dash.exceptions.PreventUpdate

@callback(
	Output("review-summary-content", "children"),
	Input("institutional-next-btn", "n_clicks"),
	Input("all-user-selection-store", "data"),
	Input('user-selection-completed-store', 'data'),
	State("customise-institutional-report-url", "search"),
	State("exposure-sector-product-mapping-store", "data"),
	State("institution-type-store", "data"),
	prevent_initial_call=True
)
def review_summary_page(_next, all_stored_data, user_selection_completed, url_search,
						exposure_sector_product_mapping_dict, institution_type):
	query = parse_qs(url_search.lstrip('?'))
	institution_type = query.get("institution-type", [None])[0]
	review_summary = query.get("review", [None])[0]

	if not (user_selection_completed and review_summary):
		raise dash.exceptions.PreventUpdate

	# Only keep user selections that are not 'N/A'
	all_user_selection_df = data_loader.get_user_selection_from_store(all_stored_data)
	all_user_selection_df = all_user_selection_df[all_user_selection_df['label'] != 'N/A']

	# Reorder rows
	scenario_user_selection_df = all_user_selection_df[all_user_selection_df['exposure'] == 'Scenario']
	exposure_sector_product_mapping_df = pd.DataFrame(exposure_sector_product_mapping_dict)
	exposure_sector_product_mapping_df = exposure_sector_product_mapping_df[
		exposure_sector_product_mapping_df['institution'].isin([institution_type, 'All'])
	]
	sort_order_df = exposure_sector_product_mapping_df[['exposure', 'sector', 'type']].drop_duplicates().rename(columns={'type': 'ptype'})
	all_user_selection_df = pd.merge(sort_order_df, all_user_selection_df, on=['exposure', 'sector', 'ptype'], how='left')
	all_user_selection_df = all_user_selection_df.dropna(subset='label')
	all_user_selection_df = pd.concat([all_user_selection_df, scenario_user_selection_df], ignore_index=True)

	# Rename columns for better presentation
	all_user_selection_df = data_loader.rename_user_selection_data_columns(all_user_selection_df)

	review_summary_layout = html.Div([
		html.H4(f"{institution_type}: Review your selections", className="ms-1 mb-3"),
		html.Div(
			"Please review your selections below. You can go back to previous steps to make any changes if needed before generating the report.",
			className="rounded-4 p-3 border border-1 border-gray-4 bg-light text-transform-none"
		),
		html.Br(),
		data_loader.create_data_table(all_user_selection_df)
	], className="rounded-4 p-4 border border-1 border-gray-4")
	return review_summary_layout
