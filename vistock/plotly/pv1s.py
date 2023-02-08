#@title _
ticker = "TSLA" #@param {type:"string"}
period = "12mo" #@param ["3mo", "6mo", "12mo", "24mo"]

"""
Show a single-subplot stock chart.
* Data from yfinance
* Plot with Plotly (for candlestick, MA, volume, volume MA)
"""
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go


# Download stock data
ticker = 'TSLA'
df = yf.Ticker(ticker).history(period=period)

# Add the candlestick chart
candlestick = go.Candlestick(
    x=df.index,
    open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    name='OHLC'
)
fig = go.Figure(data=[candlestick])

# Add moving averages to the figure
ma_days = (10, 20, 50, 150)
ma_colors = ('red', 'green', 'blue', 'brown')
for d, c in zip(ma_days, ma_colors):
    df[f'ma{d}'] = df['Close'].rolling(window=d).mean()
    ma = go.Scatter(x=df.index, y=df[f'ma{d}'], name=f'MA {d}',
                    line=dict(color=f'{c}', width=2))
    fig.add_trace(ma)

# Create separate y-axis for volume
volume = go.Bar(x=df.index, y=df['Volume'], name='Volume', yaxis='y2',
                marker_color='orange', opacity=0.3)
fig.add_trace(volume)

# Add the volume moving average line
df['vma50'] = df['Volume'].rolling(window=50).mean()
vma50 = go.Scatter(x=df.index, y=df['vma50'], name='VMA50', yaxis='y2',
                   line=dict(color='purple'))
fig.add_trace(vma50)

# Remove non-trading dates
df.index = df.index.strftime('%Y-%m-%d')
dt_all = pd.date_range(start=df.index.values[0], end=df.index.values[-1])
dt_all = [d.strftime("%Y-%m-%d") for d in dt_all]
trade_date = [d for d in df.index.values]
dt_breaks = list(set(dt_all) - set(trade_date))
fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

# Update layout
fig.update_layout(
    xaxis_rangeslider_visible=False,

    title=f'{ticker}: {df.index.values[0]}~{df.index.values[-1]}',
    title_x=0.5, title_y=.85,

    yaxis=dict(title='Price (USD)', side='right', overlaying='y2'),
    yaxis2=dict(title='Volume', side='left', showgrid=False),

    legend=dict(yanchor='middle', y=0.5, xanchor="left", x=0.01)
)

# Add crosshair cursor
fig.update_yaxes(
    spikemode='across', spikesnap='cursor',
    spikethickness=1, spikedash='solid', spikecolor='grey')
fig.update_xaxes(
    spikemode='across', spikesnap='cursor',
    spikethickness=1, spikedash='solid', spikecolor='grey')
fig.update_layout(hovermode='x')  # 'x', 'y', 'closest', False, 'x unified', 'y unified'

# Show the figure
fig.show()
