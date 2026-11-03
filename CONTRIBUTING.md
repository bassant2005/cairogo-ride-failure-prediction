# Team Contribution Guide

## Branch naming
Use:
- `phase0/<short-task>`
- `phase1/<short-task>`
- `phase2/<short-task>`
- `fix/<short-description>`

Examples:
- `phase0/repository-setup`
- `phase1/missingness-audit`
- `phase2/logistic-regression`

## Commit messages
Use short, descriptive messages:
- `docs: add project overview`
- `chore: add Python dependencies`
- `feat: add missing-value analysis`
- `fix: correct target label handling`

## Pull requests
Every Pull Request should include:
1. What changed.
2. Why it changed.
3. Files/notebooks affected.
4. How the work was checked.
5. Any known limitations.

At least one teammate should review the Pull Request before merging.

## Notebook practices
- Give notebooks descriptive names, e.g. `01_data_overview.ipynb`.
- Keep notebooks focused on one task.
- Restart the kernel and run all cells before submitting.
- Remove unnecessary output and avoid committing huge embedded outputs.
- Move reusable functions into `src/` when appropriate.

## Data and privacy
- Do not commit secrets, credentials, or restricted data.
- Keep the original raw dataset unchanged.
- Do not upload data to external services unless permitted by the project rules.
