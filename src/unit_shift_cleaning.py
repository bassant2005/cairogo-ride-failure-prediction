"""
CairoGo — Unit Shift & Confounder Cleaning Module
Phase 1: Data Cleaning Pipeline
Author: Rahma Bahgat (Person B — ID: 20231056)

Addresses Person B's Phase 1 Data Audit findings (Task 1b & Task 1d):
1. Unit Shift Repair (`est_fare` piasters -> EGP):
   - In `trips.csv` (2026-05-01 to 2026-08-30), `est_fare` is recorded in EGP
     (median ~90.10 EGP; median fare/km ~9.33 EGP/km, max ~77.43 EGP/km).
   - Starting 2026-08-31 (`recent_labelled.csv` and `holdout_inputs.csv`), an app
     release changed `est_fare` units to piasters/qirsh (x100; median ~9,090-9,190,
     minimum fare/km ~482.27 EGP/km).
   - Calibrates a train-only `fare_per_km` scale threshold from `trips.csv` and
     normalizes shifted fares back to EGP (`/ 100.0`) idempotently.
2. Data Types & Temporal Confounder Extraction:
   - Parses `request_ts` to `datetime64[ns]`, validates numerical dtypes
     (`distance_km`, `surge_multiplier`, `est_fare`, `eta_estimate_min`), and
     extracts `hour`, `day_of_week`, `month` (required to control for `hour` as
     a confirmed confounder of `surge_multiplier`).
3. Confounder Context Preparation:
   - Attaches `pickup_zone_type` and `pickup_has_metro` from `zones.csv` (controlling
     for Simpson's Paradox in `actual_trip_time_min ~ distance_km`, where global
     slope is -0.1856 min/km while within-`zone_type` slope is +0.5067 min/km).
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

NUMERICAL_FEATURES: List[str] = [
    "distance_km",
    "surge_multiplier",
    "est_fare",
    "eta_estimate_min",
]

UNIT_SHIFT_FIELD: str = "est_fare"
UNIT_SHIFT_DATE: str = "2026-08-31"
UNIT_SHIFT_FACTOR: float = 100.0
DEFAULT_FARE_PER_KM_THRESHOLD: float = 200.0
FALLBACK_EST_FARE_THRESHOLD: float = 1500.0

CONFIRMED_CONFOUNDERS: Dict[str, Dict[str, str]] = {
    "pickup_zone_type": {
        "task": "Task 1d (Simpson's Paradox)",
        "confounds": "distance_km -> actual_trip_time_min",
        "effect": "Global slope -0.1856 min/km vs within-zone_type +0.5067 min/km",
    },
    "service_level": {
        "task": "Person B Failure Audit",
        "confounds": "distance_km -> request_failed",
        "effect": "Change-in-Estimate delta_beta = +28.47%",
    },
    "hour": {
        "task": "Person B Failure Audit",
        "confounds": "surge_multiplier -> request_failed",
        "effect": "Change-in-Estimate delta_beta = +15.30%",
    },
    "pickup_zone": {
        "task": "Person B Failure Audit",
        "confounds": "eta_estimate_min -> request_failed",
        "effect": "Change-in-Estimate delta_beta = -19.29%",
    },
}


def _compute_fare_per_km(df: pd.DataFrame) -> pd.Series:
    """Compute est_fare / distance_km safely, returning NaN where distance <= 0."""
    dist = pd.to_numeric(df["distance_km"], errors="coerce")
    fare = pd.to_numeric(df["est_fare"], errors="coerce")
    valid = (dist > 0) & dist.notna() & fare.notna()
    ratio = pd.Series(np.nan, index=df.index, dtype="float64")
    ratio.loc[valid] = fare.loc[valid] / dist.loc[valid]
    return ratio


def _ols_slope(x: np.ndarray, y: np.ndarray) -> float:
    """Return OLS slope cov(x, y) / var(x) for 1D arrays."""
    x_arr = np.asarray(x, dtype="float64")
    y_arr = np.asarray(y, dtype="float64")
    mask = np.isfinite(x_arr) & np.isfinite(y_arr)
    x_valid, y_valid = x_arr[mask], y_arr[mask]
    if len(x_valid) < 2:
        return float("nan")
    x_centered = x_valid - x_valid.mean()
    denom = float(np.sum(x_centered ** 2))
    if denom == 0.0:
        return float("nan")
    return float(np.sum(x_centered * (y_valid - y_valid.mean())) / denom)


def _lookup_standard_zone(series: pd.Series, zones_df: pd.DataFrame) -> pd.Series:
    """Map legacy_name -> zone_name for joins without altering the source column."""
    if "legacy_name" not in zones_df.columns or "zone_name" not in zones_df.columns:
        return series
    mapping = zones_df.set_index("legacy_name")["zone_name"].to_dict()
    return series.replace(mapping)


def coerce_person_b_dtypes(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Standardize `request_ts` to datetime64 and audited numerical features to float64.

    Does not mutate the input DataFrame.
    """
    out = df.copy()
    report: Dict[str, Any] = {"request_ts_coerced_nat": 0, "numerical": {}}

    if "request_ts" in out.columns:
        was_notna = out["request_ts"].notna()
        out["request_ts"] = pd.to_datetime(out["request_ts"], errors="coerce")
        report["request_ts_coerced_nat"] = int((was_notna & out["request_ts"].isna()).sum())

    for col in NUMERICAL_FEATURES:
        if col not in out.columns:
            continue
        before_na = int(out[col].isna().sum())
        out[col] = pd.to_numeric(out[col], errors="coerce").astype("float64")
        after_na = int(out[col].isna().sum())
        report["numerical"][col] = {
            "dtype": str(out[col].dtype),
            "new_nans": after_na - before_na,
        }

    return out, report


def fix_est_fare_unit_shift(
    df: pd.DataFrame,
    fare_per_km_threshold: float = DEFAULT_FARE_PER_KM_THRESHOLD,
    fallback_fare_threshold: float = FALLBACK_EST_FARE_THRESHOLD,
    scale_factor: float = UNIT_SHIFT_FACTOR,
    add_flag: bool = False,
) -> pd.DataFrame:
    """
    Normalize `est_fare` values recorded in piasters (x100) back to EGP.

    A row is treated as shifted when `est_fare / distance_km > fare_per_km_threshold`
    (or, when distance is missing/non-positive, `est_fare > fallback_fare_threshold`).
    Because corrected fares fall below the threshold (~5-92 EGP/km vs >=482 EGP/km
    uncorrected), this repair is idempotent across repeated invocations.
    """
    out = df.copy()
    if UNIT_SHIFT_FIELD not in out.columns:
        return out

    out[UNIT_SHIFT_FIELD] = pd.to_numeric(out[UNIT_SHIFT_FIELD], errors="coerce").astype("float64")

    if "distance_km" in out.columns:
        fpk = _compute_fare_per_km(out)
        shifted_mask = (fpk > fare_per_km_threshold).fillna(False)
        no_valid_dist = fpk.isna()
        shifted_mask = shifted_mask | (no_valid_dist & (out[UNIT_SHIFT_FIELD] > fallback_fare_threshold))
    else:
        shifted_mask = out[UNIT_SHIFT_FIELD] > fallback_fare_threshold

    shifted_mask = shifted_mask.fillna(False)
    out.loc[shifted_mask, UNIT_SHIFT_FIELD] = out.loc[shifted_mask, UNIT_SHIFT_FIELD] / scale_factor

    if add_flag:
        out["est_fare_unit_corrected"] = shifted_mask.astype("int8")

    return out


def extract_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract `hour`, `day_of_week`, and `month` from `request_ts`.

    `hour` is required as a confirmed confounder control for `surge_multiplier`.
    Invalid/missing timestamps yield NaN in the extracted numeric columns.
    """
    out = df.copy()
    if "request_ts" not in out.columns:
        return out

    ts = pd.to_datetime(out["request_ts"], errors="coerce")
    out["request_ts"] = ts

    has_nat = ts.isna().any()
    target_dtype = "float64" if has_nat else "int64"
    out["hour"] = ts.dt.hour.astype(target_dtype)
    out["day_of_week"] = ts.dt.day_of_week.astype(target_dtype)
    out["month"] = ts.dt.month.astype(target_dtype)

    return out


def attach_zone_confounders(
    df: pd.DataFrame,
    zones_df: pd.DataFrame,
    pickup_col: str = "pickup_zone",
) -> pd.DataFrame:
    """
    Attach `pickup_zone_type` and `pickup_has_metro` from `zones_df`.

    Supports both standardized zone names (post Person A repair) and legacy
    zone names via non-destructive key lookup so zone confounding controls are
    available without overwriting `pickup_zone`.
    """
    required = {"zone_name", "zone_type", "has_metro"}
    if not required.issubset(zones_df.columns):
        raise ValueError(f"zones_df must contain columns: {required}")

    out = df.copy()
    if pickup_col not in out.columns:
        return out

    lookup_key = _lookup_standard_zone(out[pickup_col], zones_df)
    zone_meta = (
        zones_df[["zone_name", "zone_type", "has_metro"]]
        .drop_duplicates(subset=["zone_name"])
        .set_index("zone_name")
    )

    out["pickup_zone_type"] = lookup_key.map(zone_meta["zone_type"])
    out["pickup_has_metro"] = lookup_key.map(zone_meta["has_metro"])
    return out


def validate_numerical_bounds(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate finite bounds and domain rules on Person B's audited numerical features.
    """
    rules = {
        "distance_km": lambda s: s <= 0,
        "est_fare": lambda s: s <= 0,
        "eta_estimate_min": lambda s: s <= 0,
        "surge_multiplier": lambda s: s < 1.0,
    }
    summary: Dict[str, Any] = {}
    for col, bad_fn in rules.items():
        if col not in df.columns:
            continue
        series = pd.to_numeric(df[col], errors="coerce")
        non_finite = int((~np.isfinite(series)).sum())
        invalid = int(bad_fn(series.dropna()).sum())
        summary[col] = {
            "non_finite": non_finite,
            "rule_violations": invalid,
            "min": float(series.min()) if series.notna().any() else None,
            "median": float(series.median()) if series.notna().any() else None,
            "max": float(series.max()) if series.notna().any() else None,
            "passed": (non_finite == 0 and invalid == 0),
        }
    return summary


def detect_unit_shift_onset(
    earlier_df: pd.DataFrame,
    later_df: pd.DataFrame,
    ratio_jump_factor: float = 10.0,
) -> Dict[str, Any]:
    """
    Audit helper for Task 1b: detect which numerical field shifted units and on which day.
    """
    combined = pd.concat([earlier_df, later_df], ignore_index=True)
    combined["request_ts"] = pd.to_datetime(combined["request_ts"], errors="coerce")
    combined["day"] = combined["request_ts"].dt.strftime("%Y-%m-%d")

    base_fpk = float(_compute_fare_per_km(earlier_df).median())
    daily = (
        combined.assign(fare_per_km=_compute_fare_per_km(combined))
        .groupby("day", sort=True)
        .agg(
            n=("est_fare", "size"),
            median_est_fare=("est_fare", "median"),
            median_distance_km=("distance_km", "median"),
            median_fare_per_km=("fare_per_km", "median"),
        )
    )

    shifted_days = daily[daily["median_fare_per_km"] > base_fpk * ratio_jump_factor]
    onset_day = str(shifted_days.index[0]) if len(shifted_days) > 0 else None
    post_fpk = float(shifted_days["median_fare_per_km"].median()) if len(shifted_days) > 0 else base_fpk

    return {
        "field": UNIT_SHIFT_FIELD,
        "day_estimate": onset_day,
        "scale_factor_estimate": round(post_fpk / base_fpk, 2) if base_fpk > 0 else None,
        "baseline_fare_per_km_median": round(base_fpk, 4),
        "shifted_fare_per_km_median": round(post_fpk, 4),
        "shifted_days_count": int(len(shifted_days)),
    }


def compute_confounding_slopes(
    trips_df: pd.DataFrame,
    zones_df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Audit helper for Task 1d: quantify Simpson's Paradox in `actual_trip_time_min ~ distance_km`
    on completed training trips (`request_failed == 0`) stratified by `pickup_zone_type`.
    """
    if "request_failed" not in trips_df.columns or "actual_trip_time_min" not in trips_df.columns:
        raise ValueError("trips_df must contain `request_failed` and `actual_trip_time_min`.")

    completed = trips_df[trips_df["request_failed"] == 0].copy()
    completed = attach_zone_confounders(completed, zones_df)

    global_slope = _ols_slope(
        completed["distance_km"].to_numpy(),
        completed["actual_trip_time_min"].to_numpy(),
    )

    group_slopes: Dict[str, float] = {}
    num_fe = 0.0
    den_fe = 0.0
    for zone_type, grp in completed.groupby("pickup_zone_type", dropna=True):
        x = grp["distance_km"].to_numpy(dtype="float64")
        y = grp["actual_trip_time_min"].to_numpy(dtype="float64")
        valid = np.isfinite(x) & np.isfinite(y)
        x_v, y_v = x[valid], y[valid]
        group_slopes[str(zone_type)] = round(_ols_slope(x_v, y_v), 4)
        x_c = x_v - x_v.mean()
        num_fe += float(np.sum(x_c * (y_v - y_v.mean())))
        den_fe += float(np.sum(x_c ** 2))

    pooled_within = num_fe / den_fe if den_fe > 0 else float("nan")
    return {
        "confounder": "pickup_zone_type",
        "n_completed_trips": int(len(completed)),
        "global_slope": round(global_slope, 4),
        "within_slope": round(pooled_within, 4),
        "group_slopes": group_slopes,
    }


class UnitShiftAndConfounderCleaner:
    """
    Train-only calibrated cleaner for Person B's Phase 1.3 data cleaning duties.

    Usage
    -----
    cleaner = UnitShiftAndConfounderCleaner().fit(trips_df)
    trips_clean   = cleaner.transform(trips_df, zones_df=zones_df)
    recent_clean  = cleaner.transform(recent_df, zones_df=zones_df)
    holdout_clean = cleaner.transform(holdout_df, zones_df=zones_df)
    """

    def __init__(self, scale_factor: float = UNIT_SHIFT_FACTOR) -> None:
        self.scale_factor: float = scale_factor
        self.fitted_: bool = False
        self.stats_: Dict[str, Any] = {}
        self.last_transform_stats_: Dict[str, Any] = {}

    def fit(self, train_df: pd.DataFrame) -> "UnitShiftAndConfounderCleaner":
        """Learn normal EGP fare/km scale bounds strictly from training data."""
        coerced, _ = coerce_person_b_dtypes(train_df)
        fpk = _compute_fare_per_km(coerced).dropna()
        if len(fpk) == 0:
            raise ValueError("Cannot fit UnitShiftAndConfounderCleaner: no valid fare/km rows.")

        train_median_fpk = float(fpk.median())
        train_p99_fpk = float(fpk.quantile(0.99))
        train_max_fpk = float(fpk.max())
        train_max_fare = float(coerced[UNIT_SHIFT_FIELD].dropna().max())

        # Threshold sits safely above any historical EGP ride and far below piaster rides (x100)
        threshold_fpk = max(150.0, 20.0 * train_median_fpk, 2.0 * train_max_fpk)
        fallback_fare = max(FALLBACK_EST_FARE_THRESHOLD, 2.0 * train_max_fare)

        self.stats_ = {
            "train_rows": int(len(train_df)),
            "train_fare_per_km_median": round(train_median_fpk, 4),
            "train_fare_per_km_p99": round(train_p99_fpk, 4),
            "train_fare_per_km_max": round(train_max_fpk, 4),
            "fare_per_km_threshold": round(threshold_fpk, 4),
            "fallback_fare_threshold": round(fallback_fare, 4),
            "scale_factor": float(self.scale_factor),
            "unit_shift_field": UNIT_SHIFT_FIELD,
            "unit_shift_date": UNIT_SHIFT_DATE,
        }
        self.fitted_ = True
        return self

    def transform(
        self,
        df: pd.DataFrame,
        zones_df: Optional[pd.DataFrame] = None,
        add_temporal: bool = True,
        add_unit_flag: bool = False,
    ) -> pd.DataFrame:
        """Apply dtype standardization, est_fare unit fix, temporal controls, and zone confounders."""
        if not self.fitted_:
            raise ValueError(
                "UnitShiftAndConfounderCleaner must be fitted on training data before transform()."
            )

        out, dtype_report = coerce_person_b_dtypes(df)

        fpk_before = _compute_fare_per_km(out) if {"distance_km", "est_fare"}.issubset(out.columns) else None
        threshold = self.stats_["fare_per_km_threshold"]
        fallback = self.stats_["fallback_fare_threshold"]

        out = fix_est_fare_unit_shift(
            out,
            fare_per_km_threshold=threshold,
            fallback_fare_threshold=fallback,
            scale_factor=self.scale_factor,
            add_flag=add_unit_flag,
        )

        n_corrected = 0
        if fpk_before is not None:
            shifted = (fpk_before > threshold).fillna(False) | (
                fpk_before.isna() & (pd.to_numeric(df[UNIT_SHIFT_FIELD], errors="coerce") > fallback)
            )
            n_corrected = int(shifted.sum())
        elif UNIT_SHIFT_FIELD in out.columns:
            n_corrected = int((pd.to_numeric(df[UNIT_SHIFT_FIELD], errors="coerce") > fallback).sum())

        if add_temporal:
            out = extract_temporal_features(out)

        if zones_df is not None:
            out = attach_zone_confounders(out, zones_df)

        self.last_transform_stats_ = {
            "rows_in": int(len(df)),
            "rows_out": int(len(out)),
            "rows_unit_corrected": n_corrected,
            "share_unit_corrected": round(n_corrected / max(len(df), 1), 4),
            "dtype_report": dtype_report,
            "bounds": validate_numerical_bounds(out),
        }
        return out

    def fit_transform(
        self,
        df: pd.DataFrame,
        zones_df: Optional[pd.DataFrame] = None,
        add_temporal: bool = True,
        add_unit_flag: bool = False,
    ) -> pd.DataFrame:
        """Fit on df and transform df."""
        return self.fit(df).transform(
            df,
            zones_df=zones_df,
            add_temporal=add_temporal,
            add_unit_flag=add_unit_flag,
        )


def clean_unit_shift_and_confounders(
    df: pd.DataFrame,
    train_df: Optional[pd.DataFrame] = None,
    zones_df: Optional[pd.DataFrame] = None,
    add_temporal: bool = True,
    add_unit_flag: bool = False,
) -> pd.DataFrame:
    """
    Functional interface matching the team's shared cleaning pipeline (`notebooks/06_data_cleaning.ipynb`).

    Fits scale statistics strictly on `train_df` (or `df` when `train_df` is None),
    normalizes `est_fare` units to EGP, coerces numerical/datetime dtypes, extracts
    temporal confounder features, and optionally attaches zone confounder metadata.
    """
    cleaner = UnitShiftAndConfounderCleaner()
    cleaner.fit(train_df if train_df is not None else df)
    return cleaner.transform(
        df,
        zones_df=zones_df,
        add_temporal=add_temporal,
        add_unit_flag=add_unit_flag,
    )
