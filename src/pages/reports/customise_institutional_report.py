import dash
from dash import html, callback, Output, Input, State, ctx, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from urllib.parse import parse_qs
import pandas as pd
from src.utils import data_loader

dash.register_page(__name__, path='/reports/customise-institutional-report')
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
		html.H3('Institutional Report', className="text-success fw-bold"),
		html.Br(),
		html.Div(id="institution-type-radio"),
		html.Div(id="exposure-stepper-content", children=[html.Div(id="exposure-stepper")]),
		html.Div(id='exposure-type', className="d-none opacity-0 w-1"),
		html.Br(),
		html.Div(id="exposure-selection-content"),
		html.Br(),
		html.Div(id="no-customisation-error-message"),
		html.Div(id="institutional-navigation-buttons", children=[
			html.Div(id="institutional-restart-btn"),
			html.Div(id="institutional-previous-btn"),
			html.Div(id="institutional-next-btn"),
			html.Div(id="generate-report-btn"),
		]),
	], className="mx-auto py-3 container")
	return layout

@callback(
	Output("institution-type-radio", "children"),
	Input("exposure-product-mapping-store", "data"),
	State("customise-institutional-report-url", "search"),
)
def institution_type_radio(exposure_product_mapping_dict, url_search):
	query = parse_qs(url_search.lstrip('?'))
	start_page = len(query) == 0

	if start_page:
		exposure_product_mapping_df = pd.DataFrame(exposure_product_mapping_dict)
		unique_institution_types = [x for x in exposure_product_mapping_df['institution'].unique() if x.upper() != 'ALL']
		institution_selection = html.Div([
			dbc.Label("Type of institution: "),
			dbc.RadioItems(
				options=[{"label": x, "value": x} for x in unique_institution_types],
				value=unique_institution_types[0] if unique_institution_types else None,
				id="institution-type-store",
				persistence=True,
				persistence_type='memory'
			),
		])
	else:
		institution_selection = html.Div([])
	return institution_selection

@callback(
	Output("customise-institutional-report-url", "href", allow_duplicate=True),
	Input("institutional-next-btn", "n_clicks"),
	Input("institutional-restart-btn", "n_clicks"),
	Input("generate-report-btn", "n_clicks"),
	State("institution-type-store", "value"),
	State("customise-institutional-report-url", "search"),
	State("all-user-selection-store", "data"),
	prevent_initial_call=True
)
def update_url(_next, restart, generate_report, institution_type, current_search, all_stored_data):
	query = parse_qs(current_search.lstrip('?'))
	start_page = len(query) == 0

	# Only update URL if we're on the start page and have an institution type
	if start_page and _next:
		return f"/reports/customise-institutional-report?institution-type={institution_type}"
	elif restart:
		return f"/reports/select-report"
	elif generate_report and all_stored_data:
		return f"/reports/generate-report"
	return dash.no_update


@callback(
	Output("exposure-stepper-content", "children"),
	Output("exposure-type", "children", allow_duplicate=True),
	Input("exposure-product-mapping-store", "data"),
	State("customise-institutional-report-url", "search"),
	prevent_initial_call='initial_duplicate'
)
def initiate_exposure_stepper(exposure_product_mapping_dict, url_search):
	query = parse_qs(url_search.lstrip('?'))
	start_page = len(query) == 0
	institution_type = query.get("institution-type", [None])[0]

	# Only run this callback if not on start page
	if start_page:
		raise dash.exceptions.PreventUpdate

	exposure_product_mapping_df = data_loader.get_selected_institution_type_mapping(exposure_product_mapping_dict, institution_type)
	exposures = exposure_product_mapping_df['exposure'].unique()
	exposure_type = exposures[0] if len(exposures) > 0 else None

	# stepper
	stepper_children_styling = {"minWidth": "180px", "maxWidth": "220px", "overflow": "auto"}
	stepper = dmc.MantineProvider(html.Div([
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
	))
	return stepper, exposure_type

@callback(
	Output("exposure-stepper", "active", allow_duplicate=True),
	Output("exposure-type", "children", allow_duplicate=True),
	Input("exposure-product-mapping-store", "data"),
	Input("institutional-previous-btn", "n_clicks"),
	Input("institutional-next-btn", "n_clicks"),
	Input("exposure-stepper", "active"),
	State("exposure-stepper", "children"),
	State("customise-institutional-report-url", "search"),
	prevent_initial_call=True
)
def update_stepper(exposure_product_mapping_dict, back, next_, stepper_active, stepper_children, url_search):
	# Parse institution type from URL
	query = parse_qs(url_search.lstrip('?'))
	start_page = len(query) == 0
	institution_type = query.get("institution-type", [None])[0]

	# Only run this callback if not on start page or not created stepper yet
	if start_page:
		raise dash.exceptions.PreventUpdate

	# Get selected institution type mapping
	exposure_product_mapping_df = data_loader.get_selected_institution_type_mapping(exposure_product_mapping_dict, institution_type)
	max_step = len(exposure_product_mapping_df['exposure'].unique()) + 1

	# Initialize current step
	stepper_active = stepper_active or 0
	button_id = ctx.triggered_id
	step = stepper_active

	# Update step based on button clicked or direct stepper click
	if button_id == "institutional-previous-btn" and back:
		step = step - 1 if step > 0 else step
	elif button_id == "institutional-next-btn" and next_:
		step = step + 1 if step < max_step else step
	elif button_id == "exposure-stepper":
		step = stepper_active

	# Get exposure type for current step
	exposure_types = list(exposure_product_mapping_df['exposure'].unique())
	if step < len(exposure_types):
		exposure_type = exposure_types[step]
	elif step == len(exposure_types):
		exposure_type = "Scenario"
	else:
		exposure_type = None
	return step, exposure_type

@callback(
	Output("exposure-selection-dropdown", "children"),
	Input("exposure-product-mapping-store", "data"),
	Input("exposure-type", "children"),
	State("customise-institutional-report-url", "search"),
	State("all-user-selection-store", "data")
)
def initiate_exposure_selection_dropdown(exposure_product_mapping_dict, exposure_type, url_search, stored_data):
	query = parse_qs(url_search.lstrip('?'))
	start_page = len(query) == 0
	institution_type = query.get("institution-type", [None])[0]

	# Only run this callback if not on start page
	if exposure_type == "Scenario" or start_page:
		raise dash.exceptions.PreventUpdate

	stored_data = stored_data or {}
	filtered_stored_data = stored_data.get(exposure_type, [])

	exposure_product_mapping_df = data_loader.get_selected_institution_type_mapping(exposure_product_mapping_dict, institution_type)
	exposure_product_mapping_df = exposure_product_mapping_df[exposure_product_mapping_df['exposure'] == exposure_type]
	portfolios = exposure_product_mapping_df['portfolio'].unique()
	types = exposure_product_mapping_df['type'].unique()
	combinations_to_keep_list = [(p, t) for p, t in exposure_product_mapping_df[['portfolio', 'type']].drop_duplicates().values]

	table_styling = {"margin": 8, "padding": 8, "align-items": "center", "verticalAlign": "middle", "width": "100%", "height": "100%", "minWidth": 200, "maxWidth": 250}
	header = html.Tr([html.Th("Type", style=table_styling | {"maxWidth": 300})] + [html.Th(t, style=table_styling | {"textAlign": "center"}) for t in types])
	rows = []
	for p in portfolios:
		row = [html.Td(p, style=table_styling)]
		for t in types:
			options_list = [{"label": l, "value": f"{exposure_type}|{p}|{t}|{l}"} for l in value_bg_color_mapping.keys()]
			default_items = [x for x in filtered_stored_data if x['portfolio'] == p and x['type'] == t]
			default_value = default_items[0]['value'] if default_items else options_list[0]['value']
			background_color = value_bg_color_mapping.get(default_value.split('|')[-1], "white")
			row.append(html.Td(
				dcc.Dropdown(
					options=options_list,
					value=default_value,
					id={"type": 'exposure-selection-store', "exposure": exposure_type, "portfolio": p, "ptype": t},
					clearable=False,
					style=({'visibility': 'hidden', "opacity": 0} if (p, t) not in combinations_to_keep_list else {})
						  | {"background-color": background_color},
				)
			, style=table_styling | {"textAlign": "center"}))
		rows.append(html.Tr(row))
	return html.Table([html.Thead(header)] + [html.Tbody(rows)], className="table")

@callback(
	Output({"type": "exposure-selection-store", "exposure": dash.ALL, "portfolio": dash.ALL, "ptype": dash.ALL}, "style"),
	Input({"type": "exposure-selection-store", "exposure": dash.ALL, "portfolio": dash.ALL, "ptype": dash.ALL}, "value"),
	State({"type": "exposure-selection-store", "exposure": dash.ALL, "portfolio": dash.ALL, "ptype": dash.ALL}, "style"),
	State("customise-institutional-report-url", "search"),
	State("exposure-type", "children"),
	prevent_initial_call=True
)
def update_dropdown_color(values, current_styles, url_search, exposure_type):
	query = parse_qs(url_search.lstrip('?'))
	start_page = len(query) == 0

	# Only run this callback if not on start page
	if exposure_type == "Scenario" or start_page:
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
	State("customise-institutional-report-url", "search"),
	State("all-user-selection-store", "data")
)
def initiate_scenario_checklist(scenario_mapping_dict, exposure_type, url_search, stored_data):
	query = parse_qs(url_search.lstrip('?'))
	start_page = len(query) == 0

	# Only run this callback if not on start page
	if exposure_type != "Scenario" or start_page:
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
	Output("all-user-selection-store", "data", allow_duplicate=True),
	Input("institutional-previous-btn", "n_clicks"),
	Input("institutional-next-btn", "n_clicks"),
	Input("institutional-restart-btn", "n_clicks"),
	Input("generate-report-btn", "n_clicks"),
	State({"type": "exposure-selection-store", "exposure": dash.ALL, "portfolio": dash.ALL, "ptype": dash.ALL}, "value"),
	State("exposure-type", "children"),
	State("all-user-selection-store", "data"),
	State({"type": 'scenario-selection-store', "scenario": dash.ALL}, "value"),
	State("customise-institutional-report-url", "search"),
	prevent_initial_call=True
)
def store_selection(back, _next, restart, generate_report, exposure_selection_values, exposure_type, all_stored_data,
					scenario_selection_values, url_search):
	button_id = ctx.triggered_id
	all_stored_data = all_stored_data or {}

	# Parse institution type from URL
	query = parse_qs(url_search.lstrip('?'))
	start_page = len(query) == 0

	if start_page or (not back and not _next and not restart and not generate_report):
		raise dash.exceptions.PreventUpdate

	# Update selection store based on button clicked
	if (button_id in ["institutional-previous-btn", "institutional-next-btn", "generate-report-btn"]
			and (back or _next or generate_report) and not start_page):
		if exposure_type == "Scenario":
			stored_data = [{
				'id': scenario_selection_values[0],
				'exposure': 'Scenario',
				'portfolio': None,
				'type': None,
				'label': scenario_selection_values[0],
				'value': scenario_selection_values[0],
			}]
			if stored_data[0]["id"]:
				all_stored_data["Scenario"] = stored_data
		else:
			stored_data = [{
				'id': '|'.join(x.split('|')[:3]),
				'exposure': x.split('|')[0],
				'portfolio': x.split('|')[1],
				'type': x.split('|')[2],
				'label': x.split('|')[3],
				'value': x,
			} for x in exposure_selection_values if x.split('|')[3] != 'N/A']
			if stored_data:
				all_stored_data[exposure_type] = stored_data
	elif button_id == "institutional-restart-btn" and restart:
		all_stored_data = {}
	print(f'stored data: {all_stored_data}')
	return all_stored_data

@callback(
	Output("exposure-selection-content", "children"),
	Input("exposure-stepper", "active"),
	State("exposure-stepper", "children"),
	State("customise-institutional-report-url", "search"),
)
def exposure_selection_layout(stepper_active, stepper_children, url_search):
	# Parse institution type from URL
	query = parse_qs(url_search.lstrip('?'))
	start_page = len(query) == 0
	institution_type = query.get("institution-type", [None])[0]

	# Only run this callback if not on start page or not created stepper yet
	if start_page:
		raise dash.exceptions.PreventUpdate

	# title
	exposure_type = stepper_children[stepper_active]['props']['description']
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
	], className="rounded-4 p-2 mb-2 border border-1 border-gray-4 bg-light text-transform-none")

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
				html.Div(id='exposure-selection-dropdown'),
			], className="rounded-4 p-4 border border-1 border-gray-4"),
		])
	return layout

@callback(
	Output("institutional-navigation-buttons", "children"),
	Input("exposure-stepper", "active"),
	State("exposure-stepper", "children"),
	State("customise-institutional-report-url", "search"),
)
def navigation_buttons(stepper_active, stepper_children, url_search):
	# Parse institution type from URL
	query = parse_qs(url_search.lstrip('?'))
	start_page = len(query) == 0

	# Define buttons and their visibility
	button_styling = 'w-100 h-100 d-flex align-items-center justify-content-center text-center'
	button_map = {
		"restart": dbc.Button("Restart Selection", id='institutional-restart-btn', color="light", className=button_styling),
		"previous": dbc.Button("Previous", id='institutional-previous-btn', className=button_styling),
		"next": dbc.Button("Next", id='institutional-next-btn', className=button_styling),
		"generate_report": dbc.Button("Generate Report", id='generate-report-btn', color="success", className=button_styling),
	}

	# Update button styles based on step
	exposure_type = None
	if stepper_children and stepper_active is not None and stepper_active < len(stepper_children):
		exposure_type = stepper_children[stepper_active]['props']['description']
	if start_page:
		buttons = ['restart', 'previous', 'generate_report', 'next']
		visibility = [False, True, True, False]
	elif exposure_type == "Scenario":
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
				class_name="d-flex align-items-stretch w-100 h-100",
				style={'gap': "30px"}
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
		institution_type = query.get("institution-type", [None])[0]
		return not is_open, f"/reports/customise-institutional-report?institution-type={institution_type}"
	return is_open, dash.no_update
