# -*- coding: utf-8 -*-
"""Test modules in vistock.plotly package.
"""
import vistock.plotly as vsp

modules = (
    vsp.pv1s,     # Price and volume overlaid stock chart
    vsp.pv2s,     # Price and volume separated stock chart
    vsp.pbv4s,    # Volume Profile (price-by-volume) stock chart with 4 subplots
    vsp.pbv2s,    # Volume Profile (price-by-volume) stock chart with 2 subplots
)

for m in modules:
    m.plot('TSLA')
    m.plot('TSLA', period='3d', interval='5m')

