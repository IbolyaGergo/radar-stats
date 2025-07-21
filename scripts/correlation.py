#!/usr/bin/env python

from pathlib import Path
import sys
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import xradar as xd
import wradlib as wrl
import cmweather
import numpy.ma as ma


def main():
    """ Plot correlation between adjacent rays for each elevation.  """
    PROJECT_ROOT = Path(__file__).parent.parent

    FILE_NAME = sys.argv[1]
    FILE_PATH = PROJECT_ROOT / FILE_NAME

    dtree = xd.io.open_odim_datatree(FILE_PATH)

    sweeps = [ int(arg) for arg in sys.argv[2:] ]
    max_sweep_idx = dtree.sweep.size - 1

    fig, ax = plt.subplots()
    for nsweep in sweeps:
        if nsweep > max_sweep_idx:
            print(f"Max sweep index is {max_sweep_idx}")
            exit(1)

        sweep = f'sweep_{nsweep}'

        da_TH = dtree[sweep]['TH']
        noise_level_dB = da_TH.min(dim='azimuth')
        threshold_dB = 5

        data_var = "VRADV"
        data = dtree[sweep][data_var]

        elev = data['elevation'].values[0]
        print(f"Compute correlation for elevation {elev}", flush=True)

        azimuth_count = data['azimuth'].size


        corrarr = np.empty( azimuth_count - 1 )
        num_allnan = 0
        for nazim in range( azimuth_count - 1 ):

            ray_0 = data.isel(azimuth = nazim)
            mask_0 = da_TH.isel(azimuth = nazim) >= noise_level_dB + threshold_dB
            above_noise_0 = ray_0.where(mask_0)

            ray_1 = data.isel(azimuth = nazim+1)
            mask_1 = da_TH.isel(azimuth = nazim+1) >= noise_level_dB + threshold_dB
            above_noise_1 = ray_1.where(mask_1)

            # Dealing with NaNs
            ma_above_noise_0 = ma.masked_invalid(above_noise_0.values)
            ma_above_noise_1 = ma.masked_invalid(above_noise_1.values)

            corrarr[nazim] = ma.corrcoef(
                ma_above_noise_0,
                ma_above_noise_1
            ).filled(np.nan)[0,1]

        ax.plot(corrarr, label=f"elev = {elev}")
    ax.legend()
    ax.set(ylim = (-1, 1))
    ax.set_title(f"threshold = noise + {threshold_dB}dB")

    output_path = PROJECT_ROOT / "results" / "correlation" / (
    FILE_PATH.stem + "_corr" + f"_{data_var}" + f"_thrs_{threshold_dB}" + ".png")

    plt.savefig(output_path, dpi=200)
    print(f"Created {output_path}")

if __name__ == "__main__":
    main()

