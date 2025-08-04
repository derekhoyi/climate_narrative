from dash import html
import dash_bootstrap_components as dbc

from pages.navbar import create_navbar

def create_layout():

    # contents
    header1 = html.H3('Introduction to the Tool')
    text1 = html.P('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec et odio sit amet elit vulputate lobortis. Curabitur luctus in neque at feugiat. Sed a efficitur magna. Pellentesque id sollicitudin sapien, in congue risus.')
    header2 = html.H3('Purpose')
    text2 = html.P('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec et odio sit amet elit vulputate lobortis. Curabitur luctus in neque at feugiat. Sed a efficitur magna. Pellentesque id sollicitudin sapien, in congue risus.')
    header3 = html.H3('How to use the tool?')
    text3 = html.P('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec et odio sit amet elit vulputate lobortis. Curabitur luctus in neque at feugiat. Sed a efficitur magna. Pellentesque id sollicitudin sapien, in congue risus.')
    contents = [header1, text1, header2, text2, header3, text3]

    # nav buttons
    prev_button = dbc.Button("PREV", id="open", n_clicks=0, href='/')
    next_button = dbc.Button("NEXT", id="open", n_clicks=0, href='/page-3')
    button_bar = html.Div([prev_button, next_button], className="d-flex justify-content-between container")

    layout = html.Div([
        create_navbar(),
        html.Div(contents, className="mx-auto py-3 container"), 
        button_bar
    ])
    return layout