import dash
import logging
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from services.db_utils import get_regular_market_data_by_security, get_regular_market_all_security_descriptions, get_regular_market_data_by_date
from utils.logging import setup_logging
from config.template import INDEX_STRING
setup_logging()
logger = logging.getLogger(__name__)

app = dash.Dash(__name__)
server = app.server

# Custom CSS styling
app.index_string = INDEX_STRING

app.layout = html.Div(className='main-container', children=[
    # Header Section
    html.Div(className='header', children=[
        html.H1('Security Trades & TTA Analytics'),
        html.P('Real-time market analysis and trading insights dashboard')
    ]),
    
    # Controls Section
    html.Div(className='controls-container', children=[
        html.Div(className='controls-grid', children=[
            html.Div(className='control-group security-control', children=[
                html.Label('🔍 Select Security', className='control-label centered'),
                dcc.Dropdown(
                    id='security-dropdown',
                    options=[],
                    placeholder="Choose a security to analyze...",
                    className='modern-dropdown'
                )
            ]),
            html.Div(className='control-group date-control', children=[
                html.Label('📅 Date Range', className='control-label centered'),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    min_date_allowed=None,
                    max_date_allowed=None,
                    start_date=None,
                    end_date=None,
                    display_format='YYYY-MM-DD',
                    className='modern-date-picker'
                )
            ]),
            html.Div(className='control-group last-update-control', children=[
                html.Label('🕐 Last Update', className='control-label centered'),
                html.Div(id='last-update-display', className='last-update-info')
            ])
        ])
    ]),
    
    # Summary Section
    html.Div(id='summary-box', className='summary-container'),
    
    # Charts Section
    html.Div(className='charts-container', children=[
        html.Div(className='chart-wrapper', children=[
            dcc.Graph(id='trades-chart', config={'displayModeBar': False})
        ]),
        html.Div(className='chart-wrapper', children=[
            dcc.Graph(id='tta-chart', config={'displayModeBar': False})
        ])
    ]),
    
    # Loading indicator
    dcc.Loading(
        id="loading",
        type="circle",
        children=[html.Div(id="loading-output")]
    )
])

# Callback to populate dropdown
@app.callback(
    Output('security-dropdown', 'options'),
    Input('security-dropdown', 'value')
)
def update_dropdown(_):
    try:
        descriptions = get_regular_market_all_security_descriptions()
        return [{'label': desc, 'value': desc} for desc in descriptions]
    except Exception as e:
        logger.error(f"Error loading securities: {e}")
        return []

# Callback to update figures and summary box
@app.callback(
    Output('trades-chart', 'figure'),
    Output('tta-chart', 'figure'),
    Output('summary-box', 'children'),
    Output('date-picker-range', 'min_date_allowed'),
    Output('date-picker-range', 'max_date_allowed'),
    Output('date-picker-range', 'start_date'),
    Output('date-picker-range', 'end_date'),
    Output('last-update-display', 'children'),
    Output('loading-output', 'children'),
    Input('security-dropdown', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    State('date-picker-range', 'min_date_allowed'),
    State('date-picker-range', 'max_date_allowed')
)
def update_charts(selected_security, start_date, end_date, min_date_state, max_date_state):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else ''
    
    def create_empty_figure(title, subtitle=""):
        fig = go.Figure()
        fig.add_annotation(
            text=title,
            x=0.5, y=0.6,
            xref="paper", yref="paper",
            font=dict(size=20, color="#666"),
            showarrow=False
        )
        if subtitle:
            fig.add_annotation(
                text=subtitle,
                x=0.5, y=0.4,
                xref="paper", yref="paper",
                font=dict(size=14, color="#999"),
                showarrow=False
            )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=400
        )
        return fig
    
    # Default last update display
    default_last_update = [
        html.Div("🕐", className='last-update-icon'),
        html.Div("No Data", className='last-update-value'),
        html.Div("Last Update", className='last-update-label')
    ]
    
    if not selected_security:
        empty_fig = create_empty_figure("📊 Select a security to view analytics", "Choose from the dropdown above to get started")
        return empty_fig, empty_fig, [], None, None, None, None, default_last_update, ""
    
    try:
        market_data = get_regular_market_data_by_security(selected_security)
        
        if not market_data:
            empty_fig = create_empty_figure(f"📭 No data available", f"No market data found for {selected_security}")
            return empty_fig, empty_fig, [], None, None, None, None, default_last_update, ""
        
        df = pd.DataFrame([vars(s) for s in market_data])
        df['datetime'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['datetime'].dt.date
        
        min_date = df['date'].min()
        max_date = df['date'].max()
        
        # Update date picker range only when security changes
        if triggered_id == 'security-dropdown':
            start_date = min_date
            end_date = max_date
        else:
            start_date = start_date or min_date_state
            end_date = end_date or max_date_state
        
        # Filter dataframe based on date picker
        if start_date and end_date:
            df_filtered = df[(df['date'] >= pd.to_datetime(start_date).date()) & (df['date'] <= pd.to_datetime(end_date).date())]
        else:
            df_filtered = df
        
        if df_filtered.empty:
            empty_fig = create_empty_figure("📅 No data in selected range", "Try adjusting your date range")
            return empty_fig, empty_fig, [], min_date, max_date, start_date, end_date, default_last_update, ""
        
        # Get latest data for summary
        latest_data = df.loc[df['datetime'].idxmax()]
        
        last_update_display = [
            html.Div("🕐", className='last-update-icon'),
            html.Div(latest_data['datetime'].strftime('%m/%d/%y %H:%M'), className='last-update-value'),
            html.Div("Last Update", className='last-update-label')
        ]
        
        #  Additional metrics
        total_trades = df_filtered['trades'].sum()
        total_tta = df_filtered['tta'].sum()
        price_change = df_filtered['ltp'].iloc[-1] - df_filtered['ltp'].iloc[0] if len(df_filtered) > 1 else 0
        
        # Create summary cards
        summary_children = [
            html.H3("📊 Market Overview", style={'color': '#333', 'marginBottom': '20px', 'fontSize': '1.5rem'}),
            html.Div(className='summary-grid', children=[
                html.Div(className='summary-card', children=[
                    html.Div("💰", className='summary-card-icon'),
                    html.Div(f"${latest_data['ltp']:.2f}", className='summary-card-value'),
                    html.Div("Last Traded Price", className='summary-card-label')
                ]),
                html.Div(className='summary-card', children=[
                    html.Div("📈", className='summary-card-icon'),
                    html.Div(f"${latest_data['high']:.2f}", className='summary-card-value'),
                    html.Div("Day High", className='summary-card-label')
                ]),
                html.Div(className='summary-card', children=[
                    html.Div("📉", className='summary-card-icon'),
                    html.Div(f"${latest_data['low']:.2f}", className='summary-card-value'),
                    html.Div("Day Low", className='summary-card-label')
                ]),
                html.Div(className='summary-card', children=[
                    html.Div("🔄", className='summary-card-icon'),
                    html.Div(f"{total_trades:,}", className='summary-card-value'),
                    html.Div("Total Trades", className='summary-card-label')
                ]),
                html.Div(className='summary-card', children=[
                    html.Div("📊", className='summary-card-icon'),
                    html.Div(f"${total_tta:,.0f}", className='summary-card-value'),
                    html.Div("Total TTA", className='summary-card-label')
                ]),
                html.Div(className='summary-card', children=[
                    html.Div("↕️", className='summary-card-icon'),
                    html.Div(f"${price_change:+.2f}", className='summary-card-value'),
                    html.Div("Price Change", className='summary-card-label')
                ])
            ])
        ]
        
        # Group by date and aggregate
        daily_df = df_filtered.groupby('date').agg(
            trades=('trades', 'sum'),
            tta=('tta', 'sum'),
            high=('high', 'max'),
            low=('low', 'min'),
            ltp=('ltp', 'last')
        ).reset_index()
        
        # Create trades chart
        trades_fig = go.Figure()
        trades_fig.add_trace(go.Scatter(
            x=daily_df['date'],
            y=daily_df['trades'],
            mode='lines+markers',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8, color='#667eea', line=dict(width=2, color='white')),
            name='Trades',
            hovertemplate='<b>%{x}</b><br>Trades: %{y:,}<extra></extra>'
        ))
        
        trades_fig.update_layout(
            title=dict(
                text=f'📈 Daily Trades - {selected_security}',
                font=dict(size=18, color='#333'),
                x=0.5
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#333'),
            xaxis=dict(
                gridcolor='#e2e8f0',
                title='Date',
                title_font=dict(size=12, color='#666')
            ),
            yaxis=dict(
                gridcolor='#e2e8f0',
                title='Number of Trades',
                title_font=dict(size=12, color='#666')
            ),
            height=400,
            hovermode='x unified'
        )
        
        # Create TTA chart
        tta_fig = go.Figure()
        tta_fig.add_trace(go.Scatter(
            x=daily_df['date'],
            y=daily_df['tta'],
            mode='lines+markers',
            line=dict(color='#764ba2', width=3),
            marker=dict(size=8, color='#764ba2', line=dict(width=2, color='white')),
            name='TTA',
            hovertemplate='<b>%{x}</b><br>TTA: $%{y:,.0f}<extra></extra>'
        ))
        
        tta_fig.update_layout(
            title=dict(
                text=f'💼 Daily TTA - {selected_security}',
                font=dict(size=18, color='#333'),
                x=0.5
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#333'),
            xaxis=dict(
                gridcolor='#e2e8f0',
                title='Date',
                title_font=dict(size=12, color='#666')
            ),
            yaxis=dict(
                gridcolor='#e2e8f0',
                title='Total Trading Amount ($)',
                title_font=dict(size=12, color='#666')
            ),
            height=400,
            hovermode='x unified'
        )
        
        return trades_fig, tta_fig, summary_children, min_date, max_date, start_date, end_date, last_update_display, ""
        
    except Exception as e:
        logger.error(f"Error updating charts: {e}")
        error_fig = create_empty_figure("⚠️ Error loading data", "Please try again or contact support")
        return error_fig, error_fig, [], None, None, None, None, default_last_update, ""

if __name__ == '__main__':
    app.run(debug=True)