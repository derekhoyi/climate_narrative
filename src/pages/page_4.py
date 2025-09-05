import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/page-4')

def layout():

    # nav buttons
    prev_button = dbc.Button("PREV", href='/page-3')
    next_button = dbc.Button("NEXT", href='/page-5')
    button_bar = html.Div([prev_button, next_button], className="d-flex justify-content-between")

    layout = html.Div([
        html.H3('Welcome to page 4!'),
        button_bar
    ], className="mx-auto py-3 container")
    return layout