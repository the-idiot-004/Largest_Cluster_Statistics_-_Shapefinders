# scripts/utils.py

import numpy as np
import pandas as pd

def weighted_mean(values, weights):
    """Return weighted mean of values with given weights."""
    return np.sum(weights * values) / np.sum(weights)

def weighted_std(values, weights):
    """Return weighted standard deviation of values with given weights."""
    mean = weighted_mean(values, weights)
    variance = np.sum(weights * (values - mean)**2) / np.sum(weights)
    return np.sqrt(variance)

def loglog_fit(x, y):
    """
    Perform a linear fit in log10‐space: log10(y) = m * log10(x) + c.
    Returns: (slope, intercept, mask) where mask = (x>0 & y>0).
    """
    mask = (x > 0) & (y > 0)
    logx = np.log10(x[mask])
    logy = np.log10(y[mask])
    if len(logx) < 2: # np.polyfit requires at least 2 points for degree 1 fit
        # Handle cases where there are insufficient valid data points
        print(f"Warning: Insufficient valid data points ({len(logx)}) for log-log fit. Returning NaN slopes/intercepts.")
        return np.nan, np.nan, mask
    slope, intercept = np.polyfit(logx, logy, 1)
    return slope, intercept, mask

def get_common_redshifts(file1, file2, colname1='redshift', colname2='z'):
    """
    Read two CSVs, return sorted list of redshifts common to both.
    - file1: path to EoR_shapefinder_data.csv (with column colname1, typically 'redshift')
    - file2: path to Shapefinder_small_box.csv (with column colname2, typically 'z')
    """
    df1 = pd.read_csv(file1, usecols=[colname1])
    df2 = pd.read_csv(file2, usecols=[colname2])
    set1 = set(df1[colname1].unique())
    set2 = set(df2[colname2].unique())
    common = sorted(list(set1.intersection(set2)))
    return common

def bin_edges_for_vol(vol_array, n_bins=8):
    """
    Given an array of volumes, return n_bins+1 log‐spaced edges
    from vol.min() to vol.max(). (So there will be `n_bins` bins total.)
    """
    v_min = vol_array.min()
    v_max = vol_array.max()
    edges = np.logspace(np.log10(v_min), np.log10(v_max), n_bins + 1)
    return edges

def ensure_folder(path):
    """Helper to create folder if it doesn't exist."""
    import os
    if not os.path.isdir(path):
        os.makedirs(path)
