import dash
from dash import html, dcc, callback, Output, Input, State, ALL, no_update
import dash_bootstrap_components as dbc
import yaml
import json
from pathlib import Path
import re

dash.register_page(__name__, path='/sectors/underwriting')

# Compile once for performance/readability
_NAME_CLEAN_RE = re.compile(r'class|sector|underwriting', flags=re.IGNORECASE)

def _clean(name: str) -> str:
    """Remove boilerplate and trim for display/sorting."""
    return _NAME_CLEAN_RE.sub('', (name or '')).strip()

def layout():
    # define paths
    YML_FOLDER = "../../assets/page_contents/exposure_class/underwriting"
    FILE_PATH = Path(__file__).parent
    YML_DIR = FILE_PATH.joinpath(YML_FOLDER).resolve()

    # --- Load & merge all YML files deterministically
    merged = {}
    for yml_file in sorted(YML_DIR.glob("*.yml")):  # sorted -> deterministic merge order
        with open(yml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            merged.update(data)

    # Normalize keys to strings (JSON object keys are strings)
    yml = {str(k): v for k, v in merged.items()}

    if not yml:
        # Graceful empty-state
        return html.Div(
            [
                html.Div("No sectors found."),
            ],
            className="container",
        )

    # --- Compute a stable alphabetical order (case-insensitive, Unicode-friendly)
    order = sorted(yml.keys(), key=lambda k: _clean(yml[k]["name"]).casefold())

    # Default selection: keep '1' if present, else first alphabetically
    DEFAULT_INDEX = "1" if "1" in yml else order[0]

    # --- Build buttons in the computed order
    button_list = []
    for k in order:
        v = yml[k]
        clean_name = _clean(v["name"])
        button_list.append(
            dbc.Button(
                clean_name,
                id={"type": "sector3-btn", "index": k},
                class_name="btn-light text-start",
                n_clicks=0,
                active=(k == DEFAULT_INDEX),
            )
        )

    # --- Default content
    default_name = yml[DEFAULT_INDEX]["name"]
    default_desc = yml[DEFAULT_INDEX]["description"]
    default_content = html.Div(
        [
            html.H1(default_name, className="mt-3 mb-2"),
            dcc.Markdown(default_desc, link_target="_blank"),
        ]
    )

    # --- Layout (store both the data and the render order)
    return html.Div(
        [
            dcc.Store(id="yml-store", data=json.dumps(yml), storage_type="memory"),
            dcc.Store(id="order-store", data=json.dumps(order), storage_type="memory"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.ButtonGroup(button_list, vertical=True),
                        style={"height": "600px", "overflowY": "auto"},
                        md=3,
                        class_name="sidebar-btn-group",
                    ),
                    dbc.Col(html.Div(default_content, id="sector3-description")),
                ],
            ),
        ],
        className="container",
    )

# --- Display sector / set active states
@callback(
    [
        Output("sector3-description", "children"),
        Output({"type": "sector3-btn", "index": ALL}, "active"),
    ],
    Input({"type": "sector3-btn", "index": ALL}, "n_clicks"),
    State("yml-store", "data"),
    State("order-store", "data"),
    prevent_initial_call=True,
)
def display_sector3(n_clicks, yml_data, order_data):
    yml = json.loads(yml_data)
    order = json.loads(order_data)

    # Determine which button fired
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update, no_update
    btn = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    index = str(btn["index"])

    # Build content
    name_yml = yml[index]["name"]
    desc_yml = yml[index]["description"]
    content = html.Div(
        [
            html.H1(name_yml, className="mt-3 mb-2"),
            dcc.Markdown(desc_yml, link_target="_blank"),
        ]
    )

    # Active flags must align with the same order used to render the buttons
    active = [k == index for k in order]
    return content, active
