import dash_bootstrap_components as dbc
from dash import html

def create_footer():
    mailto_link = (
        "mailto:climate.forum@fca.org.uk"
        "?subject=Feedback for Online Climate Scenario Analysis Narrative Tool"
        "&body=Please%20enter%20your%20feedback%20here..."
    )
    footer = dbc.Container(
        html.Footer(
            [
                html.Hr(className="mt-5"),
                html.P(
                    "Copyright 2025 The Climate Financial Risk Forum", className="mb-1",
                ),
                html.Div(
                    [
                        html.A("Source Code", href="#", className="me-4 text-muted"),
                        html.A("Known Issues", href="#", className="me-4 text-muted"),
                        html.A("CFRF - Data and Tools Providers", href="#", className="me-4 text-muted"),
                        html.A("Data used in Charts", href="#", className="me-4 text-muted"),
                    ],
                    className="mb-3"
                ),
                html.Div(
                    dbc.Button(
                        [
                            html.Span("💬", style={
                                "verticalAlign": "middle",
                                "marginRight": "8px",
                                "fontSize": "1.5em"
                            }),
                            "FEEDBACK"
                        ],
                        id="feedback",
                        n_clicks=0,
                        style={
                            "backgroundColor": "#5ecc82",
                            "color": "white",
                            "borderRadius": "8px",
                            "border": "none",
                            "marginTop": "5px"
                        },
                        href=mailto_link,           # This makes the button open the mail client
                        external_link=True          # Ensures it works as a link
                    ),
                    className="mb-3"
                ),
            ]
        ),
        className="container small mt-auto",
    )
    return footer
