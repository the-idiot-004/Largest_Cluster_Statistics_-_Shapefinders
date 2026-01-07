# main.py

import src.config as config
from src.data_processing import create_control_file, process_subboxes
from src.analysis import (
    run_sb_analysis, 
    process_shapefinders_for_redshift,
    process_txb_for_redshifts
)
from src.plotting import (
    plot_sb_analysis, 
    plot_shapefinders_for_redshift,
    plot_txb_for_redshifts
)
import pandas as pd


def main():
    """
    Main function to run the entire analysis pipeline.
    """
    # --- 1. Data Processing ---
    print("--- Starting Data Processing ---")
    
    # Create control files
    create_control_file(config.CD_OD1_SF_EB_CSV, config.CD_OD1_CS_EB_CSV)
    create_control_file(config.CD_UD1_SF_EB_CSV, config.CD_UD1_CS_EB_CSV)
    
    # Process subboxes
    process_subboxes(config.OVERDENSE_BASE_DIR, 'CD_OD1')
    process_subboxes(config.UNDERDENSE_BASE_DIR, 'CD_UD1')

    # --- 2. Main Analysis ---
    print("\n--- Starting Main Analysis ---")
    
    # Run SB analysis
    sb_analysis_results = run_sb_analysis()
    plot_sb_analysis(sb_analysis_results)
    
    # Process and plot shapefinders for each redshift
    with open(config.Common_REDSHIFTS_TXT, 'r') as f:
        z_list = [float(l.strip()) for l in f if l.strip()]
        
    for z in z_list:
        shapefinder_data = process_shapefinders_for_redshift(z)
        plot_shapefinders_for_redshift(shapefinder_data)
        
    # Process and plot Txb for selected redshifts
    txb_results = process_txb_for_redshifts(config.FIVE_Z_FOR_TXB)
    plot_txb_for_redshifts(txb_results)

    print("\n--- Analysis Complete ---")


if __name__ == '__main__':
    main()
