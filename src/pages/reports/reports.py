import dash
from dash import html, dcc, callback, Output, Input, State, ALL
import json
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/reports')


def layout():
	# define default index
	DEFAULT_INDEX = 2

	# create buttons
	sidebar_buttons = dbc.ButtonGroup([
		dbc.Button(
			"Overview",
			id={'type': 'sidebar-report-section-btn', 'index': 1},
			class_name="btn-light text-start",
			n_clicks=0,
			active=(1 == DEFAULT_INDEX)  # set default active button
		),
		dbc.Button(
			"Select report",
			id={'type': 'sidebar-report-section-btn', 'index': 2},
			class_name="btn-light text-start",
			n_clicks=0,
			active=(2 == DEFAULT_INDEX)
		),
	], vertical=True)

	# default content
	default_content = dcc.Loading(type="circle", children=dash.page_registry['pages.reports.overview']['layout']())

	# layout
	layout = html.Div([
		dcc.Location(id='reports-url'),
		dbc.Button(id="select-report-btn", className='d-none'),
		dbc.Row([
			dbc.Col(
				sidebar_buttons,
				style={'height': '600px', 'overflowY': 'auto'},
				md=3,
				class_name="mb-3 sidebar-btn-group"
			),
			dbc.Col(html.Div(default_content, id='selected-report-section-content')),
		]),
	], className="container")
	return layout

@callback(
	Output('report-section-index', 'data', allow_duplicate=True),
	Input({'type': 'sidebar-report-section-btn', 'index': ALL}, 'n_clicks'),
	prevent_initial_call=True
)
def update_report_section(n_clicks):
	triggered_list = dash.callback_context.triggered
	button_clicked = [x for x in triggered_list if x['value']]
	if button_clicked:
		return eval(button_clicked[0]['prop_id'].split('.')[0])['index']
	return dash.no_update

@callback(
	Output('report-section-index', 'data', allow_duplicate=True),
	Input('select-report-btn', 'n_clicks'),
	prevent_initial_call=True
)
def select_report_navigation(n_clicks):
	return 2

@callback(
	Output('selected-report-section-content', 'children'),
	Output({'type': 'sidebar-report-section-btn', 'index': ALL}, 'active'),
	Input('report-section-index', 'data'),
	prevent_initial_call=False
)
def render_report_section(index):
	if index == 1:
		content = dash.page_registry['pages.reports.overview']['layout']()
	elif index == 2:
		content = dash.page_registry['pages.reports.select_report']['layout']()
	else:
		content = html.Div("Select a section to see content.")
	active = [i == index for i in range(1, 3)]
	return content, active

@callback(
	Output('user-selection-completed-store', 'data', allow_duplicate=True),
	Output("all-user-selection-store", "data", allow_duplicate=True),
	Input("reports-url", "pathname"),
	prevent_initial_call=True
)
def empty_user_selection_store(url_pathname):
	return None, {}
