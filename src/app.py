import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Dash

from components.navbar import create_navbar
from components.footer import create_footer
from utils import data_loader

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX], use_pages=True)
app.config.suppress_callback_exceptions = True
config_json, stores = data_loader.load_config_json_and_store()

app.layout = html.Div([

    create_navbar(),
    dash.page_container,
    create_footer(),

    # dcc.Store to store user input
    *stores

], className="d-flex flex-column min-vh-100")


if __name__ == '__main__':
    app.run(debug=True)
