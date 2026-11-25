"""
Data corrections module — Mariam Ehab (Person A).
Fixes implemented:
  1. Zone name standardisation (Task 1a: Join Loss & Zone Mapping)
     - Remaps legacy pickup_zone / dropoff_zone strings to official zone_name values
       using the zones.csv legacy_name column
     - Verified results: 0 unmatched zones, 0 records lost
"""

from typing import Dict
import pandas as pd


def build_legacy_zone_mapping(zones_df: pd.DataFrame) -> Dict[str, str]:
    """Map legacy_name -> zone_name using the zones reference table."""
    required = {"legacy_name", "zone_name"}
    if not required.issubset(zones_df.columns):
        raise ValueError(f"zones_df must contain columns: {required}")

    return zones_df.set_index("legacy_name")["zone_name"].to_dict()


def fix_zone_names(
    df: pd.DataFrame,
    zones_df: pd.DataFrame,
    pickup_col: str = "pickup_zone",
    dropoff_col: str = "dropoff_zone",
) -> pd.DataFrame:
    """Replace legacy zone names in pickup_zone and dropoff_zone."""
    out = df.copy()
    mapping = build_legacy_zone_mapping(zones_df)

    if pickup_col in out.columns:
        out[pickup_col] = out[pickup_col].replace(mapping)

    if dropoff_col in out.columns:
        out[dropoff_col] = out[dropoff_col].replace(mapping)

    return out


def verify_zone_fix(
    df_fixed: pd.DataFrame,
    zones_df: pd.DataFrame,
    pickup_col: str = "pickup_zone",
    dropoff_col: str = "dropoff_zone",
) -> None:
    """Check that no unmatched zone names remain after the fix."""
    valid = set(zones_df["zone_name"].dropna())

    for col in [pickup_col, dropoff_col]:
        if col not in df_fixed.columns:
            continue
        leftover = set(df_fixed[col].dropna()) - valid
        assert len(leftover) == 0, (
            f"Column '{col}' still has unmatched zone names: {leftover}"
        )

    print("Zone name fix verified: 0 unmatched values remain.")


def apply_all_corrections(
    df: pd.DataFrame,
    zones_df: pd.DataFrame,
) -> pd.DataFrame:
    """Apply all corrections by Mariam Ehab (Person A) on the raw trips dataframe."""
    out = fix_zone_names(df, zones_df)
    verify_zone_fix(out, zones_df)
    return out
