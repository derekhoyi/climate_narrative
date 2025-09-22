import dash
from dash import html, dcc, callback, Output, Input, State, ALL, page_registry
import dash_bootstrap_components as dbc
import yaml
import json
from pathlib import Path
import importlib

dash.register_page(__name__, path='/charts')


def _load_embedded_for(path_hint: str):
    """
    Find the Dash page whose (relative_)path matches path_hint and call its
    `embedded_content()` factory. This avoids direct `import ph_chart`.
    """
    # Example path_hints we’ll pass: "/charts/ph_chart", "/charts/tr_chart"
    for page in page_registry.values():
        # page keys include: 'path', 'relative_path', 'module', ...
        if page.get("path") == path_hint or page.get("relative_path") == path_hint:
            module_name = page["module"]            # e.g. "pages.ph_chart"
            mod = importlib.import_module(module_name)
            if hasattr(mod, "embedded_content"):
                return mod.embedded_content()
            return html.Div(
                f"Module '{module_name}' is missing embedded_content().",
                className="text-danger",
            )

    # If we get here, Dash didn’t discover the page at all.
    return html.Div(
        f"Could not find a page for '{path_hint}'. "
        f"Check that the file lives under your 'pages/' folder and that the app "
        f"is created with Dash(..., use_pages=True).",
        className="text-danger",
    )


def layout():
    # define paths
    YML_FOLDER = "../../assets/page_contents/section"
    YML_NAME = "charts.yml"
    FILE_PATH = Path(__file__).parent
    YML_PATH = FILE_PATH.joinpath(YML_FOLDER).joinpath(YML_NAME).resolve()

    # default index -> Physical Risk (matches "1:" in YAML)
    DEFAULT_INDEX = 1

    # open yaml
    with open(YML_PATH, encoding="utf-8") as f:
        yml = yaml.safe_load(f)

    # buttons from YAML
    button_list = []
    for k, v in yml.items():
        button_list.append(
            dbc.Button(
                v['name'],
                id={'type': 'charts-btn', 'index': k},
                class_name="btn-light text-start w-100 mb-2",
                n_clicks=0,
                active=(k == DEFAULT_INDEX),
            )
        )

    # default description
    default_desc = dcc.Markdown(
        yml[DEFAULT_INDEX]['description'],
        link_target="_blank"
    )

    # default embedded content under the description (Physical Risk)
    default_content = _load_embedded_for("/charts/ph_chart")

    return html.Div(
        [
            dcc.Store(id='yml-store', data=json.dumps(yml), storage_type='memory'),

            dbc.Row(
                [
                    dbc.Col(
                        dbc.ButtonGroup(button_list, vertical=True),
                        md=3,
                        class_name="sidebar-btn-group",
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.Div(default_desc, id='charts-description'),
                                html.Hr(),
                                html.Div(default_content, id='charts-content'),
                            ]
                        ),
                        md=9,
                    ),
                ]
            ),
        ],
        className="container"
    )


@callback(
    [
        Output('charts-description', 'children'),
        Output('charts-content', 'children'),
        Output({'type': 'charts-btn', 'index': ALL}, 'active'),
    ],
    Input({'type': 'charts-btn', 'index': ALL}, 'n_clicks'),
    State('yml-store', 'data'),
    prevent_initial_call=True
)
def display_charts(n_clicks, yml_data):
    yml = json.loads(yml_data)

    # which button was clicked?
    prop_id = dash.callback_context.triggered[0]['prop_id']
    json_str = prop_id.split('.')[0]
    button_id = json.loads(json_str)
    index = button_id['index']  # numeric in the id; YAML keys are strings

    # description from YAML
    desc_yml = yml[str(index)]['description']
    name_yml = yml[str(index)]['name']
    desc = dcc.Markdown(desc_yml, link_target="_blank")

    # choose which embedded content to render under the description
    name_l = name_yml.lower()
    if name_l.startswith("physical"):
        content = _load_embedded_for("/charts/ph_chart")
    elif name_l.startswith("transition"):
        content = _load_embedded_for("/charts/tr_chart")
    else:
        content = html.Div()

    # highlight the active button
    active = [i == str(index) for i in yml.keys()]

    return desc, content, active
