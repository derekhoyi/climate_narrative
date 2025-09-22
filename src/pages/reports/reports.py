import dash
from dash import html, dcc, callback, Output, Input, State, ALL
import json
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/reports')


def layout():
	# define default index
	DEFAULT_INDEX = 1

	# create buttons
	sidebar_buttons = dbc.ButtonGroup([
		dbc.Button(
			"Overview",
			id={'type': 'sidebar-report-tab-btn', 'index': 1},
			class_name="btn-light text-start",
			n_clicks=0,
			active=(1 == DEFAULT_INDEX)  # set default active button
		),
		dbc.Button(
			"Select report",
			id={'type': 'sidebar-report-tab-btn', 'index': 2},
			class_name="btn-light text-start",
			n_clicks=0,
			active=(2 == DEFAULT_INDEX)
		),
	], vertical=True)

	# default content
	default_content = dcc.Loading(type="circle", children=dash.page_registry['pages.reports.overview']['layout']())

	# layout
	layout = html.Div([
		dcc.Store(id='report-tab-index', data=1),
		dbc.Button(id="select-report-btn", className='d-none'),
		dbc.Row([
			dbc.Col(
				sidebar_buttons,
				style={'height': '600px', 'overflowY': 'auto'},
				md=3,
				class_name="mb-3 sidebar-btn-group"
			),
			dbc.Col(html.Div(default_content, id='selected-report-tab-content')),
		]),
	], className="container")
	return layout

@callback(
    Output('report-tab-index', 'data', allow_duplicate=True),
    Input({'type': 'sidebar-report-tab-btn', 'index': ALL}, 'n_clicks'),
prevent_initial_call=True
)
def update_report_tab(n_clicks):
	prop_id = dash.callback_context.triggered[0]['prop_id']
	json_str = prop_id.split('.')[0]
	button_id = json.loads(json_str)
	index = button_id['index']
	return index

@callback(
    Output('report-tab-index', 'data', allow_duplicate=True),
    Input('select-report-btn', 'n_clicks'),
	prevent_initial_call=True
)
def select_report_navigation(n_clicks):
	return 2

@callback(
	Output('selected-report-tab-content', 'children'),
	Output({'type': 'sidebar-report-tab-btn', 'index': ALL}, 'active'),
	Input('report-tab-index', 'data'),
	prevent_initial_call=False
)
def render_report_tab(index):
	if index == 1:
		content = dcc.Loading(type="circle", children=dash.page_registry['pages.reports.overview']['layout']())
	elif index == 2:
		content = dcc.Loading(type="circle", children=dash.page_registry['pages.reports.select_report']['layout']())
	else:
		content = html.Div("Select a tab to see content.")
	active = [i == index for i in range(1, 3)]
	return content, active
