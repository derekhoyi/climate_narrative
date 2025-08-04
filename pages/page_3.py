from dash import html, callback, Output, Input
import dash_bootstrap_components as dbc
from pages.navbar import create_navbar

def create_layout():

    # nav buttons
    prev_button = dbc.Button("PREV", id="open", n_clicks=0, href='/page-2')
    next_button = dbc.Button("NEXT", id="open", n_clicks=0, href='/page-4')
    button_bar = html.Div([prev_button, next_button], className="d-flex justify-content-between container")

    layout = html.Div([
        create_navbar(),
        html.Div([
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
                id="scneario-input",
            ),
            html.Br(), 
            html.P(id="scenario-checklist-output"),
        ], className="mx-auto py-3 container"),
        button_bar
    ])
    return layout

@callback(
    Output("scenario-checklist-output", "children"),
    Input("scneario-input", "value"),
)
def on_form_change(radio_items_value):
    template = "you have selected {}."
    output_string = template.format(radio_items_value)
    return output_string