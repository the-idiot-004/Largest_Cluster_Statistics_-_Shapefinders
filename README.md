# Large Cluster Statistics (LCS) Analysis

This repository contains code and data for analyzing Large Cluster Statistics (LCS) from cosmological simulations during the Cosmic Dawn (CD) and Epoch of Reionization (EoR) periods.

The project is structured to separate code, data, and results for better organization and reproducibility.

## Project Structure

*   `docs/`: Contains project documentation, including the `LCS_Report.pdf`.
*   `data/`: Houses all data files.
    *   `data/raw/`: Contains original, raw output files from SURFGEN. These files are typically large and are not committed to version control.
    *   `data/processed/`: Contains processed and cleaned data files used directly by the analysis scripts.
*   `notebooks/`: Stores Jupyter notebooks used for exploratory data analysis, visualization, and initial testing.
*   `results/`: Stores the final outputs of the analysis.
    *   `results/plots/`: Contains all generated plots and figures.
    *   `results/data/`: Contains any derived data or summary statistics (e.g., `slopes.csv`).
*   `src/`: Contains all Python source code, organized into modules.
    *   `src/__init__.py`: Makes `src` a Python package.
    *   `src/constants.py`: Defines physical constants and simulation parameters.
    *   `src/data_processing.py`: Scripts for processing raw data into the `data/processed` format.
    *   `src/plotting.py`: Scripts for generating plots based on processed data.
    *   `src/utils.py`: Utility functions shared across different scripts.
*   `.gitignore`: Specifies files and directories that Git should ignore (e.g., raw data, temporary files, IDE configurations).
*   `run_all.sh`: A shell script to run the entire analysis pipeline.

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Set up your environment:**
    It is recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt # (You may need to create this file based on your dependencies)
    ```

3.  **Place raw data:**
    If you have the original raw output files from `SURFGEN`, place them in the `data/raw/` directory following the expected subdirectory structure (e.g., `data/raw/CD_overdensity_SURFGEN/output1/`).

4.  **Run the analysis pipeline:**
    The `run_all.sh` script orchestrates the entire analysis.
    ```bash
    bash run_all.sh
    ```
    This script will typically:
    *   Process raw data into `data/processed/`.
    *   Run analysis scripts to generate results.
    *   Generate plots and save them in `results/plots/`.

5.  **Explore notebooks:**
    Open the Jupyter notebooks in the `notebooks/` directory for interactive exploration of the data and results.
    ```bash
    jupyter notebook
    ```

## Dependencies

(List your Python dependencies here, e.g., pandas, numpy, matplotlib, etc.)
You may need to create a `requirements.txt` file by running `pip freeze > requirements.txt` before sharing or deploying.

## Contact

For any questions or issues, please refer to the `LCS_Report.pdf` or contact the original author.
