import dash
from dash import html, dcc
import yaml
from pathlib import Path

dash.register_page(__name__, path='/purpose/purpose-overview')


def layout():

    # define paths
    YML_FOLDER = "../../../assets/page_contents/section/purpose"
    YML_NAME = "purpose_overview.yml"
    FILE_PATH = Path(__file__).parent
    YML_PATH = FILE_PATH.joinpath(YML_FOLDER).joinpath(YML_NAME).resolve()
    print('yml path', YML_PATH)

    # open yaml
    with open(YML_PATH, encoding="utf-8") as f:
        yml = yaml.safe_load(f)

    # create layout
    layout = html.Div([
        dcc.Markdown(yml['description'])
    ], className="mx-auto py-3 container")
    return layout
