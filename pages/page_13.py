from dash import html
from pages.navbar import create_navbar
import dash_bootstrap_components as dbc

def create_layout():

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
        create_navbar(),
        html.Div(html.H3('Welcome to page 13!'), className="mx-auto py-3 container"),
        html.Div([
            dbc.Tabs([
                dbc.Tab(tab1_content, label="Tab 1"),
                dbc.Tab(tab2_content, label="Tab 2"),
            ])    
        ], 
        className="mx-auto py-3 container")
    ])
    return layout