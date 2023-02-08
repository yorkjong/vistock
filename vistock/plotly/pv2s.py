#@title _
ticker = "TSLA" #@param {type:"string"}
period = "12mo" #@param ["3mo", "6mo", "12mo", "24mo"]

"""
Show a 2-split (price, volume) stock chart.
* Data from yfinance
* Plot with Plotly (for candlestick, MA, volume, volume MA)
"""
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots


# Download stock data
df = yf.Ticker(ticker).history(period=period)

# Initialize empty plot with a marginal subplot
fig = make_subplots(
    rows=2, cols=1,
    row_heights=[0.7, 0.3],
    #shared_xaxes=True,
    vertical_spacing=0.03,
    figure=go.Figure(layout=go.Layout(height=720))
)
#print(fig)

# Plot the candlestick chart
candlestick = go.Candlestick(
    x=df.index,
    open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    name='OHLC'
)
fig.add_trace(candlestick)

# Add moving averages to the figure
ma_days = (5, 10, 20, 50, 150)
ma_colors = ('orange', 'red', 'green', 'blue', 'brown')
for d, c in zip(ma_days, ma_colors):
    df[f'ma{d}'] = df['Close'].rolling(window=d).mean()
    ma = go.Scatter(x=df.index, y=df[f'ma{d}'], name=f'MA {d}',
                    line=dict(color=f'{c}', width=2), opacity=0.4)
    fig.add_trace(ma)

# Add volume trace to 2nd row
colors = ['green' if o - c >= 0
          else 'red' for o, c in zip(df['Open'], df['Close'])]
volume = go.Bar(x=df.index, y=df['Volume'], name='Volume',
                marker_color=colors, opacity=0.5)
fig.add_trace(volume, row=2, col=1)

# Add moving average volume to 2nd row
df['vma50'] = df['Volume'].rolling(window=50).mean()
vma50 = go.Scatter(x=df.index, y=df['vma50'], name='VMA 50',
                   line=dict(color='purple', width=2))
fig.add_trace(vma50, row=2, col=1)

# Remove non-trading dates
df.index = df.index.strftime('%Y-%m-%d')
dt_all = pd.date_range(start=df.index.values[0], end=df.index.values[-1])
dt_all = [d.strftime("%Y-%m-%d") for d in dt_all]
trade_date = [d for d in df.index.values]
dt_breaks = list(set(dt_all) - set(trade_date))
fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

# Update layout
fig.update_layout(
    title=f'{ticker}: {df.index.values[0]}~{df.index.values[-1]}',
    title_x=0.5, title_y=.9,

    xaxis=dict(anchor='free'),
    yaxis=dict(anchor='x2', side='right', title='Price (USD)'),
    yaxis2=dict(anchor='x', side='right', title='Volume'),

    legend=dict(yanchor='middle', y=0.5, xanchor="left", x=0.01),
    xaxis_rangeslider_visible=False,
)

# Add crosshair cursor
fig.update_yaxes(
    spikemode='across', spikesnap='cursor',
    spikethickness=1, spikedash='solid', spikecolor='grey')
fig.update_xaxes(
    spikemode='across', spikesnap='cursor',
    spikethickness=1, spikedash='solid', spikecolor='grey')
fig.update_layout(hovermode='x')  # 'x', 'y', 'closest', False, 'x unified',
                                  # 'y unified'

# Show the figure
fig.show()

