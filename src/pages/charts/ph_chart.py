import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px

# Register the page still works independently at /charts/ph_chart
dash.register_page(__name__, path='/charts/ph_chart')

# Load data
df_ph = pd.read_csv("src/assets/data/physical_risk_data.csv")

# Extract year columns
def get_years_ph(df):
    return [int(col) for col in df.columns if str(col).isdigit()]

# --- NEW: return only filters + graph (no H1) for embedding on /charts ---
def embedded_content():
    return html.Div([
        # ----------- FILTERS -----------
        html.Div([
            html.Label("Select Region"),
            dcc.Dropdown(id='ph-region-dropdown'),

            html.Label("Select Variable"),
            dcc.Dropdown(
                id='ph-variable-dropdown',
                style={'width': '100%', 'whiteSpace': 'normal'}
            ),

            html.Label("Select Scenario"),
            dcc.Dropdown(
                id='ph-scenario-dropdown',
                multi=True
            ),

            html.Label("Select Year Range"),
            dcc.RangeSlider(
                id='ph-year-slider',
                step=1,
                tooltip={"placement": "bottom", "always_visible": True}
            ),

            html.Div([
                html.Button(
                    "Reset Filters",
                    id='ph-reset-button',
                    n_clicks=0,
                    className='box-style'
                )
            ], style={'marginTop': '12px'})
        ], style={'width': '100%', 'padding': '10px'}),

        # ----------- CHART -----------
        dcc.Graph(id='ph-line-chart', style={'width': '100%', 'height': '600px'})
    ])

def layout():
    # Keep the standalone page with its title
    return html.Div([
        html.H1("Physical Risk Chart", className="container"),
        embedded_content()  # reuse the same content
    ])

# --- Controls population & dependencies ---
@dash.callback(
    Output('ph-region-dropdown', 'options'),
    Output('ph-region-dropdown', 'value'),
    Input('ph-reset-button', 'n_clicks')
)
def update_ph_region(reset_clicks):
    region_options = [{'label': r, 'value': r}
                      for r in sorted(df_ph['Region'].dropna().unique())]
    return region_options, None

@dash.callback(
    Output('ph-variable-dropdown', 'options'),
    Output('ph-variable-dropdown', 'value'),
    Input('ph-region-dropdown', 'value')
)
def update_ph_variable(region):
    if region is None:
        return [], None
    filtered_df = df_ph[df_ph['Region'] == region]
    variable_options = [{'label': v, 'value': v}
                        for v in sorted(filtered_df['Variable'].dropna().unique())]
    return variable_options, None

@dash.callback(
    Output('ph-scenario-dropdown', 'options'),
    Output('ph-scenario-dropdown', 'value'),
    Input('ph-region-dropdown', 'value'),
    Input('ph-variable-dropdown', 'value')
)
def update_ph_scenario(region, variable):
    if region is None or variable is None:
        return [], []
    filtered_df = df_ph[
        (df_ph['Region'] == region) &
        (df_ph['Variable'] == variable)
    ]
    scenario_options = [{'label': s, 'value': s}
                        for s in sorted(filtered_df['Scenario'].dropna().unique())]
    return scenario_options, []

@dash.callback(
    Output('ph-year-slider', 'min'),
    Output('ph-year-slider', 'max'),
    Output('ph-year-slider', 'value'),
    Output('ph-year-slider', 'marks'),
    Input('ph-region-dropdown', 'value'),
    Input('ph-variable-dropdown', 'value'),
    Input('ph-scenario-dropdown', 'value')  # NOTE: this is a list (multi)
)
def update_ph_year_slider(region, variable, scenarios):
    # If selections are incomplete, expose full global year range
    if not region or not variable or not scenarios:
        years = get_years_ph(df_ph)
    else:
        # Filter by selected region/variable/scenarios
        filtered_df = df_ph[
            (df_ph['Region'] == region) &
            (df_ph['Variable'] == variable) &
            (df_ph['Scenario'].isin(scenarios))
        ]
        # Keep years that have at least one non-NA value
        years = [
            int(col) for col in filtered_df.columns
            if str(col).isdigit() and filtered_df[col].notna().any()
        ]
        if not years:
            return 2020, 2100, [2020, 2100], {2020: '2020', 2100: '2100'}

    years = sorted(set(years))
    marks = {year: str(year) for year in years if year % 10 == 0}
    return min(years), max(years), [min(years), max(years)], marks

# --- Chart ---
@dash.callback(
    Output('ph-line-chart', 'figure'),
    Input('ph-region-dropdown', 'value'),
    Input('ph-variable-dropdown', 'value'),
    Input('ph-scenario-dropdown', 'value'),  # list
    Input('ph-year-slider', 'value')
)
def update_ph_chart(region, variable, scenarios, year_range):
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

    def add_top_title(fig, text, font_size=16, band=0.16):
        band = max(0.06, min(band, 0.30))
        top_of_plot = 1.0 - band
        fig.update_layout(margin=dict(t=20, r=20, l=60, b=80))
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

    if not region or not variable or not scenarios:
        fig = px.line(title=None)
        fig.update_layout(
            plot_bgcolor=background,
            paper_bgcolor=background,
            font=dict(color="#222"),
            xaxis=dict(gridcolor="#EEE"),
            yaxis=dict(gridcolor="#EEE"),
            showlegend=False,
            yaxis_title=None
        )
        fig = add_footer(fig, "Please select region, variable, and at least one scenario to display the chart")
        return fig

    filtered_df = df_ph[
        (df_ph['Region'] == region) &
        (df_ph['Variable'] == variable) &
        (df_ph['Scenario'].isin(scenarios))
    ]

    all_years = get_years_ph(df_ph)
    if not year_range:
        selected_years = all_years
    else:
        selected_years = [y for y in all_years if year_range[0] <= y <= year_range[1]]

    if filtered_df.empty or not selected_years:
        fig = px.line(title=None)
        fig.update_layout(
            plot_bgcolor=background,
            paper_bgcolor=background,
            font=dict(color="#222"),
            xaxis=dict(gridcolor="#EEE"),
            yaxis=dict(gridcolor="#EEE"),
            showlegend=False,
            yaxis_title=None
        )
        fig = add_footer(fig, "No data available for the selected filters")
        return fig

    melted_df = filtered_df.melt(
        id_vars=['Region', 'Variable', 'Scenario'],
        value_vars=[str(y) for y in selected_years],
        var_name='Year', value_name='Value'
    )
    melted_df['Year'] = melted_df['Year'].astype(int)

    fig = px.line(
        melted_df,
        x='Year',
        y='Value',
        color='Scenario',
        category_orders={'Scenario': scenarios}
    )
    fig.update_layout(
        title=None,
        plot_bgcolor=background,
        paper_bgcolor=background,
        font=dict(color="#222"),
        xaxis=dict(gridcolor="#EEE"),
        yaxis=dict(gridcolor="#EEE"),
        showlegend=True,
        legend_title_text="Scenario",
        yaxis_title=variable
    )
    scenario_text = ", ".join(scenarios)
    title_text = (
        f"<b>Physical Risk</b><br>"
        f"{region} - {variable}"
    )
    fig = add_top_title(fig, title_text, font_size=16, band=0.16)
    return fig
