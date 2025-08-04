from dash import html
from pages.navbar import create_navbar

def create_layout():
    layout = html.Div([
        create_navbar(),
        html.Div(html.H3('Welcome to page 4!'), className="mx-auto py-3 container"),
    ])
    return layout