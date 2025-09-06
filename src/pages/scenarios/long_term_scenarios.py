import dash
from dash import html, dcc, callback, Output, Input, State, MATCH, ALL, dcc
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import yaml
import json
from pathlib import Path

dash.register_page(__name__, path='/scenarios/long-term-scenarios')


def layout():

    # define paths
    YML_FOLDER = "../../../assets/page_contents/section/scenarios"
    YML_NAME = "long_term_scenarios.yml"
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
                id={'type': 'scenario-btn', 'index': k},
                class_name="btn-light text-start",
                n_clicks=0
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
                        width="auto",
                    ),
                    dbc.Col(
                        html.Div(
                            default_desc,
                            id='scenario-description'
                        )
                    ),
                ]
            ),
        ],
        className="container"
    )
    return layout


# display scenario
@callback(
    Output('scenario-description', 'children'),
    Input({'type': 'scenario-btn', 'index': ALL}, 'n_clicks'),
    State('yml-store', 'data'),
    prevent_initial_call=True
)
def display_scenario(n_clicks, yml_data):

    # load yml
    yml = json.loads(yml_data)

    # determine which button was clicked
    prop_id = dash.callback_context.triggered[0]['prop_id']
    json_str = prop_id.split('.')[0]
    button_id = json.loads(json_str)
    index = button_id['index']  
    # print('Clicked index:', index)

    # get markdown from yml
    desc_yml = yml[str(index)]['description']
    desc = dcc.Markdown(desc_yml, link_target="_blank")

    return desc
