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

    # Load all YML files in the folder
    yml = {}
    for yml_file in YML_DIR.glob("*.yml"):
        with open(yml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            yml.update(data)

    # --- SORT KEYS BY SECTOR NAME ---
    # Create a list of (key, value) tuples sorted by the 'name' field (case-insensitive)
    sorted_items = sorted(
        yml.items(),
        key=lambda item: item[1]['name'].lower()
    )

    # Use the first sorted item as default
    default_key, default_val = sorted_items[0]
    default_name = default_val['name']
    default_desc = default_val['description']
    default_content = html.Div([
        html.H1(default_name, className="mt-3 mb-2"),
        dcc.Markdown(default_desc, link_target="_blank")
    ])

    # create buttons (in sorted order)
    button_list = []
    for k, v in sorted_items:
        clean_name = re.sub(r'class\nsector', '', v['name'], flags=re.IGNORECASE).strip()
        button_list.append(
            dbc.Button(
                clean_name,
                id={'type': 'sector1-btn', 'index': k},
                class_name="btn-light text-start",
                n_clicks=0,
                active=(k == default_key)  # set default active button
            ),
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
    [
        Output('sector1-description', 'children'),
        Output({'type': 'sector1-btn', 'index': ALL}, 'active')
    ],
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
    # set active button (order must match the sorted order)
    # To ensure correct highlighting, get the sorted keys
    sorted_keys = [k for k, v in sorted(
        yml.items(), key=lambda item: item[1]['name'].lower()
    )]
    active = [k == index for k in sorted_keys]
    return content, active
