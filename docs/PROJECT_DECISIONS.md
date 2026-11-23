# Project Decisions Log

> سجّل هنا كل قرار بيتاخد. ممنوع تغيّر افتراض مشترك من غير ما تضيفه هنا.

| Date | Decision | Reason | Agreed by |
|---|---|---|---|
| 2026-11-21 | Pack version = v17 | Leader ID 20231067 → 1067 % 25 = 17 | Team |
| 2026-11-21 | Repo structure: data/raw, processed, notebooks, src, models, reports, docs, tests | Standard ML project layout | Team |
| 2026-11-21 | Data files NOT committed to Git (in .gitignore) | Privacy + file size | Team |
| 2026-11-21 | Target variable: `request_failed` (1 = failed, 0 = completed) | data_dictionary.md | Team |
| 2026-11-21 | Prediction point: at_request — only features with recorded_at = "at_request" allowed | Prevent data leakage | Team |
| 2026-11-21 | LEAKAGE columns (never use as features): actual_trip_time_min, cancel_reason, driver_arrival_min, support_ticket_flag | recorded_at = after_decision or after_completion | Team |
| 2026-11-21 | Train set: trips.csv — Validation set: recent_labelled.csv (forward-in-time) | Temporal split prevents leakage | Team |
| 2026-11-21 | Branch naming: phase0/, phase1/, phase2/, fix/ | CONTRIBUTING.md | Team |
| 2026-11-21 | Random seed = 42 for all splits and models | Reproducibility | Team |
| 2026-11-21 | Variable naming: snake_case for all Python variables and column names | Consistency | Team |
| 2026-11-21 | Notebook naming: 01_data_overview, 02_data_audit, 03_feature_engineering, 04_model_*, 05_model_comparison | notebooks/README.md | Team |
| 2026-11-24 | Weather missingness handled as distinct category ('missing') | Task 2 Missingness Analysis: missing weather has +4.06% higher failure rate (informative / MNAR) | Team / Person D |
| 2026-11-24 | Driver rating_avg handled via median imputation + missingness indicator flag (`rating_avg_is_missing`) | Task 2 Missingness Analysis: unrated drivers have +5.04% higher failure rate (informative / MNAR) | Team / Person D |

---

## Items confirmed from official project brief

- [x] Target column: `request_failed` — positive class = 1 (failed)
- [x] Prediction point: at time of ride request (at_request features only)
- [x] Dataset: Pack v17 — not to be committed (private)
- [x] Train/val strategy: trips.csv (train) → recent_labelled.csv (validation, forward-in-time)
- [x] Holdout: holdout_inputs.csv (2,767 rows) — submit predictions as holdout_predictions.csv
- [x] Missingness audit (Task 2): weather and driver rating_avg are informative (MNAR)
- [ ] Required evaluation metrics — to confirm from CairoGo_Assignment.pdf
- [ ] Required models — to confirm from CairoGo_Assignment.pdf

---

## Open Questions

| Question | Status |
|---|---|
| هل ممكن نستخدم features من customers/drivers/zones كـ join مع trips؟ | ✅ نعم — مسموح |
| rating_avg فيها missing — نعمل إيه؟ | ✅ Impute with train median + binary indicator `rating_avg_is_missing` |
| weather فيها 4.5% missing — نعمل إيه؟ | ✅ Include 'missing' as distinct category level in one-hot encoding |
