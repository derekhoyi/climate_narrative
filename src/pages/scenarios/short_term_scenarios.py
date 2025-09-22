import dash
from dash import html, dcc, callback, Output, Input, State, ALL
import dash_bootstrap_components as dbc
import yaml
import json
import re
from pathlib import Path

dash.register_page(__name__, path='/scenarios/short-term-scenarios')


# ---------- Parsing helpers ----------
def extract_sector_sections(desc_text):
    """
    Splits the 'Example of some questions to consider by sector' markdown into:
      - a 'preamble' (the YAML headings you want visible above the tabs), and
      - an ordered dict of {sector_name: sector_markdown (without the sector header line)}.
    """
    sector_names = (
        "Financial Services",
        "Manufacturing",
        "Agriculture",
        "Construction",
        "Energy Underwriting",
    )
    # Match lines like:  "# Financial Services" etc. (multiline mode)
    pattern = re.compile(rf"(?m)^\s*#\s+({'|'.join(map(re.escape, sector_names))})\s*$")
    matches = list(pattern.finditer(desc_text))
    if not matches:
        return "", {}

    # Everything above the first sector header is the "preamble" we keep above the tabs
    preamble = desc_text[: matches[0].start()].strip()

    sectors = {}
    for i, m in enumerate(matches):
        sector = m.group(1)
        start = m.end()  # start right after the header line
        end = matches[i + 1].start() if i + 1 < len(matches) else len(desc_text)
        content = desc_text[start:end].strip()
        sectors[sector] = content

    return preamble, sectors


def build_sector_tabs(sector_desc):
    """
    Builds the UI for the sector section:
      [ YAML headings (preamble) ]
      [ Tabs ]
      [ Selected tab title ]
      [ Selected tab content ]
    """
    preamble, sectors = extract_sector_sections(sector_desc)
    if not sectors:
        # Fallback: show the original markdown if parsing fails
        return dcc.Markdown(sector_desc, className="markdown-body")

    first_sector = next(iter(sectors.keys()))
    first_content = sectors[first_sector]

    return html.Div(
        [
            # YAML headings appear above the tabs
            dcc.Markdown(preamble, className="markdown-body", style={"marginBottom": "0.5rem"}),

            # Tabs (no card wrapper -> no gray background)
            dbc.Tabs(
                id="sector-tabs",
                active_tab=first_sector,
                class_name="custom-tabs",  # styling in assets/short_term_scenarios.css
                children=[
                    dbc.Tab(label=sector, tab_id=sector, tab_class_name="box-style")
                    for sector in sectors.keys()
                ],
            ),

            # Title of the active tab (sector) shown below the tabs
            html.Div(first_sector, id="sector-tab-title", className="sector-title"),

            # Content area below the title
            html.Div(
                dcc.Markdown(first_content, className="markdown-body"),
                id="sector-tab-content",
                className="bg-transparent",
                style={"backgroundColor": "transparent"},
            ),

            # Store the sector markdown blocks for the tab callback
            dcc.Store(id="sector-content-store", data=sectors),
        ],
        className="p-0",
        style={"backgroundColor": "transparent"},
    )


# ---------- Page layout ----------
def layout():
    # define paths
    YML_FOLDER = "../../assets/page_contents/section/scenarios"
    YML_NAME = "short_term_scenarios.yml"
    FILE_PATH = Path(__file__).parent
    YML_PATH = FILE_PATH.joinpath(YML_FOLDER).joinpath(YML_NAME).resolve()

    # open yaml
    with open(YML_PATH, encoding="utf-8") as f:
        yml = yaml.safe_load(f)

    # Left-side buttons for each YAML section
    button_list = []
    for k, v in yml.items():
        button_list.append(
            dbc.Button(
                v['name'],
                id={'type': 'short_scenario-btn', 'index': k},
                class_name="btn-light text-start",
                n_clicks=0,
                active=(k == 1),  # default active button
            ),
        )

    # Default content (Markdown)
    default_desc = yml[1]['description']

    # Layout
    return html.Div(
        [
            dcc.Store(id='yml-store', data=json.dumps(yml), storage_type='memory'),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.ButtonGroup(button_list, vertical=True),
                        md=3,
                        class_name="sidebar-btn-group"
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


# ---------- Callbacks ----------
@callback(
    Output('short_scenario-description', 'children'),
    Output({'type': 'short_scenario-btn', 'index': ALL}, 'active'),
    Input({'type': 'short_scenario-btn', 'index': ALL}, 'n_clicks'),
    State('yml-store', 'data'),
    prevent_initial_call=True
)
def display_scenario(n_clicks, yml_data):
    """
    When a left-side button is clicked, either:
      - render the sector tabs (for the 'Example of some questions...' section), or
      - render the section markdown directly.
    Also returns the 'active' state array for the button group.
    """
    yml = json.loads(yml_data)
    prop_id = dash.callback_context.triggered[0]['prop_id']
    json_str = prop_id.split('.')[0]
    button_id = json.loads(json_str)
    index = button_id['index']

    # yml loaded from json has string keys
    desc_yml = yml[str(index)]['description']
    name_yml = yml[str(index)]['name']

    if name_yml.lower().startswith("example of some questions"):
        content = build_sector_tabs(desc_yml)
    else:
        content = dcc.Markdown(desc_yml, className="markdown-body")

    # Mark only the clicked index as active
    active_map = [i == str(index) for i in yml.keys()]
    return content, active_map


@callback(
    Output("sector-tab-content", "children"),
    Output("sector-tab-title", "children"),
    Input("sector-tabs", "active_tab"),
    State("sector-content-store", "data"),
    prevent_initial_call=False  # allow initial render (content/title already pre-set)
)
def render_sector_tab(active_tab, sectors):
    """
    Updates the sector content and the title when a tab is changed.
    """
    if not sectors:
        return html.Div("No sector content found."), ""

    if not active_tab or active_tab not in sectors:
        first_key = next(iter(sectors.keys()))
        return dcc.Markdown(sectors[first_key], className="markdown-body"), first_key

    return dcc.Markdown(sectors[active_tab], className="markdown-body"), active_tab
