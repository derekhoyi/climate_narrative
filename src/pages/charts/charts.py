import dash
from dash import html

dash.register_page(__name__, path='/charts')


def layout():

    # create layout
    layout = html.H3('Coming Soon!', className="container")
    return layout
