import dash
from dash import html, callback, Output, Input, State, ctx, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from urllib.parse import parse_qs, urlparse
import pandas as pd
from src.utils import data_loader

dash.register_page(__name__, path='/reports/generate-institutional-report')
value_bg_color_mapping = {
    "N/A": "white",
    "Low": "#BFEBCE",
    "Medium": "#61CD85",
    "High": "#00B050"
}

def layout(institution_type=None, **kwargs):
    # page layout
    layout = html.Div([
        dcc.Location(id="generate-institution-report-url"),
        html.H3('Institutional Report', className="text-success fw-bold"),
        html.Br(),
        html.Div(id="institution-type-radio"),
        html.Div(id="exposure-stepper-content", children=[html.Div(id="exposure-stepper")]),
        html.Div(id='exposure-type', className="d-none opacity-0 w-1"),
        html.Br(),
        html.Div(id="step-title"),
        html.Div(id="exposure-selection-content"),
    ], className="mx-auto py-3 container")
    return layout

def navigation_buttons(buttons=None):
    button_map = {
        "restart": dbc.Button("Restart Selection", href='/reports/select-report', id='institutional-restart-btn', color="light"),
        "previous": dbc.Button("Previous", id='institutional-previous-btn'),
        "next": dbc.Button("Next", id='institutional-next-btn'),
        "generate_report": dbc.Button("Generate Report", href='/page-5', id='generate-report-btn', color="success"),
    }
    if buttons is None:
        buttons = ["restart", "previous", "next", "generate_report"]
    button_bar = html.Div([
        html.Div([button_map[b] for b in button_map if b not in buttons], className="d-none opacity-0 w-1"),
        html.Div([button_map[b] for b in button_map if b in buttons], className="d-flex justify-content-between")
    ])
    return button_bar

@callback(
    Output("institution-type-radio", "children"),
    Input("exposure-product-mapping-store", "data"),
    State("generate-institution-report-url", "search"),
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
            html.Br(),
            navigation_buttons(['restart', 'next'])
        ])
    else:
        institution_selection = html.Div([])
    return institution_selection


@callback(
    Output("generate-institution-report-url", "href"),
    Input("institutional-next-btn", "n_clicks"),
    State("institution-type-store", "value"),
    State("generate-institution-report-url", "search"),
    prevent_initial_call=True
)
def update_url_on_institution_type_selection(n_clicks, institution_type, current_search):
    query = parse_qs(current_search.lstrip('?'))
    start_page = len(query) == 0

    # Only update URL if we're on the start page and have an institution type
    if start_page and n_clicks:
        return f"/reports/generate-institutional-report?institution-type={institution_type}"

    return dash.no_update


@callback(
    Output("exposure-stepper-content", "children"),
    Output("exposure-type", "children", allow_duplicate=True),
    Input("exposure-product-mapping-store", "data"),
    State("generate-institution-report-url", "search"),
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
    stepper = dmc.MantineProvider(html.Div([
        dmc.Stepper(
            id="exposure-stepper",
            active=0,
            color="green",
            children=[
                dmc.StepperStep(label=f"Step {i + 1}", description=f"{exposure}", style={"minWidth": "180px", "maxWidth": "220px"})
                for i, exposure in enumerate(exposures)
            ] + [
                dmc.StepperStep(label=f"Step {len(exposures) + 1}", description=f"Scenario", style={"minWidth": "180px", "maxWidth": "220px"}),
                dmc.StepperCompleted()
            ],
            className="m-0 p-2 pt-4 g-4 align-items-stretch"
        )], className="rounded-4 p-3 border border-1 border-gray-4"
    ))
    return stepper, exposure_type

@callback(
    Output("exposure-stepper", "active", allow_duplicate=True),
    Output("step-title", "children"),
    Output("exposure-type", "children", allow_duplicate=True),
    Output("institutional-previous-btn", "style"),
    Output("institutional-next-btn", "style"),
    Input("exposure-product-mapping-store", "data"),
    Input("institutional-previous-btn", "n_clicks"),
    Input("institutional-next-btn", "n_clicks"),
    State("exposure-stepper", "active"),
    State("exposure-stepper", "children"),
    State("generate-institution-report-url", "search"),
    prevent_initial_call=True
)
def update_exposure_stepper(exposure_product_mapping_dict, back, next_, current, stepper_children, url_search):
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
    if current is None:
        current = 0
    button_id = ctx.triggered_id
    step = current

    # Update step based on button clicked
    if button_id == "institutional-previous-btn":
        step = step - 1 if step > 0 else step
    elif button_id == "institutional-next-btn":
        step = step + 1 if step < max_step else step

    # Update title based on step
    if step < max_step:
        description = stepper_children[step]['props']['description']
        title_text = f"{institution_type}: {description}" + (" Exposures" if description != "Scenario" else "")
    else:
        title_text = "End of Selection - Generate Report or Restart"
    title = html.H4(title_text)

    # Get exposure type for current step
    exposure_types = list(exposure_product_mapping_df['exposure'].unique())
    exposure_type = exposure_types[step] if step < len(exposure_types) else None

    # Update button styles based on step
    if step == 0:
        prev_btn_style = {'display': None, 'opacity': 0}
        next_btn_style = {}
    elif step == max_step - 1:
        prev_btn_style = {}
        next_btn_style = {'display': None, 'opacity': 0}
    else:
        prev_btn_style = {}
        next_btn_style = {}
    return step, title, exposure_type, prev_btn_style, next_btn_style

@callback(
    Output("exposure-selection-dropdown", "children"),
    Input("exposure-product-mapping-store", "data"),
    Input("exposure-type", "children"),
    State("generate-institution-report-url", "search"),
    State("all-exposure-selection-store", "data")
)
def initiate_exposure_selection_dropdown(exposure_product_mapping_dict, exposure_type, url_search, stored_data):
    query = parse_qs(url_search.lstrip('?'))
    start_page = len(query) == 0
    institution_type = query.get("institution-type", [None])[0]

    # Only run this callback if not on start page
    if start_page:
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
            default_value = [x for x in filtered_stored_data if x['portfolio'] == p and x['type'] == t][0]['value'] if filtered_stored_data != [] else options_list[0]['value']
            background_color = value_bg_color_mapping.get(default_value.split('|')[-1], "white")
            row.append(html.Td(
                dcc.Dropdown(
                    options=options_list,
                    value=default_value,
                    id={"type": 'exposure-selection-store', "exposure": exposure_type, "portfolio": p, "ptype": t},
                    clearable=False,
                    style=({"display": None, "opacity": 0} if (p, t) not in combinations_to_keep_list else {})
                          | {"background-color": background_color},
                )
            , style=table_styling | {"textAlign": "center"}))
        rows.append(html.Tr(row))
    return html.Table([html.Thead(header)] + [html.Tbody(rows)], className="table")

@callback(
    Output({"type": "exposure-selection-store", "exposure": dash.ALL, "portfolio": dash.ALL, "ptype": dash.ALL}, "style"),
    Input({"type": "exposure-selection-store", "exposure": dash.ALL, "portfolio": dash.ALL, "ptype": dash.ALL}, "value"),
    State({"type": "exposure-selection-store", "exposure": dash.ALL, "portfolio": dash.ALL, "ptype": dash.ALL}, "style"),
    State("generate-institution-report-url", "search"),
    prevent_initial_call=True
)
def update_dropdown_color(values, current_styles, url_search):
    query = parse_qs(url_search.lstrip('?'))
    start_page = len(query) == 0

    # Only run this callback if not on start page
    if start_page:
        raise dash.exceptions.PreventUpdate

    # Merge color with existing style
    updated_style = [
        {**{k: v for k, v in current_styles[idx].items() if k != "background-color"},
         "background-color": value_bg_color_mapping.get(val.split('|')[-1], "white")}
        for idx, val in enumerate(values)
    ]
    return updated_style

@callback(
    Output("all-exposure-selection-store", "data"),
    Input("institutional-previous-btn", "n_clicks"),
    Input("institutional-next-btn", "n_clicks"),
    Input("institutional-restart-btn", "n_clicks"),
    Input("generate-report-btn", "n_clicks"),
    State({"type": "exposure-selection-store", "exposure": dash.ALL, "portfolio": dash.ALL, "ptype": dash.ALL}, "value"),
    State({"type": "exposure-selection-store", "exposure": dash.ALL, "portfolio": dash.ALL, "ptype": dash.ALL}, "id"),
    State("exposure-type", "children"),
    State("all-exposure-selection-store", "data"),
    prevent_initial_call=True
)
def store_selection(back, _next, restart, generate_report, values, ids, exposure_type, all_stored_data):
    button_id = ctx.triggered_id

    # Update selection store based on button clicked
    all_stored_data = all_stored_data or {}
    if button_id in ["institutional-previous-btn", "institutional-next-btn"]:
        all_stored_data[exposure_type] = [{
            'id': '|'.join(x.split('|')[:3]),
            'exposure': x.split('|')[0],
            'portfolio': x.split('|')[1],
            'type': x.split('|')[2],
            'label': x.split('|')[3],
            'value': x,
        } for x in values]
    elif button_id == "institutional-restart-btn":
        all_stored_data = {}
    return all_stored_data

@callback(
    Output("exposure-selection-content", "children"),
    Input("exposure-product-mapping-store", "data"),
    State("generate-institution-report-url", "search"),
)
def exposure_selection_layout(exposure_product_mapping_dict, url_search):
    # Parse institution type from URL
    query = parse_qs(url_search.lstrip('?'))
    start_page = len(query) == 0

    # Only run this callback if not on start page or not created stepper yet
    if start_page:
        raise dash.exceptions.PreventUpdate

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
    layout = html.Div([
        html.Div([
            html.Div(id='step-title', className="ms-1 mb-3"),
            description,
            html.Div(id='exposure-selection-dropdown'),
        ], className="rounded-4 p-4 border border-1 border-gray-4"),
        html.Br(),
        navigation_buttons()
    ])
    return layout

# all_dfs = pd.DataFrame()
# for k, v in all_stored_data.items():
# 	df = pd.DataFrame(all_stored_data[k])
# 	all_dfs = pd.concat([all_dfs, df])
