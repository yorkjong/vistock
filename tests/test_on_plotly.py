# -*- coding: utf-8 -*-
"""Test modules in vistock.plotly package.
"""
import vistock.plotly as vsp

modules = (vsp.pv1s, vsp.pv2s, vsp.pbv4s, vsp.pbv2s)
#modules = (vsp.pbv2s, )

for m in modules:
    m.plot('TSLA')
