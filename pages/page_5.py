from dash import html, callback, Output, Input, dcc, State
import dash_bootstrap_components as dbc
import yaml

def create_layout():
    layout = html.Div([
        html.H3('Welcome to page 5'), 
        html.P(id="print-storage-page5"),
        dbc.Button("GENERATE REPORT", id='generate_report_button', n_clicks=0),
        html.Div(id='report-contents'),
        html.Div(dbc.Button("PREV", href='/page-4'), className="text-left") 
    ], className="mx-auto py-3 container")
    return layout

# print value in storage
@callback(
    Output('print-storage-page5', 'children'), 
    Input('storage-sector', 'data')
)
def print_store_scenario2(value):
    return f'Storage: {value}'

@callback(
    Output('report-contents', 'children'), 
    Input('generate_report_button', 'n_clicks'),
    State('storage-sector', 'data')
)
def generate_report(n_clicks, sector):

    if n_clicks:

        # open yaml 
        with open('data/exposure_class/agriculture.yml') as f:
            dict = yaml.safe_load(f)    

        # parse yaml
        desc = dict['description']
        transition_high = dict['transition']['high']['always']
        physical_low = dict['physical']['low']['always']

        # create reprot layout
        report_div = [
            html.H4('Description'),
            dcc.Markdown(desc), 
            html.H4('Transition'),
            dcc.Markdown(transition_high, link_target="_blank"),
            html.H4('Physical'),
            dcc.Markdown(physical_low)
        ]
        return report_div   
    return None
    