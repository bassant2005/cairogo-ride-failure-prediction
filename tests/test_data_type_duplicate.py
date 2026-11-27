"""Unit and integration tests for src/data_type_duplicate.py (Person C)."""

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_type_duplicate import (
    apply_all_validation,
    check_duplicate_ids,
    drop_duplicates,
    fix_dtypes,
    validate_numeric_ranges,
    verify_types,
)

RAW_CANDIDATES = [
    ROOT / "data" / "raw" / "CairoGo_pack_v17",
    ROOT / "data" / "raw" / "cairogo_pack",
]
RAW_PACK_DIR = next(
    (path for path in RAW_CANDIDATES if (path / "trips.csv").exists()),
    RAW_CANDIDATES[0],
)


class TestDataValidationUnit(unittest.TestCase):
    """Unit tests using synthetic DataFrames and edge cases."""

    def setUp(self) -> None:
        self.df = pd.DataFrame(
            {
                "trip_id": [100001, 100002, 100002],
                "customer_id": [20001, 20002, 20002],
                "driver_id": [5001, 5002, 5002],
                "request_ts": [
                    "2026-05-01 00:01:46",
                    "2026-05-01 00:37:36",
                    "2026-05-01 00:37:36",
                ],
                "pickup_zone": ["Downtown", "Zamalek", "Zamalek"],
                "dropoff_zone": ["Maadi", "Obour", "Obour"],
                "distance_km": ["12.5", "8.0", "8.0"],
                "surge_multiplier": [1.0, 1.2, 1.2],
                "est_fare": [90.5, 75.0, 75.0],
                "eta_estimate_min": [6.4, 7.3, 7.3],
                "weather": ["rain", np.nan, np.nan],
                "payment_method": ["card", "cash", "cash"],
                "service_level": ["economy", "comfort", "comfort"],
                "request_failed": [0, 1, 1],
                "support_ticket_flag": [0, 0, 0],
            }
        )

    def test_fix_dtypes_converts_expected_schema(self) -> None:
        fixed = fix_dtypes(self.df)

        self.assertEqual(str(fixed["trip_id"].dtype), "string")
        self.assertEqual(str(fixed["customer_id"].dtype), "string")
        self.assertEqual(str(fixed["driver_id"].dtype), "string")
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(fixed["request_ts"]))
        self.assertTrue(pd.api.types.is_float_dtype(fixed["distance_km"]))
        self.assertTrue(pd.api.types.is_integer_dtype(fixed["request_failed"]))
        self.assertIsInstance(fixed["weather"].dtype, pd.CategoricalDtype)
        self.assertIsInstance(fixed["pickup_zone"].dtype, pd.CategoricalDtype)
        verify_types(fixed)

    def test_fix_dtypes_preserves_nan_and_handles_missing_columns(self) -> None:
        partial_df = pd.DataFrame(
            {
                "trip_id": [1, 2],
                "request_ts": ["2026-05-01 10:00:00", np.nan],
                "weather": ["clear", np.nan],
                "request_failed": [0, np.nan],
            }
        )
        fixed = fix_dtypes(partial_df)

        self.assertTrue(pd.isna(fixed.loc[1, "request_ts"]))
        self.assertTrue(pd.isna(fixed.loc[1, "weather"]))
        self.assertTrue(pd.isna(fixed.loc[1, "request_failed"]))
        self.assertTrue(pd.api.types.is_integer_dtype(fixed["request_failed"]))
        verify_types(fixed)

    def test_fix_dtypes_handles_empty_dataframe(self) -> None:
        empty_df = self.df.iloc[0:0].copy()
        fixed = fix_dtypes(empty_df)

        self.assertEqual(len(fixed), 0)
        verify_types(fixed)

    def test_immutability_of_fix_dtypes_and_drop_duplicates(self) -> None:
        original = self.df.copy(deep=True)
        _ = fix_dtypes(self.df)
        _ = drop_duplicates(self.df)
        pd.testing.assert_frame_equal(self.df, original)

    def test_idempotency_of_apply_all_validation(self) -> None:
        once = apply_all_validation(self.df)
        twice = apply_all_validation(once)
        pd.testing.assert_frame_equal(once, twice)

    def test_drop_duplicates_removes_exact_duplicates(self) -> None:
        deduped = drop_duplicates(self.df)
        self.assertEqual(len(deduped), 2)
        self.assertEqual(deduped["trip_id"].tolist(), [100001, 100002])

    def test_error_cases_raise_value_or_assertion_error(self) -> None:
        with self.assertRaises(ValueError):
            fix_dtypes("not a dataframe")  # type: ignore[arg-type]

        bad_date_df = pd.DataFrame({"request_ts": ["2026-05-01", "not-a-date"]})
        with self.assertRaises(ValueError):
            fix_dtypes(bad_date_df)

        bad_num_df = pd.DataFrame({"distance_km": ["10.5", "bad"]})
        with self.assertRaises(ValueError):
            fix_dtypes(bad_num_df)

        bad_int_df = pd.DataFrame({"request_failed": [0, 1.5]})
        with self.assertRaises(ValueError):
            fix_dtypes(bad_int_df)

        with self.assertRaises(AssertionError):
            verify_types(self.df)

        with self.assertRaises(AssertionError):
            verify_types(pd.DataFrame())

        with self.assertRaises(ValueError):
            drop_duplicates(self.df, subset=["missing_col"])

    def test_check_duplicate_ids_and_numeric_ranges(self) -> None:
        self.assertEqual(check_duplicate_ids(self.df, id_col="trip_id"), 1)
        with self.assertRaises(AssertionError):
            check_duplicate_ids(self.df, id_col="trip_id", raise_on_duplicates=True)

        range_df = pd.DataFrame({"distance_km": [5.0, -1.0], "rating_avg": [4.5, 5.5]})
        summary = validate_numeric_ranges(range_df)
        self.assertEqual(summary.loc[0, "Invalid_Values"], 1)
        self.assertEqual(summary.loc[1, "Invalid_Values"], 1)


@unittest.skipUnless(
    (RAW_PACK_DIR / "trips.csv").exists(),
    "Raw CairoGo trips.csv not found.",
)
class TestDataValidationIntegration(unittest.TestCase):
    """Integration tests on the actual CairoGo Pack dataset."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.trips_df = pd.read_csv(RAW_PACK_DIR / "trips.csv")
        cls.result = apply_all_validation(cls.trips_df)

    def test_no_records_lost_and_columns_preserved(self) -> None:
        self.assertEqual(self.result.shape, self.trips_df.shape)
        self.assertEqual(list(self.result.columns), list(self.trips_df.columns))

    def test_dtypes_verified_on_real_trips(self) -> None:
        verify_types(self.result)

    def test_no_duplicate_trip_ids_and_numeric_values_unchanged(self) -> None:
        self.assertEqual(
            check_duplicate_ids(self.result, id_col="trip_id", raise_on_duplicates=True),
            0,
        )
        for col in ("distance_km", "surge_multiplier", "est_fare", "eta_estimate_min"):
            pd.testing.assert_series_equal(self.result[col], self.trips_df[col])

        range_summary = validate_numeric_ranges(self.result)
        self.assertTrue((range_summary["Invalid_Values"] == 0).all())
