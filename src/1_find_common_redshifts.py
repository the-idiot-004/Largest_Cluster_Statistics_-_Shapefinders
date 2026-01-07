# scripts/1_select_redshifts.py

import os
import sys
import pandas as pd
from utils import ensure_folder

if __name__ == "__main__":
    # Path to the small‐box CSV (relative from scripts/)
    small_box_path = "../shapefinders_all_small_box.csv"

    # 1) Check that the file exists
    if not os.path.exists(small_box_path):
        print(f"ERROR: Could not find '{small_box_path}'. Please ensure Shapefinder_small_box.csv lives in Results/.")
        sys.exit(1)

    # 2) Read the small‐box file and extract unique redshifts
    try:
        df_small = pd.read_csv(small_box_path, usecols=['z'])
    except Exception as e:
        print("ERROR: Could not read column 'z' from Shapefinder_small_box.csv.")
        print("Details:", e)
        sys.exit(1)

    # 3) Filter redshift values between 8.000 and 15.132 (inclusive)
    z_values = df_small['z'].unique()
    # Keep only those in the desired range
    selected = [z for z in z_values if 8.0 <= z <= 15.132]

    if len(selected) == 0:
        print("WARNING: No redshift values found in [8.0, 15.132]. Exiting.")
        sys.exit(0)

    # 4) Sort them
    selected_sorted = sorted(selected)

    # 5) Ensure output directory exists
    ensure_folder("../output")

    # 6) Write to output/common_redshifts.txt
    out_path = "../output/common_redshifts.txt"
    with open(out_path, 'w') as f:
        for z in selected_sorted:
            f.write(f"{z}\n")

    # 7) Print the chosen redshifts
    print("Selected redshifts (8.0 ≤ z ≤ 15.132):")
    for z in selected_sorted:
        print(z)
