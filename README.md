# Hotel Bookings Dashboard

A multi-page interactive dashboard built with **Dash** and **Plotly**, analyzing hotel booking cancellations and trends.

## Project Structure

```
dashboard/
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── assets/
│   └── style.css          # Custom styling
├── pages/
│   ├── overview.py        # Page 1: KPIs and overview charts
│   ├── trends.py          # Page 2: Seasonal & booking trends
│   └── cancellation_analysis.py  # Page 3: Deep-dive analysis
└── README.md
```

## Setup & Run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure `hotel_bookings.csv` is in the `dashboard/` project root (same folder as `app.py`).

3. Run the app:
```bash
python app.py
```

4. Open your browser at: [http://127.0.0.1:8050](http://127.0.0.1:8050)

## Dashboard Pages

### Page 1: Overview
- KPI cards (Total bookings, Cancellation rate, Avg ADR, Avg Lead Time)
- Cancellation rate by hotel type
- Revenue comparison (realized vs lost)
- Deposit type impact
- Customer type analysis

### Page 2: Booking Trends
- Monthly booking trends (line/bar toggle)
- Seasonal booking & cancellation patterns
- Market segment cancellation risk
- Top guest countries (interactive slider)

### Page 3: Cancellation Analysis
- Lead time as cancellation predictor
- ADR distribution comparison
- Special requests impact
- Repeat guest loyalty
- **Booking Risk Estimator** (interactive tool)

## Interactive Components Used
- **Dropdowns**: Hotel type, year, metric selection
- **Sliders**: Lead time range, ADR range, country count
- **Radio buttons**: Cancellation status filter
- **Buttons**: Chart type toggle, Apply filters, Calculate risk
- **Input fields**: Numeric inputs for risk estimator
- **Callbacks**: All charts update dynamically based on filter selections

## Data Source
Hotel Bookings dataset (`hotel_bookings.csv`) — contains ~119,000 booking records from City and Resort hotels.

## Key Insights
- City Hotels have a 41.7% cancellation rate vs 27.8% for Resort Hotels
- Lead time is the strongest predictor of cancellation
- Special requests significantly reduce cancellation probability
- Repeat guests are far more loyal than first-time visitors
- Summer months (July-August) see peak bookings and cancellations
