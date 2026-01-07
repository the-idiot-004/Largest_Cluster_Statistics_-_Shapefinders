# src/analysis.py

import pandas as pd
import numpy as np
from . import config

def find_snapshot_redshift(df_ff_map, target_ff):
    """
    Finds the redshift of the snapshot that has the filling factor closest to the target.
    """
    closest_idx = (df_ff_map['FF'] - target_ff).abs().idxmin()
    return df_ff_map.loc[closest_idx, 'redshift']

def get_binned_statistic(df, bins):
    """
    Calculates the binned statistic for a given dataframe and bins.
    """
    df = df[df['Volume_phys'] > 0].copy()
    if df.empty or bins is None or len(bins) < 2:
        return pd.DataFrame()
    df['vol_bin'] = pd.cut(df['Volume_phys'], bins=bins, right=False)
    binned_df = df.groupby('vol_bin', observed=True).mean(numeric_only=True)
    binned_df['vol_center'] = [np.sqrt(bin.left * bin.right) if bin.left > 0 else 0 for bin in binned_df.index]
    return binned_df.dropna(subset=['vol_center'])

def run_sb_analysis():
    """
    Runs the main analysis from the old SB_anal.py script.
    """
    # --- Load Data ---
    try:
        print(f"Loading entire box (emission) data from: {config.CD_OD1_SF_EB_CSV}")
        df_emi_eb = pd.read_csv(config.CD_OD1_SF_EB_CSV)
        print(f"Loading entire box (absorption) data from: {config.CD_UD1_SF_EB_CSV}")
        df_abs_eb = pd.read_csv(config.CD_UD1_SF_EB_CSV)
        print("Loading control files for redshift mapping...")
        df_ff_emi_map = pd.read_csv(config.CD_OD1_CS_EB_CSV)
        df_ff_abs_map = pd.read_csv(config.CD_UD1_CS_EB_CSV)
        for df in [df_emi_eb, df_abs_eb, df_ff_emi_map, df_ff_abs_map]:
            df.columns = df.columns.str.strip()
            if 'redshift' in df.columns:
                df['redshift'] = df['redshift'].round(5)
    except FileNotFoundError as e:
        print(f"\n---FATAL ERROR---")
        print(f"Could not find a required CSV file: {e.filename}")
        exit()

    results = {}
    # --- Main Analysis Loop ---
    for i, ff_target in enumerate(config.TARGET_FFS):
        print(f"--- Processing FF ≈ {ff_target} ---")
        z_emi = find_snapshot_redshift(df_ff_emi_map, ff_target)
        z_abs = find_snapshot_redshift(df_ff_abs_map, ff_target)

        # --- Process Emission Regions ---
        emi_data_z_eb = df_emi_eb[df_emi_eb['redshift'] == z_emi]
        if not emi_data_z_eb.empty:
            min_vol_emi, max_vol_emi = np.log10(emi_data_z_eb['Volume_phys'].min()), np.log10(emi_data_z_eb['Volume_phys'].max())
            log_bins_emi = np.logspace(min_vol_emi, max_vol_emi, num=config.NUM_BINS)
            emi_binned_eb = get_binned_statistic(emi_data_z_eb, bins=log_bins_emi)
            sb_results_emi = []
            overdense_sf_files_sb = [
                f"{config.OVERDENSE_BASE_DIR}subbox{i}/CD_OD1_SF_SB{i}.csv"
                for i in range(1, 9)
            ]
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
            log_bins_abs = np.logspace(min_vol_abs, max_vol_abs, num=config.NUM_BINS)
            abs_binned_eb = get_binned_statistic(abs_data_z_eb, bins=log_bins_abs)
            sb_results_abs = []
            underdense_sf_files_sb = [
                f"{config.UNDERDENSE_BASE_DIR}subbox{i}/CD_UD1_SF_SB{i}.csv"
                for i in range(1, 9)
            ]
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
        
        results[ff_target] = {
            'emi_binned_eb': emi_binned_eb,
            'errors_emi': errors_emi,
            'abs_binned_eb': abs_binned_eb,
            'errors_abs': errors_abs
        }
    return results

def process_shapefinders_for_redshift(z_value):
    # 1) Load the CSV and filter by redshift
    fn = config.SHAPEFINDERS_ALL_SMALL_BOX_CSV
    df = pd.read_csv(fn)
    df_z = df[(df['z'] == z_value) & (df['vol'] > 0)].copy()
    vol = df_z['vol'].values

    # 2) Define log‐spaced bins in vol (8 bins)
    from .utils import bin_edges_for_vol, weighted_mean, weighted_std, loglog_fit
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
    
    return {
        "z_value": z_value,
        "vol_mean": vol_mean, "vol_std": vol_std,
        "T_mean": T_mean, "T_std": T_std,
        "B_mean": B_mean, "B_std": B_std,
        "L_mean": L_mean, "L_std": L_std,
        "P_mean": P_mean, "P_std": P_std,
        "F_mean": F_mean, "F_std": F_std,
        "G_mean": G_mean, "G_std": G_std,
        "fits": {
            "T": (mT, cT), "B": (mB, cB), "L": (mL, cL),
            "P": (mP, cP), "G": (mG, cG)
        },
        "masks": {"P": maskP, "G": maskG}
    }

def process_txb_for_redshifts(z_values):
    """
    For each z in z_values, compute T×B in each volume bin.
    """
    results = {}
    from .utils import bin_edges_for_vol, weighted_mean, weighted_std
    for z in z_values:
        # Load the CSV and filter
        fn = config.SHAPEFINDERS_ALL_SMALL_BOX_CSV
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

        results[z] = {
            "vol_mean": np.array(vol_mean),
            "vol_std": np.array(vol_std),
            "TXB_mean": np.array(TXB_mean),
            "TXB_std": np.array(TXB_std)
        }
    return results
