import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

dash.register_page(__name__, path='/cancellation-analysis', name='Cancellation Analysis',
                   title='Cancellation Analysis')

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

# Layout
layout = dbc.Container([
    html.H2("Cancellation Deep-Dive Analysis", className="page-title"),
    html.P("Investigate key cancellation drivers: lead time, ADR, special requests, and repeat guests.",
           className="page-subtitle"),

    # Filters
    dbc.Row([
        dbc.Col([
            html.Label("Hotel Type:", className="fw-bold mb-1"),
            dcc.Dropdown(
                id='cancel-hotel-filter',
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
            html.Label("Lead Time Range (days):", className="fw-bold mb-1"),
            dcc.RangeSlider(
                id='cancel-lead-slider',
                min=0, max=800, step=10,
                value=[0, 800],
                marks={0: '0', 100: '100', 200: '200', 400: '400', 600: '600', 800: '800'},
                tooltip={"placement": "bottom", "always_visible": False},
            ),
        ], md=4),
        dbc.Col([
            html.Label("ADR Range (€):", className="fw-bold mb-1"),
            dcc.RangeSlider(
                id='cancel-adr-slider',
                min=0, max=500, step=10,
                value=[0, 500],
                marks={0: '0', 100: '100', 200: '200', 300: '300', 400: '400', 500: '500'},
                tooltip={"placement": "bottom", "always_visible": False},
            ),
        ], md=4),
        dbc.Col([
            html.Label("Apply Filters:", className="fw-bold mb-1"),
            html.Br(),
            dbc.Button("Update Charts", id='cancel-apply-btn', color="primary",
                       className="w-100", n_clicks=0),
        ], md=1),
    ], className="filter-section"),

    # Row 1: Lead Time Analysis
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Lead Time: The #1 Predictor of Cancellation"),
                dbc.CardBody(dcc.Graph(id='cancel-lead-chart'))
            ])
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("ADR Distribution: Canceled vs Not Canceled"),
                dbc.CardBody(dcc.Graph(id='cancel-adr-chart'))
            ])
        ], md=6),
    ], className="mb-4"),

    # Row 2: Special Requests & Repeat Guests
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Special Requests Reduce Cancellations"),
                dbc.CardBody(dcc.Graph(id='cancel-special-chart'))
            ])
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Repeat Guests vs First-Time Visitors"),
                dbc.CardBody(dcc.Graph(id='cancel-repeat-chart'))
            ])
        ], md=6),
    ], className="mb-4"),

    # Row 3: Booking Risk Estimator
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fa-solid fa-calculator me-2"),
                    "Booking Risk Estimator",
                    dbc.Badge("Interactive Tool", color="warning", className="ms-2")
                ]),
                dbc.CardBody([
                    html.P("Enter booking parameters to estimate cancellation risk based on historical data:",
                           className="text-muted"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Lead Time (days):", className="fw-bold"),
                            dbc.Input(id='risk-lead-input', type='number', value=60,
                                      min=0, max=800, step=1),
                        ], md=3),
                        dbc.Col([
                            html.Label("ADR (€):", className="fw-bold"),
                            dbc.Input(id='risk-adr-input', type='number', value=100,
                                      min=0, max=1000, step=5),
                        ], md=3),
                        dbc.Col([
                            html.Label("Special Requests:", className="fw-bold"),
                            dcc.Dropdown(
                                id='risk-special-input',
                                options=[{'label': str(i), 'value': i} for i in range(6)],
                                value=0, clearable=False
                            ),
                        ], md=2),
                        dbc.Col([
                            html.Label("Is Repeat Guest:", className="fw-bold"),
                            dcc.Dropdown(
                                id='risk-repeat-input',
                                options=[
                                    {'label': 'No', 'value': 0},
                                    {'label': 'Yes', 'value': 1}
                                ],
                                value=0, clearable=False
                            ),
                        ], md=2),
                        dbc.Col([
                            html.Label("Estimate:", className="fw-bold"),
                            dbc.Button("Calculate", id='risk-calc-btn', color="success",
                                       className="w-100", n_clicks=0),
                        ], md=2),
                    ], className="mb-3"),
                    html.Div(id='risk-result-output')
                ])
            ])
        ], md=12),
    ]),
], fluid=True)


@callback(
    [Output('cancel-lead-chart', 'figure'),
     Output('cancel-adr-chart', 'figure'),
     Output('cancel-special-chart', 'figure'),
     Output('cancel-repeat-chart', 'figure')],
    [Input('cancel-apply-btn', 'n_clicks')],
    [State('cancel-hotel-filter', 'value'),
     State('cancel-lead-slider', 'value'),
     State('cancel-adr-slider', 'value')]
)
def update_cancellation_charts(n_clicks, hotel, lead_range, adr_range):
    filtered = df.copy()
    if hotel != 'All':
        filtered = filtered[filtered['hotel'] == hotel]
    filtered = filtered[(filtered['lead_time'] >= lead_range[0]) & (filtered['lead_time'] <= lead_range[1])]
    filtered = filtered[(filtered['adr'] >= adr_range[0]) & (filtered['adr'] <= adr_range[1])]

    # Chart 1: Lead time binned analysis
    bins = [0, 30, 90, 180, 365, 800]
    labels = ['0-30', '31-90', '91-180', '181-365', '365+']
    filtered_lt = filtered.copy()
    filtered_lt['lead_group'] = pd.cut(filtered_lt['lead_time'], bins=bins, labels=labels, include_lowest=True)

    lead_data = filtered_lt.groupby('lead_group', observed=True).agg(
        count=('is_canceled', 'count'),
        cancel_rate=('is_canceled', 'mean')
    ).reset_index()
    lead_data['cancel_pct'] = lead_data['cancel_rate'] * 100

    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(go.Bar(x=lead_data['lead_group'], y=lead_data['count'],
                          name='Bookings', marker_color='#3498db', opacity=0.6),
                   secondary_y=False)
    fig1.add_trace(go.Scatter(x=lead_data['lead_group'], y=lead_data['cancel_pct'],
                              name='Cancellation Rate', mode='lines+markers',
                              line=dict(color='#e74c3c', width=3), marker=dict(size=10)),
                   secondary_y=True)
    fig1.update_layout(template='plotly_white', height=370, margin=dict(t=30, b=30))
    fig1.update_xaxes(title_text='Lead Time (days)')
    fig1.update_yaxes(title_text='Bookings', secondary_y=False)
    fig1.update_yaxes(title_text='Cancel Rate (%)', secondary_y=True)

    # Chart 2: ADR distribution
    df_adr = filtered[(filtered['adr'] > 0) & (filtered['adr'] < 500)]
    fig2 = go.Figure()
    for status, color, name in [(0, '#2ecc71', 'Not Canceled'), (1, '#e74c3c', 'Canceled')]:
        fig2.add_trace(go.Histogram(x=df_adr[df_adr['is_canceled'] == status]['adr'],
                                    name=name, marker_color=color, opacity=0.6, nbinsx=40))
    fig2.update_layout(barmode='overlay', template='plotly_white', height=370,
                       margin=dict(t=30, b=30), xaxis_title='ADR (€)', yaxis_title='Count')

    # Chart 3: Special requests
    sr_data = filtered.groupby('total_of_special_requests')['is_canceled'].mean().reset_index()
    sr_data['pct'] = sr_data['is_canceled'] * 100

    colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#27ae60', '#1abc9c']
    fig3 = px.bar(sr_data, x='total_of_special_requests', y='pct',
                  text=[f"{v:.1f}%" for v in sr_data['pct']],
                  labels={'total_of_special_requests': 'Number of Special Requests',
                          'pct': 'Cancellation Rate (%)'},
                  template='plotly_white',
                  color='total_of_special_requests',
                  color_continuous_scale='RdYlGn_r')
    fig3.update_traces(textposition='outside')
    fig3.update_layout(height=370, margin=dict(t=30, b=30), coloraxis_showscale=False)

    # Chart 4: Repeat guests
    repeat_data = filtered.groupby('is_repeated_guest')['is_canceled'].mean().reset_index()
    repeat_data['label'] = repeat_data['is_repeated_guest'].map({0: 'First-Time', 1: 'Repeat Guest'})
    repeat_data['pct'] = repeat_data['is_canceled'] * 100

    fig4 = px.bar(repeat_data, x='label', y='pct',
                  color='label',
                  color_discrete_map={'First-Time': '#e67e22', 'Repeat Guest': '#2ecc71'},
                  text=[f"{v:.1f}%" for v in repeat_data['pct']],
                  labels={'label': 'Guest Type', 'pct': 'Cancellation Rate (%)'},
                  template='plotly_white')
    fig4.update_traces(textposition='outside')
    fig4.update_layout(height=370, margin=dict(t=30, b=30), showlegend=False)

    return fig1, fig2, fig3, fig4
 

@callback(
    Output('risk-result-output', 'children'),
    [Input('risk-calc-btn', 'n_clicks')],
    [State('risk-lead-input', 'value'),
     State('risk-adr-input', 'value'),
     State('risk-special-input', 'value'),
     State('risk-repeat-input', 'value'),
     State('cancel-hotel-filter', 'value')]
)
def estimate_risk(n_clicks, lead_time, adr, special_req, repeat_guest, hotel):
    if n_clicks == 0:
        return html.P("Click 'Calculate' to estimate cancellation risk.", className="text-muted mt-2")

    # Simple rule-based risk estimation from historical data
    filtered = df.copy()
    if hotel != 'All':
        filtered = filtered[filtered['hotel'] == hotel]

    # Find similar bookings
    lead_margin = 30
    adr_margin = 30
    similar = filtered[
        (filtered['lead_time'].between(max(0, lead_time - lead_margin), lead_time + lead_margin)) &
        (filtered['adr'].between(max(0, adr - adr_margin), adr + adr_margin)) &
        (filtered['total_of_special_requests'] == special_req) &
        (filtered['is_repeated_guest'] == repeat_guest)
    ]

    if len(similar) < 10:
        # Widen search if too few matches
        similar = filtered[
            (filtered['lead_time'].between(max(0, lead_time - 60), lead_time + 60)) &
            (filtered['adr'].between(max(0, adr - 60), adr + 60))
        ]

    if len(similar) == 0:
        risk_pct = filtered['is_canceled'].mean() * 100
        sample_size = len(filtered)
    else:
        risk_pct = similar['is_canceled'].mean() * 100
        sample_size = len(similar)

    # Determine risk level
    if risk_pct < 25:
        color = "success"
        level = "LOW"
        icon = "fa-solid fa-circle-check"
    elif risk_pct < 50:
        color = "warning"
        level = "MEDIUM"
        icon = "fa-solid fa-triangle-exclamation"
    else:
        color = "danger"
        level = "HIGH"
        icon = "fa-solid fa-circle-exclamation"

    return dbc.Alert([
        html.H4([
            html.I(className=f"{icon} me-2"),
            f"Estimated Cancellation Risk: {risk_pct:.1f}% ({level})"
        ], className="alert-heading"),
        html.P(f"Based on {sample_size:,} similar historical bookings with comparable "
               f"lead time (~{lead_time} days), ADR (~€{adr}), "
               f"{special_req} special request(s), and "
               f"{'repeat' if repeat_guest else 'first-time'} guest status."),
    ], color=color, className="mt-3")
