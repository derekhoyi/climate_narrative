from dash import html, callback, Output, Input, dcc
import dash_bootstrap_components as dbc

def create_layout():
    layout = html.Div([
        html.H3('Welcome to page 5'), 
        html.P(id="print-storage-page5"),
        html.Div(dbc.Button("PREV", href='/page-4'), className="text-left") 
    ], className="mx-auto py-3 container")
    return layout

# print value in storage
@callback(
    Output('print-storage-page5', 'children'), 
    Input('storage-scenario', 'data')
)
def generate_report(value):
    return f'Storage: {value}'