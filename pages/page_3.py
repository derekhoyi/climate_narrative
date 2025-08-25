from dash import html, callback, Output, Input, dcc
import dash_bootstrap_components as dbc

def create_layout():

    # nav buttons
    prev_button = dbc.Button("PREV", href='/page-2')
    next_button = dbc.Button("NEXT", href='/page-4')
    button_bar = html.Div([prev_button, next_button], className="d-flex justify-content-between")

    layout = html.Div([
        html.H3('Welcome to page 3!'),
        dbc.Label("Select the scenario to show"),
        dbc.RadioItems(
            options=[
                {"label": "All relevant scenarios", "value": "All relevant scenarios"},
                {"label": "NGFS Orderly Scenarios", "value": "NGFS Orderly Scenarios"},
                {"label": "NGFS Disorderly Scenarios", "value": "NGFS Disorderly Scenarios"},
                {"label": "NGFS Hot House World scenario", "value": "NGFS Hot House World scenario"},
            ],
            value="All relevant scenarios",
            id="scenario-input",
        ),
        html.Br(), 
        # html.P(id="scenario-checklist-output"),
        html.P(id="print-storage"),
        button_bar
    ], className="mx-auto py-3 container")
    return layout

# print selected option
# @callback(
#     Output("scenario-checklist-output", "children"),
#     Input("scenario-input", "value"),
# )
# def on_form_change(radio_items_value):
#     template = "you have selected {}."
#     output_string = template.format(radio_items_value)
#     return output_string

# store value using dcc.Store
@callback(
    Output('storage-scenario', 'data'), 
    Input('scenario-input', 'value')
)
def store_scenario(value):
    return value

# print value in storage
@callback(
    Output('print-storage', 'children'), 
    Input('storage-scenario', 'data')
)
def print_store_scenario(value):
    return f'Storage: {value}'