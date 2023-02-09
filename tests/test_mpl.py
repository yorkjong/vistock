# -*- coding: utf-8 -*-
"""Test modules in vistock.mpl package.
"""
import vistock.mpl as vsm

modules = (vsm.rsi, vsm.pbv)

for m in modules:
    m.plot('TSLA')

