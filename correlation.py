#!/usr/bin/env python

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib import gridspec
import xradar as xd
import wradlib as wrl
import cmweather
import sys

if len(sys.argv) == 2:
    sweep = "sweep_" + sys.argv[1]
else:
    sweep = "sweep_0"

filename = "data/raw/odim_2024/vol_2024-10-11_00-05-00.h5"

ds = xr.open_dataset(filename, group=sweep, engine="odim")
dtree = xd.io.open_odim_datatree(filename)

nsweep = len(dtree.sweep)
fig, ax = plt.subplots()
for i in range(nsweep):
    sweep = f"sweep_{i}"
    data = dtree[sweep]['TH']
    elev = data['elevation'].values[0]
    print(sweep, flush=True)
 
    arr = xr.concat(
        [
            xr.corr(
                data.isel(azimuth=i+1),
                data.isel(azimuth=i)
            )
            for i in range (359)
        ],
        dim='azimuth_neighbor'
    )
    arr.plot(ylim=(0,1), add_legend=True, ax=ax, label=f'elev = {elev}')
ax.legend()
plt.show()
# plt.savefig('results/correlation/corr_azim_dbzh_24', dpi=200)
