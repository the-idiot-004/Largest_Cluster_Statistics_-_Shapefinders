# src/data_processing.py

import os
import re
import pandas as pd
from . import config

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

    # Group data by redshift and sum the volume of all regions for each snapshot
    total_region_volume = df_sf.groupby('redshift')['Volume_phys'].sum()

    # Calculate the Filling Factor (FF)
    filling_factor = total_region_volume / config.TOTAL_SIMULATION_VOLUME

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


def process_subboxes(base_directory, region_prefix, num_subboxes=8):
    """
    Processes raw shapefinder data from sub-box directories and saves to CSV
    inside each respective sub-box directory.

    Args:
        base_directory (str): The path to the 'small_box' directory.
        region_prefix (str): The prefix for the output file, e.g., 'CD_OD1' or 'CD_UD1'.
        num_subboxes (int): The number of sub-box directories to process.
    """
    print(f"\n--- Starting processing for {region_prefix} ---")
    print(f"Base directory: {base_directory}")

    if not os.path.isdir(base_directory):
        print(f"Error: Base directory not found at '{base_directory}'")
        return

    # A regular expression to find files containing redshift information
    redshift_pattern = re.compile(r'z(\d+\.\d+)_')

    # Loop through each sub-box (from 1 to 8)
    for i in range(1, num_subboxes + 1):
        subbox_dir = os.path.join(base_directory, f'subbox{i}')
        print(f"\nProcessing subbox {i} in: {subbox_dir}")

        if not os.path.isdir(subbox_dir):
            print(f"  - Warning: Directory not found. Skipping subbox {i}.")
            continue

        # Initialize a list to store data for the current sub-box
        subbox_data = []

        # Loop through all files in the current sub-box directory
        for filename in os.listdir(subbox_dir):
            match = redshift_pattern.search(filename)
            if match:
                try:
                    redshift = float(match.group(1))
                    filepath = os.path.join(subbox_dir, filename)

                    with open(filepath, 'r') as file:
                        for line in file:
                            line = line.strip()
                            if not line or line.startswith('#'):
                                continue

                            values = line.split()
                            if len(values) < 11:
                                continue

                            # Read raw shapefinders and sort them to find L, B, T
                            raw_sf1 = abs(float(values[8]))
                            raw_sf2 = abs(float(values[9]))
                            raw_sf3 = abs(float(values[10]))
                            
                            shapefinders = sorted([raw_sf1, raw_sf2, raw_sf3])
                            T_grid, B_grid, L_grid = shapefinders[0], shapefinders[1], shapefinders[2]
                            
                            # Recalculate Planarity (P) and Filamentarity (F)
                            sum_bt = B_grid + T_grid
                            sum_lb = L_grid + B_grid
                            P_val = 0 if sum_bt == 0 else (B_grid - T_grid) / sum_bt
                            F_val = 0 if sum_lb == 0 else (L_grid - B_grid) / sum_lb

                            # Append the processed data with physical units
                            subbox_data.append({
                                'redshift': redshift,
                                'Volume_phys': float(values[2]) * (config.CELL_SIZE_MPC_H ** 3),
                                'Area_phys': float(values[3]) * (config.CELL_SIZE_MPC_H ** 2),
                                'Genus': float(values[5]),
                                'IMC_phys': float(values[6]) * config.CELL_SIZE_MPC_H,
                                'L_phys': L_grid * config.CELL_SIZE_MPC_H,
                                'B_phys': B_grid * config.CELL_SIZE_MPC_H,
                                'T_phys': T_grid * config.CELL_SIZE_MPC_H,
                                'P': P_val,
                                'F': F_val,
                            })
                except Exception as e:
                    print(f"    - Error processing {filename}: {e}")

        # After processing all files for a sub-box, create and save the CSV
        if not subbox_data:
            print(f"  - No data processed for subbox {i}. No CSV will be created.")
        else:
            df = pd.DataFrame(subbox_data)
            # --- MODIFIED SECTION ---
            # Construct the base filename, e.g., 'CD_OD1_SF_SB1.csv'
            base_filename = f'{region_prefix}_SF_SB{i}.csv'
            # Construct the full output path to save inside the subbox directory
            output_filepath = os.path.join(subbox_dir, base_filename)
            df.to_csv(output_filepath, index=False)
            print(f"  - Complete. Saved {len(df)} rows to '{output_filepath}'")
            # --- END OF MODIFICATION ---

def create_shapefinders_all_small_box_csv():
    """
    Combines shapefinder data from all sub-boxes into a single CSV.
    Performs cleaning and recalculates P and F.
    """
    print("\n--- Combining and cleaning all sub-box shapefinder data ---")
    all_dfs = []

    for base_dir, region_prefix in [
        (config.OVERDENSE_BASE_DIR, 'CD_OD1'),
        (config.UNDERDENSE_BASE_DIR, 'CD_UD1')
    ]:
        for i in range(1, 9): # Assuming 8 subboxes
            filepath = os.path.join(base_dir, f'subbox{i}', f'{region_prefix}_SF_SB{i}.csv')
            if os.path.exists(filepath):
                try:
                    df = pd.read_csv(filepath)
                    all_dfs.append(df)
                except Exception as e:
                    print(f"Warning: Could not read {filepath}: {e}")
            else:
                print(f"Warning: File not found, skipping: {filepath}")

    if not all_dfs:
        print("No sub-box shapefinder data found to combine.")
        return

    combined_df = pd.concat(all_dfs, ignore_index=True)

    # Clean the data: remove rows with any negative values in numerical columns
    # This specifically addresses the cleaning step observed in Spahefinder_stat.ipynb
    numerical_columns = combined_df.select_dtypes(include=['number']).columns
    # Ensure 'z' is not accidentally removed if it becomes negative due to some error, though typically redshift is positive.
    # We are specifically targeting physical quantities that shouldn't be negative.
    cols_to_check_positive = ['Volume_phys', 'Area_phys', 'Genus', 'IMC_phys', 'L_phys', 'B_phys', 'T_phys']
    
    # Filter for columns that are present in the numerical columns and are expected to be positive
    actual_cols_to_check = [col for col in cols_to_check_positive if col in numerical_columns]
    
    # Apply the filter
    cleaned_df = combined_df[(combined_df[actual_cols_to_check] >= 0).all(axis=1)].copy()

    # Rename columns for consistency with analysis functions
    cleaned_df = cleaned_df.rename(columns={
        'redshift': 'z',
        'Volume_phys': 'vol',
        'T_phys': 'T',
        'B_phys': 'B',
        'L_phys': 'L'
    })

    # Save the combined and cleaned DataFrame
    output_filepath = config.SHAPEFINDERS_ALL_SMALL_BOX_CSV
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    cleaned_df.to_csv(output_filepath, index=False)
    print(f"Successfully combined and cleaned {len(cleaned_df)} rows to: {output_filepath}")
    print(f"Original rows: {len(combined_df)}, Cleaned rows: {len(cleaned_df)}")
    print("-" * 30)
    return cleaned_df

def generate_common_redshifts_txt():
    """
    Generates a list of common redshifts from the combined shapefinder data
    and saves them to a text file.
    """
    print("\n--- Generating common redshifts list ---")
    try:
        df_sf_all = pd.read_csv(config.SHAPEFINDERS_ALL_SMALL_BOX_CSV)
    except FileNotFoundError:
        print(f"FATAL ERROR: Combined shapefinder CSV not found at {config.SHAPEFINDERS_ALL_SMALL_BOX_CSV}.")
        print("Please ensure it's created before generating common redshifts.")
        return

    # Extract unique, sorted redshifts
    unique_redshifts = sorted(df_sf_all['z'].unique())

    # Save to file
    output_filepath = config.COMMON_REDSHIFTS_TXT
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    with open(output_filepath, 'w') as f:
        for z in unique_redshifts:
            f.write(f"{z}\n")
    print(f"Successfully generated common redshifts list to: {output_filepath}")
    print("-" * 30)