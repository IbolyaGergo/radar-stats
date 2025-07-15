#!/usr/bin/env python

"""
Plot correlation between adjacent rays for each elevation.
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib import gridspec
import xradar as xd
import wradlib as wrl
import cmweather
import sys

filename = "data/raw/odim_2024/vol_2024-10-11_00-05-00.h5"

dtree = xd.io.open_odim_datatree(filename)

nsweep = len(dtree.sweep)


fig, ax = plt.subplots()
for ns in range(nsweep):
    sweep = f'sweep_{ns}'
    data = dtree[sweep]['TH']
    elev = data['elevation'].values[0]

    print(f"Compute correlation for elevation {elev}", flush=True)

    nazim = data['azimuth'].size
    corrarr = np.empty( nazim - 1 )
    for na in range( nazim - 1 ):
        corrarr[na] = xr.corr( data.isel(azimuth=na+1),data.isel(azimuth=na) ) 
    ax.plot(corrarr, label=f"elev = {elev}")
ax.legend()
ax.set(ylim = (0, 1))
plt.show()
# plt.savefig('results/correlation/corr_azim_dbzh_24', dpi=200)
