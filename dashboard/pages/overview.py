import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

dash.register_page(__name__, path='/', name='Overview', title='Overview')

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


def create_kpi_card(title, value, icon, color):
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.I(className=f"{icon}", style={"fontSize": "1.5rem", "color": color}),
            ], className="mb-2"),
            html.H3(value, className="kpi-value", style={"color": color}),
            html.P(title, className="kpi-label"),
        ], className="kpi-card"),
        className="h-100"
    )


# Layout
layout = dbc.Container([
    # Page Header
    html.H2("Hotel Bookings Overview", className="page-title"),
    html.P("Key performance metrics and cancellation insights across hotel types.",
           className="page-subtitle"),

    # Filters
    dbc.Row([
        dbc.Col([
            html.Label("Select Hotel Type:", className="fw-bold mb-1"),
            dcc.Dropdown(
                id='overview-hotel-filter',
                options=[
                    {'label': 'All Hotels', 'value': 'All'},
                    {'label': 'City Hotel', 'value': 'City Hotel'},
                    {'label': 'Resort Hotel', 'value': 'Resort Hotel'}
                ],
                value='All',
                clearable=False,
            ),
        ], md=4),
        dbc.Col([
            html.Label("Select Year:", className="fw-bold mb-1"),
            dcc.Dropdown(
                id='overview-year-filter',
                options=[{'label': 'All Years', 'value': 'All'}] +
                        [{'label': str(y), 'value': y} for y in sorted(df['arrival_date_year'].unique())],
                value='All',
                clearable=False,
            ),
        ], md=4),
        dbc.Col([
            html.Label("Cancellation Status:", className="fw-bold mb-1"),
            dcc.RadioItems(
                id='overview-cancel-filter',
                options=[
                    {'label': ' All', 'value': 'All'},
                    {'label': ' Not Canceled', 'value': 0},
                    {'label': ' Canceled', 'value': 1},
                ],
                value='All',
                inline=True,
                className="mt-2"
            ),
        ], md=4),
    ], className="filter-section"),

    # KPI Cards
    html.Div(id='overview-kpi-row'),

    html.Br(),

    # Charts Row 1
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Cancellation Rate by Hotel Type"),
                dbc.CardBody(dcc.Graph(id='overview-cancel-bar'))
            ])
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Revenue: Realized vs Lost to Cancellations"),
                dbc.CardBody(dcc.Graph(id='overview-revenue-bar'))
            ])
        ], md=6),
    ], className="mb-4"),

    # Charts Row 2
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Deposit Type Impact on Cancellations"),
                dbc.CardBody(dcc.Graph(id='overview-deposit-bar'))
            ])
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Customer Type Cancellation Rates"),
                dbc.CardBody(dcc.Graph(id='overview-customer-bar'))
            ])
        ], md=6),
    ]),
], fluid=True)


@callback(
    [Output('overview-kpi-row', 'children'),
     Output('overview-cancel-bar', 'figure'),
     Output('overview-revenue-bar', 'figure'),
     Output('overview-deposit-bar', 'figure'),
     Output('overview-customer-bar', 'figure')],
    [Input('overview-hotel-filter', 'value'),
     Input('overview-year-filter', 'value'),
     Input('overview-cancel-filter', 'value')]
)
def update_overview(hotel, year, cancel_status):
    filtered = df.copy()
    if hotel != 'All':
        filtered = filtered[filtered['hotel'] == hotel]
    if year != 'All':
        filtered = filtered[filtered['arrival_date_year'] == year]
    if cancel_status != 'All':
        filtered = filtered[filtered['is_canceled'] == cancel_status]

    # KPIs
    total_bookings = len(filtered)
    cancel_rate = filtered['is_canceled'].mean() * 100 if len(filtered) > 0 else 0
    avg_adr = filtered['adr'].mean() if len(filtered) > 0 else 0
    total_revenue = filtered['estimated_revenue'].sum()
    avg_lead = filtered['lead_time'].mean() if len(filtered) > 0 else 0

    kpi_row = dbc.Row([
        dbc.Col(create_kpi_card("Total Bookings", f"{total_bookings:,}",
                                "fa-solid fa-book", "#3498db"), md=3),
        dbc.Col(create_kpi_card("Cancellation Rate", f"{cancel_rate:.1f}%",
                                "fa-solid fa-ban", "#e74c3c"), md=3),
        dbc.Col(create_kpi_card("Avg. Daily Rate", f"€{avg_adr:.0f}",
                                "fa-solid fa-euro-sign", "#2ecc71"), md=3),
        dbc.Col(create_kpi_card("Avg. Lead Time", f"{avg_lead:.0f} days",
                                "fa-solid fa-clock", "#f39c12"), md=3),
    ], className="mb-4")

    # Chart 1: Cancellation by hotel type
    cancel_by_hotel = df.groupby('hotel')['is_canceled'].agg(['sum', 'count', 'mean']).reset_index()
    cancel_by_hotel.columns = ['Hotel Type', 'Canceled', 'Total', 'Rate']
    cancel_by_hotel['Not Canceled'] = cancel_by_hotel['Total'] - cancel_by_hotel['Canceled']

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(name='Not Canceled', x=cancel_by_hotel['Hotel Type'],
                          y=cancel_by_hotel['Not Canceled'], marker_color='#2ecc71'))
    fig1.add_trace(go.Bar(name='Canceled', x=cancel_by_hotel['Hotel Type'],
                          y=cancel_by_hotel['Canceled'], marker_color='#e74c3c'))
    fig1.update_layout(barmode='stack', template='plotly_white', height=350,
                       margin=dict(t=30, b=30))

    # Chart 2: Revenue
    rev_data = df.copy()
    if hotel != 'All':
        rev_data = rev_data[rev_data['hotel'] == hotel]
    if year != 'All':
        rev_data = rev_data[rev_data['arrival_date_year'] == year]

    revenue_summary = rev_data.groupby(['hotel', 'is_canceled'])['estimated_revenue'].sum().reset_index()
    revenue_summary['Status'] = revenue_summary['is_canceled'].map({0: 'Realized', 1: 'Lost'})

    fig2 = px.bar(revenue_summary, x='hotel', y='estimated_revenue', color='Status',
                  barmode='group',
                  color_discrete_map={'Realized': '#2ecc71', 'Lost': '#e74c3c'},
                  labels={'estimated_revenue': 'Revenue (€)', 'hotel': 'Hotel Type'},
                  template='plotly_white')
    fig2.update_layout(height=350, margin=dict(t=30, b=30))

    # Chart 3: Deposit type
    deposit_data = filtered.groupby('deposit_type').agg(
        cancel_rate=('is_canceled', 'mean'),
        count=('is_canceled', 'count')
    ).reset_index()
    deposit_data['cancel_pct'] = deposit_data['cancel_rate'] * 100

    fig3 = px.bar(deposit_data, x='deposit_type', y='cancel_pct',
                  color='cancel_pct',
                  color_continuous_scale=['#2ecc71', '#f39c12', '#e74c3c'],
                  text=[f"{v:.1f}%" for v in deposit_data['cancel_pct']],
                  labels={'deposit_type': 'Deposit Type', 'cancel_pct': 'Cancellation Rate (%)'},
                  template='plotly_white')
    fig3.update_traces(textposition='outside')
    fig3.update_layout(height=350, margin=dict(t=30, b=30), coloraxis_showscale=False)

    # Chart 4: Customer type
    cust_data = filtered.groupby('customer_type')['is_canceled'].mean().sort_values(ascending=False).reset_index()
    cust_data['pct'] = cust_data['is_canceled'] * 100

    fig4 = px.bar(cust_data, x='customer_type', y='pct',
                  color='pct',
                  color_continuous_scale=['#2ecc71', '#f39c12', '#e74c3c'],
                  text=[f"{v:.1f}%" for v in cust_data['pct']],
                  labels={'customer_type': 'Customer Type', 'pct': 'Cancellation Rate (%)'},
                  template='plotly_white')
    fig4.update_traces(textposition='outside')
    fig4.update_layout(height=350, margin=dict(t=30, b=30), coloraxis_showscale=False)

    return kpi_row, fig1, fig2, fig3, fig4
