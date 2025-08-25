import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/page-13')

def layout():

    tab1_content = dbc.Card(
        dbc.CardBody(
            [
                html.P("This is tab 1!", className="card-text"),
                dbc.Button("Click here", color="success"),
            ]
        ),
        className="mt-3",
        style={'border-top-width': '1px', 'border-top-style': 'solid'}
    )

    tab2_content = dbc.Card(
        dbc.CardBody(
            [
                html.P("This is tab 2!", className="card-text"),
                dbc.Button("Don't click here", color="danger"),
            ]
        ),
        className="mt-3",
        style={'border-top-width': '1px', 'border-top-style': 'solid'}
    )

    layout = html.Div([
        html.H3('Welcome to page 13!'),
        dbc.Tabs([
            dbc.Tab(tab1_content, label="Tab 1"),
            dbc.Tab(tab2_content, label="Tab 2"),
        ])    
    ], className="mx-auto py-3 container")
    return layout