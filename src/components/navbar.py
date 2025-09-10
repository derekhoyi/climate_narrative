import dash_bootstrap_components as dbc
import dash
from dash import html
from PIL import Image


def create_navbar():

    navbar = dbc.NavbarSimple(
        children=[
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Purpose",
                children=[
                    dbc.DropdownMenuItem("Overview", href='/purpose/purpose-overview'),
                    dbc.DropdownMenuItem("Introduction to the tool", href='/purpose/introduction-to-the-tool'),
                    dbc.DropdownMenuItem("How to use the tool?", href='/purpose/how-to-use-the-tool'),
                    dbc.DropdownMenuItem("How can the reports be used?", href='/purpose/how-can-the-reports-be-used'),
                    dbc.DropdownMenuItem("What is next?", href='/purpose/what-is-next'),
                ],
            ),
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Limitations",
                children=[
                    dbc.DropdownMenuItem("Limitations Overview", href='/limitations/limitations-overview'),
                    dbc.DropdownMenuItem("Long Term Scenario Limitations", href='/limitations/long-term-scenario-limitations'),
                    dbc.DropdownMenuItem("Short Term Scenario Limitations", href='/limitations/short-term-scenario-limitations'),
                ],
            ),
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Scenarios",
                children=[
                    dbc.DropdownMenuItem("Long-term scenarios", href='/scenarios/long-term-scenarios'),
                    dbc.DropdownMenuItem("Short-term scenarios", href='/scenarios/short-term-scenarios'),
                ],
            ),
            dbc.NavItem(dbc.NavLink("Sectors", href="/sectors")),
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Reports",
                children=[
                    dbc.DropdownMenuItem("Overview", href='/reports/report-overview'),
                    dbc.DropdownMenuItem("Generate report", href='/reports/generate-report'),
                    dbc.DropdownMenuItem("Institutional report", href='/reports/institutional-report'),
                    dbc.DropdownMenuItem("Sector report", href='/reports/sector-report'),
                    dbc.DropdownMenuItem("Scenario report", href='/reports/scenario-report'),
                    dbc.DropdownMenuItem("Full report", href='/reports/full-report'),
                ],
            ),
            dbc.NavItem(dbc.NavLink("Charts", href="/charts")),
            dbc.NavItem(dbc.NavLink("FAQs", href="/faqs")),
        ],
        brand=html.Img(src=Image.open("assets/logos/cfrf_logo.png"), height="48px", alt="CFRF"),
        brand_href="/",
        sticky="top",
        color="white",
        dark=False,
        expand='xl',
        links_left=True,
        class_name="mb-4", ####### changed from mb-4 to mb-0 #######
        style={"backgroundColor": "#ffffff", "color": "#000000"}  # <-- Force white bg and black text
    )

    return navbar
