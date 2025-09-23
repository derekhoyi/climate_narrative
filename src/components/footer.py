import dash_bootstrap_components as dbc
from dash import html, get_asset_url
from urllib.parse import quote

def create_footer():
    # Build correct asset URLs (paths are relative to the /assets folder)
    zip_href = get_asset_url("data/chart_data.zip")

    # Safely URL-encode the mailto subject and body
    subject = quote("Feedback for Online Climate Scenario Analysis Narrative Tool")
    body = quote("Please enter your feedback here...")
    mailto_link = f"mailto:climate.forum@fca.org.uk?subject={subject}&body={body}"

    footer = dbc.Container(
        html.Footer(
            [
                html.Hr(className="mt-5"),
                html.P(
                    "Copyright 2025 The Climate Financial Risk Forum",
                    className="mb-1",
                ),
                html.Div(
                    [
                        html.A(
                            "Source Code",
                            href="https://github.com/derekhoyi/climate_narrative",
                            className="me-4 text-muted",
                            target="_blank",
                            rel="noopener noreferrer",
                        ),
                        html.A(
                            "Known Issues",
                            href="https://github.com/derekhoyi/climate_narrative/issues",
                            className="me-4 text-muted",
                            target="_blank",
                            rel="noopener noreferrer",
                        ),
                        html.A(
                            "Chart Data (.zip)",
                            href=zip_href,
                            className="me-4 text-muted",
                            download="chart_data.zip",
                        ),
                    ],
                    className="mb-3",
                ),
                html.Div(
                    dbc.Button(
                        [
                            html.Span("💬", style={
                                "verticalAlign": "middle",
                                "marginRight": "8px",
                                "fontSize": "1.5em",
                            }),
                            "FEEDBACK",
                        ],
                        id="feedback",
                        n_clicks=0,
                        style={
                            "backgroundColor": "#5ecc82",
                            "color": "white",
                            "borderRadius": "8px",
                            "border": "none",
                            "marginTop": "5px",
                        },
                        href=mailto_link,        # Open mail client
                        external_link=True,      # Open in a new tab/window
                    ),
                    className="mb-3",
                ),
            ]
        ),
        className="container small mt-auto",
    )

    return footer
