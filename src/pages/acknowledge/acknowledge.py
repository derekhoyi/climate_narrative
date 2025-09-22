import dash
from dash import html, dcc, callback, Output, Input, State, ALL
import dash_bootstrap_components as dbc
import yaml
import json
from pathlib import Path
dash.register_page(__name__, path='/acknowledge')

def layout():
    # define paths
    YML_FOLDER = "../../assets/page_contents/section"
    YML_NAME = "acknowledgements.yml"
    FILE_PATH = Path(__file__).parent
    YML_PATH = FILE_PATH.joinpath(YML_FOLDER).joinpath(YML_NAME).resolve()

    # open yaml
    with open(YML_PATH, encoding="utf-8") as f:
        # Load as a dictionary: section name -> content (string or list)
        yml = yaml.safe_load(f)

    # Create buttons for each section
    button_list = []
    section_names = list(yml.keys())
    for idx, section in enumerate(section_names):
        button_list.append(
            dbc.Button(
                section,
                id={'type': 'acknowledge-btn', 'index': idx},
                class_name="btn-light text-start",
                n_clicks=0,
                active=(idx == 0)  # First button active by default
            )
        )

    # Default description (first section)
    first_section = section_names[0]
    default_desc = dcc.Markdown(
        format_section_content(yml[first_section]),
        link_target="_blank"
    )

    # Layout
    layout = html.Div(
        [
            dcc.Store(
                id='yml-store',
                data=json.dumps(yml),
                storage_type='memory'
            ),
            dcc.Store(
                id='section-names-store',
                data=json.dumps(section_names),
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
                            default_desc,
                            id='acknowledge-description'
                        )
                    ),
                ]
            ),
        ],
        className="container"
    )
    return layout

def format_section_content(content):
    """
    Helper to format section content as Markdown.
    Handles strings, lists, or dicts.
    """
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return "\n".join(str(item) for item in content)
    elif isinstance(content, dict):
        # For dicts, pretty print as Markdown
        return "\n".join(f"**{k}**: {v}" for k, v in content.items())
    else:
        return str(content)

# Display section callback
@callback(
    [Output('acknowledge-description', 'children'),
     Output({'type': 'acknowledge-btn', 'index': ALL}, 'active')],
    Input({'type': 'acknowledge-btn', 'index': ALL}, 'n_clicks'),
    State('yml-store', 'data'),
    State('section-names-store', 'data'),
    prevent_initial_call=True
)
def display_acknowledge(n_clicks, yml_data, section_names_data):
    yml = json.loads(yml_data)
    section_names = json.loads(section_names_data)
    # Determine which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        idx = 0
    else:
        prop_id = ctx.triggered[0]['prop_id']
        json_str = prop_id.split('.')[0]
        button_id = json.loads(json_str)
        idx = button_id['index']
    # Get content for the selected section
    section = section_names[idx]
    desc_yml = yml[section]
    desc = dcc.Markdown(format_section_content(desc_yml), link_target="_blank")
    # Set active button
    active = [i == idx for i in range(len(section_names))]
    return desc, active
