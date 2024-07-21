"""
Test modules in vistock.mpl package.
"""
import vistock.mpl as vsm


modules = (
    vsm.rsi,        # Plot a 3-split (price, volume, RSI) stock chart.
    vsm.bull_draw,  # Plot a bull-run-and-drawdown stock chart.
    vsm.profile.Volume,     # Plot a volume-profile stock chart.
    vsm.profile.Turnover,   # Plot a turnover-profile stock chart.
)

for m in modules:
    #m.plot('TSLA')
    m.plot('TSLA', period="6mo", interval="1d")
    m.plot('台積電', period="6mo", interval="1d")
    #m.plot('台積電', period="3d", interval="5m")
    #m.plot('2330', period="3d", interval="5m")

