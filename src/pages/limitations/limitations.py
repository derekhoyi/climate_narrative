import dash
from dash import html, dcc, callback, Output, Input, State, ALL
import dash_bootstrap_components as dbc
import yaml
import json
from pathlib import Path
import re

dash.register_page(__name__, path='/limitations')

def layout():
    # define paths
    YML_FOLDER = "../../assets/page_contents/section/limitations"
    FILE_PATH = Path(__file__).parent
    YML_DIR = FILE_PATH.joinpath(YML_FOLDER).resolve()

    # define default index
    DEFAULT_INDEX = 1

    # Load all YML files in the folder
    yml = {}
    for yml_file in YML_DIR.glob("*.yml"):
        with open(yml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            # Merge or append limitation sections; assumes each file is a dict of limitation sections
            yml.update(data)

    # create buttons
    button_list = []
    for k, v in yml.items():
        clean_name = re.sub(r'limitations', '', v['name'], flags=re.IGNORECASE).strip()
        button_list.append(
            dbc.Button(
                clean_name,
                id={'type': 'limitations-btn', 'index': k},
                class_name="btn-light text-start",
                n_clicks=0,
                active=(k == DEFAULT_INDEX)  # set default active button
            ),
        )

    # default description
    default_desc = dcc.Markdown(
        yml[DEFAULT_INDEX]['description'],
        link_target="_blank"
    )

    # layout
    layout = html.Div(
        [
            dcc.Store(
                id='yml-store',
                data=json.dumps(yml),
                storage_type='memory'
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.ButtonGroup(button_list, vertical=True),
                        style={'height': '600px', 'overflowY': 'auto'},
                        md=3,
                        class_name="sidebar-btn-group"
                    ),
                    dbc.Col(
                        html.Div(
                            default_desc,
                            id='limitations-description'
                        )
                    ),
                ]
            ),
        ],
        className="container"
    )
    return layout


# display sector
@callback(
    [Output('limitations-description', 'children'),
     Output({'type': 'limitations-btn', 'index': ALL}, 'active')],
    Input({'type': 'limitations-btn', 'index': ALL}, 'n_clicks'),
    State('yml-store', 'data'),
    prevent_initial_call=True
)
def display_sector(n_clicks, yml_data):

    # load yml
    yml = json.loads(yml_data)

    # determine which button was clicked
    prop_id = dash.callback_context.triggered[0]['prop_id']
    json_str = prop_id.split('.')[0]
    button_id = json.loads(json_str)
    index = button_id['index']

    # get markdown from yml
    desc_yml = yml[str(index)]['description']
    desc = dcc.Markdown(desc_yml, link_target="_blank")

    # set active button
    active = [i == str(index) for i in yml.keys()]

    return desc, active
