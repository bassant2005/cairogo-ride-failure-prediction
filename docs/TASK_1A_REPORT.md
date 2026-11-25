# Technical Audit Report — Task 1a: Join Loss & Geographic Zone Mapping

**Project:** CairoGo Ride-Hailing Failure Prediction  
**Author:** Mariam Ehab Hassan (Person A)  
**Student ID:** 20231160  
**Dataset Version:** Pack v17 (Leader ID: 20231067)  
**Branch:** `phase1/data-joins`  
**Evaluation Criteria Reference:** `CairoGo_Assignment_V4.pdf` — Task 1a (`join.unmatched_before`, `join.unmatched_zones`, `join.fix`)

---

## 1. Executive Summary

During the initial data audit phase of the CairoGo operational dataset (`trips.csv`), a critical relational mismatch was detected when joining trip request records with the official reference zones registry (`zones.csv`). Historical zone renaming events in Cairo resulted in unstandardized zone strings within `pickup_zone` (and `dropoff_zone`), causing severe **Join Loss**.

### Key Quantified Findings:
- **Pre-Remediation Join Loss:** **`0.1148`** (11.48% of total historical ride requests, representing **3,243 affected trips** out of 28,244).
- **Unmatched Identifiers Detected:** Exactly three legacy zone names: `['Badr City', 'Dokki', 'New Cairo']`.
- **Target Distributional Discrepancy:** The ride failure rate (`request_failed = 1`) among unmatched trips is **19.24%**, compared to **17.61%** among matched trips (+1.63% absolute discrepancy). Discarding these records would have introduced significant selection bias into subsequent modeling stages.
- **Remediation Result:** By extracting the authoritative `legacy_name → zone_name` dictionary from `zones.csv`, all 3,243 affected records were successfully remapped. **Post-repair join loss is 0.0000 (0 records lost)**.
- **Multimodal Integration:** All trip records were losslessly joined with zone attributes (`zone_type`, `has_metro`), customer demographics, and driver metrics, yielding an integrated dataset of shape `(28244, 29)`.

---

## 2. Problem Formulation & Audit Objective

In ride-hailing operations, geographic zones serve as fundamental spatial anchors for pricing, ETA calculations, fleet rebalancing, and failure risk prediction. CairoGo maintains an official geographic reference table (`zones.csv`) comprising 24 administrative zones, categorized into specific urban types (`downtown`, `midtown`, `new_city`, `suburb`, `airport`).

When joining `trips.csv` with `zones.csv` on `pickup_zone = zone_name`:
1. If legacy or unstandardized strings exist, an inner join silently drops valid trip records.
2. A left join retains the rows but leaves critical geographic features (`zone_type`, `has_metro`) as missing (`NaN`).

**Task 1a Objective:**
Quantify the extent of join loss, identify the offending zone identifiers, establish an automated, leakage-free remediation mechanism, and document the verified payload for the final `results.json` submission.

---

## 3. Systematic Investigation & Discovery

### 3.1 Zone Set Intersection
Extracting unique values from both entities revealed a divergence:
- Unique zones defined in `zones.csv`: 24 official zones.
- Unique pickup zones present in `trips.csv`: 24 unique string values.
- **Set Difference (`trips_pickup_zones - valid_zone_names`):**
  $$\text{Unmatched Zones} = \{ \text{'Badr City'}, \text{'Dokki'}, \text{'New Cairo'} \}$$

Correspondingly, three official zones in `zones.csv` never appeared as pickup locations in raw `trips.csv`:
$$\text{Unreferenced Official Zones} = \{ \text{'Badr City District'}, \text{'Dokki District'}, \text{'New Cairo District'} \}$$

### 3.2 Volume of Impaired Records
```python
unmatched_mask = trips["pickup_zone"].isin(["Badr City", "Dokki", "New Cairo"])
n_unmatched = unmatched_mask.sum() # 3,243
total_records = len(trips)         # 28,244
join_loss_fraction = 3243 / 28244  # 0.114817... -> 0.1148
```

| Legacy Zone Name | Affected Trips Count | Percentage of Dataset |
|---|---|---|
| `Dokki` | 1,189 | 4.21% |
| `New Cairo` | 1,062 | 3.76% |
| `Badr City` | 992 | 3.51% |
| **Total Affected** | **3,243** | **11.48%** |

### 3.3 Selection Bias & Target Disparity Analysis
To determine whether this mismatch was missing completely at random (MCAR) or non-random, we evaluated the empirical failure rate across partitions:
- **Failure rate in Unmatched Records:** $\frac{624}{3,243} = \mathbf{19.24\%}$
- **Failure rate in Matched Records:** $\frac{4,399}{25,001} = \mathbf{17.60\%}$
- **Overall Dataset Failure Rate:** $\frac{5,023}{28,244} = \mathbf{17.78\%}$

**Interpretation:** The failure rate in the affected zones is over 1.6% higher than in the rest of the network. New cities and high-congestion districts (e.g., Dokki, New Cairo, Badr City) exhibit distinct dispatch dynamics. Dropping these trips would have systematically pruned high-risk requests, distorting model calibration.

---

## 4. Remediation Strategy & Implementation

Inspection of `zones.csv` confirmed that the data engineering team had preserved a `legacy_name` column representing historical zone nomenclature:

```text
zone_id  zone_name            legacy_name     zone_type  has_metro
Z11      Dokki District       Dokki           midtown    0
Z13      New Cairo District   New Cairo       new_city   0
Z21      Badr City District   Badr City       suburb     0
```

### 4.1 Automated Mapping Transformation
Rather than hardcoding arbitrary string replacements, we constructed a programmatic mapping dictionary directly from the authoritative reference table:

```python
legacy_to_standard = zones.set_index("legacy_name")["zone_name"].to_dict()

# Vectorized replacement across both spatial endpoints
trips["pickup_zone"]  = trips["pickup_zone"].replace(legacy_to_standard)
trips["dropoff_zone"] = trips["dropoff_zone"].replace(legacy_to_standard)
```

### 4.2 Post-Remediation Verification
- Unmatched pickup zones remaining: `0`
- Unmatched dropoff zones remaining: `0`
- Records discarded: `0`
- Verification Status: **100% Match Rate (0.0000 Join Loss)**.

---

## 5. Multi-Table Integration & Schema Harmonization

Following zone remediation, `trips` was integrated with auxiliary tables to build the unified feature table:

1. **Zone Metadata Join:**
   `pickup_zone` joined with `zones.csv` (`zone_name`) to attach `zone_type` and `has_metro`. Zero missing values were generated.
2. **Customer Demographics Join:**
   Joined with `customers.csv` on `customer_id`. The customer's `home_zone` was explicitly aliased to `customer_home_zone` to avoid suffix collisions.
3. **Driver Operational Attributes Join:**
   Joined with `drivers.csv` on `driver_id`. The driver's `home_zone` was explicitly aliased to `driver_home_zone`.

**Final Integrated Dataset Dimensions:** `28,244` rows $\times$ `29` columns.  
Exported to: `data/processed/trips_cleaned.csv`.

---

## 6. Official Submission Payload (`results.json`)

Per the contract documented in `RESULTS_SCHEMA.md`, the extracted values for Task 1a are:

```json
{
  "join": {
    "unmatched_before": 0.1148,
    "unmatched_zones": [
      "Badr City",
      "Dokki",
      "New Cairo"
    ],
    "fix": "Replaced legacy zone names in pickup_zone and dropoff_zone using legacy_name to zone_name mapping from zones.csv"
  }
}
```
