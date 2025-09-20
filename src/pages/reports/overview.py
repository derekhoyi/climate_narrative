import dash
from dash import html, dcc
import yaml
from pathlib import Path
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/reports/overview')


def layout():

    # define paths
    YML_FOLDER = "../../assets/page_contents/section/reports"
    FILE_PATH = Path(__file__).parent

    # get overview markdown from yml
    YML_PATH = FILE_PATH.joinpath(YML_FOLDER).joinpath('summary_description.yml').resolve()
    with open(YML_PATH, encoding="utf-8") as f:
        yml = yaml.safe_load(f)
    desc_yml = html.Div(dcc.Markdown(yml["overview"], link_target="_blank", dangerously_allow_html=True, className='small', style={'textTransform': 'none'}))

    # Generate report button
    generate_report_button = dbc.Button("Select report", href='/reports/select-report', color="success", class_name="mb-3")

    # layout
    layout = html.Div([
        html.H3('Report overview', className="text-success fw-bold"),
        html.P(desc_yml),
	    generate_report_button
    ], className="container")
    return layout
