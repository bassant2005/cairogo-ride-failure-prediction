# CairoGo — Data Dictionary (Pack v17)

> `recorded_at` indicates when each value becomes known:
> - **at_request** ✅ → Safe to use as a feature
> - **after_decision / after_completion** ❌ → Data leakage — never use as a feature

---

## trips.csv — Main Table (28,244 rows)

| Column | Type | recorded_at | Use as Feature? | Notes |
|---|---|---|---|---|
| `trip_id` | int | at_request | ❌ ID only | |
| `customer_id` | int | at_request | ⚠️ Join key | Use joined customer attributes instead |
| `driver_id` | int | at_request | ⚠️ Join key | Use joined driver attributes instead |
| `request_ts` | datetime str | at_request | ✅ Extract from it | hour, day_of_week, month |
| `pickup_zone` | str | at_request | ✅ | Requires encoding |
| `dropoff_zone` | str | at_request | ✅ | Requires encoding |
| `distance_km` | float | at_request | ✅ | |
| `surge_multiplier` | float | at_request | ✅ | |
| `est_fare` | float | at_request | ✅ | |
| `eta_estimate_min` | float | at_request | ✅ | Key input for REASSIGN_DRIVER policy |
| `weather` | str | at_request | ✅ | Missing: 1,279 (4.5%) — values: clear / dust / rain / NaN |
| `payment_method` | str | at_request | ✅ | Values: wallet / cash / card |
| `service_level` | str | at_request | ✅ | Values: economy / comfort / premium |
| **`request_failed`** | int (0/1) | **TARGET** | 🎯 Target | 0 = completed (82.2%), 1 = failed (17.8%) |
| `actual_trip_time_min` | float | after_completion | ❌ LEAKAGE | Missing for failed trips (5,023 rows) |
| `cancel_reason` | str | after_decision | ❌ LEAKAGE | Missing for completed trips (23,221 rows) |
| `driver_arrival_min` | float | after_completion | ❌ LEAKAGE | Missing for failed trips (5,023 rows) |
| `support_ticket_flag` | int (0/1) | after_completion | ❌ LEAKAGE | |

---

## customers.csv (6,000 rows)

| Column | Type | Use as Feature? | Notes |
|---|---|---|---|
| `customer_id` | int | Join key | |
| `signup_date` | str | ✅ | Extract customer tenure from it |
| `channel` | str | ✅ | Acquisition channel: ads / organic / referral |
| `home_zone` | str | ✅ | |
| `loyalty_tier` | str | ✅ | Values: bronze / silver / gold |

---

## drivers.csv (1,500 rows)

| Column | Type | Use as Feature? | Notes |
|---|---|---|---|
| `driver_id` | int | Join key | |
| `join_date` | str | ✅ | Extract driver tenure from it |
| `vehicle_type` | str | ✅ | Values: hatchback / sedan / van |
| `experience_months` | int | ✅ | |
| `home_zone` | str | ✅ | |
| `rating_avg` | float | ✅ | Missing for 264 drivers (insufficient rated trips) |

---

## zones.csv (24 rows)

| Column | Type | Use as Feature? | Notes |
|---|---|---|---|
| `zone_id` | str | Join key | |
| `zone_name` | str | — | |
| `legacy_name` | str | — | |
| `zone_type` | str | ✅ | Values: downtown / midtown / new_city / suburb / airport |
| `has_metro` | int (0/1) | ✅ | |

---

## recent_labelled.csv (3,533 rows)
Same columns as `trips.csv` — labelled recent data.
- Target distribution: 0 = 3,022 / 1 = 511
- Use as the **validation set** (chronologically after `trips.csv` — forward-in-time split)

## holdout_inputs.csv (2,767 rows)
Same columns as `trips.csv` **without** the target and without leakage columns.
- This is the graded input for `predict.py` — submit predictions as `holdout_predictions.csv`

---

## Foundation Pack (Individual — F_v17)

### foundation/drivers.csv (4,896 rows)
Driver data for the individual regression task (Part 0).
- Target 1: `churn_next_month` (classification)
- Target 2: `next_month_earnings` (regression)

### foundation/telemetry.csv (9,000 rows)
Sensor data for the individual anomaly detection task (Part 0).
- 30 sensor features: `s00` → `s29`
- Target: `harsh_event` (0/1)

---

> ⚠️ **Note:** `data_dictionary.md` inside `data/raw/cairogo_pack/` is the official reference from the assignment. This file is the team's expanded version with feature guidance.
