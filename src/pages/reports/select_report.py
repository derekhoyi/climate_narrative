import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from src.utils import data_loader
import pandas as pd

dash.register_page(__name__, path='/reports/select-report')

def layout():
    layout = html.Div([
        dcc.Location(id='select-report-url'),
        html.H3('Generate report', className="text-success fw-bold"),
        html.P('The tool can generate four types of reports:'),
        dbc.Container(dbc.Row(id="report-type-buttons", class_name="d-flex g-4 align-items-stretch"), fluid=True),
    ], className="container")
    return layout


@callback(
    Output("report-type-buttons", "children"),
    Input("output-structure-mapping-store", "data"),
)
def report_type_buttons(output_structure_mapping_dict):
    button_list = []
    output_structure_mapping_df = pd.DataFrame(output_structure_mapping_dict)
    yml = data_loader.load_yml_file('section/reports', 'button_description.yml')
    for i, report_type in enumerate(output_structure_mapping_df['report_type'].unique()):
        # get markdown from yml
        desc_title = dcc.Markdown(report_type, link_target="_blank", className='h4 fw-bolder text-white')
        desc_yml = dcc.Markdown(yml[report_type.lower()], link_target="_blank", className='display-12', style={'textTransform': 'none'})
        desc = html.Div([desc_title, desc_yml])

        button_list.append(
            dbc.Col(
                dbc.Button(
                    desc,
                    id=f'{report_type.lower()}-btn',
                    color='success',
                    class_name='rounded-4 w-100 h-100 align-items-start justify-content-center d-flex pt-4',
                    href=f'/reports/customise-{report_type.lower()}-report',
                ), xs=12, sm=6, md=4, lg=3
            )
        )
    return button_list
