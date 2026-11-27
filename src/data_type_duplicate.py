"""
Data types and duplicate validation module — Bassant Tarek (Person C).

Reusable transformations and schema checks extracted from
notebooks/07_data_types_validation.ipynb for Section 4 of
notebooks/06_data_cleaning.ipynb:
  1. fix_dtypes(df)        — Standardize IDs, datetimes, numeric, and categorical dtypes
  2. drop_duplicates(df)   — Remove exact duplicate rows and report count removed
  3. verify_types(df)      — Assert all known columns match the expected schema
  4. check_duplicate_ids   — Count (or assert 0) duplicate primary key values
  5. validate_numeric_ranges — Run domain range checks on numeric columns
  6. apply_all_validation  — Run fix_dtypes, drop_duplicates, and verify_types
"""

from typing import Callable, Dict, Optional, Sequence, Tuple
import pandas as pd

ID_COLUMNS: Tuple[str, ...] = ("trip_id", "customer_id", "driver_id", "zone_id")
DATETIME_COLUMNS: Tuple[str, ...] = ("request_ts", "signup_date", "join_date")
FLOAT_COLUMNS: Tuple[str, ...] = (
    "distance_km",
    "surge_multiplier",
    "est_fare",
    "eta_estimate_min",
    "actual_trip_time_min",
    "driver_arrival_min",
    "rating_avg",
)
INT_COLUMNS: Tuple[str, ...] = (
    "request_failed",
    "support_ticket_flag",
    "experience_months",
    "has_metro",
)
CATEGORICAL_COLUMNS: Tuple[str, ...] = (
    "pickup_zone",
    "dropoff_zone",
    "weather",
    "payment_method",
    "service_level",
    "cancel_reason",
    "channel",
    "loyalty_tier",
    "vehicle_type",
    "zone_type",
    "home_zone",
    "customer_home_zone",
    "driver_home_zone",
)

NUMERIC_RANGE_RULES: Dict[str, Callable[[pd.Series], pd.Series]] = {
    "distance_km": lambda s: s <= 0,
    "surge_multiplier": lambda s: s < 1,
    "est_fare": lambda s: s <= 0,
    "eta_estimate_min": lambda s: s <= 0,
    "actual_trip_time_min": lambda s: s <= 0,
    "driver_arrival_min": lambda s: s <= 0,
    "experience_months": lambda s: s < 0,
    "rating_avg": lambda s: (s < 1) | (s > 5),
}


def _ensure_dataframe(df: pd.DataFrame) -> None:
    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"Expected a pandas DataFrame, got {type(df).__name__}.")


def fix_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize identifier, datetime, numeric, and categorical column dtypes."""
    _ensure_dataframe(df)
    out = df.copy(deep=True)

    for col in ID_COLUMNS:
        if col in out.columns:
            out[col] = out[col].astype("string")

    for col in DATETIME_COLUMNS:
        if col in out.columns:
            non_null = out[col].notna()
            parsed = pd.to_datetime(out[col], errors="coerce")
            invalid_count = int((non_null & parsed.isna()).sum())
            if invalid_count > 0:
                raise ValueError(
                    f"Column '{col}' contains {invalid_count} invalid datetime value(s)."
                )
            out[col] = parsed

    for col in FLOAT_COLUMNS:
        if col in out.columns:
            try:
                out[col] = pd.to_numeric(out[col], errors="raise").astype("float64")
            except (ValueError, TypeError) as exc:
                raise ValueError(
                    f"Column '{col}' could not be cast to float64."
                ) from exc

    for col in INT_COLUMNS:
        if col in out.columns:
            try:
                numeric = pd.to_numeric(out[col], errors="raise")
            except (ValueError, TypeError) as exc:
                raise ValueError(
                    f"Column '{col}' could not be cast to integer."
                ) from exc

            non_null = numeric.dropna()
            if len(non_null) > 0 and ((non_null % 1) != 0).any():
                raise ValueError(
                    f"Column '{col}' contains non-integer fractional values."
                )

            out[col] = (
                numeric.astype("Int64")
                if numeric.isna().any()
                else numeric.astype("int64")
            )

    for col in CATEGORICAL_COLUMNS:
        if col in out.columns:
            out[col] = out[col].astype("category")

    return out


def drop_duplicates(
    df: pd.DataFrame,
    subset: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    """Remove exact duplicate rows (or duplicates on subset) and print count removed."""
    _ensure_dataframe(df)
    if subset is not None:
        missing = [col for col in subset if col not in df.columns]
        if missing:
            raise ValueError(f"Subset columns not found in DataFrame: {missing}")

    n_before = len(df)
    out = df.drop_duplicates(subset=subset, keep="first").reset_index(drop=True)
    n_removed = n_before - len(out)
    print(f"Exact duplicate rows removed: {n_removed} (rows: {n_before} -> {len(out)})")
    return out


def verify_types(df: pd.DataFrame) -> None:
    """Assert that all recognized columns in df match the expected schema dtypes."""
    _ensure_dataframe(df)
    assert len(df.columns) > 0, "DataFrame has no columns to verify."

    for col in ID_COLUMNS:
        if col in df.columns:
            assert str(df[col].dtype) == "string", (
                f"Expected column '{col}' to have dtype 'string', got '{df[col].dtype}'."
            )

    for col in DATETIME_COLUMNS:
        if col in df.columns:
            assert pd.api.types.is_datetime64_any_dtype(df[col]), (
                f"Expected column '{col}' to be datetime64, got '{df[col].dtype}'."
            )

    for col in FLOAT_COLUMNS:
        if col in df.columns:
            assert pd.api.types.is_float_dtype(df[col]), (
                f"Expected column '{col}' to be float64, got '{df[col].dtype}'."
            )

    for col in INT_COLUMNS:
        if col in df.columns:
            assert pd.api.types.is_integer_dtype(df[col]), (
                f"Expected column '{col}' to be integer, got '{df[col].dtype}'."
            )

    for col in CATEGORICAL_COLUMNS:
        if col in df.columns:
            assert isinstance(df[col].dtype, pd.CategoricalDtype), (
                f"Expected column '{col}' to be 'category', got '{df[col].dtype}'."
            )

    print("All column dtypes verified successfully.")


def check_duplicate_ids(
    df: pd.DataFrame,
    id_col: str = "trip_id",
    raise_on_duplicates: bool = False,
) -> int:
    """Return the count of duplicate values in id_col, optionally asserting zero."""
    _ensure_dataframe(df)
    if id_col not in df.columns:
        raise ValueError(f"Primary key column '{id_col}' not found in DataFrame.")

    dup_count = int(df[id_col].duplicated().sum())
    if raise_on_duplicates:
        assert dup_count == 0, (
            f"Column '{id_col}' has {dup_count} duplicate identifier(s)."
        )
    return dup_count


def validate_numeric_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """Evaluate domain range rules on present numeric columns and return a summary."""
    _ensure_dataframe(df)
    results = []
    for col, invalid_rule in NUMERIC_RANGE_RULES.items():
        if col not in df.columns:
            continue
        series = pd.to_numeric(df[col], errors="coerce")
        invalid_count = int(invalid_rule(series).fillna(False).sum())
        results.append(
            {
                "Column": col,
                "Invalid_Values": invalid_count,
                "Status": "Passed" if invalid_count == 0 else "Needs Investigation",
            }
        )
    return pd.DataFrame(results, columns=["Column", "Invalid_Values", "Status"])


def apply_all_validation(df: pd.DataFrame) -> pd.DataFrame:
    """Apply dtype standardization, duplicate removal, and schema verification."""
    out = fix_dtypes(df)
    out = drop_duplicates(out)
    verify_types(out)
    return out
