# scripts/2_plot_shapefinders.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils import (
    weighted_mean, weighted_std, loglog_fit,
    bin_edges_for_vol, ensure_folder
)

def process_and_plot(z_value):
    # 1) Load the CSV and filter by redshift
    fn = "../shapefinders_all_small_box.csv"
    df = pd.read_csv(fn)
    df_z = df[(df['z'] == z_value) & (df['vol'] > 0)].copy()
    vol = df_z['vol'].values

    # 2) Define log‐spaced bins in vol (8 bins)
    edges = bin_edges_for_vol(vol, n_bins=8)

    # 3) Prepare containers for weighted means & stds
    vol_mean, vol_std = [], []
    T_mean, T_std = [], []
    B_mean, B_std = [], []
    L_mean, L_std = [], []
    P_mean, P_std = [], []
    F_mean, F_std = [], []
    G_mean, G_std = [], []

    # 4) Loop over bins
    for i in range(len(edges) - 1):
        vmin, vmax = edges[i], edges[i + 1]
        mask = (vol >= vmin) & (vol < vmax)
        if not np.any(mask):
            continue

        bin_data = df_z[mask]
        vol_vals = bin_data['vol'].values
        weights = vol_vals  # weight by volume

        # Volume
        vm = weighted_mean(vol_vals, weights)
        vs = weighted_std(vol_vals, weights)
        vol_mean.append(vm)
        vol_std.append(vs)

        # T, B, L
        for arr_list, colname in zip(
            [(T_mean, T_std), (B_mean, B_std), (L_mean, L_std)],
            ['T', 'B', 'L']
        ):
            vals = bin_data[colname].values
            arr_list[0].append(weighted_mean(vals, weights))
            arr_list[1].append(weighted_std(vals, weights))

        # Planarity P, Filamentarity F, Genus G
        for arr_list, colname in zip(
            [(P_mean, P_std), (F_mean, F_std), (G_mean, G_std)],
            ['P', 'F', 'Genus']
        ):
            vals = bin_data[colname].values
            arr_list[0].append(weighted_mean(vals, weights))
            arr_list[1].append(weighted_std(vals, weights))

    # 5) Convert to numpy arrays
    vol_mean = np.array(vol_mean)
    vol_std  = np.array(vol_std)
    T_mean   = np.array(T_mean);   T_std   = np.array(T_std)
    B_mean   = np.array(B_mean);   B_std   = np.array(B_std)
    L_mean   = np.array(L_mean);   L_std   = np.array(L_std)
    P_mean   = np.array(P_mean);   P_std   = np.array(P_std)
    F_mean   = np.array(F_mean);   F_std   = np.array(F_std)
    G_mean   = np.array(G_mean);   G_std   = np.array(G_std)

    # 6) Compute log–log fits for T, B, L
    mT, cT, _ = loglog_fit(vol_mean, T_mean)
    mB, cB, _ = loglog_fit(vol_mean, B_mean)
    mL, cL, _ = loglog_fit(vol_mean, L_mean)

    # 7) Compute log–log fits for P, G
    mP, cP, maskP = loglog_fit(vol_mean, P_mean)
    mG, cG, maskG = loglog_fit(vol_mean, G_mean)

    # 8) Prepare finer volume vector for fit curves
    vol_fit = np.logspace(np.log10(vol_mean.min()), np.log10(vol_mean.max()), 200)
    T_fit = 10**(mT * np.log10(vol_fit) + cT)
    B_fit = 10**(mB * np.log10(vol_fit) + cB)
    L_fit = 10**(mL * np.log10(vol_fit) + cL)
    P_fit = 10**(mP * np.log10(vol_fit) + cP)
    G_fit = 10**(mG * np.log10(vol_fit) + cG)

    # 9) Plot 1: T, B, L vs Volume (two y‐axes)
    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax2 = ax1.twinx()

    ax1.errorbar(vol_mean, T_mean, xerr=vol_std, yerr=T_std,
                 fmt='o', color='red', capsize=3, label=r'Thickness $T$')
    ax1.plot(vol_fit, T_fit, linestyle=':', color='red')

    ax1.errorbar(vol_mean, B_mean, xerr=vol_std, yerr=B_std,
                 fmt='s', color='blue', capsize=3, label=r'Breadth $B$')
    ax1.plot(vol_fit, B_fit, linestyle=':', color='blue')

    ax2.errorbar(vol_mean, L_mean, xerr=vol_std, yerr=L_std,
                 fmt='^', color='teal', capsize=3, label=r'Length $L$')
    ax2.plot(vol_fit, L_fit, linestyle=':', color='teal')

    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax2.set_yscale('log')
    ax1.set_xlabel(r'Volume in $(0.56\times\mathrm{Mpc})^3$')
    ax1.set_ylabel(r'$T,B$ in $(0.56\times\mathrm{Mpc})$')
    ax2.set_ylabel(r'$L$ in $(0.56\times\mathrm{Mpc})$')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    plt.title(f'Bubble Statistics: $T,B,L$ vs Volume (z={z_value})')
    plt.tight_layout()
    ensure_folder("../plots/shapefinders")
    fig.savefig(f"../plots/shapefinders/shapefinders_z_{z_value:.3f}.png")
    plt.close(fig)

    # 10) Plot 2: P, F, Genus vs Volume
    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax2 = ax1.twinx()

    ax1.errorbar(vol_mean[maskP], P_mean[maskP],
                 xerr=vol_std[maskP], yerr=P_std[maskP],
                 fmt='o', color='red', capsize=3, label=r'Planarity $P$')
    ax1.plot(vol_fit, P_fit, linestyle='--', color='red')

    ax1.errorbar(vol_mean, F_mean, xerr=vol_std, yerr=F_std,
                 fmt='s', color='blue', capsize=3, label=r'Filamentarity $F$')
    # Join F points with a dashed line
    sorted_idx = np.argsort(vol_mean)
    vol_sorted = vol_mean[sorted_idx]
    F_sorted = F_mean[sorted_idx]
    ax1.plot(vol_sorted, F_sorted, linestyle='-', color='blue', alpha=0.7)

    ax2.errorbar(vol_mean[maskG], G_mean[maskG],
                 xerr=vol_std[maskG], yerr=G_std[maskG],
                 fmt='^', color='teal', capsize=3, label=r'Genus')
    ax2.plot(vol_fit, G_fit, linestyle=':', color='teal', alpha=0.9)

    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax2.set_yscale('log')
    ax1.set_xlabel(r'Volume in $(0.56\times\mathrm{Mpc})^3$')
    ax1.set_ylabel('Planarity & Filamentarity')
    ax2.set_ylabel('Genus')

    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.title(f'Planarity, Filamentarity & Genus vs Volume (z={z_value})')
    plt.tight_layout()
    ensure_folder("../plots/shapefinders")
    fig.savefig(f"../plots/shapefinders/PFG_z_{z_value:.3f}.png")
    plt.close(fig)

    # 11) Print slopes
    print(f"[z={z_value}] Slopes:")
    print(f"  mT  = {mT:.3f}")
    print(f"  mB  = {mB:.3f}")
    print(f"  mL  = {mL:.3f}")
    print(f"  mP  = {mP:.3f}")
    print(f"  mG  = {mG:.3f}")
    print("")

if __name__ == "__main__":
    # Read common redshifts
    common_file = "../output/common_redshifts.txt"
    with open(common_file, 'r') as f:
        lines = f.readlines()
    z_list = [float(l.strip()) for l in lines if l.strip()]

    for zval in z_list:
        print(f"Processing z = {zval} ...")
        process_and_plot(zval)
    print("Done plotting shapefinders for all z.")
