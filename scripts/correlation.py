#!/usr/bin/env python

"""
Plot correlation between adjacent rays for each elevation.
"""

from pathlib import Path
import sys
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib import gridspec
import xradar as xd
import wradlib as wrl
import cmweather

PROJECT_ROOT = Path(__file__).parent.parent

filename =  "data/raw/odim_2023/vol_2023-03-12_05-00-56.h5"
filepath = PROJECT_ROOT / filename

dtree = xd.io.open_odim_datatree(filepath)

sweep_count = [ int(arg) for arg in sys.argv[1:] ]

fig, ax = plt.subplots()
for nsweep in sweep_count:
    sweep = f'sweep_{nsweep}'

    data = dtree[sweep]['TH']

    elev = data['elevation'].values[0]
    print(f"Compute correlation for elevation {elev}", flush=True)

    azimuth_count = data['azimuth'].size
    noise_level_dB = data.min(dim='azimuth')
    threshold_dB = noise_level_dB + 0

    corrarr = np.empty( azimuth_count - 1 )
    num_allnan = 0
    for nazim in range( azimuth_count - 1 ):
        ray_0 = data.isel(azimuth = nazim)
        ray_1 = data.isel(azimuth = nazim+1)

        above_noise_0 = ray_0.where(ray_0 >= threshold_dB)
        above_noise_1 = ray_1.where(ray_1 >= threshold_dB)

        # Check for sufficient number of valid data to compute correlation
        # Using ufuncs.isfinite insted of notnull:
        # notnull only deals with nan
        # ufuncs.isfinite deals also with +-inf (e.g. div by zero)
        valid = xr.ufuncs.isfinite(above_noise_0) & xr.ufuncs.isfinite(above_noise_1)
        n_valid = valid.sum()

        if n_valid >= 2: # required for xr.corr
            corrarr[nazim] = xr.corr( above_noise_0, above_noise_1 ) 
        else:
            corrarr[nazim] = np.nan

    ax.plot(corrarr, label=f"elev = {elev}")
ax.legend()
ax.set(ylim = (-1, 1))

output_path = PROJECT_ROOT / "results" / "correlation" / (filepath.stem + "_corr_" + ".png")
plt.savefig(output_path, dpi=200)
