"""
Test modules in vistock.plotly package.
"""
import vistock.plotly as vsp

modules = (
<<<<<<< HEAD
    #vsp.pv1s,       # Price and volume overlaid stock chart
    #vsp.pv2s,       # Price and volume separated stock chart
    #vsp.bull_draw,  # Bull-run & drawdown stock chart
    vsp.ibd_rs,     # IBD RS stock chart
    #vsp.prf2s.Volume,   # Volume Profile stock chart with 2 subplots
    #vsp.prf2s.Turnover, # Turnover Profile stock chart with 2 subplots
    #vsp.prf4s.Volume,   # Volume Profile stock chart with 2x2 subplots
    #vsp.prf4s.Turnover, # Turnover Profile stock chart with 2x2 subplots
)

for m in modules:
    #m.plot('TSLA', hides_nontrading=False)
=======
    vsp.pv1s,       # Price and volume overlaid stock chart
    vsp.pv2s,       # Price and volume separated stock chart
    vsp.bull_draw,  # Bull-run & drawdown stock chart
    vsp.prf2s.Volume,   # Volume Profile stock chart with 2 subplots
    vsp.prf2s.Turnover, # Turnover Profile stock chart with 2 subplots
    vsp.prf4s.Volume,   # Volume Profile stock chart with 2x2 subplots
    vsp.prf4s.Turnover, # Turnover Profile stock chart with 2x2 subplots
)

for m in modules:
    m.plot('TSLA', hides_nontrading=False)
>>>>>>> main
    #m.plot('TSLA', period='6mo', interval='1d')
    #m.plot('台積電', period='6mo', interval='1d')
    #m.plot('TSLA', period='1mo', interval='1h')
    #m.plot('TSLA', period='1y', interval='1wk')
    #m.plot('TSLA', period='2y', interval='1mo')
    #m.plot('台積電', period='2y', interval='1wk')
    m.plot('TSLA', period='2y', interval='1wk')

