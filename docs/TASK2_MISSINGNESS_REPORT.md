# CairoGo — Phase 1: Task 2 Missingness Analysis Report
**Dataset Pack:** v17 | **Leader ID:** 20231067 | **Target:** `request_failed`  
**Author:** Rawda Raafat (Student ID: 20231067 — Person D)  
**Role:** Data Audit & Missingness Analysis Lead  
**Date:** 24 November 2026  

---

## 1. Executive Summary

In Phase 1 (Data Understanding & Audit), Task 2 requires investigating missing values in **`weather`** (from `trips.csv`) and **`rating_avg`** (from `drivers.csv` joined to `trips.csv`). 

### The Core Question:
Is missingness **completely at random (MCAR)**, or is it **informative (MNAR — Missing Not At Random)**?
* If missingness is random, missing values can be dropped or simply replaced with means.
* If missingness carries information, the absence of data is **itself a predictive signal** that correlates with whether a ride will fail.

### Key Finding:
Both **`weather`** and **`rating_avg`** exhibit **statistically significant, informative missingness (MNAR)**:
1. Ride requests with **missing weather** have a **+4.06% higher failure rate** ($p = 0.00024$).
2. Ride requests with **unrated drivers** have a **+5.04% higher failure rate** ($p = 5.22 \times 10^{-12}$).

---

## 2. Statistical Findings & Evidence (Pack v17)

### A. Weather Missingness (`weather` in `trips.csv`)

| Metric | Value | Meaning |
|---|---|---|
| **Total Trips** | 28,244 | Full historical dataset |
| **Missing Weather Count** | 1,279 rows | 4.53% of all trips |
| **Failure Rate (Weather Missing)** | **21.66%** (277 / 1,279) | High risk |
| **Failure Rate (Weather Present)** | **17.60%** (4,746 / 26,965) | Normal risk |
| **Difference ($\Delta p$)** | **+0.0406** (+4.06 percentage points) | Informative gap |
| **Chi-Square ($\chi^2$) Test** | $\chi^2 = 13.4692$, $p = 0.00024$ | Statistically significant ($p < 0.001$) |
| **Interpretation** | **`"informative"`** (MNAR) | Missing weather behaves like rainy weather |

#### Breakdown by Weather Condition:
* `clear`: 22,739 trips $\rightarrow$ **17.36%** failure rate
* `dust`: 2,562 trips $\rightarrow$ **17.21%** failure rate
* `rain`: 1,664 trips $\rightarrow$ **21.51%** failure rate
* `Missing (NaN)`: 1,279 trips $\rightarrow$ **21.66%** failure rate

> **Insight:** Rides where weather logging fails have practically the same high cancellation rate as rainy rides. This occurs during severe weather disruptions or connectivity loss.

---

### B. Driver Rating Missingness (`rating_avg` in `drivers.csv`)

| Metric | Value | Meaning |
|---|---|---|
| **Fleet Drivers Missing Rating** | 264 / 1,500 drivers (17.60%) | New drivers with few rated trips |
| **Trips Handled by Unrated Drivers** | 3,103 / 28,244 trips (10.99%) | Volume of trips affected |
| **Failure Rate (Unrated Driver)** | **22.27%** (691 / 3,103) | High failure rate |
| **Failure Rate (Rated Driver)** | **17.23%** (4,332 / 25,141) | Baseline driver failure rate |
| **Difference ($\Delta p$)** | **+0.0504** (+5.04 percentage points) | Significant operational risk |
| **Chi-Square ($\chi^2$) Test** | $\chi^2 = 47.6023$, $p = 5.22 \times 10^{-12}$ | Extremely significant ($p < 10^{-11}$) |
| **Interpretation** | **`"informative"`** (MNAR) | Driver experience signal |

> **Insight:** Per official project documentation, `rating_avg` is missing when a driver lacks sufficient rated trips. New drivers are less familiar with optimal routes, less committed, and more likely to reject rides, leading to a 5.04% jump in failure rate.

---

## 3. Official Deliverable: `mnar` Block for `results.json`

This exact block will be merged into the team's final `results.json`:

```json
{
  "mnar": {
    "weather_missing_share": 0.0453,
    "weather_failure_rate_missing": 0.2166,
    "weather_failure_rate_present": 0.1760,
    "weather_diff": 0.0406,
    "weather_interpretation": "informative",
    "driver_rating_missing_share_drivers": 0.1760,
    "driver_rating_missing_share_trips": 0.1099,
    "driver_rating_failure_rate_missing": 0.2227,
    "driver_rating_failure_rate_present": 0.1723,
    "driver_rating_diff": 0.0504,
    "driver_rating_interpretation": "informative"
  }
}
```

---

## 4. Pipeline Directives for Phase 2 Modeling

To prevent data leakage and maximize prediction recall, the modeling team must follow these two rules:

1. **NEVER DROP ROWS:**
   * In `holdout_inputs.csv` (the graded test set), **6.43% of rows miss weather** and **10.91% miss driver ratings**.
   * Dropping rows will violate the submission contract, which requires predictions for 100% of holdout rows.
2. **PRESERVE INFORMATIVE SIGNALS:**
   * **For `weather`:** Treat `NaN` as a distinct categorical level: `['clear', 'dust', 'rain', 'missing']`. One-hot encoding will allow models to learn the $+4.06\%$ risk penalty.
   * **For `rating_avg`:**
     1. Impute missing numeric values with the **training set median rating** (prevents models from crashing on `NaN`).
     2. Add a binary feature indicator: `rating_avg_is_missing = rating_avg.isna().astype(int)`. This retains the $+5.04\%$ risk signal.
