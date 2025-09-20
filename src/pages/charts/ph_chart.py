import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px

# Register the page
dash.register_page(__name__, path='/charts/ph_chart')

# Load data
df_ph = pd.read_csv("src/assets/data/physical_risk_data.csv")

# Extract year columns
def get_years_ph(df):
    return [int(col) for col in df.columns if str(col).isdigit()]

def layout():
    return html.Div([
        html.H1("Physical Risk Charting", className="container"),
        html.Div([
            html.Div([
                html.Label("Select Region"),
                dcc.Dropdown(id='ph-region-dropdown'),

                html.Label("Select Variable"),
                dcc.Dropdown(
                    id='ph-variable-dropdown',
                    style={'width': '100%', 'whiteSpace': 'normal'}
                ),

                html.Label("Select Scenario"),
                dcc.Dropdown(id='ph-scenario-dropdown'),

                html.Label("Select Year Range"),
                dcc.RangeSlider(
                    id='ph-year-slider',
                    step=1,
                    tooltip={"placement": "bottom", "always_visible": True}
                ),

                html.Div([
                    html.Button("Reset Filters", id='ph-reset-button',
                                n_clicks=0, className='box-style')
                ], style={'marginTop': '20px'})
            ], style={'width': '30%', 'display': 'inline-block',
                      'verticalAlign': 'top', 'padding': '10px'}),

            html.Div([
                dcc.Graph(id='ph-line-chart'),
            ], style={'width': '68%', 'display': 'inline-block', 'padding': '10px'})
        ])
    ])

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
        return [], None
    filtered_df = df_ph[
        (df_ph['Region'] == region) &
        (df_ph['Variable'] == variable)
    ]
    scenario_options = [{'label': s, 'value': s}
                        for s in sorted(filtered_df['Scenario'].dropna().unique())]
    return scenario_options, None

@dash.callback(
    Output('ph-year-slider', 'min'),
    Output('ph-year-slider', 'max'),
    Output('ph-year-slider', 'value'),
    Output('ph-year-slider', 'marks'),
    Input('ph-region-dropdown', 'value'),
    Input('ph-variable-dropdown', 'value'),
    Input('ph-scenario-dropdown', 'value')
)
def update_ph_year_slider(region, variable, scenario):
    if not all([region, variable, scenario]):
        years = get_years_ph(df_ph)
    else:
        filtered_df = df_ph[
            (df_ph['Region'] == region) &
            (df_ph['Variable'] == variable) &
            (df_ph['Scenario'] == scenario)
        ]
        years = [int(col) for col in filtered_df.columns
                 if str(col).isdigit() and not filtered_df[col].isna().all()]

    if not years:
        return 2020, 2100, [2020, 2100], {2020: '2020', 2100: '2100'}

    marks = {year: str(year) for year in years if year % 10 == 0}
    return min(years), max(years), [min(years), max(years)], marks


@dash.callback(
    Output('ph-line-chart', 'figure'),
    Input('ph-region-dropdown', 'value'),
    Input('ph-variable-dropdown', 'value'),
    Input('ph-scenario-dropdown', 'value'),
    Input('ph-year-slider', 'value')
)
def update_ph_chart(region, variable, scenario, year_range):
    # Colors & backgrounds
    line_color = '#00B050'
    background = '#FFFFFF'

    def add_footer(fig, text, font_size=14):
        """Keep footer for status messages (e.g., when selections are incomplete)."""
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

    # NEW: Title helper to place title inside the figure at the top without overlapping
    def add_top_title(fig, text, font_size=16, band=0.12):
        """
        Reserve a top band inside the figure (not outside), and place a centered
        annotation in that band so it exports with the image and doesn't overlap the plot.
        """
        # clamp band between 6% and 30% of the figure height
        band = max(0.06, min(band, 0.30))
        top_of_plot = 1.0 - band

        # Ensure the plot area leaves room for the band
        # Keep gridcolor applied; don't overwrite existing yaxis settings beyond domain
        fig.update_layout(
            margin=dict(t=20, r=20, l=60, b=80),
        )
        # Merge/extend yaxis settings carefully to keep grid styling
        yaxis = fig.layout.yaxis.to_plotly_json() if fig.layout.yaxis else {}
        yaxis['domain'] = [0.0, top_of_plot]
        fig.update_layout(yaxis=yaxis)

        # Add the title annotation centered in the reserved band
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

    # Case: selections incomplete -> keep the footer message
    if not all([region, variable, scenario]):
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
        fig = add_footer(fig, "Please select all options to display the chart")
        return fig

    # Filter & years
    filtered_df = df_ph[
        (df_ph['Region'] == region) &
        (df_ph['Variable'] == variable) &
        (df_ph['Scenario'] == scenario)
    ]
    years = get_years_ph(df_ph)
    if not year_range:
        selected_years = years
    else:
        selected_years = [y for y in years if year_range[0] <= y <= year_range[1]]

    # Case: no data -> keep the footer message
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

    # Melt for plotting
    melted_df = filtered_df.melt(
        id_vars=['Region', 'Variable', 'Scenario'],
        value_vars=[str(y) for y in selected_years],
        var_name='Year', value_name='Value'
    )

    # Plot a single line, no legend
    fig = px.line(
        melted_df,
        x='Year',
        y='Value',
        color_discrete_sequence=[line_color]
    )
    fig.update_traces(showlegend=False)

    # Base layout (grid, backgrounds, axis title set to variable)
    fig.update_layout(
        title=None,
        plot_bgcolor=background,
        paper_bgcolor=background,
        font=dict(color="#222"),
        xaxis=dict(gridcolor="#EEE"),
        yaxis=dict(gridcolor="#EEE"),
        showlegend=False,
        yaxis_title=variable
    )

    # Compose the title text (multi-line)
    title_text = (
        f"<b>Physical Risk</b><br>"
        f"{region} - {variable}<br>"
        f"<b>Scenario:</b> {scenario}"
    )

    # Add the title at the top inside the figure
    fig = add_top_title(fig, title_text, font_size=16, band=0.16)

    return fig
