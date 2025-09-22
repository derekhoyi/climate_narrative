import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px

# Register the page still works independently at /charts/tr_chart
dash.register_page(__name__, path='/charts/tr_chart')

# Load data
df = pd.read_csv("src/assets/data/transition_risk_data.csv")

def get_years(df):
    return [int(col) for col in df.columns if str(col).isdigit()]

# ---  return only filters + graph (no H1) for embedding on /charts ---
def embedded_content():
    return html.Div([
        # Filter section above the graph
        html.Div([
            html.Label("Select Region"),
            dcc.Dropdown(id='region-dropdown'),
            html.Label("Select Variable"),
            dcc.Dropdown(id='variable-dropdown', style={'width': '100%', 'whiteSpace': 'normal'}),
            html.Label("Select Scenario"),
            dcc.Dropdown(id='scenario-dropdown', multi=True),
            html.Label("Select Year Range"),
            dcc.RangeSlider(
                id='year-slider',
                step=1,
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            html.Div([
                html.Button("Reset Filters", id='reset-button', n_clicks=0, className='box-style')
            ], style={'marginTop': '20px'})
        ], style={'width': '100%', 'padding': '10px'}),
        # Graph section below the filters
        html.Div([
            dcc.Graph(id='line-chart'),
        ], style={'width': '100%', 'padding': '10px'})
    ])

def layout():
    # Keep the standalone page with its title
    return html.Div([
        html.H1("Transition Risk Charting", className="container"),
        embedded_content()
    ])

@dash.callback(
    Output('region-dropdown', 'options'),
    Output('region-dropdown', 'value'),
    Input('reset-button', 'n_clicks')
)
def update_region(reset_clicks):
    region_options = [{'label': r, 'value': r} for r in sorted(df['Region'].dropna().unique())]
    return region_options, None

@dash.callback(
    Output('variable-dropdown', 'options'),
    Output('variable-dropdown', 'value'),
    Input('region-dropdown', 'value')
)
def update_variable(region):
    if region is None:
        return [], None
    filtered_df = df[df['Region'] == region]
    variable_options = [{'label': v, 'value': v} for v in sorted(filtered_df['Variable'].dropna().unique())]
    return variable_options, None

@dash.callback(
    Output('scenario-dropdown', 'options'),
    Output('scenario-dropdown', 'value'),
    Input('region-dropdown', 'value'),
    Input('variable-dropdown', 'value')
)
def update_scenario(region, variable):
    if not all([region, variable]):
        return [], None
    filtered_df = df[
        (df['Region'] == region) &
        (df['Variable'] == variable)
    ]
    scenario_options = [{'label': s, 'value': s} for s in sorted(filtered_df['Scenario'].dropna().unique())]
    return scenario_options, None

@dash.callback(
    Output('year-slider', 'min'),
    Output('year-slider', 'max'),
    Output('year-slider', 'value'),
    Output('year-slider', 'marks'),
    Input('region-dropdown', 'value'),
    Input('variable-dropdown', 'value'),
    Input('scenario-dropdown', 'value')
)
def update_year_slider(region, variable, scenarios):
    years = get_years(df)
    if not all([region, variable, scenarios]):
        return min(years), max(years), [min(years), max(years)], {year: str(year) for year in years if year % 10 == 0}
    if not isinstance(scenarios, list):
        scenarios = [scenarios]
    filtered_df = df[
        (df['Region'] == region) &
        (df['Variable'] == variable) &
        (df['Scenario'].isin(scenarios))
    ]
    years = [int(col) for col in filtered_df.columns if str(col).isdigit() and not filtered_df[col].isna().all()]
    if not years:
        return 2025, 2100, [2025, 2100], {2025: '2025', 2100: '2100'}
    marks = {year: str(year) for year in years if year % 10 == 0}
    return min(years), max(years), [min(years), max(years)], marks

@dash.callback(
    Output('line-chart', 'figure'),
    Input('region-dropdown', 'value'),
    Input('variable-dropdown', 'value'),
    Input('scenario-dropdown', 'value'),
    Input('year-slider', 'value')
)
def update_chart(region, variable, scenarios, year_range):
    palette = px.colors.qualitative.Plotly
    background = '#FFFFFF'

    def add_footer(fig, text, font_size=14):
        fig.update_layout(margin=dict(t=40, r=20, l=60, b=140))
        fig.add_annotation(
            text=text,
            x=0.5, y=-0.18,
            xref="paper", yref="paper",
            showarrow=False,
            xanchor="center", yanchor="top",
            align="center",
            font=dict(size=font_size)
        )
        return fig

    def add_top_title(fig, text, font_size=16, band=0.26):
        band = max(0.06, min(band, 0.30))
        top_of_plot = 1.0 - band
        fig.update_layout(
            margin=dict(t=20, r=20, l=60, b=80),
        )
        yaxis = fig.layout.yaxis.to_plotly_json() if fig.layout.yaxis else {}
        yaxis['domain'] = [0.0, top_of_plot]
        fig.update_layout(yaxis=yaxis)
        fig.add_annotation(
            text=text,
            x=0.5, y=top_of_plot + band / 2.0,
            xref="paper", yref="paper",
            showarrow=False,
            xanchor="center", yanchor="middle",
            align="center",
            font=dict(size=font_size),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(0,0,0,0)",
            borderpad=6
        )
        return fig

    if not all([region, variable, scenarios]):
        fig = px.line(title=None)
        fig.update_layout(
            plot_bgcolor=background,
            paper_bgcolor=background,
            font=dict(color="#222"),
            xaxis=dict(gridcolor="#EEE"),
            yaxis=dict(gridcolor="#EEE"),
            showlegend=False
        )
        fig = add_footer(fig, "Please select all options to display the chart")
        return fig

    if not isinstance(scenarios, list):
        scenarios = [scenarios]
    filtered_df = df[
        (df['Region'] == region) &
        (df['Variable'] == variable) &
        (df['Scenario'].isin(scenarios))
    ]
    years = get_years(df)
    selected_years = years if not year_range else [y for y in years if year_range[0] <= y <= year_range[1]]
    if filtered_df.empty or not selected_years:
        fig = px.line(title=None)
        fig.update_layout(
            plot_bgcolor=background,
            paper_bgcolor=background,
            font=dict(color="#222"),
            xaxis=dict(gridcolor="#EEE"),
            yaxis=dict(gridcolor="#EEE"),
            showlegend=False
        )
        fig = add_footer(fig, "No data available for the selected filters")
        return fig
    melted_df = filtered_df.melt(
        id_vars=['Region', 'Variable', 'Scenario'],
        value_vars=[str(y) for y in selected_years],
        var_name='Year', value_name='Value'
    )
    fig = px.line(
        melted_df,
        x='Year',
        y='Value',
        color='Scenario',
        color_discrete_sequence=palette
    )
    fig.update_layout(
        title=None,
        plot_bgcolor=background,
        paper_bgcolor=background,
        font=dict(color="#222"),
        xaxis=dict(gridcolor="#EEE"),
        yaxis=dict(gridcolor="#EEE"),
        showlegend=True,
        yaxis_title=variable
    )
    title_text = (
        f"<b>Transition Risk</b> <br>"
        f"{region} - {variable}"
    )
    fig = add_top_title(fig, title_text, font_size=16, band=0.26)
    return fig
