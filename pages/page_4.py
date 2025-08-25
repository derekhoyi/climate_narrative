from dash import html
import dash_bootstrap_components as dbc
from pages.navbar import create_navbar

def create_layout():
    layout = html.Div([
        create_navbar(),
        html.Div(html.H3('Welcome to page 4!'), className="mx-auto py-3 container"),
        html.Div(dbc.Button("GENERATE REPORT", href='/page-5'), className="text-center")
    ])
    return layout