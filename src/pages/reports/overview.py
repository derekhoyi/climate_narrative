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
    desc_yml = html.Div(dcc.Markdown(yml["overview"], link_target="_blank", dangerously_allow_html=True, style={'textTransform': 'none'}))

    # Select report button
    select_report_button = dbc.Button("Select report", id="select-report-btn", color="success", class_name="mb-3")

    # layout
    layout = html.Div([
        html.H1('Reports'),
        html.H3('Overview'),
        html.P(desc_yml),
	    select_report_button
    ], className="container")
    return layout
