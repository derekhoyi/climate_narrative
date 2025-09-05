import dash
from dash import html, dcc
import yaml
from pathlib import Path

dash.register_page(__name__, path='/purpose/introduction-to-the-tool')


def layout():

    # define paths
    YML_FOLDER = "../../../assets/page_contents/section/purpose"
    YML_NAME = "introduction_to_the_tool.yml"
    FILE_PATH = Path(__file__).parent
    YML_PATH = FILE_PATH.joinpath(YML_FOLDER).joinpath(YML_NAME).resolve()

    # open yaml
    with open(YML_PATH, encoding="utf-8") as f:
        yml = yaml.safe_load(f)

    # create layout
    layout = html.Div([
        dcc.Markdown(yml['description'])
    ], className="container")
    return layout
