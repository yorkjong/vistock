"""
Test modules in vistock.mpl package.
"""
import vistock.mpl as vsm


modules = (
    #vsm.rsi,        # Plot a 3-split (price, volume, RSI) stock chart.
    vsm.profile.Volume, # Plot a price-by-volume stock chart.
)

for m in modules:
    #m.plot('TSLA')
    m.plot('TSLA', period="6mo", interval="1d")
    #m.plot('台積電', period="3d", interval="5m")
    #m.plot('2330', period="3d", interval="5m")

