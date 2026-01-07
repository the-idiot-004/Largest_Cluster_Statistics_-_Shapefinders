import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import os
import re

# --- Set plot style to match the academic paper's aesthetic ---
plt.rcParams['font.family'] = 'serif'
plt.rcParams['mathtext.fontset'] = 'dejavuserif'
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.top'] = True
plt.rcParams['ytick.right'] = True
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 10

# --- File Paths ---
# 1. Entire Box Data CSVs
overdense_eb_csv = '/home/amnkmr/SIP/LCS_data/data-team5/output_CD_overdensity_SURFGEN/CD_OD1_SF_EB.csv'
underdense_eb_csv = '/home/amnkmr/SIP/LCS_data/data-team5/output_CD_overdensity_SURFGEN/CD_UD1_SF_EB.csv'

# 2. Sub-box Data CSVs
num_subboxes = 8
overdense_sf_files_sb = [
    f"/home/amnkmr/SIP/LCS_data/data-team5/output_CD_overdensity_SURFGEN/output1/Shapefinder_stat/small_box/subbox{i}/CD_OD1_SF_SB{i}.csv"
    for i in range(1, num_subboxes + 1)
]
underdense_sf_files_sb = [
    f"/home/amnkmr/SIP/LCS_data/data-team5/output_CD_underdensity_SURFGEN/output1/Shapefinder_stat/small_box/subbox{i}/CD_UD1_SF_SB{i}.csv"
    for i in range(1, num_subboxes + 1)
]

# 3. Control Files for Redshift Mapping
overdense_cs_file = '/home/amnkmr/SIP/LCS_data/data-team5/output_CD_overdensity_SURFGEN/output1/Cluster_stat/entire_box/CD_OD1_CS_EB.csv'
underdense_cs_file = '/home/amnkmr/SIP/LCS_data/data-team5/output_CD_underdensity_SURFGEN/output1/Cluster_stat/entire_box/CD_UD1_CS_EB.csv'

# --- Load Data ---
try:
    print(f"Loading entire box (emission) data from: {overdense_eb_csv}")
    df_emi_eb = pd.read_csv(overdense_eb_csv)
    print(f"Loading entire box (absorption) data from: {underdense_eb_csv}")
    df_abs_eb = pd.read_csv(underdense_eb_csv)
    print("Loading control files for redshift mapping...")
    df_ff_emi_map = pd.read_csv(overdense_cs_file)
    df_ff_abs_map = pd.read_csv(underdense_cs_file)
    for df in [df_emi_eb, df_abs_eb, df_ff_emi_map, df_ff_abs_map]:
        df.columns = df.columns.str.strip()
        if 'redshift' in df.columns:
            df['redshift'] = df['redshift'].round(5)
except FileNotFoundError as e:
    print(f"\n---FATAL ERROR---")
    print(f"Could not find a required CSV file: {e.filename}")
    exit()

# --- Helper Functions ---
def find_snapshot_redshift(df_ff_map, target_ff):
    closest_idx = (df_ff_map['FF'] - target_ff).abs().idxmin()
    return df_ff_map.loc[closest_idx, 'redshift']

def get_binned_statistic(df, bins):
    df = df[df['Volume_phys'] > 0].copy()
    if df.empty or bins is None or len(bins) < 2:
        return pd.DataFrame()
    df['vol_bin'] = pd.cut(df['Volume_phys'], bins=bins, right=False)
    binned_df = df.groupby('vol_bin', observed=True).mean(numeric_only=True)
    binned_df['vol_center'] = [np.sqrt(bin.left * bin.right) if bin.left > 0 else 0 for bin in binned_df.index]
    return binned_df.dropna(subset=['vol_center'])

# --- Plotting Setup ---
# MODIFICATION: Increased figure size for better visibility
fig, axes = plt.subplots(2, 4, figsize=(28, 14))
fig.tight_layout(pad=6.0, h_pad=4.0, w_pad=3.0)
target_ffs = [0.01, 0.05, 0.1, 0.3]
num_bins = 15

# --- Main Analysis Loop ---
for i, ff_target in enumerate(target_ffs):
    print(f"--- Processing FF ≈ {ff_target} ---")
    z_emi = find_snapshot_redshift(df_ff_emi_map, ff_target)
    z_abs = find_snapshot_redshift(df_ff_abs_map, ff_target)

    # --- Process Emission Regions ---
    emi_data_z_eb = df_emi_eb[df_emi_eb['redshift'] == z_emi]
    if not emi_data_z_eb.empty:
        min_vol_emi, max_vol_emi = np.log10(emi_data_z_eb['Volume_phys'].min()), np.log10(emi_data_z_eb['Volume_phys'].max())
        log_bins_emi = np.logspace(min_vol_emi, max_vol_emi, num=num_bins)
        emi_binned_eb = get_binned_statistic(emi_data_z_eb, bins=log_bins_emi)
        sb_results_emi = []
        for f in overdense_sf_files_sb:
            try:
                df_sb = pd.read_csv(f)
                df_sb_z = df_sb[df_sb['redshift'].round(5) == z_emi]
                sb_results_emi.append(get_binned_statistic(df_sb_z, bins=log_bins_emi))
            except FileNotFoundError:
                print(f"Warning: Sub-box file not found, skipping: {f}")
        errors_emi = pd.concat(sb_results_emi).groupby(level=0, observed=True).std() if sb_results_emi else pd.DataFrame()
    else:
        emi_binned_eb, errors_emi = pd.DataFrame(), pd.DataFrame()

    # --- Process Absorption Regions ---
    abs_data_z_eb = df_abs_eb[df_abs_eb['redshift'] == z_abs]
    if not abs_data_z_eb.empty:
        min_vol_abs, max_vol_abs = np.log10(abs_data_z_eb['Volume_phys'].min()), np.log10(abs_data_z_eb['Volume_phys'].max())
        log_bins_abs = np.logspace(min_vol_abs, max_vol_abs, num=num_bins)
        abs_binned_eb = get_binned_statistic(abs_data_z_eb, bins=log_bins_abs)
        sb_results_abs = []
        for f in underdense_sf_files_sb:
            try:
                df_sb = pd.read_csv(f)
                df_sb_z = df_sb[df_sb['redshift'].round(5) == z_abs]
                sb_results_abs.append(get_binned_statistic(df_sb_z, bins=log_bins_abs))
            except FileNotFoundError:
                print(f"Warning: Sub-box file not found, skipping: {f}")
        errors_abs = pd.concat(sb_results_abs).groupby(level=0, observed=True).std() if sb_results_abs else pd.DataFrame()
    else:
        abs_binned_eb, errors_abs = pd.DataFrame(), pd.DataFrame()

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
    ax_top.set_title(f'$FF \\approx {ff_target}$', fontsize=16)
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
plt.savefig('figure10_with_errors.png', dpi=300, bbox_inches='tight')
print("\nPlot saved as 'figure10_with_errors.png'")
plt.show()
