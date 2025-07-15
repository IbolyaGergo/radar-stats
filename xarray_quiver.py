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

max_dist = 8000
ds = ds.sel(range=slice(None, max_dist))
ds.attrs["sweep_mode"] = "azimuth_surveillence"
ds = wrl.georef.polar.georeference(ds)

ds = ds.assign(
    u = ds['VRADH'] * np.sin( np.deg2rad( ds['azimuth'] ) ),
    v = ds['VRADH'] * np.cos( np.deg2rad( ds['azimuth'] ) )
    )

ds['VRADH'].plot(x='x', y='y')
ds.plot.quiver(x="x", y="y", u='u', v='v', scale=100, units='width')
plt.show()

