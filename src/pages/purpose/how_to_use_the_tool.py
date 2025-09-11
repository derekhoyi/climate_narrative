import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import yaml
from pathlib import Path

dash.register_page(__name__, path='/purpose/how-to-use-the-tool')


def layout():

    # define paths
    YML_FOLDER = "../../../assets/page_contents/section/purpose"
    YML_NAME = "how_to_use_the_tool.yml"
    FILE_PATH = Path(__file__).parent
    YML_PATH = FILE_PATH.joinpath(YML_FOLDER).joinpath(YML_NAME).resolve()

    # create header
    header = html.Div(
        html.H2("HOW TO USE THE TOOL", style={"color": "#51C876", "margin": "0"}),
        style={
            "backgroundColor": "#fff",  # white background
            "borderRadius": "8px",
            "textAlign": "left",
            "padding": "5px 0",
            "marginBottom": "10px"
        }
    )

    # open yaml
    with open(YML_PATH, encoding="utf-8") as f:
        yml = yaml.safe_load(f)

    # create layout
    layout = html.Div([
        header,
        dcc.Markdown(yml['description']),
        dbc.Button("Generate report", href='/reports/generate-report')
    ], className="container")
    return layout
