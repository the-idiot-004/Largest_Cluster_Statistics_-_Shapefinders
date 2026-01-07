# scripts/4_extract_slopes.py

import numpy as np
import pandas as pd
from utils import (
    weighted_mean, weighted_std, loglog_fit,
    bin_edges_for_vol, ensure_folder
)

def extract_and_save_slopes(z_values, out_csv):
    """
    For each z in z_values, compute slopes mT, mB, mL, mP, mF, mG, mTxB
    and write them to out_csv. 
    """
    cols = ['z', 'mT', 'mB', 'mL', 'mP', 'mF', 'mG', 'mTxB']
    results = []

    for z in z_values:
        df = pd.read_csv("../shapefinders_all_small_box.csv")
        df_z = df[(df['z'] == z) & (df['vol'] > 0)].copy()
        vol = df_z['vol'].values

        # Binning (8 bins)
        edges = bin_edges_for_vol(vol, n_bins=8)

        vol_mean, vol_std = [], []
        T_mean, T_std = [], []
        B_mean, B_std = [], []
        L_mean, L_std = [], []
        P_mean, P_std = [], []
        F_mean, F_std = [], []
        G_mean, G_std = [], []
        TxB_mean, TxB_std = [], []

        for i in range(len(edges) - 1):
            vmin, vmax = edges[i], edges[i + 1]
            mask = (vol >= vmin) & (vol < vmax)
            if not np.any(mask):
                continue

            bin_data = df_z[mask]
            vol_vals = bin_data['vol'].values
            weights = vol_vals

            vol_mean.append(weighted_mean(vol_vals, weights))

            # T, B, L
            T_vals = bin_data['T'].values
            T_mean.append(weighted_mean(T_vals, weights))
            B_vals = bin_data['B'].values
            B_mean.append(weighted_mean(B_vals, weights))
            L_vals = bin_data['L'].values
            L_mean.append(weighted_mean(L_vals, weights))

            # Planarity, Filamentarity, Genus
            P_vals = bin_data['P'].values
            P_mean.append(weighted_mean(P_vals, weights))
            F_vals = bin_data['F'].values
            F_mean.append(weighted_mean(F_vals, weights))
            G_vals = bin_data['Genus'].values
            G_mean.append(weighted_mean(G_vals, weights))

            # TxB
            TxB_vals = bin_data['T'].values * bin_data['B'].values
            TxB_mean.append(weighted_mean(TxB_vals, weights))

        vol_mean = np.array(vol_mean)
        T_mean   = np.array(T_mean)
        B_mean   = np.array(B_mean)
        L_mean   = np.array(L_mean)
        P_mean   = np.array(P_mean)
        F_mean   = np.array(F_mean)
        G_mean   = np.array(G_mean)
        TxB_mean = np.array(TxB_mean)

        mT, _, _    = loglog_fit(vol_mean, T_mean)
        mB, _, _    = loglog_fit(vol_mean, B_mean)
        mL, _, _    = loglog_fit(vol_mean, L_mean)
        mP, _, _    = loglog_fit(vol_mean, P_mean)
        mF, _, _    = loglog_fit(vol_mean, F_mean)
        mG, _, _    = loglog_fit(vol_mean, G_mean)
        mTxB, _, _  = loglog_fit(vol_mean, TxB_mean)

        results.append({
            'z': z,
            'mT': mT,
            'mB': mB,
            'mL': mL,
            'mP': mP,
            'mF': mF,
            'mG': mG,
            'mTxB': mTxB
        })

        print(f"Slopes at z={z:.3f}: mT={mT:.3f}, mB={mB:.3f}, mL={mL:.3f}, "
              f"mP={mP:.3f}, mF={mF:.3f}, mG={mG:.3f}, mTxB={mTxB:.3f}")

    ensure_folder("../output")
    df_out = pd.DataFrame(results, columns=cols)
    df_out.to_csv(out_csv, index=False)
    print(f"Wrote all slopes to {out_csv}")

if __name__ == "__main__":
    # Read common redshifts
    common_file = "../output/common_redshifts.txt"
    with open(common_file, 'r') as f:
        lines = f.readlines()
    z_list = [float(l.strip()) for l in lines if l.strip()]

    out_csv = "../output/slopes.csv"
    extract_and_save_slopes(z_list, out_csv)
