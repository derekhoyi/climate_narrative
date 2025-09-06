import dash
from dash import html, callback, Output, Input, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/page-3')

def layout():

    # nav buttons
    prev_button = dbc.Button("PREV", href='/page-2')
    next_button = dbc.Button("NEXT", href='/page-4')
    button_bar = html.Div([prev_button, next_button], className="d-flex justify-content-between")

    layout = html.Div([
        html.H3('Welcome to page 3!'),
        dbc.Label("Select one option: "),
        dbc.RadioItems(
            options=[
                {"label": "Agriculture", "value": "Agriculture"},
                {"label": "Aviation", "value": "Aviation"},
            ],
            value="Agriculture",
            id="sector-input",
            persistence=True,
            persistence_type='memory'
        ),
        html.Br(), 
        # html.P(id="scenario-checklist-output"),
        html.P(id="print-storage"),
        button_bar
    ], className="container")
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
    Output('storage-sector', 'data'), 
    Input('sector-input', 'value')
)
def add_to_storege(value):
    return value

# print value in storage
@callback(
    Output('print-storage', 'children'), 
    Input('storage-sector', 'data')
)
def print_stored_value(value):
    return f'Storage: {value}'
