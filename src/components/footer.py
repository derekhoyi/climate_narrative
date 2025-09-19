import dash_bootstrap_components as dbc
from dash import html, get_asset_url


def create_footer():
    # Build the correct assets URL (respects base path / proxies)
    data_zip_href = get_asset_url("assets/data/chart_data.zip")

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
                            "Data used in Charts",
                            href=data_zip_href,            # Generates the right /assets URL
                            className="me-4 text-muted",
                            download="chart_data.zip",     # Triggers browser download
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
                        href=mailto_link,       # Open mail client
                        external_link=True,     # Ensure button behaves like a link
                    ),
                    className="mb-3",
                ),
            ]
        ),
        className="container small mt-auto",
    )
    return footer
