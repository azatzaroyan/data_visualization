import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

dash.register_page(__name__, path='/trends', name='Trends', title='Booking Trends')

# Load data
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'hotel_bookings.csv')
df = pd.read_csv(data_path)

# Data cleaning
df['children'] = df['children'].fillna(0)
df['country'] = df['country'].fillna('Unknown')
df['agent'] = df['agent'].replace('NULL', 0).astype(float)
df['company'] = df['company'].replace('NULL', 0).astype(float)
df['total_nights'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
df['estimated_revenue'] = df['adr'] * df['total_nights']

month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

# Layout
layout = dbc.Container([
    html.H2("Booking & Seasonal Trends", className="page-title"),
    html.P("Explore monthly booking patterns, seasonal cancellation rates, and market segment performance.",
           className="page-subtitle"),

    # Filters
    dbc.Row([
        dbc.Col([
            html.Label("Hotel Type:", className="fw-bold mb-1"),
            dcc.Dropdown(
                id='trends-hotel-filter',
                options=[
                    {'label': 'All Hotels', 'value': 'All'},
                    {'label': 'City Hotel', 'value': 'City Hotel'},
                    {'label': 'Resort Hotel', 'value': 'Resort Hotel'}
                ],
                value='All',
                clearable=False,
            ),
        ], md=3),
        dbc.Col([
            html.Label("Year:", className="fw-bold mb-1"),
            dcc.Dropdown(
                id='trends-year-filter',
                options=[{'label': 'All Years', 'value': 'All'}] +
                        [{'label': str(y), 'value': y} for y in sorted(df['arrival_date_year'].unique())],
                value='All',
                clearable=False,
            ),
        ], md=3),
        dbc.Col([
            html.Label("Metric to Display:", className="fw-bold mb-1"),
            dcc.Dropdown(
                id='trends-metric-filter',
                options=[
                    {'label': 'Number of Bookings', 'value': 'bookings'},
                    {'label': 'Cancellation Rate', 'value': 'cancel_rate'},
                    {'label': 'Average ADR', 'value': 'avg_adr'},
                    {'label': 'Average Lead Time', 'value': 'avg_lead'},
                ],
                value='bookings',
                clearable=False,
            ),
        ], md=3),
        dbc.Col([
            html.Label("Chart Type:", className="fw-bold mb-1"),
            dbc.ButtonGroup([
                dbc.Button("Line", id="btn-line", color="primary", outline=True, size="sm", n_clicks=0),
                dbc.Button("Bar", id="btn-bar", color="primary", outline=True, size="sm", n_clicks=0),
            ], className="mt-1"),
        ], md=3),
    ], className="filter-section"),

    # Monthly Trends Chart
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Monthly Booking Trends"),
                dbc.CardBody(dcc.Graph(id='trends-monthly-chart'))
            ])
        ], md=12),
    ], className="mb-4"),

    # Second Row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Seasonal Booking & Cancellation Patterns (Both Hotels)"),
                dbc.CardBody(dcc.Graph(id='trends-seasonal-chart'))
            ])
        ], md=7),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Market Segment Cancellation Risk"),
                dbc.CardBody(dcc.Graph(id='trends-segment-chart'))
            ])
        ], md=5),
    ], className="mb-4"),

    # Third Row: Country analysis
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    "Top Guest Countries",
                    dbc.Badge("Interactive", color="info", className="ms-2")
                ]),
                dbc.CardBody([
                    html.Label("Number of countries to show:", className="fw-bold mb-1"),
                    dcc.Slider(
                        id='trends-country-slider',
                        min=5, max=20, step=1, value=10,
                        marks={5: '5', 10: '10', 15: '15', 20: '20'},
                    ),
                    dcc.Graph(id='trends-country-chart')
                ])
            ])
        ], md=12),
    ]),
], fluid=True)


@callback(
    Output('trends-monthly-chart', 'figure'),
    [Input('trends-hotel-filter', 'value'),
     Input('trends-year-filter', 'value'),
     Input('trends-metric-filter', 'value'),
     Input('btn-line', 'n_clicks'),
     Input('btn-bar', 'n_clicks')]
)
def update_monthly_chart(hotel, year, metric, line_clicks, bar_clicks):
    # Determine chart type based on which button was last clicked
    chart_type = 'line' if line_clicks >= bar_clicks else 'bar'

    filtered = df.copy()
    if hotel != 'All':
        filtered = filtered[filtered['hotel'] == hotel]
    if year != 'All':
        filtered = filtered[filtered['arrival_date_year'] == year]

    monthly = filtered.groupby('arrival_date_month').agg(
        bookings=('is_canceled', 'count'),
        cancel_rate=('is_canceled', 'mean'),
        avg_adr=('adr', 'mean'),
        avg_lead=('lead_time', 'mean'),
    ).reset_index()
    monthly['arrival_date_month'] = pd.Categorical(monthly['arrival_date_month'],
                                                    categories=month_order, ordered=True)
    monthly = monthly.sort_values('arrival_date_month')
    monthly['cancel_rate'] = monthly['cancel_rate'] * 100

    metric_labels = {
        'bookings': 'Number of Bookings',
        'cancel_rate': 'Cancellation Rate (%)',
        'avg_adr': 'Average Daily Rate (€)',
        'avg_lead': 'Average Lead Time (days)',
    }

    if chart_type == 'line':
        fig = px.line(monthly, x='arrival_date_month', y=metric,
                      markers=True,
                      labels={'arrival_date_month': 'Month', metric: metric_labels[metric]},
                      template='plotly_white')
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
    else:
        fig = px.bar(monthly, x='arrival_date_month', y=metric,
                     labels={'arrival_date_month': 'Month', metric: metric_labels[metric]},
                     template='plotly_white', color=metric,
                     color_continuous_scale='Blues')
        fig.update_layout(coloraxis_showscale=False)

    fig.update_layout(height=400, margin=dict(t=30, b=30),
                      xaxis_title='Month', yaxis_title=metric_labels[metric])
    return fig


@callback(
    Output('trends-seasonal-chart', 'figure'),
    [Input('trends-year-filter', 'value')]
)
def update_seasonal_chart(year):
    filtered = df.copy()
    if year != 'All':
        filtered = filtered[filtered['arrival_date_year'] == year]

    monthly = filtered.groupby(['arrival_date_month', 'hotel']).agg(
        bookings=('is_canceled', 'count'),
        cancel_rate=('is_canceled', 'mean'),
    ).reset_index()
    monthly['arrival_date_month'] = pd.Categorical(monthly['arrival_date_month'],
                                                    categories=month_order, ordered=True)
    monthly = monthly.sort_values('arrival_date_month')
    monthly['cancel_pct'] = monthly['cancel_rate'] * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for hotel_type, color in [('City Hotel', '#3498db'), ('Resort Hotel', '#e67e22')]:
        mask = monthly['hotel'] == hotel_type
        fig.add_trace(go.Bar(x=monthly[mask]['arrival_date_month'], y=monthly[mask]['bookings'],
                             name=f'{hotel_type} - Bookings', marker_color=color, opacity=0.4),
                      secondary_y=False)
        fig.add_trace(go.Scatter(x=monthly[mask]['arrival_date_month'], y=monthly[mask]['cancel_pct'],
                                 name=f'{hotel_type} - Cancel Rate', mode='lines+markers',
                                 line=dict(color=color, width=2.5), marker=dict(size=7)),
                      secondary_y=True)

    fig.update_layout(template='plotly_white', height=400, barmode='group',
                      margin=dict(t=30, b=30), legend=dict(orientation="h", yanchor="bottom",
                                                            y=1.02, xanchor="right", x=1))
    fig.update_xaxes(title_text='Month')
    fig.update_yaxes(title_text='Bookings', secondary_y=False)
    fig.update_yaxes(title_text='Cancellation Rate (%)', secondary_y=True)
    return fig


@callback(
    Output('trends-segment-chart', 'figure'),
    [Input('trends-hotel-filter', 'value'),
     Input('trends-year-filter', 'value')]
)
def update_segment_chart(hotel, year):
    filtered = df.copy()
    if hotel != 'All':
        filtered = filtered[filtered['hotel'] == hotel]
    if year != 'All':
        filtered = filtered[filtered['arrival_date_year'] == year]

    seg = filtered.groupby('market_segment').agg(
        bookings=('is_canceled', 'count'),
        cancel_rate=('is_canceled', 'mean')
    ).reset_index()
    seg['cancel_pct'] = seg['cancel_rate'] * 100
    seg = seg.sort_values('cancel_pct', ascending=True)

    fig = px.bar(seg, y='market_segment', x='cancel_pct', orientation='h',
                 color='cancel_pct', color_continuous_scale='RdYlGn_r',
                 text=[f"{v:.1f}%" for v in seg['cancel_pct']],
                 labels={'market_segment': 'Market Segment', 'cancel_pct': 'Cancellation Rate (%)'},
                 template='plotly_white')
    fig.update_traces(textposition='outside')
    fig.update_layout(height=400, margin=dict(t=30, b=30, l=100), coloraxis_showscale=False)
    return fig


@callback(
    Output('trends-country-chart', 'figure'),
    [Input('trends-hotel-filter', 'value'),
     Input('trends-year-filter', 'value'),
     Input('trends-country-slider', 'value')]
)
def update_country_chart(hotel, year, n_countries):
    filtered = df.copy()
    if hotel != 'All':
        filtered = filtered[filtered['hotel'] == hotel]
    if year != 'All':
        filtered = filtered[filtered['arrival_date_year'] == year]

    country_stats = filtered.groupby('country').agg(
        bookings=('is_canceled', 'count'),
        cancel_rate=('is_canceled', 'mean')
    ).reset_index()
    top_countries = country_stats.nlargest(n_countries, 'bookings').sort_values('cancel_rate', ascending=False)
    top_countries['cancel_pct'] = top_countries['cancel_rate'] * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(x=top_countries['country'], y=top_countries['bookings'],
                         name='Bookings', marker_color='#3498db', opacity=0.6),
                  secondary_y=False)

    fig.add_trace(go.Scatter(x=top_countries['country'], y=top_countries['cancel_pct'],
                             name='Cancellation Rate', mode='lines+markers',
                             line=dict(color='#e74c3c', width=3), marker=dict(size=10)),
                  secondary_y=True)

    fig.update_layout(template='plotly_white', height=400, margin=dict(t=30, b=30))
    fig.update_xaxes(title_text='Country Code')
    fig.update_yaxes(title_text='Number of Bookings', secondary_y=False)
    fig.update_yaxes(title_text='Cancellation Rate (%)', secondary_y=True)
    return fig
