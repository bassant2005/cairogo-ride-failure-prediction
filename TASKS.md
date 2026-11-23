# CairoGo — Task Tracker

> Deadline: **10 December 2026** — 23:59 Cairo time
> Pack: **v17** | Leader ID: **20231067**

---

## 🟢 Phase 0 — Setup & Understanding (2–3 days)

| Task | Owner | Status | Notes |
|---|---|---|---|
| إنشاء GitHub Repository | A | ✅ Done | bassant2005/cairogo-ride-failure-prediction |
| تنظيم folder structure | A | ✅ Done | |
| تجهيز Python environment | B | ✅ Done | Python 3.14, all libs installed |
| مراجعة starter notebooks | C | ✅ Done | Part0_Foundations_starter.ipynb + team_analysis_starter.ipynb |
| استخراج Dataset (Pack v17) | — | ✅ Done | data/raw/cairogo_pack + foundation + common |
| Data Dictionary | D | ✅ Done | docs/DATA_DICTIONARY.md |
| Project Decisions Log | D | ✅ Done | docs/PROJECT_DECISIONS.md |
| Task Tracker | D | ✅ Done | هذا الملف |
| أسماء الفريق في README.md | A | ⬜ TODO | |
| `01_data_overview.ipynb` | All | ⬜ TODO | Phase 0.2 |
| Git branching strategy | A | ⬜ TODO | اعمل branch لكل phase |

---

## 🔵 Phase 1 — Data Understanding & Audit

| Task | Owner | Status | Branch |
|---|---|---|---|
| EDA على trips.csv | B | ⬜ TODO | `phase1/B-eda-trips` |
| Missing values analysis | D | ✅ Done | `phase1/person-d-missingness` |
| Join trips + customers + drivers + zones | A | ⬜ TODO | `phase1/A-data-joins` |
| Leakage audit — confirm forbidden columns | C | ⬜ TODO | `phase1/person-c-data-audit` |
| Target distribution & class imbalance | B | ⬜ TODO | `phase1/B-target-dist` |
| Temporal analysis (request_ts) | C | ⬜ TODO | `phase1/C-temporal` |
| Data cleaning strategy (team agreement) | All | ⬜ TODO | PR review |

---

## 🟡 Phase 2 — Feature Engineering & Modeling (Team notebook)

| Task | Owner | Status | Branch |
|---|---|---|---|
| Feature engineering pipeline | A+B | ⬜ TODO | `phase2/feature-engineering` |
| Baseline model (Logistic Regression) | A | ⬜ TODO | `phase2/A-logistic-regression` |
| Decision Tree / Random Forest | B | ⬜ TODO | `phase2/B-tree-models` |
| Gradient Boosting (XGBoost/LightGBM) | C | ⬜ TODO | `phase2/C-boosting` |
| Neural Network | D | ⬜ TODO | `phase2/D-neural-network` |
| Local-k kNN (research task) | All | ⬜ TODO | `phase2/local-k` |
| Customer segmentation (K-means) | B+C | ⬜ TODO | `phase2/segmentation` |
| Model comparison & evaluation | All | ⬜ TODO | `phase2/model-comparison` |
| Holdout predictions (holdout_predictions.csv) | All | ⬜ TODO | |

---

## 🟠 Phase 3 — Decision Layer & Service

| Task | Owner | Status | Branch |
|---|---|---|---|
| policy.py + DECISION_RULES.json | C | ⬜ TODO | `phase3/policy` |
| customer_history.csv (build_history.py) | B | ⬜ TODO | `phase3/customer-history` |
| predict.py (inference script) | A | ⬜ TODO | `phase3/predict-script` |
| FastAPI service (service/app.py) | D | ⬜ TODO | `phase3/service` |
| Dashboard (Streamlit) | B+C | ⬜ TODO | `phase3/dashboard` |
| results.json + segments.csv | All | ⬜ TODO | |
| check_submission.py — final check | All | ⬜ TODO | |

---

## 📦 Final Submission

| Item | Status |
|---|---|
| `I_20231067.zip` (Individual — Foundation) | ⬜ TODO |
| `T_20231067.zip` (Team) | ⬜ TODO |
| Run `check_submission.py` on both | ⬜ TODO |
| Upload by 10 Dec 2026 23:59 | ⬜ TODO |

---

## 👥 Team Members

| Member | Student ID | GitHub | Role |
|---|---|---|---|
| Leader | 20231067 | bassant2005 | Repo owner + coordination |
| Member B | — | — | |
| Member C | — | — | |
| Member D | — | — | |

> عدّل الجدول بأسماء وـ IDs الفريق كله.
