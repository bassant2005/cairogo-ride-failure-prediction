# CairoGo – Data Leakage Analysis

## Project Overview

This notebook performs a data audit for the CairoGo ride-request prediction task. Its main objective is to identify features that could expose information that would only become available after a ride request has been created.

The prediction target is `request_failed`:
- `0`: Completed request
- `1`: Failed request

**Prediction-time assumption:** The model is expected to make its prediction when the request is created, at `request_ts`. Therefore, a feature is safe only if its value would genuinely be available at that moment.

---

## Notebook Workflow (Steps 1–12)

### 1. Data Loading and Initial Setup
Imports the required Python libraries and loads the four CairoGo datasets: `trips`, `customers`, `drivers`, and `zones`. It parses the relevant date columns (`request_ts`, `signup_date`, and `join_date`) as datetime values, checks that the dataset folder exists, and displays each dataset's dimensions.

### 2. Dataset Schema Inspection
Lists the columns in all four datasets. This provides an overview of the available fields and helps identify which features may be known at request time and which ones need further investigation. Decisions are based on the actual dataset structure, not column names alone.

### 3. Trips Dataset Inspection
Inspects the main `trips` table by displaying its data types, non-null counts, and first ten records. It also checks the distribution of the target variable `request_failed` and verifies whether the target contains missing values.

### 4. Missing Values Analysis by Target Class
Compares the percentage of missing values in each trip column for completed requests (`request_failed = 0`) and failed requests (`request_failed = 1`). The difference is calculated as:

`Failed Missing % - Completed Missing %`

Large differences can reveal fields whose values are recorded differently depending on the request outcome. This is an initial warning signal, not proof of leakage on its own.

### 5. Identification of Confirmed Data Leakage Features
Identifies three fields that contain information unavailable at request creation:
- `actual_trip_time_min`: The actual trip duration, known only after the trip has progressed or finished.
- `cancel_reason`: Describes the cancellation/failure outcome.
- `driver_arrival_min`: The actual driver arrival time, which is not known when the request is first created.

These columns are recorded in `confirmed_leakage` and must be excluded from model features.

### 6. Investigation of Suspicious Features
Investigates `driver_id` and `support_ticket_flag` using counts and failure rates. It then performs supporting checks on driver and customer records, profile attributes, missing values, experience, loyalty tiers, ratings, and zone information.

The subsections cover:
- **6.1 Suspicious Features Analysis Results:** Compares failure rates for driver IDs and support-ticket flags. The strong association for `support_ticket_flag` is treated as a warning because the ticket may be created after a failure.
- **6.2 Driver Join-Date Consistency Check:** Checks whether each driver's `join_date` is earlier than the related request timestamp.
- **6.3 Customer Signup-Date Consistency Check:** Checks whether each customer's `signup_date` is earlier than the related request timestamp.
- **6.4 Customer and Driver Feature Inspection:** Reviews profile fields and considers whether they could be available at prediction time.
- **6.5 Customer and Driver Missing Values Analysis:** Checks missing values in customer and driver profiles, including missing driver ratings.
- **6.6 Driver Experience Temporal Consistency:** Compares recorded driving experience with the driver's platform tenure at the time of the request.
- **6.7 Loyalty Tier and Driver Rating Analysis:** Compares failure rates across loyalty tiers and rating availability, while noting that association does not automatically mean leakage.
- **6.8 Zones Dataset Inspection:** Reviews the zone table and its geographic attributes, including zone IDs, current and legacy names, zone type, and metro availability.

The key unresolved questions are when a driver is assigned, when a support ticket is created, and whether profile values represent historical values at the request timestamp.

### 7. Additional Data Leakage Checks
Performs broader data-quality and leakage checks, including duplicate identifiers, key integrity, relationships between trips and customer/driver records, target patterns, and possible indirect signals. The accompanying interpretation explains why duplicate IDs and strong target associations need investigation but are not automatically leakage.

### 8. Temporal Analysis and Potential Time Leakage
Examines the time coverage of the data and failure patterns by day and hour. It also considers record ordering and the possibility that IDs or row order reflect time. These checks help identify temporal shifts and inform a suitable train/test split. For a model intended to predict future requests, a chronological split is generally more representative.

### 9. Feature Audit Based on Prediction Time
Audits the candidate features using the stated prediction point: request creation at `request_ts`. It distinguishes information that is definitely generated later from fields whose historical availability cannot be confirmed from the available timestamps.

### 10. Investigating Suspicious Feature Associations
Compares failure rates across categories of selected features. The purpose is to highlight patterns that deserve a timestamp/availability check, rather than removing every feature that happens to be associated with the target.

### 11. Leakage Prevention Rules for Model Development
Provides rules to carry into the modeling stage:
1. Keep `request_failed` separate from the predictors; never include it in `X`.
2. Remove confirmed leakage fields. Keep `support_ticket_flag` and `driver_id` excluded until their availability at request time is verified.
3. Do not use `actual_trip_time_min` or `driver_arrival_min` to impute missing values.
4. Fit imputation, encoding, and scaling only on the training data, preferably within a machine-learning pipeline.
5. Use a chronological train/test split when the goal is to predict future requests. Do not use test data for feature selection or tuning.
6. Verify that joined customer and driver profiles are historical snapshots as of each request, rather than their latest values.

### 12. Final Data Leakage Audit Summary
Collects the audit decisions into three groups:

**Confirmed leakage – exclude**
- `actual_trip_time_min`
- `cancel_reason`
- `driver_arrival_min`

**Exclude until verified**
- `support_ticket_flag`: Its failure-rate association is strong, and its creation time must be checked.
- `driver_id`: The dataset does not provide the assignment timestamp. A driver's join date being earlier than a request does not prove that the driver had already been assigned.

**Requires historical snapshot verification**
- `loyalty_tier`
- `rating_avg`
- `experience_months`
- `vehicle_type`
- `home_zone` from customer and driver profiles

The final conclusion is to exclude information generated after `request_ts`, verify uncertain fields against their creation/assignment timestamps, and perform all preprocessing using training data only.

---

## Dataset Requirements

The notebook expects the following folder structure relative to the notebook's working directory:

```text
project/
├── data/
│   └── raw/
│       └── cairogo_pack/
│           ├── trips.csv
│           ├── customers.csv
│           ├── drivers.csv
│           └── zones.csv
└── notebooks/
    └── Data_Leakage_Analysis_English.ipynb
```

The notebook sets the dataset directory to:

```python
Path("../data/raw/cairogo_pack").resolve()
```

If your project uses a different folder structure, update the `PACK` path in the first code section.

## Requirements

- Python 3
- pandas
- numpy
- Jupyter Notebook or JupyterLab

Install the Python packages if needed:

```bash
pip install pandas numpy jupyter
```

## How to Run

1. Place the four CSV files in `../data/raw/cairogo_pack`.
2. Open the notebook in Jupyter Notebook, JupyterLab, or a compatible environment.
3. Make sure the notebook's working directory makes the relative `PACK` path resolve to the dataset folder.
4. Run the notebook cells in order, from Step 1 through Step 12.
5. Review the audit decisions before selecting features for model training.

## Important Notes and Limitations

- A strong correlation or association with `request_failed` does not, by itself, prove data leakage.
- The audit assumes predictions are made at `request_ts`. If the actual prediction point changes, feature eligibility must be reviewed again.
- The available join-date and signup-date checks establish that the records predate the requests; they do not establish when a driver was assigned or when every profile attribute was last updated.
- Fields requiring historical snapshots or event timestamps should remain excluded until their availability at prediction time is documented.
- The notebook's conclusions are an audit guide. The modeling team should preserve these exclusions and checks when building the final training pipeline.

## Final Outcome

This audit identifies three confirmed leakage features, flags two additional fields for exclusion pending verification, and documents several profile attributes that require historical snapshot checks. It provides the data-quality and feature-availability rules needed to build a more realistic ride-request failure prediction model.
