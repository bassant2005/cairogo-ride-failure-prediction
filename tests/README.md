# Tests

Unit and integration tests for reusable preprocessing, data-cleaning, and feature-engineering modules in `src/`.

## Running the tests

Run all tests in `tests/` using `pytest`

```bash
python -m pytest tests -v
```
## Expected output

Run `python -m pytest tests -v` to verify all unit and integration suites.

## Current test suites

- `tests/test_data_corrections.py` — Unit tests (`TestZoneCorrectionsUnit`) and Pack v17 dataset integration/invariant tests (`TestZoneCorrectionsIntegration`) for `src/data_corrections.py` (zone name standardization, immutability, idempotency, error handling, and 0% join loss with `zones.csv`).
- `tests/test_data_validation.py` — Unit tests (`TestDataValidationUnit`) and dataset integration tests (`TestDataValidationIntegration`) for `src/data_validation.py` (dtype standardization, duplicate removal, schema verification, primary key uniqueness, numeric range checks, immutability, and idempotency).
