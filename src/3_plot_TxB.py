# scripts/3_plot_TxB.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils import (
    weighted_mean, weighted_std,
    bin_edges_for_vol, ensure_folder
)

def plot_TxB_for_redshifts(z_values):
    """
    For each z in z_values, compute T×B in each volume bin and plot
    all curves together on a single log–log plot.
    """
    plt.figure(figsize=(8, 6))

    for z in z_values:
        # Load the CSV and filter
        fn = "../shapefinders_all_small_box.csv"
        df = pd.read_csv(fn)
        df_z = df[(df['z'] == z) & (df['vol'] > 0)].copy()
        vol = df_z['vol'].values

        # Define bins (8 bins)
        edges = bin_edges_for_vol(vol, n_bins=8)

        vol_mean, vol_std = [], []
        TXB_mean, TXB_std = [], []

        for i in range(len(edges) - 1):
            vmin, vmax = edges[i], edges[i + 1]
            mask = (vol >= vmin) & (vol < vmax)
            if not np.any(mask):
                continue

            bin_data = df_z[mask]
            vol_vals = bin_data['vol'].values
            weights = vol_vals

            vm = weighted_mean(vol_vals, weights)
            vs = weighted_std(vol_vals, weights)
            vol_mean.append(vm)
            vol_std.append(vs)

            TxB_vals = (bin_data['T'].values * bin_data['B'].values)
            TXB_mean.append(weighted_mean(TxB_vals, weights))
            TXB_std.append(weighted_std(TxB_vals, weights))

        vol_mean = np.array(vol_mean)
        vol_std  = np.array(vol_std)
        TXB_mean = np.array(TXB_mean)
        TXB_std  = np.array(TXB_std)

        plt.errorbar(vol_mean, TXB_mean, xerr=vol_std, yerr=TXB_std,
                     fmt='o-', capsize=3, label=f"z={z:.3f}")

    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel(r'Volume in $(0.56\times\mathrm{Mpc})^3$')
    plt.ylabel(r'$T\times B$ (in $(0.56\times\mathrm{Mpc})^2$)')
    plt.title(r'T$_{\!x}$B vs Volume for selected redshifts')
    plt.legend(loc='upper left')
    plt.tight_layout()

    ensure_folder("../plots/TxB")
    plt.savefig("../plots/TxB/TxB_vs_V.png")
    plt.close()
    print("Saved TxB plot to ../plots/TxB/TxB_vs_V.png")

if __name__ == "__main__":
    # Hardcode the five redshift values to plot
    five_z = [10.11, 13.221, 14.294, 11.09, 9.938]
    plot_TxB_for_redshifts(five_z)
