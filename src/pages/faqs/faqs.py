import dash
from dash import html, dcc, callback, Output, Input, State, ALL
import dash_bootstrap_components as dbc
import yaml
import json
from pathlib import Path
import pydash

dash.register_page(__name__, path='/faqs')

# ---- Stable ordering & labels ----------------------------------------------

# Canonical order (keys as they appear in the YML files)
DESIRED_ORDER = [
    "use and purpose",
    "sector and scenario coverage",
    "reports",
    "charts",
    "next steps and improvements",
]

# Button/heading labels (display text) for each topic
LABEL_MAP = {
    "use and purpose": "Use and Purpose",
    "sector and scenario coverage": "Sector and scenario coverage",
    "reports": "Reports",
    "charts": "Charts",
    "next steps and improvements": "Next steps and improvements",
}

def _ordered_topics(yml_dict: dict) -> list:
    """Return topics in the pinned order, appending any unexpected topics at the end (alphabetically)"""
    present = [k for k in DESIRED_ORDER if k in yml_dict]
    extras = sorted([k for k in yml_dict.keys() if k not in DESIRED_ORDER])
    return present + extras

# ---- Layout ----------------------------------------------------------------

def layout():
    # Define paths
    YML_FOLDER = "../../assets/page_contents/section/faqs"
    FILE_PATH = Path(__file__).parent
    YML_DIR = FILE_PATH.joinpath(YML_FOLDER).resolve()

    # Load all YML files in the folder
    yml = {}
    for yml_file in sorted(YML_DIR.glob("*.yml")):  # sort for determinism; final order is controlled below
        with open(yml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            # Normalize keys to lower-case to match DESIRED_ORDER/LABEL_MAP
            normalized = {str(k).strip().lower(): v for k, v in data.items()}
            yml.update(normalized)

    topics = _ordered_topics(yml)
    default_topic = topics[0] if topics else None

    # Button group for topics (stable order + friendly labels)
    button_list = [
        dbc.Button(
            LABEL_MAP.get(topic, topic.title()),
            id={"type": "topic-btn", "index": topic},
            class_name="btn-light text-start",
            n_clicks=0,
            active=(topic == default_topic),
        )
        for topic in topics
    ]

    # Accordion for default topic
    faqs = pydash.get(yml, default_topic, [])
    accordion_items = [
        dbc.AccordionItem(
            [dcc.Markdown(pydash.get(faq, "answer", ""), className="mb-0", link_target="_self")],
            title=pydash.get(faq, "question", f"Question {idx+1}"),
            item_id=str(idx),
        )
        for idx, faq in enumerate(faqs)
    ]

    layout = html.Div(
        [
            dcc.Store(
                id='faq-store',
                data=json.dumps(yml),
                storage_type='memory'
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.ButtonGroup(button_list, vertical=True),
                        md=3,
                        class_name="sidebar-btn-group"
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H1("Frequently Asked Questions"),
                                html.H3(LABEL_MAP.get(default_topic, (default_topic or ""))),
                                dbc.Accordion(
                                    accordion_items,
                                    id="faq-accordion",
                                    active_item=None,
                                    always_open=False,
                                ),
                            ],
                            id='faq-content'
                        )
                    ),
                ]
            ),
        ],
        className="container"
    )
    return layout

# ---- Callback ---------------------------------------------------------------

@callback(
    Output('faq-content', 'children'),
    Output({'type': 'topic-btn', 'index': ALL}, 'active'),
    Input({'type': 'topic-btn', 'index': ALL}, 'n_clicks'),
    State('faq-store', 'data'),
    prevent_initial_call=True
)
def display_topic(n_clicks, yml_data):
    yml = json.loads(yml_data) if yml_data else {}
    topics = _ordered_topics(yml)  # ensure same order here as in layout

    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    prop_id = ctx.triggered[0]['prop_id']
    json_str = prop_id.split('.')[0]
    button_id = json.loads(json_str)
    topic = button_id['index']

    faqs = pydash.get(yml, topic, [])
    accordion_items = [
        dbc.AccordionItem(
            [dcc.Markdown(pydash.get(faq, "answer", ""), className="mb-0", link_target="_self")],
            title=pydash.get(faq, "question", f"Question {idx+1}"),
            item_id=str(idx)
        )
        for idx, faq in enumerate(faqs)
    ]

    content = [
        html.H1("Frequently Asked Questions"),
        html.H3(LABEL_MAP.get(topic, topic.title())),
        dbc.Accordion(
            accordion_items,
            id="faq-accordion",
            active_item=None,
            always_open=False,
        ),
    ]

    # Active state aligned with the ordered button list
    active = [t == topic for t in topics]
    return content, active
