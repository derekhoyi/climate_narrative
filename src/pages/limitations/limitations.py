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

    # define default index as string for consistency with JSON keys
    DEFAULT_INDEX = "1"

    # Load all YML files in the folder -> normalized dict with string keys
    sections = {}
    # Read files (order here won't matter anymore)
    for yml_file in YML_DIR.glob("*.yml"):
        with open(yml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            # normalize keys to strings; last write wins if duplicate keys appear
            for k, v in data.items():
                sections[str(k)] = v

    # Fixed, deterministic order by numeric key (1, 2, 3)
    order = sorted(sections.keys(), key=lambda x: int(x))

    # helper to create the exact labels the user wants
    def prettify_label(name: str) -> str:
        # remove the word 'limitations' anywhere, tidy whitespace
        base = re.sub(r'limitations', '', name, flags=re.IGNORECASE).strip()
        lower = base.lower()
        if 'overview' in lower:
            return 'Overview'
        if 'long' in lower:
            return 'Long-term scenario'
        if 'short' in lower:
            return 'Short-term scenario'
        # fallback (shouldn't be needed here)
        return base
    # create buttons in the exact deterministic order
    button_list = []
    for k in order:
        v = sections[k]
        label = prettify_label(v.get('name', f'Section {k}'))
        button_list.append(
            dbc.Button(
                label,
                id={'type': 'limitations-btn', 'index': k},  # keep index as string
                class_name="btn-light text-start",
                n_clicks=0,
                active=(k == DEFAULT_INDEX)  # default active button
            )
        )

    # default description (from DEFAULT_INDEX)
    default_desc = dcc.Markdown(
        sections.get(DEFAULT_INDEX, {}).get('description', ''),
        link_target="_blank"
    )

    # Store both the sections and the fixed order to reuse in the callback
    store_payload = {'sections': sections, 'order': order}

    # layout
    layout = html.Div(
        [
            dcc.Store(
                id='yml-store',
                data=json.dumps(store_payload),
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


# display section
@callback(
    [
        Output('limitations-description', 'children'),
        Output({'type': 'limitations-btn', 'index': ALL}, 'active')
    ],
    Input({'type': 'limitations-btn', 'index': ALL}, 'n_clicks'),
    State('yml-store', 'data'),
    prevent_initial_call=True
)
def display_sector(n_clicks, yml_data):
    # load sections and fixed order from the store
    payload = json.loads(yml_data)
    sections = payload['sections']
    order = payload['order']  # order is a list of string keys, e.g. ["1","2","3"]

    # determine which button was clicked
    ctx = dash.callback_context
    prop_id = ctx.triggered[0]['prop_id']  # e.g. {"type":"limitations-btn","index":"2"}.n_clicks
    json_str = prop_id.split('.')[0]
    button_id = json.loads(json_str)
    index = str(button_id['index'])  # ensure string key

    # get markdown for the clicked section
    desc_yml = sections.get(index, {}).get('description', '')
    desc = dcc.Markdown(desc_yml, link_target="_blank")

    # set active buttons aligned to the fixed deterministic order used in layout
    active = [key == index for key in order]

    return desc, active
