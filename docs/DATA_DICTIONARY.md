# CairoGo — Data Dictionary (Pack v17)

> `recorded_at` = متى تبقى القيمة معروفة:
> - **at_request** ✅ → آمن كـ Feature
> - **after_decision / after_completion** ❌ → Data Leakage — لا تستخدمه كـ Feature

---

## trips.csv — الجدول الرئيسي (28,244 صف)

| Column | Type | recorded_at | Use as Feature? | Notes |
|---|---|---|---|---|
| `trip_id` | int | at_request | ❌ ID فقط | |
| `customer_id` | int | at_request | ⚠️ Join key | استخدم بيانات الـ customer بدله |
| `driver_id` | int | at_request | ⚠️ Join key | استخدم بيانات الـ driver بدله |
| `request_ts` | datetime str | at_request | ✅ استخرج منه | hour, day_of_week, month |
| `pickup_zone` | str | at_request | ✅ | يتعمله encoding |
| `dropoff_zone` | str | at_request | ✅ | يتعمله encoding |
| `distance_km` | float | at_request | ✅ | |
| `surge_multiplier` | float | at_request | ✅ | |
| `est_fare` | float | at_request | ✅ | |
| `eta_estimate_min` | float | at_request | ✅ | مهم لـ REASSIGN_DRIVER policy |
| `weather` | str | at_request | ✅ | Missing: 1,279 (4.5%) — قيم: clear/dust/rain/NaN |
| `payment_method` | str | at_request | ✅ | قيم: wallet/cash/card |
| `service_level` | str | at_request | ✅ | قيم: economy/comfort/premium |
| **`request_failed`** | int (0/1) | **TARGET** | 🎯 Target | 0=نجح (82.2%), 1=فشل (17.8%) |
| `actual_trip_time_min` | float | after_completion | ❌ LEAKAGE | Missing عند الـ failed trips (5,023) |
| `cancel_reason` | str | after_decision | ❌ LEAKAGE | Missing عند الـ completed trips (23,221) |
| `driver_arrival_min` | float | after_completion | ❌ LEAKAGE | Missing عند الـ failed trips (5,023) |
| `support_ticket_flag` | int (0/1) | after_completion | ❌ LEAKAGE | |

---

## customers.csv (6,000 صف)

| Column | Type | Use as Feature? | Notes |
|---|---|---|---|
| `customer_id` | int | Join key | |
| `signup_date` | str | ✅ | استخرج منه tenure |
| `channel` | str | ✅ | قناة التسجيل |
| `home_zone` | str | ✅ | |
| `loyalty_tier` | str | ✅ | مهم جداً |

---

## drivers.csv (1,500 صف)

| Column | Type | Use as Feature? | Notes |
|---|---|---|---|
| `driver_id` | int | Join key | |
| `join_date` | str | ✅ | استخرج منه tenure |
| `vehicle_type` | str | ✅ | |
| `experience_months` | int | ✅ | |
| `home_zone` | str | ✅ | |
| `rating_avg` | float | ✅ | Missing: 264 — drivers بدون تقييم كافي |

---

## zones.csv (24 صف)

| Column | Type | Use as Feature? | Notes |
|---|---|---|---|
| `zone_id` | str | Join key | |
| `zone_name` | str | — | |
| `legacy_name` | str | — | |
| `zone_type` | str | ✅ | نوع المنطقة |
| `has_metro` | int (0/1) | ✅ | |

---

## recent_labelled.csv (3,533 صف)
نفس أعمدة `trips.csv` — بيانات حديثة بـ labels.
- Target dist: 0=3,022 / 1=511
- استخدمها كـ **validation set** (بيانات مستقبلية بالنسبة لـ trips)

## holdout_inputs.csv (2,767 صف)
نفس أعمدة `trips.csv` **بدون** الـ target وبدون الـ leakage columns.
- هي الـ input لـ `predict.py` اللي بيتقيَّم عليه الـ grade

---

## Foundation pack (Individual — F_v17)

### foundation/drivers.csv (4,896 صف)
بيانات drivers لـ regression task (Part 0 الفردي)
- Target 1: `churn_next_month` (classification)
- Target 2: `next_month_earnings` (regression)

### foundation/telemetry.csv (9,000 صف)
بيانات sensors لـ anomaly detection (Part 0 الفردي)
- 30 sensor features: `s00` → `s29`
- Target: `harsh_event` (0/1)

---

> ⚠️ **مهم:** `data_dictionary.md` الموجود في `data/raw/cairogo_pack/` هو المرجع الرسمي من الـ assignment. هذا الملف شرح مبسط للفريق.
