import dash
import logging
from dash import dcc, html, Input, Output
import plotly.express as px
import datetime
import pandas as pd
from services.db_utils import get_regular_market_data_by_security, get_regular_market_all_security_descriptions, get_regular_market_data_by_date
from utils.logging import setup_logging
from scripts.backfill_increment import main as backfill_increment

setup_logging()
logger = logging.getLogger(__name__)

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children=[
    html.H1(children='Security Trades and TTA Analysis'),

    html.Div([
        dcc.Dropdown(id='security-dropdown', options=[], placeholder="Select a security..."),
    ]),

    dcc.Graph(id='trades-chart'),
    dcc.Graph(id='tta-chart')
])

# Callback to populate dropdown
@app.callback(
    Output('security-dropdown', 'options'),
    Input('security-dropdown', 'value')
)
def update_dropdown(_):
    today_date = datetime.date.today()
    do_backfill = get_regular_market_data_by_date(today_date)

    if not do_backfill:
        logger.info(f"No data found for {today_date}. Run backfill script.")
        backfill_increment()
        
    descriptions = get_regular_market_all_security_descriptions()
    return [{'label': desc, 'value': desc} for desc in descriptions]

# Callback to update figures
@app.callback(
    Output('trades-chart', 'figure'),
    Output('tta-chart', 'figure'),
    Input('security-dropdown', 'value')
)
def update_charts(selected_security):
    if not selected_security:
        empty_trades_fig = px.line(title="Please select a security to see the chart")
        empty_tta_fig = px.line() 
        return empty_trades_fig, empty_tta_fig


    market_data = get_regular_market_data_by_security(selected_security)

    if not market_data:
        empty_trades_fig = px.line(title=f"No data available for {selected_security}")
        empty_tta_fig = px.line() 
        return empty_trades_fig, empty_tta_fig

    df = pd.DataFrame([vars(s) for s in market_data])
    df['datetime'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['datetime'].dt.date

    # Group by date and aggregate trades and TTA
    daily_df = df.groupby('date').agg(
        trades=('trades', 'sum'),
        tta=('tta', 'sum')
    ).reset_index()

    trades_fig = px.line(
        daily_df, x='date', y='trades',
        title=f'Daily Trades for {selected_security}',
        labels={'trades': 'Trades', 'date': 'Date'},
        markers=True
    )
    trades_fig.update_traces(marker=dict(size=10))

    tta_fig = px.line(
        daily_df, x='date', y='tta',
        title=f'Daily TTA for {selected_security}',
        labels={'tta': 'TTA', 'date': 'Date'},
        markers=True
    )
    tta_fig.update_traces(marker=dict(size=10))


    return trades_fig, tta_fig


if __name__ == '__main__':
    app.run(debug=True)