import pandas as pd
import os

def create_control_file(input_sf_csv_path, output_cs_csv_path):
    """
    Generates a control file (redshift vs Filling Factor) from a
    shapefinder statistics file.

    Args:
        input_sf_csv_path (str): Full path to the input shapefinder CSV file.
        output_cs_csv_path (str): Full path where the output control file will be saved.
    """
    print(f"--- Generating Control File ---")
    print(f"Reading input: {input_sf_csv_path}")

    try:
        df_sf = pd.read_csv(input_sf_csv_path)
    except FileNotFoundError:
        print(f"FATAL ERROR: Input file not found at the specified path.")
        print("Please ensure the entire box shapefinder CSV exists before running this script.")
        return

    # Define the total volume of the simulation box in (Mpc/h)^3
    total_simulation_volume = 500.0 ** 3

    # Group data by redshift and sum the volume of all regions for each snapshot
    total_region_volume = df_sf.groupby('redshift')['Volume_phys'].sum()

    # Calculate the Filling Factor (FF)
    filling_factor = total_region_volume / total_simulation_volume

    # Create a new DataFrame with the results
    # The index of the 'filling_factor' Series is the redshift
    df_control = filling_factor.reset_index()
    # Rename the 'Volume_phys' column to 'FF' for clarity
    df_control = df_control.rename(columns={'Volume_phys': 'FF'})

    # Ensure the output directory exists before saving
    output_dir = os.path.dirname(output_cs_csv_path)
    os.makedirs(output_dir, exist_ok=True)

    # Save the new control file
    df_control.to_csv(output_cs_csv_path, index=False)
    print(f"Successfully created control file: {output_cs_csv_path}")
    print("-" * 30)


# --- Main script execution ---

# Define the paths for the input (SF) and output (CS) files

# 1. For Overdense (Emission) Regions
input_overdense_sf = '/home/amnkmr/SIP/LCS_data/data-team5/output_CD_overdensity_SURFGEN/CD_OD1_SF_EB.csv'
output_overdense_cs = '/home/amnkmr/SIP/LCS_data/data-team5/output_CD_overdensity_SURFGEN/output1/Cluster_stat/entire_box/CD_OD1_CS_EB.csv'

# 2. For Underdense (Absorption) Regions
input_underdense_sf = '/home/amnkmr/SIP/LCS_data/data-team5/output_CD_overdensity_SURFGEN/CD_UD1_SF_EB.csv'
output_underdense_cs = '/home/amnkmr/SIP/LCS_data/data-team5/output_CD_underdensity_SURFGEN/output1/Cluster_stat/entire_box/CD_UD1_CS_EB.csv'


# --- Generate the files ---
create_control_file(input_overdense_sf, output_overdense_cs)
create_control_file(input_underdense_sf, output_underdense_cs)

print("\nAll control files have been generated successfully.")
