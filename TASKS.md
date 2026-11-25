# CairoGo — Project Task Tracker

> **Deadline:** 10 December 2026 — 23:59 Cairo Time
> **Pack Version:** v17 | **Leader ID:** 20231067
> **Repository:** `bassant2005/cairogo-ride-failure-prediction`

---

## Team Roster

| Member | Person | Student ID | GitHub |
|---|---|---|---|
| **Rawda Raafat Ramadan** (Leader) | Person D | 20231067 | `rawdaraafat` |
| **Mariam Ehab Hassan** | Person A | 20231160 | `Marria-m` |
| **Rahma Bahgat** | Person B | 20231056 | `RahmaBahgat` |
| **Bassant Tarek** | Person C | 20231037 | `bassant2005` |

---

## Phase 0 — Environment Setup & Initial Ingestion

| Task | Owner | Status | Notes |
|---|---|---|---|
| Initialize private GitHub repository | Bassant | ✅ Done | `bassant2005/cairogo-ride-failure-prediction` |
| Project directory structure setup | Bassant | ✅ Done | `data`, `docs`, `notebooks`, `src`, `models`, `reports` |
| Python environment & dependencies | Team | ✅ Done | Python 3.11, `requirements.txt` |
| Review project brief & starter notebooks | Team | ✅ Done | `CairoGo_Assignment_V4.pdf`, starters, contracts |
| Extract Pack v17 & common assets | Team | ✅ Done | `data/raw/CairoGo_pack_v17/` and `data/raw/common/` |
| Data Dictionary (`docs/DATA_DICTIONARY.md`) | Team | ✅ Done | |
| Project Decisions Log (`docs/PROJECT_DECISIONS.md`) | Team | ✅ Done | |
| Task Tracker (`TASKS.md`) | Team | ✅ Done | This file |
| Team roster in `README.md` | Team | ✅ Done | |

---

## Phase 1 — Data Understanding & Audit
**Goal:** Identify and document all data quality problems before modelling. Parallel work, 5–6 days.

### Task 1a — Join Loss & Zone Mapping (Person A: Mariam)

| Step | Status | Branch | Notes |
|---|---|---|---|
| Identify unmatched `pickup_zone` values vs `zones.csv` | ✅ Done | `phase1/data-joins` | 3 legacy zones found |
| Quantify fraction of affected records | ✅ Done | `phase1/data-joins` | `join.unmatched_before = 0.1148` |
| Build `legacy_name → zone_name` mapping | ✅ Done | `phase1/data-joins` | From `zones.csv` |
| Apply fix to `pickup_zone` and `dropoff_zone` | ✅ Done | `phase1/data-joins` | 0 unmatched remaining |
| Full merge: trips + zones + customers + drivers | ✅ Done | `phase1/data-joins` | Shape `(28244, 29)` |
| Export `data/processed/trips_cleaned.csv` | ✅ Done | `phase1/data-joins` | |
| Audit report (`docs/TASK_1A_REPORT.md` + `.html`) | ✅ Done | `phase1/data-joins` | |
| Reusable functions (`src/data_cleaning.py`) | ✅ Done | `phase1/data-joins` | `fix_zone_names`, `integrate_trips_data` |
| Notebook (`notebooks/02_data_audit.ipynb`) | ✅ Done | `phase1/data-joins` | |

**Results:**
- `join.unmatched_before`: `0.1148`
- `join.unmatched_zones`: `['Badr City', 'Dokki', 'New Cairo']`
- `join.fix`: Replaced via `legacy_name → zone_name` mapping from `zones.csv`

---

### Task 1b — Unit Shift & Confounding (Person B: Rahma)

| Step | Status | Branch | Notes |
|---|---|---|---|
| Identify which field changed its unit (`est_fare` or `distance_km`) | ⬜ TODO | `phase1/B-unit-shift` | |
| Detect the date of the app version change | ⬜ TODO | `phase1/B-unit-shift` | |
| Compute global slope: minutes per km (all completed trips) | ⬜ TODO | `phase1/B-confounding` | Required for `confounding.global_slope` |
| Find the confounder variable driving both distance and trip time | ⬜ TODO | `phase1/B-confounding` | Required for `confounding.confounder` |
| Compute within-group slopes to compare vs global | ⬜ TODO | `phase1/B-confounding` | Required for `confounding.within_slope` |
| Document impact on modelling and populate `results.json` blocks | ⬜ TODO | `phase1/B-unit-shift` | `shift.*` and `confounding.*` |

---

### Task 1c — Target Leakage Analysis (Person C: Bassant)

| Step | Status | Branch | Notes |
|---|---|---|---|
| Identify all post-request columns (from `data_dictionary.md`) | ⬜ TODO | `phase1/C-leakage` | |
| Confirm which columns are unavailable at request time | ⬜ TODO | `phase1/C-leakage` | `actual_trip_time_min`, `cancel_reason`, `driver_arrival_min`, `support_ticket_flag` |
| Compute single-feature AUC for each leaking column | ⬜ TODO | `phase1/C-leakage` | Required for `leakage.single_feature_auc` |
| Verify no valid request-time feature is mistakenly removed | ⬜ TODO | `phase1/C-leakage` | |
| Populate `leakage.columns_removed` and `leakage.single_feature_auc` in `results.json` | ⬜ TODO | `phase1/C-leakage` | |

---

### Task 2 — Missingness Analysis / MNAR (Person D: Rawda)

| Step | Status | Branch | Notes |
|---|---|---|---|
| Compute missing share for `weather` and `driver.rating_avg` | ⬜ TODO | `phase1/D-missingness` | |
| Compare failure rate: rows with vs without `weather` value | ⬜ TODO | `phase1/D-missingness` | Required for `mnar.weather_missing_fail_diff` |
| Compare failure rate: rows with vs without `rating_avg` | ⬜ TODO | `phase1/D-missingness` | Required for `mnar.rating_missing_fail_diff` |
| Decide: MNAR (informative) or MCAR (random) for each field | ⬜ TODO | `phase1/D-missingness` | Required for `mnar.interpretation` |
| Propose handling strategy for each missing field | ⬜ TODO | `phase1/D-missingness` | |
| Populate `mnar.*` block in `results.json` | ⬜ TODO | `phase1/D-missingness` | |

---

### Phase 1 Review & Merge Meeting (All)

| Step | Status | Notes |
|---|---|---|
| All four members open Pull Requests for review | ⬜ TODO | Each on their own branch |
| Team meeting: cross-check findings (leakage vs features, zone fix vs other columns) | ⬜ TODO | |
| Agree on final Data Preparation Strategy before Phase 2 | ⬜ TODO | |
| Merge all Phase 1 branches into `main` | ⬜ TODO | After PR review and approval |

---

## Phase 2 — Feature Engineering & Model Training
**Goal:** Build a leakage-free feature pipeline and train all required models on a shared time-based split. Parallel experiments, 7–8 days.

### 2.1 — Shared Feature Engineering (All Members)

| Step | Status | Branch | Notes |
|---|---|---|---|
| Agree on final feature set (numerical, categorical, time, location) | ⬜ TODO | `phase2/feature-pipeline` | |
| Define encoding and scaling strategy | ⬜ TODO | `phase2/feature-pipeline` | |
| Agree on missing value imputation strategy | ⬜ TODO | `phase2/feature-pipeline` | |
| Build shared `ColumnTransformer` pipeline (fit on train only) | ⬜ TODO | `phase2/feature-pipeline` | |

### 2.2 — Time-Based Train / Validation Split (All Members)

| Step | Status | Notes |
|---|---|---|
| Define time-ordered split using `request_ts` | ⬜ TODO | `trips.csv` = train; `recent_labelled.csv` = validation |
| Confirm all models use the same split | ⬜ TODO | No random splitting allowed |

### 2.3 — Model Training (Parallel)

| Task | Owner | Status | Branch | Notes |
|---|---|---|---|---|
| **Logistic Regression** (baseline) | Mariam (A) | ⬜ TODO | `phase2/A-logistic` | Regularization variants, AUC, Recall@15%, Brier, cost |
| **Gradient Boosted Trees** (`hgb`) | Rahma (B) | ⬜ TODO | `phase2/B-boosting` | `HistGradientBoostingClassifier`, Feature Importance |
| **kNN** (scaled and unscaled) | Bassant (C) | ⬜ TODO | `phase2/C-knn` | Fixed k via CV; `knn_scaling` decision |
| **MLPClassifier** (early stopping) | Rawda (D) | ⬜ TODO | `phase2/D-mlp` | With/without scaling; `nn_scaling`, `nn_decision` |

### 2.4 — Additional Required Tasks (All)

| Task | Owner | Status | Branch | Notes |
|---|---|---|---|---|
| **Local-k Research** | All | ⬜ TODO | `phase2/local-k` | Per `LOCAL_K_NOTES.md`; `local_k.*` block |
| **Customer Segmentation** (K-Means) | All | ⬜ TODO | `phase2/segmentation` | k ∈ [2,10]; `segments.csv`; `segmentation.*` block |
| **Model Benchmarking** | All | ⬜ TODO | `phase2/model-eval` | Populate `validation.*` in `results.json` |
| **Holdout Predictions** | All | ⬜ TODO | — | Generate `holdout_predictions.csv` |
| **Reviews NLP** (Task 7) | All | ⬜ TODO | `phase2/reviews-nlp` | Naive Bayes vs SVM; `review_disagreements.*` |
| **Recent Period Repair** (Task 6) | All | ⬜ TODO | `phase2/recent-fix` | Diagnose drift in `recent_labelled.csv`; `investigation.*` |
| **Reproducible `predict.py`** (Task 8) | Mariam (A) | ⬜ TODO | `phase3/predict` | Per `PREDICT_CONTRACT.md`; includes zone fix |

---

## Phase 3 — Decision Layer & Business Optimization
**Goal:** Convert predictions into actionable decisions within capacity (15%) and budget (3 EGP/request). 3 days.

### 3.1 — All Members Review

| Task | Status |
|---|---|
| Read `DECISION_NOTES.md`, `DECISION_RULES.json`, `policy.py` starter, `build_history.py` | ⬜ TODO |

### 3.2 — Task Distribution (Parallel)

| Task | Owner | Status | Branch | Notes |
|---|---|---|---|---|
| **Policy Implementation** — `policy.py` TODOs, benefit formula, action selection | Mariam (A) | ⬜ TODO | `phase3/A-policy` | |
| **Policy Baselines** — no-action, top-15% contact, cost-aware | Rahma (B) | ⬜ TODO | `phase3/B-baselines` | |
| **Segment-Informed Decisions** — compare segment vs segment-free | Bassant (C) | ⬜ TODO | `phase3/C-segments` | `decision.segments_analysis.*` |
| **Decision Evaluation** — calibration, uncertainty, zone-type miss rate | Rawda (D) | ⬜ TODO | `phase3/D-evaluation` | `decision.calibration.*`, `decision.uncertainty.*`, `decision.error_by_group.*` |

### 3.3 — Integration & Validation (All)

| Task | Status | Notes |
|---|---|---|
| Run `build_history.py` → produce `customer_history.csv` | ⬜ TODO | |
| Run `policy.py` on holdout predictions → produce `decisions.csv` | ⬜ TODO | |
| Verify capacity (≤ 15%) and budget (≤ 3 EGP × n) | ⬜ TODO | |
| Populate `decision.*` block in `results.json` | ⬜ TODO | |

---

## Phase 4 — Service, Dashboard & Final Submission
**Goal:** Package the finished model into a working API, Docker container, and dashboard. 4 days + 2 days for review.

### 4.1 — Part 3: FastAPI & Docker (Team)

| Task | Owner | Status | Branch | Notes |
|---|---|---|---|---|
| **FastAPI Integration** — `service/app.py`, `/predict`, `/decide` endpoints | Mariam (A) | ⬜ TODO | `phase4/A-fastapi` | Per `SERVICE_NOTES.md` |
| **Docker & Testing** — `Dockerfile`, build & run, `test_request.py` | Rahma (B) | ⬜ TODO | `phase4/B-docker` | |
| **Streamlit Dashboard** — risk view, actions, budget, segments | Bassant (C) | ⬜ TODO | `phase4/C-dashboard` | Per starter in `dashboard_starter/` |
| **Dashboard Validation** — `summary.json`, screenshot, `README_SERVICE.md` | Rawda (D) | ⬜ TODO | `phase4/D-docs` | `dashboard.png` required |

### 4.2 — Part 4: Personal Decision Memo (Individual — Each Alone)

| Member | Memo File | Data Slice | Status |
|---|---|---|---|
| Mariam Ehab (A) — ID 20231160 | `memo_4.md` (1160 % 6 = 2 → check formula) | (1160 // 6) % 4 | ⬜ TODO |
| Rahma Bahgat (B) — ID 20231056 | `memo_0.md` (1056 % 6 = 0) | (1056 // 6) % 4 | ⬜ TODO |
| Bassant Tarek (C) — ID 20231037 | `memo_1.md` (1037 % 6 = 1) | (1037 // 6) % 4 | ⬜ TODO |
| Rawda Raafat (D) — ID 20231067 | `memo_1.md` (1067 % 6 = 1) | (1067 // 6) % 4 | ⬜ TODO |

> Each member opens their own `memo_k.md`, extracts 3 numeric findings, identifies the flaw, and writes decision in `memo.yaml`. **No sharing.**

---

## Final Submission Checklist

### Individual ZIP: `I_<studentID>.zip` (each member separately)

| File | Required | Status |
|---|---|---|
| `foundation.ipynb` | ✅ | ⬜ TODO |
| `foundation_answers.json` | ✅ | ⬜ TODO |
| `memo.yaml` | ✅ | ⬜ TODO |

### Team ZIP: `T_20231067.zip` (Rawda uploads once)

| File / Folder | Required | Status |
|---|---|---|
| `results.json` | ✅ | 🔄 In Progress (`join.*` done) |
| `team_analysis.ipynb` | ⬜ TODO |
| `holdout_predictions.csv` | ⬜ TODO |
| `segments.csv` | ⬜ TODO |
| `team.csv` | ⬜ TODO |
| `predict.py` + model files | ⬜ TODO |
| `README.md` | ✅ Done |
| `decisions.csv` | ⬜ TODO |
| `policy.py` | ⬜ TODO |
| `DECISION_RULES.json` (unchanged) | ⬜ TODO |
| `customer_history.csv` | ⬜ TODO |
| `service/app.py` | ⬜ TODO |
| `service/Dockerfile` | ⬜ TODO |
| `service/requirements.txt` | ⬜ TODO |
| `service/test_request.py` | ⬜ TODO |
| `service/README_SERVICE.md` | ⬜ TODO |
| `dashboard/app.py` or `index.html` | ⬜ TODO |
| `dashboard/summary.json` | ⬜ TODO |
| `dashboard/dashboard.png` |⬜ TODO |
| Run `check_submission.py` → OK | ⬜ TODO |
| Upload by **10 Dec 2026 at 23:59** | ⬜ TODO |
