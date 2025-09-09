import dash_bootstrap_components as dbc
from dash import html


def create_footer():
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
                        html.A("Support", href="#", className="me-4 text-muted"),
                        html.A("Known Issues", href="#", className="me-4 text-muted"),
                        html.A("Contributors", href="#", className="me-4 text-muted"),
                        html.A("CFRF - Data and Tools Providers", href="#", className="me-4 text-muted"),
                        html.A("Data used in Charts", href="#", className="me-4 text-muted"),
                    ],
                    className="mb-3"
                ),
            ],
        ),
        className="container small mt-auto",
    )

    return footer
