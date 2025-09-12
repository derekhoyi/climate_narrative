import dash
from dash import html, dcc, callback, Output, Input, State, ALL
import dash_bootstrap_components as dbc
import yaml
import json
from pathlib import Path
import pydash

dash.register_page(__name__, path='/faqs')

def layout():
    # Define paths
    YML_FOLDER = "../../../assets/page_contents/section/faqs"
    FILE_PATH = Path(__file__).parent
    YML_DIR = FILE_PATH.joinpath(YML_FOLDER).resolve()

    # Load all YML files in the folder
    yml = {}
    for yml_file in YML_DIR.glob("*.yml"):
        with open(yml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            # Merge or append sectors; assumes each file is a dict of sectors
            yml.update(data)

    topics = list(yml.keys())
    default_topic = topics[0] if topics else None

    # Button group for topics
    button_list = [
        dbc.Button(
            topic,
            id={'type': 'topic-btn', 'index': topic},
            class_name="btn-light text-start",
            n_clicks=0,
            active=(topic == default_topic)
        )
        for topic in topics
    ]

    # Accordion for default topic
    faqs = pydash.get(yml, default_topic, [])
    accordion_items = [
        dbc.AccordionItem(
            [html.P(pydash.get(faq, "answer", ""), className="mb-0")],
            title=pydash.get(faq, "question", f"Question {idx+1}"),
            item_id=str(idx)
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
                        class_name="mb-3"
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H2(default_topic),
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

@callback(
    Output('faq-content', 'children'),
    Output({'type': 'topic-btn', 'index': ALL}, 'active'),
    Input({'type': 'topic-btn', 'index': ALL}, 'n_clicks'),
    State('faq-store', 'data'),
    prevent_initial_call=True
)
def display_topic(n_clicks, yml_data):
    yml = json.loads(yml_data)
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
            [html.P(pydash.get(faq, "answer", ""), className="mb-0")],
            title=pydash.get(faq, "question", f"Question {idx+1}"),
            item_id=str(idx)
        )
        for idx, faq in enumerate(faqs)
    ]

    content = [
        html.H2(topic),
        dbc.Accordion(
            accordion_items,
            id="faq-accordion",
            active_item=None,
            always_open=False,
        ),
    ]

    active = [i == topic for i in yml.keys()]
    return content, active
