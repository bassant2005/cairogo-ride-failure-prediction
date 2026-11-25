# Phase 1 — Person B Audit Report
## Unit Shift, Distribution Drift, Feature–Target Relationships & Confounder Analysis

**Project:** CairoGo Ride Failure Prediction  
**Phase:** Phase 1 — Data Understanding & Audit (Task 1: Data Audit)  
**Role:** Person B (Numeric Analysis, Distribution Drift & Confounding)  
**Assigned Student:** Mariam Ehab Hassan (20231160)  
**Branch:** `phase1/B-unit-shift-confounding`  
**Date:** November 2026  
**Primary Dataset:** `trips.csv` (Pack v17, 28,244 ride requests)

---

## 1. Executive Summary

As part of **Phase 1: Data Understanding & Audit**, Person B is responsible for auditing the numerical integrity of the CairoGo operations dataset before any feature engineering or machine learning models are developed.

The primary objective is to prevent models from learning invalid or superficial patterns caused by:
1. **Unit shifts** (changes in the scale or metric of recorded variables over time).
2. **Distribution drift** (unstable feature properties across the observation period).
3. **Misunderstood feature-target relationships** (assuming linearity where non-linear patterns dominate).
4. **Confounding variables** (third variables that distort bivariate relationships and create spurious correlations).

All five sub-tasks assigned to Person B have been completed, verified with statistical tests, visualized, and documented in the reproducible notebook:  
📂 [`notebooks/02_unit_shift_confounding.ipynb`](../notebooks/02_unit_shift_confounding.ipynb)

---

## 2. Dataset Scope & Safety Boundaries

The audit strictly adheres to the project's **Zero-Leakage Policy**:
* **Included features:** Only columns with `recorded_at = 'at_request'` (`distance_km`, `surge_multiplier`, `est_fare`, `eta_estimate_min`, `service_level`, `pickup_zone`, and temporal extractions from `request_ts`).
* **Excluded leakage columns:** `actual_trip_time_min`, `cancel_reason`, `driver_arrival_min`, and `support_ticket_flag` are strictly omitted.
* **Observation period:** May 1, 2026 to August 30, 2026 (4 full months, 18 calendar weeks).
* **Target:** `request_failed` (binary: $0 = \text{Completed } [82.2\%]$, $1 = \text{Failed } [17.8\%]$).

---

## 3. Task 1: Unit Shift Detection

### 3.1 Objective
A **unit shift** occurs when a measurement system changes its scale part-way through data collection (for instance, distances shifting from kilometers to meters, or fares recorded in different currencies).

### 3.2 Methodology
* **Weekly Median Tracking:** Computed weekly medians across all 18 weeks for all four numerical features (`distance_km`, `surge_multiplier`, `est_fare`, `eta_estimate_min`).
* **Rate-of-Change Check:** Flagged any consecutive week-over-week median shift exceeding $\pm 50\%$.
* **Ratio Consistency Check:** Tracked the weekly median of the ratio:
  $$\text{Fare per Kilometer} = \frac{\text{est\_fare}}{\text{distance\_km}}$$
  A sudden jump in this ratio would immediately isolate a unit shift in either distance or fare calculation.

### 3.3 Findings
* **Weekly Medians:**
  * `distance_km`: Highly stable around a median of $8.66\text{ km} - 9.43\text{ km}$ across all 18 weeks (maximum week-over-week change: $8.1\%$).
  * `est_fare`: Stable around a median of $84.30 - 98.05\text{ EGP}$ (maximum weekly change: $11.9\%$).
  * `eta_estimate_min`: Stable around $8.20 - 8.40\text{ minutes}$.
  * `surge_multiplier`: Median remained exactly $1.10\times$ across all months.
* **Ratio Check:** The coefficient of variation for $\text{Fare per Kilometer}$ was $CV = 0.038 \ll 0.10$, indicating near-perfect mathematical stability.

### 3.4 Conclusion
✅ **No unit shifts exist.** All numerical features maintain uniform measurement units throughout the entire four-month collection window.

---

## 4. Task 2: Distribution Changes & Drift (Statistical vs. Practical)

### 4.1 Objective
Detect whether feature distributions drifted over time. A critical focus was evaluating whether observed differences are **statistically significant** versus **practically meaningful**.

### 4.2 Methodology
1. **Monthly Box Plots:** Visual inspection of medians, interquartile ranges (IQR), and extreme outliers across May, June, July, and August.
2. **Two-Sample Kolmogorov–Smirnov (K-S) Tests:**
   * **Endpoint Test:** May ($N = 6,639$) vs. August ($N = 7,451$).
   * **Consecutive Month Tests:** May vs. Jun, Jun vs. Jul, and Jul vs. Aug to audit non-monotonic fluctuations.
3. **Effect Size Evaluation:** Distinguished between the test $p$-value and the **K-S Statistic ($D$)**, representing the maximum vertical distance between two empirical cumulative distribution functions (CDFs):
   * $D < 0.05$: Negligible / practically minor drift ($< 5\%$ maximum CDF divergence).
   * $0.05 \le D < 0.10$: Moderate drift.
   * $D \ge 0.10$: Substantial drift requiring retraining or domain adaptation.

### 4.3 Results & Statistical Proof

#### A. Endpoint Test (May vs. August)
| Feature | K-S Stat ($D$) | $p$-value | Statistical Verdict | Practical Effect Size |
|---|---|---|---|---|
| `distance_km` | **0.0098** | **0.8823** | $p \ge 0.05$ (Same) | **Identical** ($D < 0.01$) |
| `surge_multiplier` | **0.0277** | **0.0089** | $p < 0.05$ (Diff) | **Negligible** ($D = 2.8\%$) |
| `est_fare` | **0.0242** | **0.0317** | $p < 0.05$ (Diff) | **Negligible** ($D = 2.4\%$) |
| `eta_estimate_min` | **0.0308** | **0.0025** | $p < 0.05$ (Diff) | **Negligible** ($D = 3.1\%$) |

#### B. Consecutive Month Dynamics
* **`distance_km`:**
  * May vs Jun: $D = 0.0132, p = 0.5928$
  * Jun vs Jul: $D = 0.0116, p = 0.7244$
  * Jul vs Aug: $D = 0.0113, p = 0.7230$
* **`surge_multiplier`:**
  * May vs Jun: $D = 0.0239, p = 0.0417$
  * Jun vs Jul: $D = 0.0225, p = 0.0543$
  * Jul vs Aug: $D = 0.0298, p = 0.0027$
* **`est_fare`:**
  * May vs Jun: $D = 0.0126, p = 0.6494$
  * Jun vs Jul: $D = 0.0315, p = 0.0017$
  * Jul vs Aug: $D = 0.0365, p = 0.0001$
* **`eta_estimate_min`:**
  * May vs Jun: $D = 0.0341, p = 0.0008$
  * Jun vs Jul: $D = 0.0219, p = 0.0658$
  * Jul vs Aug: $D = 0.0263, p = 0.0116$

### 4.4 Resolving the Statistical Contradiction
* **Why did the K-S test reject $H_0$ ($p < 0.05$) for 3 features?**
  Because the sample size is very large ($N \approx 7,000$ per month), the statistical power of the test approaches $1.0$. Consequently, tiny fluctuations in summer traffic and fuel price adjustments are detected as statistically significant.
* **Is this drift practically dangerous for machine learning?**
  **No.** The maximum CDF divergence across all features never exceeds $D = 0.036$ ($3.6\%$). The distributions are **substantively stable**. 
* **Conclusion:** `distance_km` is fully invariant. Minor practical shifts in `est_fare` and `eta` will be cleanly controlled by incorporating temporal features (`hour`, `day_of_week`).

---

## 5. Task 3: Feature–Target Relationships

### 5.1 Overview
Every numerical feature was evaluated against `request_failed` using non-parametric **Mann-Whitney U tests**, **Kernel Density Estimation (KDE)**, and **quantile-based failure rate binning**.

### 5.2 Key Numerical Insights

| Feature | Correlation ($r$) | Mann-Whitney $p$-value | Mean (Completed) | Mean (Failed) | Dominant Behavior |
|---|---|---|---|---|---|
| `distance_km` | **+0.2697** | $< 0.0001$ | 9.84 km | **14.51 km** | Strong positive non-linear |
| `surge_multiplier` | **-0.2780** | $< 0.0001$ | 1.305x | **1.060x** | Counter-intuitive negative |
| `eta_estimate_min` | **-0.2728** | $< 0.0001$ | 9.66 min | **6.77 min** | Counter-intuitive negative |
| `est_fare` | **-0.0784** | $< 0.0001$ | 104.76 EGP | **93.08 EGP** | Weak, redundant predictor |

### 5.3 Non-Linearity & Segment Patterns

1. **`distance_km` (Driver Rejection on Long Trips):**
   * $0 - 3\text{ km}$: Failure rate = **0.1%** ($n = 2,544$).
   * $3 - 7\text{ km}$: Failure rate = **4.0%** ($n = 8,197$).
   * $7 - 15\text{ km}$: Failure rate = **26.1%** ($n = 11,273$).
   * $> 30\text{ km}$: Failure rate = **53.0%** ($n = 413$).
   * *Interpretation:* A sharp inflection point occurs at $7\text{ km}$. Drivers frequently reject requests exceeding $15-30\text{ km}$ due to unprofitable return trips.

2. **`surge_multiplier` (Incentive Effect):**
   * Baseline $1.0\times$: Failure rate = **29.5%** ($n = 11,171$).
   * $1.0 - 1.5\times$: Failure rate = **14.8%** ($n = 10,240$).
   * $1.5 - 2.0\times$: Failure rate = **0.7%** ($n = 5,147$).
   * $> 2.0\times$: Failure rate = **0.6%** ($n = 1,686$).
   * *Interpretation:* Higher surge pricing dramatically suppresses ride failures because drivers eagerly accept high-margin rides.

3. **`eta_estimate_min` (Urban Congestion Discrepancy):**
   * $< 5\text{ min}$: Failure rate = **33.7%** ($n = 4,204$).
   * $5 - 10\text{ min}$: Failure rate = **22.6%** ($n = 15,221$).
   * $15 - 20\text{ min}$: Failure rate = **1.6%** ($n = 1,940$).
   * *Interpretation:* Counter-intuitive on the surface (short ETA fails more). This discrepancy directly pointed to geographical and temporal confounding.

---

## 6. Task 4: Formal Confounder Analysis

### 6.1 Methodological Framework
To move beyond descriptive correlation, we applied the formal **Change-in-Estimate Criterion** from epidemiology and causal inference:
1. Fit a crude Logistic Regression: $\text{logit}(P(Y=1)) = \beta_0 + \beta_{\text{crude}} X$
2. Fit an adjusted Logistic Regression: $\text{logit}(P(Y=1)) = \beta_0 + \beta_{\text{adj}} X + \sum \gamma_k Z_k$
3. Compute relative parameter shift:
   $$\Delta \beta = \frac{\beta_{\text{adj}} - \beta_{\text{crude}}}{\beta_{\text{crude}}} \times 100\%$$
   **Criterion:** $|\Delta \beta| \ge 10\%$ confirms a **True Confounder**.

### 6.2 Empirical Proofs

#### Test A: `service_level` confounds `distance_km`
* **Crude Model:** $\beta_{\text{crude}} = 0.0945$ ($\text{Odds Ratio} = 1.0991$).
* **Adjusted Model:** $\beta_{\text{adj}} = 0.1214$ ($\text{Odds Ratio} = 1.1291$).
* **Relative Shift:** **$\Delta \beta = +28.47\%$** ($|\Delta| \gg 10\%$).
* **Proof:** In the crude model, the true negative effect of distance was masked by Premium rides (which naturally travel longer distances with different completion dynamics). Controlling for service tier reveals a **$28.5\%$ stronger penalty** for trip distance.
* **Verdict:** ✅ **CONFIRMED CONFOUNDER**.

#### Test B: `hour` of day confounds `surge_multiplier`
* **Crude Model:** $\beta_{\text{crude}} = -4.8917$ ($\text{Odds Ratio} = 0.0075$).
* **Adjusted Model:** $\beta_{\text{adj}} = -5.6403$ ($\text{Odds Ratio} = 0.0036$).
* **Relative Shift:** **$\Delta \beta = +15.30\%$** ($|\Delta| \ge 10\%$).
* **Proof:** During late off-peak hours (e.g., 2:00 AM – 5:00 AM), surge pricing remains at $1.0\times$ despite driver scarcity. This temporal misalignment artificially inflated the failure rate of $1.0\times$ trips. Controlling for the 24 hours shifts the coefficient by $15.3\%$.
* **Verdict:** ✅ **CONFIRMED CONFOUNDER**.

#### Test C: `pickup_zone` confounds `eta_estimate_min`
* **Crude Model:** $\beta_{\text{crude}} = -0.2441$ ($\text{Odds Ratio} = 0.7834$).
* **Adjusted Model:** $\beta_{\text{adj}} = -0.1970$ ($\text{Odds Ratio} = 0.8212$).
* **Relative Shift:** **$\Delta \beta = -19.29\%$** ($|\Delta| \ge 10\%$).
* **Proof:** High-density zones (e.g., Downtown, Zamalek) report very short estimated arrival times because drivers are geographically close, but intense competition and traffic lead to frequent cancellation. Controlling for the 24 pickup zones absorbs **$19.3\%$** of the apparent ETA effect.
* **Verdict:** ✅ **CONFIRMED CONFOUNDER**.

### 6.3 Confounding Synthesis Table

| Feature (Exposure) | Suspected Confounder | Crude $\beta$ | Adjusted $\beta$ | Relative Shift ($\Delta \beta$) | Odds Ratio Shift | Confounder Status |
|---|---|---|---|---|---|---|
| `distance_km` | `service_level` | $+0.0945$ | $+0.1214$ | **$+28.47\%$** | $1.099 \to 1.129$ | **CONFIRMED** |
| `surge_multiplier` | `hour` (24h) | $-4.8917$ | $-5.6403$ | **$+15.30\%$** | $0.0075 \to 0.0036$ | **CONFIRMED** |
| `eta_estimate_min` | `pickup_zone` (24 zones) | $-0.2441$ | $-0.1970$ | **$-19.29\%$** | $0.783 \to 0.821$ | **CONFIRMED** |

---

## 7. Task 5: Concrete Implications for Phase 2 Modeling

Based on the empirical evidence gathered by Person B, the following guidelines are established for the Phase 2 modeling team:

1. **Feature Pruning:**
   * **Drop `est_fare`:** It exhibits weak standalone predictive power ($r = -0.08$) and is mathematically redundant ($R^2 \approx 0.98$) given `distance_km`, `surge_multiplier`, and `service_level`. Dropping it prevents multicollinearity in linear models and reduces tree split fragmentation.

2. **Essential Control Features:**
   * **`hour` and `day_of_week`:** Must be explicitly included as cyclical features ($\sin / \cos$ encoding) or categorical features to control for temporal confounding.
   * **`pickup_zone`:** Must be included (via Target Encoding or Frequency Encoding) to disentangle geographical supply shortages from ETA estimates.

3. **Feature Transformations:**
   * **Non-linear Distance Penalty:** Apply $\log(1 + \text{distance\_km})$ or binning (`<3km`, `3-7km`, `7-15km`, `>15km`) to linear models, or allow tree models to split at the discovered $7\text{ km}$ threshold.

4. **Model Architecture Selection:**
   * Due to strong non-linear threshold effects (step-changes in failure rates at $7\text{ km}$ distance and $1.5\times$ surge) and complex 3-way interactions, **Gradient Boosted Trees (LightGBM, XGBoost, CatBoost)** are expected to substantially outperform standard Logistic Regression.

---

## 8. Summary of Generated Figures & Artifacts

All supporting figures have been exported to [`reports/figures/`](../reports/figures/):

| Figure File | Description |
|---|---|
| `unit_shift_weekly_medians.png` | 18-week median stability across all numerical features |
| `unit_shift_fare_per_km.png` | Consistency check tracking Fare-per-Km ratio ($CV = 0.038$) |
| `distribution_monthly_boxplots.png` | Month-by-month box plot distributions across May–August |
| `feature_target_kde.png` | Density plots of features split by completion vs. failure |
| `failure_rate_by_feature_bucket.png` | Failure rates across distance, surge, fare, and ETA buckets |
| `confounder_hour_surge_failure.png` | Temporal confounding between hour, surge, and failure rate |
| `confounder_zone_eta_failure.png` | Geographical confounding between pickup zones, ETA, and failure |
| `correlation_matrix.png` | Full correlation heatmap including one-hot encoded categorical controls |

---

*Report prepared and validated for CairoGo ML Assignment — Phase 1.*
