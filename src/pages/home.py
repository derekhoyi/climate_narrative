import dash
from dash import html, callback, Output, Input
import dash_bootstrap_components as dbc
from PIL import Image
from pathlib import Path
import yaml
dash.register_page(__name__, path='/')

def _load_disclaimer_text():
    # Use the exact path you provided
    yml_path = Path(__file__).parent.parent.parent / "src" / "assets" / "page_contents" / "section" / "disclaimer.yml"
    if yml_path.exists():
        with yml_path.open(encoding="utf-8") as f:
            yml = yaml.safe_load(f) or {}
        return yml['description']
    return ["Disclaimer text is not available."]

def layout():
    paragraphs = _load_disclaimer_text()
    # --- AMENDED SECTION STARTS HERE ---
    # Ensure paragraphs is a list of strings, each representing a paragraph or line
    if isinstance(paragraphs, str):
        # Split by line breaks if it's a single string
        modal_body_content = [html.P(line) for line in paragraphs.split('\n') if line.strip()]

    else:
        # If already a list, wrap each in html.P
        modal_body_content = [html.P(p) for p in paragraphs if p.strip()]
    # --- AMENDED SECTION ENDS HERE ---

    layout = html.Div([
        # Header
        html.Div(
            [
                html.H3('Climate Financial Risk Forum', style={"margin-bottom": "0", "color": "white"}),
                html.H6('Online Climate Scenario Analysis Narrative Tool', style={"margin-top": "0", "color": "white"})
            ],
            style={
                "background": "#000000", "color": "white", "padding": "8px 1px 8px 1px",
                "borderRadius": "0px", "textAlign": "center", "marginBottom": "0px",
                "marginTop": "0px", "width": "60%", "marginLeft": "auto", "marginRight": "auto",
                "boxSizing": "border-box"
            }
        ),
        # Hero image
        html.Div(
            html.Img(
                src="./assets/images/CFRF image cover.jpg",
                style={"display": "block", "marginLeft": "auto", "marginRight": "auto", "height": "auto", "width": "100%",},
                alt="CFRF Logo"
            ),
            style={"backgroundColor": "#000000", "width": "60%", "padding": "5px 0", "marginLeft": "auto", "marginRight": "auto"}
        ),
        # CTA
        html.Div(
            dbc.Button(
                "Generate Report",
                id="open",
                n_clicks=0,
                href='/reports/overview',
                style={"backgroundColor": "#51C876", "color": "white", "borderRadius": "8px", "border": "none"}
            ),
            className="text-center",
            style={"backgroundColor": "#000000", "width": "60%", "padding": "5px 0",
                   "marginLeft": "auto", "marginRight": "auto", "textAlign": "center"}
        ),
        # Disclaimer modal
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.ModalTitle("Disclaimer", style={"color": "white"}),
                    style={"backgroundColor": "#51C876"}
                ),
                dbc.ModalBody(
                    modal_body_content,
                    style={"backgroundColor": "#51C876", "color": "white"}
                ),
                dbc.ModalFooter(
                    [
                        dbc.Button(
                            "Acknowledge",
                            id="acknowledge",
                            class_name="mx-auto",
                            style={
                                "backgroundColor": "#fff", "color": "#51C876",
                                "borderRadius": "8px", "border": "none", "fontWeight": "bold"
                            }
                        )
                    ],
                    style={"backgroundColor": "#51C876", "color": "white"}
                ),
            ],
            id="modal",
            size="lg",
            is_open=True  # Always open when the page loads
        ),
    ], style={"marginTop": "0px", "paddingTop": "0px"})
    return layout

@callback(
    Output("modal", "is_open"),
    Input("acknowledge", "n_clicks"),
    prevent_initial_call=False
)
def handle_modal(n_ack):
    # Open by default; close after first click
    return not bool(n_ack)
