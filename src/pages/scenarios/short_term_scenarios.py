import dash
from dash import html, dcc, callback, Output, Input, State, ALL
import dash_bootstrap_components as dbc
import yaml
import json
import re
from pathlib import Path

dash.register_page(__name__, path='/scenarios/short-term-scenarios')

def extract_sector_sections(desc_text):
    """
    Extracts sector sections (**Financial Services**, **Manufacturing**, etc.) from the description text.
    Returns a dict: {sector_name: sector_markdown}
    """
    sector_pattern = r"\# (Financial Services|Manufacturing|Agriculture|Construction|Energy Underwriting)"
    matches = list(re.finditer(sector_pattern, desc_text))
    sectors = {}
    for i, match in enumerate(matches):
        sector_name = match.group(1)
        start = match.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(desc_text)
        sector_content = desc_text[start:end].strip()
        sectors[sector_name] = sector_content
    return sectors

def build_sector_tabs(sector_desc):
    sectors = extract_sector_sections(sector_desc)
    if not sectors:
        return html.Div("No sector content found.")
    tabs = [
        dbc.Tab(
            dcc.Markdown(content, className="markdown-body"),
            label=sector,
            tab_id=sector
        )
        for sector, content in sectors.items()
    ]
    return dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs(
                    tabs,
                    id="sector-tabs",
                    active_tab=list(sectors.keys())[0],
                    class_name="box-style"
                )
            ),
            dbc.CardBody(
                id="sector-tab-content"
            ),
            dcc.Store(id="sector-content-store", data=sectors)
        ]
    )

def layout():
    # define paths
    YML_FOLDER = "../../assets/page_contents/section/scenarios"
    YML_NAME = "short_term_scenarios.yml"
    FILE_PATH = Path(__file__).parent
    YML_PATH = FILE_PATH.joinpath(YML_FOLDER).joinpath(YML_NAME).resolve()

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
                active=(k == 1)  # default active button
            ),
        )

    # default description (Markdown only)
    default_desc = yml[1]['description']

    # layout
    return html.Div(
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
                            dcc.Markdown(default_desc, className="markdown-body"),
                            id='short_scenario-description'
                        )
                    ),
                ]
            ),
        ],
        className="container"
    )

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
    name_yml = yml[str(index)]['name']
    # If this is the sector section, show tabs
    if name_yml.lower().startswith("example of some questions"):
        return build_sector_tabs(desc_yml), [i == str(index) for i in yml.keys()]
    # Otherwise, show Markdown
    return dcc.Markdown(desc_yml, className="markdown-body"), [i == str(index) for i in yml.keys()]

@callback(
    Output("sector-tab-content", "children"),
    Input("sector-tabs", "active_tab"),
    State("sector-content-store", "data"),
    prevent_initial_call=True
)
def render_sector_tab(active_tab, sectors):
    if not sectors or not active_tab:
        return html.Div("No sector content found.")
    return dcc.Markdown(sectors[active_tab], className="markdown-body")
