# src/config.py

import os

# --- Project Root ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- Simulation Parameters ---
BOXSIZE_MPC_H = 500.0
GRID_SIZE = 300.0
CELL_SIZE_MPC_H = BOXSIZE_MPC_H / GRID_SIZE
TOTAL_SIMULATION_VOLUME = BOXSIZE_MPC_H ** 3

# --- Data Directories ---
DATA_DIR = os.path.join(ROOT_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

# --- Results Directories ---
RESULTS_DIR = os.path.join(ROOT_DIR, 'results')
PLOTS_DIR = os.path.join(RESULTS_DIR, 'plots')
RESULTS_DATA_DIR = os.path.join(RESULTS_DIR, 'data')

# --- Input Data Files ---
# Processed CSVs
SHAPEFINDERS_ALL_SMALL_BOX_CSV = os.path.join(PROCESSED_DATA_DIR, 'shapefinders_all_small_box.csv')
SHAPEFINDERS_ALL_SUBBOX0_CLEANED_CSV = os.path.join(PROCESSED_DATA_DIR, 'shapefinders_all_subbox0_cleaned.csv')
EOR_SHAPEFINDER_DATA_CSV = os.path.join(PROCESSED_DATA_DIR, 'EoR_shapefinder_data.csv')
CD_OD1_SF_EB_CSV = os.path.join(PROCESSED_DATA_DIR, 'CD_OD1_SF_EB.csv')
CD_UD1_SF_EB_CSV = os.path.join(PROCESSED_DATA_DIR, 'CD_UD1_SF_EB.csv')

# Raw Data (example paths, adjust as needed)
OVERDENSE_BASE_DIR = os.path.join(RAW_DATA_DIR, 'CD_overdensity_SURFGEN/output1/Shapefinder_stat/small_box/')
UNDERDENSE_BASE_DIR = os.path.join(RAW_DATA_DIR, 'CD_underdensity_SURFGEN/output1/Shapefinder_stat/small_box/')


# --- Output Data Files ---
# Control files
CD_OD1_CS_EB_CSV = os.path.join(PROCESSED_DATA_DIR, 'CD_OD1_CS_EB.csv')
CD_UD1_CS_EB_CSV = os.path.join(PROCESSED_DATA_DIR, 'CD_UD1_CS_EB.csv')
COMMON_REDSHIFTS_TXT = os.path.join(RESULTS_DATA_DIR, 'common_redshifts.txt')


# --- Analysis Parameters ---
TARGET_FFS = [0.01, 0.05, 0.1, 0.3]
NUM_BINS = 15
FIVE_Z_FOR_TXB = [10.11, 13.221, 14.294, 11.09, 9.938]

# --- Plotting Parameters ---
# Add any plot-specific configurations here
plt_style = {
    'font.family': 'serif',
    'mathtext.fontset': 'dejavuserif',
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.top': True,
    'ytick.right': True,
    'axes.linewidth': 1.0,
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 10,
}

# Ensure directories exist
os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(RESULTS_DATA_DIR, exist_ok=True)
