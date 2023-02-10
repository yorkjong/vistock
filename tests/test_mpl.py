"""Test modules in vistock.mpl package.
"""
import vistock.mpl as vsm


modules = (
    vsm.rsi,    # Plot a 3-split (price, volume, RSI) stock chart.
    vsm.pbv,    # Plot a price-by-volume stock chart.
)

for m in modules:
    m.plot('TSLA')
    m.plot('TSLA', period="3d", interval="5m")

