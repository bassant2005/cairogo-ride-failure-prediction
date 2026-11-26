import json
import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()
nb.metadata = {
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'version': '3.14.4'}
}

cells = []

# Title & Metadata
cells.append(nbf.v4.new_markdown_cell("""# 🧹 Phase 1 — Data Cleaning: Missing Values Strategy

**Owner:** Rawda Raafat (Person D / Lead — ID: 20231067)  
**Role:** Missing Values Cleaning Module Lead  
**Module:** `src/missing_values.py`  
**Branch:** `phase1/Pd-missing-values-cleaning`

---

## 🎯 Objective

Translate the **Phase 1 Missingness Analysis findings (Task 2)** into a robust, leakage-free data cleaning component for the team's shared cleaning pipeline:
1. **`weather` (Categorical):** Handled as a distinct category `'missing'` + binary indicator flag `weather_was_missing`.
2. **`rating_avg` (Numerical):** Imputed with training set median + binary indicator flag `rating_avg_was_missing`.
3. **Train-Only Fitting:** Fitted strictly on `trips.csv`, and applied to `recent_labelled.csv` (validation) and `holdout_inputs.csv` (test).
4. **No Dropped Rows:** 100% of rows are retained to satisfy the holdout scoring contract.
5. **Leakage Protection:** Post-request leakage columns are cleanly isolated from feature imputation."""))

# Cell 1: Imports
cells.append(nbf.v4.new_code_cell("""import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(str(Path('../src').resolve()))
from missing_values import MissingValuesHandler, clean_missing_values

DATA_DIR = Path('../data/raw').resolve()
print('Cleaning module imported successfully.')"""))

# Cell 2: Load Data
cells.append(nbf.v4.new_code_cell("""trips = pd.read_csv(DATA_DIR / 'trips.csv', parse_dates=['request_ts'])
drivers = pd.read_csv(DATA_DIR / 'drivers.csv')
recent = pd.read_csv(DATA_DIR / 'recent_labelled.csv', parse_dates=['request_ts'])
holdout = pd.read_csv(DATA_DIR / 'holdout_inputs.csv', parse_dates=['request_ts'])

# Merge driver rating into trips, recent, and holdout
trips_df = trips.merge(drivers[['driver_id', 'rating_avg']], on='driver_id', how='left')
recent_df = recent.merge(drivers[['driver_id', 'rating_avg']], on='driver_id', how='left')
holdout_df = holdout.merge(drivers[['driver_id', 'rating_avg']], on='driver_id', how='left')

print('=== MISSING VALUES BEFORE CLEANING ===')
print('trips (Train)   :', trips_df[['weather', 'rating_avg']].isna().sum().to_dict())
print('recent (Val)    :', recent_df[['weather', 'rating_avg']].isna().sum().to_dict())
print('holdout (Test)  :', holdout_df[['weather', 'rating_avg']].isna().sum().to_dict())"""))

# Cell 3: Fit Handler on Train Data
cells.append(nbf.v4.new_code_cell("""# Initialize and fit the handler strictly on the training set
handler = MissingValuesHandler()
handler.fit(trips_df)

print('Learned Training Imputation Parameters:')
for k, v in handler.stats_.items():
    print(f'  {k:25s}: {v}')"""))

# Cell 4: Transform Datasets
cells.append(nbf.v4.new_code_cell("""# Transform all datasets
trips_clean = handler.transform(trips_df)
recent_clean = handler.transform(recent_df)
holdout_clean = handler.transform(holdout_df)

print('=== MISSING VALUES AFTER CLEANING ===')
print('trips (Train)   :', trips_clean[['weather', 'rating_avg']].isna().sum().to_dict())
print('recent (Val)    :', recent_clean[['weather', 'rating_avg']].isna().sum().to_dict())
print('holdout (Test)  :', holdout_clean[['weather', 'rating_avg']].isna().sum().to_dict())

print('\\n=== NEW INDICATOR COLUMNS CREATED ===')
print('trips weather_was_missing sum   :', trips_clean['weather_was_missing'].sum())
print('trips rating_avg_was_missing sum:', trips_clean['rating_avg_was_missing'].sum())
print('holdout weather_was_missing sum :', holdout_clean['weather_was_missing'].sum())
print('holdout rating_was_missing sum  :', holdout_clean['rating_avg_was_missing'].sum())"""))

# Cell 5: Validation Check
cells.append(nbf.v4.new_code_cell("""# Final Shape & Integrity Check
assert len(trips_clean) == len(trips_df), 'Row count mismatch in trips!'
assert len(recent_clean) == len(recent_df), 'Row count mismatch in recent!'
assert len(holdout_clean) == len(holdout_df), 'Row count mismatch in holdout!'
assert holdout_clean[['weather', 'rating_avg']].isna().sum().sum() == 0, 'Remaining NaNs in holdout!'

print('All validation assertions passed successfully! ✓')
print('Cleaned trips shape  :', trips_clean.shape)
print('Cleaned holdout shape:', holdout_clean.shape)"""))

nb.cells = cells

with open('notebooks/03_missing_values_cleaning.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print('notebooks/03_missing_values_cleaning.ipynb created successfully!')
