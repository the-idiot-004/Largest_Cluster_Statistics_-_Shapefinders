# scripts/6_plot_slopes_PG.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils import ensure_folder

if __name__ == "__main__":
    df = pd.read_csv("../output/slopes.csv")

    # Group by integer redshift
    df['z_int'] = df['z'].astype(int)
    grouped = df.groupby('z_int').mean().reset_index()

    z_int = grouped['z_int'].values
    mP    = grouped['mP'].values
    mG    = grouped['mG'].values

    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax2 = ax1.twinx()

    ax1.plot(z_int, mP, 'o-', color='tab:red', label='mP')
    ax2.plot(z_int, mG, '^--', color='tab:blue', label='mG')

    ax1.set_xlabel('Integer Redshift')
    ax1.set_ylabel(r'Slope $m_P$ (Planarity)')
    ax2.set_ylabel(r'Slope $m_G$ (Genus)')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='best')

    plt.title('Slopes mP and mG vs Redshift')
    plt.tight_layout()

    ensure_folder("../plots/slopes/PG")
    fig.savefig("../plots/slopes/PG/slopes_PG.png")
    plt.close(fig)
    print("Saved Planarity/Genus slopes vs redshift to ../plots/slopes/PG/slopes_PG.png")
