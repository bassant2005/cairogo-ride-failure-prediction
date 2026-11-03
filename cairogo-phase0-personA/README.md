# CairoGo — Ride Request Failure Prediction

A team machine-learning project focused on understanding and predicting failed ride requests.

> **Target variable:** `request_failed` (confirm the exact spelling and meaning against the supplied dataset/project brief before modeling).

## Project objectives
- Understand the business problem and prediction point.
- Audit and prepare the supplied dataset.
- Build and evaluate classification models.
- Compare model performance using metrics appropriate for failed-request detection.

## Repository structure

```text
cairogo-ride-failure-prediction/
├── data/
│   ├── raw/                 # Original data; do not commit private/large datasets
│   └── processed/           # Reproducible cleaned/intermediate data
├── docs/                    # Project brief, decisions, data dictionary
├── notebooks/               # Exploratory analysis and experiments
├── reports/
│   └── figures/             # Exported plots used in reports
├── models/                  # Saved model artifacts (usually not committed)
├── src/                     # Reusable project code
├── tests/                   # Tests for reusable code
├── .gitignore
├── CONTRIBUTING.md
└── requirements.txt
```

## Getting started

### 1. Clone the repository
```bash
git clone <REPOSITORY_URL>
cd cairogo-ride-failure-prediction
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Add the dataset
Place the authorized project dataset in `data/raw/`. Keep the original file unchanged.
Do not commit private, restricted, or large dataset files unless the course/project rules explicitly permit it.

### 5. Start Jupyter
```bash
jupyter notebook
```

Open the notebooks in `notebooks/`.

## Team workflow
1. Pull the latest `main` branch before starting work.
2. Create a separate branch for each task, for example `phase1/person-a-data-audit`.
3. Make focused commits with clear messages.
4. Push the branch and open a Pull Request.
5. Ask another team member to review the changes.
6. Merge into `main` only after review and resolving conflicts.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Reproducibility rules
- Use the same agreed train/validation/test split across model comparisons.
- Fit preprocessing steps on training data only; apply the fitted transformations to validation/test data.
- Prevent target leakage: only use information available at the intended prediction time.
- Record random seeds, data versions, parameters, and evaluation metrics.
- Never overwrite the original raw dataset.

## Team
Add all four members' names and GitHub usernames here.

## Project status
- [ ] Phase 0 — Repository and environment setup
- [ ] Phase 1 — Data understanding and audit
- [ ] Phase 2 — Feature engineering and model training
