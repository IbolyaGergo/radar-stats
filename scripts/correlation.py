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

filename = "../data/raw/odim_2023/vol_2023-03-12_05-55-56.h5"

dtree = xd.io.open_odim_datatree(filename)

sweep_nums = [ int(arg) for arg in sys.argv[1:] ]

fig, ax = plt.subplots()
for ns in sweep_nums:
    sweep = f'sweep_{ns}'
    data = dtree[sweep]['TH']
    elev = data['elevation'].values[0]

    print(f"Compute correlation for elevation {elev}", flush=True)

    nazim = data['azimuth'].size
    corrarr = np.empty( nazim - 1 )
    threshold = data.min(dim='azimuth') + 20
    for na in range( nazim - 1 ):
        ray_0 = data.isel(azimuth = na)
        ray_1 = data.isel(azimuth = na+1)

        corrarr[na] = xr.corr(
            ray_0.where(ray_0 >= threshold),
            ray_1.where(ray_1 >= threshold) 
        ) 
    ax.plot(corrarr, label=f"elev = {elev}")
ax.legend()
ax.set(ylim = (-1, 1))
plt.show()
# plt.savefig('results/correlation/corr_azim_dbzh_24', dpi=200)
