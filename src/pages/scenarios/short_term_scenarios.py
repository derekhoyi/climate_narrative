import dash
from dash import html, dcc, callback, Output, Input, State, ALL
import dash_bootstrap_components as dbc
import yaml
import json
from pathlib import Path

dash.register_page(__name__, path='/scenarios/short-term-scenarios')

def _build_description_components(desc_text: str):
    # Render the Markdown, including the table, with the custom CSS class
    return [dcc.Markdown(desc_text, link_target="_blank", className="markdown-body")]

def layout():
    # define paths
    YML_FOLDER = "../../../assets/page_contents/section/scenarios"
    YML_NAME = "short_term_scenarios.yml"
    FILE_PATH = Path(__file__).parent
    YML_PATH = FILE_PATH.joinpath(YML_FOLDER).joinpath(YML_NAME).resolve()
    # define default index
    DEFAULT_INDEX = 1
    # open yaml
    with open(YML_PATH, encoding="utf-8") as f:
        yml = yaml.safe_load(f)
    # create buttons
    button_list = []
    for k, v in yml.items():
        button_list.append(
            dbc.Button(
                v['name'],
                id={'type': 'short_scenario-btn', 'index': k},
                class_name="btn-light text-start",
                n_clicks=0,
                active=(k == DEFAULT_INDEX)  # set default active button
            ),
        )
    # default description (Markdown only)
    default_desc_components = _build_description_components(
        yml[DEFAULT_INDEX]['description']
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
                        md=3,
                        class_name="mb-3"
                    ),
                    dbc.Col(
                        html.Div(
                            default_desc_components,  # list of components
                            id='short_scenario-description'
                        )
                    ),
                ]
            ),
        ],
        className="container"
    )
    return layout

@callback(
    Output('short_scenario-description', 'children'),
    Output({'type': 'short_scenario-btn', 'index': ALL}, 'active'),
    Input({'type': 'short_scenario-btn', 'index': ALL}, 'n_clicks'),
    State('yml-store', 'data'),
    prevent_initial_call=True
)
def display_scenario(n_clicks, yml_data):
    yml = json.loads(yml_data)
    prop_id = dash.callback_context.triggered[0]['prop_id']
    json_str = prop_id.split('.')[0]
    button_id = json.loads(json_str)
    index = button_id['index']
    desc_yml = yml[str(index)]['description']
    desc_components = _build_description_components(desc_yml)
    active = [i == str(index) for i in yml.keys()]
    return desc_components, active
