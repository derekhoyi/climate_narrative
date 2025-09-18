import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Dash

from components.navbar import create_navbar
from components.footer import create_footer

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX], use_pages=True)
app.config.suppress_callback_exceptions = True

app.layout = html.Div([

    create_navbar(),
    dash.page_container,
    create_footer(),
    
    # dcc.Store to store user input
    dcc.Store(id='storage-sector', storage_type='memory'),
], className="d-flex flex-column min-vh-100")


if __name__ == '__main__':
    app.run(debug=False)
