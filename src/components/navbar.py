import dash_bootstrap_components as dbc
import dash
from dash import html
from PIL import Image


def create_navbar():

    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("purpose", href="/purpose")),
            dbc.NavItem(dbc.NavLink("limitations", href="/limitations")),
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Scenarios",
                children=[
                    dbc.DropdownMenuItem("Long-term scenarios", href='/scenarios/long-term-scenarios',class_name="box-style"),
                    dbc.DropdownMenuItem("Short-term scenarios", href='/scenarios/short-term-scenarios',class_name="box-style"),
                ],
            ),
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Sectors",
                children=[
                    dbc.DropdownMenuItem("Sectors", href='/sectors/sector',class_name="box-style"),
                    dbc.DropdownMenuItem("Underwriting Classes", href='/sectors/underwriting',class_name="box-style"),
                    dbc.DropdownMenuItem("Sovereigns", href='/sectors/sovereigns',class_name="box-style"),
                ],
            ),
            dbc.NavItem(dbc.NavLink("Reports", href="/reports")),
            dbc.NavItem(dbc.NavLink("Charts", href="/charts")),
            dbc.NavItem(dbc.NavLink("FAQs", href="/faqs")),
            dbc.NavItem(dbc.NavLink("Acknowledgements", href="/acknowledge")),
        ],
        brand=html.Img(src=Image.open("src/assets/logos/cfrf_logo.png"), height="48px", alt="CFRF"),
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
