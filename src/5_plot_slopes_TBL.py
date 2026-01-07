# scripts/5_plot_slopes_TBL.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils import ensure_folder

def weighted_avg_and_std(values, weights):
    """Return the weighted average and standard deviation."""
    average = np.average(values, weights=weights)
    variance = np.average((values - average)**2, weights=weights)
    return average, np.sqrt(variance)

if __name__ == "__main__":
    df = pd.read_csv("../output/slopes.csv")

    # Compute integer redshift bins
    df['z_int'] = df['z'].astype(int)

    # Define 8 bins from min(z_int) to max(z_int)
    zmin = df['z_int'].min()
    zmax = df['z_int'].max()
    n_bins = 8
    bins = np.linspace(zmin, zmax, n_bins + 1)  # Use float to ensure unique edges
    
    # Create bins and calculate centers
    df['z_bin'] = pd.cut(df['z_int'], bins=bins, include_lowest=True)
    
    # Prepare containers
    z_centers = []
    mT_vals, mT_err = [], []
    mB_vals, mB_err = [], []
    mTxB_vals, mTxB_err = [], []
    mL_vals, mL_err = [], []

    for bin_interval, bin_df in df.groupby('z_bin'):
        if bin_df.empty:
            continue
        weights = np.ones(len(bin_df))
        
        # Calculate bin center
        z_center = bin_interval.mid
        z_centers.append(z_center)

        for col, store_mean, store_std in [
            ('mT', mT_vals, mT_err),
            ('mB', mB_vals, mB_err),
            ('mTxB', mTxB_vals, mTxB_err),
            ('mL', mL_vals, mL_err),
        ]:
            mean, std = weighted_avg_and_std(bin_df[col].values, weights)
            store_mean.append(mean)
            store_std.append(std)

    # Convert to arrays
    z_centers = np.array(z_centers)
    mT_vals, mT_err = np.array(mT_vals), np.array(mT_err)
    mB_vals, mB_err = np.array(mB_vals), np.array(mB_err)
    mTxB_vals, mTxB_err = np.array(mTxB_vals), np.array(mTxB_err)
    mL_vals, mL_err = np.array(mL_vals), np.array(mL_err)

    # Plotting
    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax2 = ax1.twinx()

    # Left y-axis: mT, mB, mTxB
    ax1.errorbar(z_centers, mT_vals, yerr=mT_err, fmt='o-', label='$m_T$')
    ax1.errorbar(z_centers, mB_vals, yerr=mB_err, fmt='s-', label='$m_B$')
    ax1.errorbar(z_centers, mTxB_vals, yerr=mTxB_err, fmt='d:', 
                label=r'$m_{T\times B} = m_B \times m_T$')

    # Right y-axis: mL
    ax2.errorbar(z_centers, mL_vals, yerr=mL_err, fmt='^--', color='tab:purple', 
                 label='$m_L$')

    ax1.set_xlabel('Redshift Bin Center')
    ax1.set_ylabel(r'Slopes: $m_T$, $m_B$, $m_{T\times B}$')
    ax2.set_ylabel(r'Slope: $m_L$', color='tab:purple')
    ax2.tick_params(axis='y', labelcolor='tab:purple')

    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='best')

    plt.title('Slope vs Redshift (Binned, with Std Dev)')
    plt.tight_layout()

    ensure_folder("../plots/slopes/TBL")
    plt.savefig("../plots/slopes/TBL/slopes_TBL.png")
    plt.close()
    print("Saved T,B,L,TxB slopes vs redshift to ../plots/slopes/TBL/slopes_TBL.png")
