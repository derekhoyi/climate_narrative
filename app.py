import dash_bootstrap_components as dbc
from dash import html, dcc, Dash
from dash.dependencies import Input, Output, State

from pages import home
from pages import page_2
from pages import page_3
from pages import page_4
from pages import page_11
from pages import page_12
from pages import page_13


app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX])
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-2':
        return page_2.create_layout()
    if pathname == '/page-3':
        return page_3.create_layout()
    if pathname == '/page-4':
        return page_4.create_layout()
    if pathname == '/page-11':
        return page_11.create_layout()
    if pathname == '/page-12':
        return page_12.create_layout()
    if pathname == '/page-13':
        return page_13.create_layout()
    else:
        return home.create_layout()

if __name__ == '__main__':
    app.run(debug=True)


# https://medium.com/@mcmanus_data_works/how-to-create-a-multipage-dash-app-75c2ddb79315