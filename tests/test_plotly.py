"""
Test modules in vistock.plotly package.
"""
import vistock.plotly as vsp

modules = (
    #vsp.pv1s,     # Price and volume overlaid stock chart
    #vsp.pv2s,     # Price and volume separated stock chart
    vsp.prf2s,    # Volume Profile (price-by-volume) stock chart with 2 subplots
    vsp.prf4s,    # Volume Profile (price-by-volume) stock chart with 4 subplots
)

for m in modules:
    #m.plot('TSLA', hides_nontrading=False)
    m.plot('TSLA', period='6mo', interval='1d')
    #m.plot('TSLA', period='1mo', interval='1h')
    #m.plot('TSLA', period='1y', interval='1wk')
    #m.plot('TSLA', period='2y', interval='1mo')

