# Notebooks

## Naming convention
Numbered notebooks (`NN_name.ipynb`) follow the project pipeline order.
Shared/exploratory notebooks that belong to a specific sub-task but don't occupy a main pipeline slot are kept without a number.

## Current notebooks

| File | Phase | Owner | Description |
|---|---|---|---|
| `01_data_overview.ipynb` | Phase 0 | Team | Initial data overview and shape inspection |
| `02_data_audit.ipynb` | Phase 1 — Task 1a | Person A (Mariam) | Zone mapping audit and join-loss analysis |
| `03_missingness_analysis.ipynb` | Phase 1 — Task 2 | Person D (Rawda) | MNAR missingness analysis for `weather` and `driver_rating_avg` |
| `04_unit_shift_confounding.ipynb` | Phase 1 — Task 1b | Person B (Rahma) | Unit shift detection and confounding variable analysis |
| `05_data_leakage_analysis.ipynb` | Phase 1 — Task 1c | Person C (Bassant) | Target leakage identification and single-feature AUC |
| `06_data_cleaning.ipynb` | Phase 1.3 | All (shared pipeline) | Shared data cleaning pipeline — Sections 2–6 |