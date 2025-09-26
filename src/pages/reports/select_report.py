import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from utils import data_loader
import pandas as pd

dash.register_page(__name__, path='/reports/select-report')

def layout():
    layout = html.Div([
        dcc.Location(id='select-report-url'),
        html.H1('Reports'),
        html.H3('Select report'),
        html.P('The tool can generate three types of reports:'),
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
        desc_title = dcc.Markdown(report_type, link_target="_blank", dangerously_allow_html=True, className='h4 fw-bolder text-white')
        desc_yml = dcc.Markdown(yml[report_type.lower()], link_target="_blank", dangerously_allow_html=True, className='display-12', style={'textTransform': 'none'})
        desc = html.Div([desc_title, desc_yml])

        button_list.append(
            dbc.Col(
                dbc.Button(
                    desc,
                    id={"type": "report-type-btn", "index": report_type},
                    color='success',
                    class_name='rounded-4 w-100 h-100 align-items-start justify-content-center d-flex pt-4',
                )
            )
        )
    return button_list

@callback(
    Output("report-type-store", "data"),
    Output('user-selection-completed-store', 'data', allow_duplicate=True),
    Output({"type": "report-type-btn", "index": dash.ALL}, "href"),
    Output("select-report-url", "href"),
    Input({"type": "report-type-btn", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True
)
def store_report_type(btn_clicks):
    triggered_list = dash.callback_context.triggered
    button_clicked = [x for x in triggered_list if x['value']]
    if button_clicked:
        button_clicked_report_type = eval(button_clicked[0]['prop_id'].split('.')[0])['index']
        button_clicked_href = f'/reports/customise-report?report-type={button_clicked_report_type}'
        href_list = []
        for x in dash.callback_context.inputs:
            report_type = eval(x.split('.')[0])['index']
            url_pathname = f'/reports/customise-report?report-type={report_type}'
            if report_type == button_clicked_report_type:
                href_list.append(url_pathname)
            else:
                href_list.append(dash.no_update)
        return button_clicked_report_type, None, href_list, button_clicked_href
    return dash.no_update, dash.no_update, [dash.no_update] * len(btn_clicks), dash.no_update
