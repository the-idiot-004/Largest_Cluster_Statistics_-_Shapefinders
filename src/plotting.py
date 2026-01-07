# src/plotting.py

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import numpy as np
from . import config
from .utils import ensure_folder

def plot_sb_analysis(analysis_results):
    """
    Plots the results from the SB analysis.
    """
    plt.rcParams.update(config.plt_style)

    fig, axes = plt.subplots(2, 4, figsize=(28, 14))
    fig.tight_layout(pad=6.0, h_pad=4.0, w_pad=3.0)

    for i, (ff_target, data) in enumerate(analysis_results.items()):
        emi_binned_eb = data['emi_binned_eb']
        errors_emi = data['errors_emi']
        abs_binned_eb = data['abs_binned_eb']
        errors_abs = data['errors_abs']
        
        # --- Plotting Panels ---
        ax_top = axes[0, i]
        ax_bottom = axes[1, i]

        if not emi_binned_eb.empty and not errors_emi.empty:
            common_index_emi = emi_binned_eb.index.intersection(errors_emi.index)
            emi_binned_eb_common = emi_binned_eb.loc[common_index_emi]
            errors_emi_common = errors_emi.loc[common_index_emi]
        else:
            emi_binned_eb_common, errors_emi_common = pd.DataFrame(), pd.DataFrame()

        if not abs_binned_eb.empty and not errors_abs.empty:
            common_index_abs = abs_binned_eb.index.intersection(errors_abs.index)
            abs_binned_eb_common = abs_binned_eb.loc[common_index_abs]
            errors_abs_common = errors_abs.loc[common_index_abs]
        else:
            abs_binned_eb_common, errors_abs_common = pd.DataFrame(), pd.DataFrame()
            
        # MODIFICATION: Increased elinewidth and capsize for better visibility
        plot_params = {'elinewidth': 0.8, 'capsize': 2.0, 'alpha': 0.6}

        # Plot Top Panel with Error Bars
        for shape, color, z_order in [('T_phys', 'black', 10), ('B_phys', 'red', 20), ('L_phys', 'blue', 30)]:
            if not emi_binned_eb_common.empty:
                ax_top.errorbar(emi_binned_eb_common['vol_center'], emi_binned_eb_common[shape], yerr=errors_emi_common.get(shape), xerr=errors_emi_common.get('vol_center'),
                                  linestyle='--', color=color, ecolor=color, zorder=z_order, **plot_params)
            if not abs_binned_eb_common.empty:
                ax_top.errorbar(abs_binned_eb_common['vol_center'], abs_binned_eb_common[shape], yerr=errors_abs_common.get(shape), xerr=errors_abs_common.get('vol_center'),
                                  linestyle='-', color=color, ecolor=color, zorder=z_order, **plot_params)

        # Plot Bottom Panel with Error Bars
        for shape, color, ls, z_order in [('P', 'black', ':', 10), ('F', 'red', ':', 20), ('Genus', 'blue', '--', 30)]:
            if not emi_binned_eb_common.empty:
                y_val = abs(emi_binned_eb_common[shape]) if shape == 'Genus' else emi_binned_eb_common[shape]
                ax_bottom.errorbar(emi_binned_eb_common['vol_center'], y_val, yerr=errors_emi_common.get(shape), xerr=errors_emi_common.get('vol_center'),
                                     linestyle=ls, color=color, ecolor=color, zorder=z_order, **plot_params)
        for shape, color, ls, z_order in [('P', 'black', '-', 10), ('F', 'red', '-', 20), ('Genus', 'blue', '-', 30)]:
            if not abs_binned_eb_common.empty:
                y_val = abs(abs_binned_eb_common[shape]) if shape == 'Genus' else abs_binned_eb_common[shape]
                ax_bottom.errorbar(abs_binned_eb_common['vol_center'], y_val, yerr=errors_abs_common.get(shape), xerr=errors_abs_common.get('vol_center'),
                                     linestyle=ls, color=color, ecolor=color, zorder=z_order, **plot_params)

        # --- Formatting ---
        ax_top.set_title(f'FF ~ {ff_target}', fontsize=16)
        ax_top.set_yscale('log')
        ax_top.set_xscale('log')
        ax_top.set_ylim(1e0, 1e2)
        ax_top.set_xlim(1e2, 1e4)
        ax_top.set_ylabel(r'Shapefinders $(h^{-1}\mathrm{Mpc})$', fontsize=14)

        ax_bottom.set_xlabel(r'$V\ (h^{-1}\mathrm{Mpc})^{3}$', fontsize=14)
        ax_bottom.set_yscale('log')
        ax_bottom.set_xscale('log')
        ax_bottom.set_xlim(1e2, 1e4)
        if i == 0:
            ax_bottom.set_ylim(1e-2, 1e3)
        else:
            ax_bottom.set_ylim(1e-2, 1e3)
        ax_bottom.set_ylabel(r'P, F, G', fontsize=14)

    # --- Final Touches: Legends ---
    axes[0, 0].legend(handles=[Line2D([0], [0], color='black', lw=1.5, ls='--', label=r'T-emi'), Line2D([0], [0], color='red', lw=1.5, ls='--', label=r'B-emi'), Line2D([0], [0], color='blue', lw=1.5, ls='--', label=r'L-emi'),
                                 Line2D([0], [0], color='black', lw=1.5, ls='-', label=r'T-abs'), Line2D([0], [0], color='red', lw=1.5, ls='-', label=r'B-abs'), Line2D([0], [0], color='blue', lw=1.5, ls='-', label=r'L-abs')],
                      loc='lower right', ncol=1, frameon=False)
    axes[1, 0].legend(handles=[Line2D([0], [0], color='black', lw=1.5, ls=':', label=r'P-emi'), Line2D([0], [0], color='red', lw=1.5, ls=':', label=r'F-emi'), Line2D([0], [0], color='blue', lw=1.5, ls='--', label=r'G-emi'),
                                 Line2D([0], [0], color='black', lw=1.5, ls='-', label=r'P-abs'), Line2D([0], [0], color='red', lw=1.5, ls='-', label=r'F-abs'), Line2D([0], [0], color='blue', lw=1.5, ls='-', label=r'G-abs')],
                      loc='lower right', ncol=1, frameon=False)

    # --- Save and Show the Final Figure ---
    plt.savefig(f'{config.PLOTS_DIR}/figure10_with_errors.png', dpi=300, bbox_inches='tight')
    print(f"\nPlot saved as '{config.PLOTS_DIR}/figure10_with_errors.png'")
    plt.show()

def plot_shapefinders_for_redshift(data):
    
    from .utils import ensure_folder
    
    z_value = data['z_value']
    vol_mean = data['vol_mean']

    if vol_mean.size == 0:
        print(f"Warning: No data to plot for shapefinders at z={z_value}. Skipping plot generation.")
        return

    vol_std = data['vol_std']
    T_mean = data['T_mean']
    T_std = data['T_std']
    B_mean = data['B_mean']
    B_std = data['B_std']
    L_mean = data['L_mean']
    L_std = data['L_std']
    P_mean = data['P_mean']
    P_std = data['P_std']
    F_mean = data['F_mean']
    F_std = data['F_std']
    G_mean = data['G_mean']
    G_std = data['G_std']
    fits = data['fits']
    masks = data['masks']

    # 8) Prepare finer volume vector for fit curves
    vol_fit = np.logspace(np.log10(vol_mean.min()), np.log10(vol_mean.max()), 200)
    T_fit = 10**(fits['T'][0] * np.log10(vol_fit) + fits['T'][1])
    B_fit = 10**(fits['B'][0] * np.log10(vol_fit) + fits['B'][1])
    L_fit = 10**(fits['L'][0] * np.log10(vol_fit) + fits['L'][1])
    P_fit = 10**(fits['P'][0] * np.log10(vol_fit) + fits['P'][1])
    G_fit = 10**(fits['G'][0] * np.log10(vol_fit) + fits['G'][1])

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
    ensure_folder(f"{config.PLOTS_DIR}/shapefinders")
    fig.savefig(f"{config.PLOTS_DIR}/shapefinders/shapefinders_z_{z_value:.3f}.png")
    plt.close(fig)

    # 10) Plot 2: P, F, Genus vs Volume
    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax2 = ax1.twinx()

    ax1.errorbar(vol_mean[masks['P']], P_mean[masks['P']],
                 xerr=vol_std[masks['P']], yerr=P_std[masks['P']],
                 fmt='o', color='red', capsize=3, label=r'Planarity $P$')
    ax1.plot(vol_fit, P_fit, linestyle='--', color='red')

    ax1.errorbar(vol_mean, F_mean, xerr=vol_std, yerr=F_std,
                 fmt='s', color='blue', capsize=3, label=r'Filamentarity $F$')
    # Join F points with a dashed line
    sorted_idx = np.argsort(vol_mean)
    vol_sorted = vol_mean[sorted_idx]
    F_sorted = F_mean[sorted_idx]
    ax1.plot(vol_sorted, F_sorted, linestyle='-', color='blue', alpha=0.7)

    ax2.errorbar(vol_mean[masks['G']], G_mean[masks['G']],
                 xerr=vol_std[masks['G']], yerr=G_std[masks['G']],
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
    ensure_folder(f"{config.PLOTS_DIR}/shapefinders")
    fig.savefig(f"{config.PLOTS_DIR}/shapefinders/PFG_z_{z_value:.3f}.png")
    plt.close(fig)

    # 11) Print slopes
    print(f"[z={z_value}] Slopes:")
    print(f"  mT  = {fits['T'][0]:.3f}")
    print(f"  mB  = {fits['B'][0]:.3f}")
    print(f"  mL  = {fits['L'][0]:.3f}")
    print(f"  mP  = {fits['P'][0]:.3f}")
    print(f"  mG  = {fits['G'][0]:.3f}")
    print("")

def plot_txb_for_redshifts(results):
    """
    For each z in z_values, compute T×B in each volume bin and plot
    all curves together on a single log–log plot.
    """
    plt.figure(figsize=(8, 6))

    for z, data in results.items():
        plt.errorbar(data['vol_mean'], data['TXB_mean'], xerr=data['vol_std'], yerr=data['TXB_std'],
                     fmt='o-', capsize=3, label=f"z={z:.3f}")

    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel(r'Volume in $(0.56\times\mathrm{Mpc})^3$')
    plt.ylabel(r'$T\times B$ (in $(0.56\times\mathrm{Mpc})^2$)')
    plt.title(r'T$_{\!x}$B vs Volume for selected redshifts')
    plt.legend(loc='upper left')
    plt.tight_layout()

    ensure_folder(f"{config.PLOTS_DIR}/TxB")
    plt.savefig(f"{config.PLOTS_DIR}/TxB/TxB_vs_V.png")
    plt.close()
    print(f"Saved TxB plot to {config.PLOTS_DIR}/TxB/TxB_vs_V.png")
