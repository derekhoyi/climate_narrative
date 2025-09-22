import dash
from dash import html, dcc, callback, Output, Input, State, ALL
import dash_bootstrap_components as dbc
import yaml
import json
from pathlib import Path
import re

dash.register_page(__name__, path='/sectors/sector')

def layout():
    # define paths
    YML_FOLDER = "../../assets/page_contents/exposure_class/sector"
    FILE_PATH = Path(__file__).parent
    YML_DIR = FILE_PATH.joinpath(YML_FOLDER).resolve()
    # define default index
    DEFAULT_INDEX = 1
    # Load all YML files in the folder
    yml = {}
    for yml_file in YML_DIR.glob("*.yml"):
        with open(yml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            # Merge or append sectors; assumes each file is a dict of sectors
            yml.update(data)
    # create buttons
    button_list = []
    for k, v in yml.items():
        clean_name = re.sub(r'class\nsector', '', v['name'], flags=re.IGNORECASE).strip()
        button_list.append(
            dbc.Button(
                clean_name,
                id={'type': 'sector1-btn', 'index': k},
                class_name="btn-light text-start",
                n_clicks=0,
                active=(k == DEFAULT_INDEX)  # set default active button
            ),
        )
    # default description and title
    default_name = yml[DEFAULT_INDEX]['name']
    default_desc = yml[DEFAULT_INDEX]['description']
    default_content = html.Div([
        html.H1(default_name, className="mt-3 mb-2"),
        dcc.Markdown(default_desc, link_target="_blank")
    ])
    
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
                            default_content,
                            id='sector1-description'
                        )
                    ),
                ],
            ),
        ],
        className="container"
    )
    return layout

# display sector
@callback(
    [Output('sector1-description', 'children'),
     Output({'type': 'sector1-btn', 'index': ALL}, 'active')],
    Input({'type': 'sector1-btn', 'index': ALL}, 'n_clicks'),
    State('yml-store', 'data'),
    prevent_initial_call=True
)
def display_sector1(n_clicks, yml_data):
    # load yml
    yml = json.loads(yml_data)
    # determine which button was clicked
    prop_id = dash.callback_context.triggered[0]['prop_id']
    json_str = prop_id.split('.')[0]
    button_id = json.loads(json_str)
    index = button_id['index']
    # get name and description from yml
    name_yml = yml[str(index)]['name']
    desc_yml = yml[str(index)]['description']
    content = html.Div([
        html.H1(name_yml, className="mt-3 mb-2"),
        dcc.Markdown(desc_yml, link_target="_blank")
    ])
    # set active button
    active = [i == str(index) for i in yml.keys()]
    return content, active
