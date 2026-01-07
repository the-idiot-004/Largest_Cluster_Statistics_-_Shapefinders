#!/usr/bin/env bash

# --------------- Prep directories ---------------
mkdir -p plots/shapefinders
mkdir -p plots/TxB
mkdir -p plots/slopes/TBL
mkdir -p plots/slopes/PG
mkdir -p output

# --------------- Step 1: Find common redshifts ---------------
echo "========== 1) Finding common redshifts =========="
python3 scripts/1_find_common_redshifts.py

# --------------- Step 2: Plot Shapefinders for each z ---------------
echo "========== 2) Plotting Shapefinders T,B,L,P,F,Genus =========="
python3 scripts/2_plot_shapefinders.py

# --------------- Step 3: Plot TxB curves for five z ---------------
echo "========== 3) Plotting T×B vs Volume for first five redshifts =========="
python3 scripts/3_plot_TxB.py

# --------------- Step 4: Extract slopes from all z ---------------
echo "========== 4) Extracting slopes (mT,mB,mL,mP,mF,mG,mTxB) =========="
python3 scripts/4_extract_slopes.py

# --------------- Step 5: Plot slopes mT,mB,mL,m(T×B) vs z ---------------
echo "========== 5) Plotting slopes T,B,L,TxB vs integer redshift =========="
python3 scripts/5_plot_slopes_TBL.py

# --------------- Step 6: Plot slopes mP and mG vs z ---------------
echo "========== 6) Plotting slopes P and Genus vs integer redshift =========="
python3 scripts/6_plot_slopes_PG.py

echo "========== All tasks completed! =========="


