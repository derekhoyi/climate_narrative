import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import yaml
import json
from pathlib import Path

dash.register_page(__name__, path="/purpose")

# Fixed, required section order by display name
SECTION_ORDER = [
    "Overview",
    "Introduction to the tool",
    "How to use the tool",
    "How can the reports be used",
    "What is next",
]

def _norm(s: str) -> str:
    """Normalize a section name for robust matching."""
    return " ".join((s or "").strip().lower().split())

def layout():
    # --- define paths
    YML_FOLDER = "../../assets/page_contents/section/purpose"
    FILE_PATH = Path(__file__).parent
    YML_DIR = FILE_PATH.joinpath(YML_FOLDER).resolve()

    # --- load and merge all YML files
    # Expected structure per YML: { "<key>": {"name": "...", "description": "..."} }
    merged = {}
    for yml_file in YML_DIR.glob("*.yml"):
        with open(yml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            # Last-in update wins, which is fine since we will reindex and sort deterministically
            merged.update(data)

    # --- convert to a list of sections and sort deterministically by SECTION_ORDER
    # We sort by the position of v["name"] in SECTION_ORDER (unknown names go to the end, alphabetical)
    order_lookup = { _norm(name): i for i, name in enumerate(SECTION_ORDER) }
    items_unsorted = []
    for _, v in merged.items():
        # Defensive defaults
        name = (v or {}).get("name", "").strip()
        desc = (v or {}).get("description", "")
        items_unsorted.append({
            "name": name,
            "description": desc,
            "_sort_key": (order_lookup.get(_norm(name), 10_000), name.lower())
        })

    # Sort by our tuple: first the configured order, then name for stability
    items_unsorted.sort(key=lambda x: x["_sort_key"])

    # Reindex deterministically as "0", "1", ... and drop helper keys
    indexed = {}
    keys = []
    for i, item in enumerate(items_unsorted):
        k = str(i)
        keys.append(k)
        indexed[k] = {"name": item["name"], "description": item["description"]}

    # Handle empty case gracefully
    if not keys:
        empty_msg = dcc.Markdown(
            "> No purpose sections found. Please add *.yml files under `assets/page_contents/section/purpose`.",
            link_target="_blank",
        )
        return html.Div(
            [html.Div(empty_msg, id="purpose-description")],
            className="container"
        )

    # --- default selection: first item
    DEFAULT_INDEX = "0"
    default_desc = dcc.Markdown(indexed[DEFAULT_INDEX]["description"], link_target="_blank")

    # --- create buttons in the deterministic order
    button_list = []
    for k in keys:
        button_list.append(
            dbc.Button(
                indexed[k]["name"],
                id={"type": "purpose-btn", "index": k},
                class_name="btn-light text-start",
                n_clicks=0,
                active=(k == DEFAULT_INDEX),
            )
        )

    # --- layout
    return html.Div(
        [
            dcc.Store(
                id="yml-store",
                # Keep both the map and explicit order for reliable callback behavior
                data=json.dumps({"items": indexed, "order": keys}),
                storage_type="memory",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.ButtonGroup(button_list, vertical=True),
                        style={"height": "600px", "overflowY": "auto"},
                        md=3,
                        class_name="sidebar-btn-group",
                    ),
                    dbc.Col(html.Div(default_desc, id="purpose-description")),
                ]
            ),
        ],
        className="container",
    )


# --- callback: display section and update active state
@callback(
    [
        Output("purpose-description", "children"),
        Output({"type": "purpose-btn", "index": dash.ALL}, "active"),
    ],
    Input({"type": "purpose-btn", "index": dash.ALL}, "n_clicks"),
    State("yml-store", "data"),
    prevent_initial_call=True,
)
def display_sector(_n_clicks, yml_data):
    # Load stored data
    data = json.loads(yml_data or "{}")
    items = data.get("items", {})
    order = data.get("order", [])

    # Identify which button fired
    ctx = dash.callback_context
    if not ctx.triggered:
        # Fallback to first item if nothing triggered (shouldn't happen due to prevent_initial_call)
        index = order[0] if order else "0"
    else:
        prop_id = ctx.triggered[0]["prop_id"]
        json_str = prop_id.split(".")[0]
        btn_id = json.loads(json_str)
        index = str(btn_id.get("index", order[0] if order else "0"))

    # Build description
    desc_text = (items.get(index, {}) or {}).get("description", "")
    desc = dcc.Markdown(desc_text, link_target="_blank")

    # Active flags in the same order as the buttons rendered
    active = [k == index for k in order]

    return desc, active
