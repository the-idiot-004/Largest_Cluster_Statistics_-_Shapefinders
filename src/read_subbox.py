import os
import re
import pandas as pd

# --- Define constants for physical unit conversion ---
# These values should match the simulation parameters
boxsize_mpc_h = 500.0
grid_size = 300.0
cell_size_mpc_h = boxsize_mpc_h / grid_size

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
                                'Volume_phys': float(values[2]) * (cell_size_mpc_h ** 3),
                                'Area_phys': float(values[3]) * (cell_size_mpc_h ** 2),
                                'Genus': float(values[5]),
                                'IMC_phys': float(values[6]) * cell_size_mpc_h,
                                'L_phys': L_grid * cell_size_mpc_h,
                                'B_phys': B_grid * cell_size_mpc_h,
                                'T_phys': T_grid * cell_size_mpc_h,
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

# --- Main script execution ---

# Define the base paths for the two sets of sub-boxes
overdense_base_dir = "/home/amnkmr/SIP/LCS_data/data-team5/output_CD_overdensity_SURFGEN/output1/Shapefinder_stat/small_box/"
underdense_base_dir = "/home/amnkmr/SIP/LCS_data/data-team5/output_CD_underdensity_SURFGEN/output1/Shapefinder_stat/small_box/"

# Process the overdense sub-boxes
process_subboxes(overdense_base_dir, 'CD_OD1')

# Process the underdense sub-boxes
process_subboxes(underdense_base_dir, 'CD_UD1')

print("\n--- All processing finished. ---")
