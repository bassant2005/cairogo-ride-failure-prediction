"""Unit and integration tests for src/unit_shift_cleaning.py (Person B — Rahma Bahgat)."""

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.unit_shift_cleaning import (
    UnitShiftAndConfounderCleaner,
    attach_zone_confounders,
    clean_unit_shift_and_confounders,
    compute_confounding_slopes,
    detect_unit_shift_onset,
    extract_temporal_features,
    fix_est_fare_unit_shift,
    validate_numerical_bounds,
)


def _find_pack_dir() -> Path:
    for name in ("cairogo_pack", "CairoGo_pack_v17"):
        candidate = ROOT / "data" / "raw" / name
        if (candidate / "trips.csv").exists():
            return candidate
    return ROOT / "data" / "raw" / "cairogo_pack"


RAW_PACK_DIR = _find_pack_dir()


class TestUnitShiftAndConfounderUnit(unittest.TestCase):
    """Synthetic unit tests covering fit/transform, immutability, idempotency, and edge cases."""

    def setUp(self) -> None:
        self.train_df = pd.DataFrame(
            {
                "trip_id": [1, 2, 3, 4],
                "request_ts": [
                    "2026-05-01 08:15:00",
                    "2026-06-15 14:30:00",
                    "2026-07-20 19:45:00",
                    "2026-08-30 23:41:00",
                ],
                "pickup_zone": ["Downtown", "Dokki District", "Maadi", "New Cairo"],
                "distance_km": [5.0, 10.0, 8.0, 12.0],
                "surge_multiplier": [1.0, 1.2, 1.5, 1.0],
                "est_fare": [55.0, 95.0, 110.0, 105.0],
                "eta_estimate_min": [6.0, 8.5, 9.0, 7.5],
                "service_level": ["economy", "comfort", "premium", "economy"],
            }
        )
        self.shifted_df = pd.DataFrame(
            {
                "trip_id": [101, 102],
                "request_ts": ["2026-08-31 00:05:48", "2026-09-02 18:10:00"],
                "pickup_zone": ["Dokki", "Downtown"],
                "distance_km": [6.0, 10.0],
                "surge_multiplier": [1.0, 1.4],
                "est_fare": [5670.0, 11200.0],  # x100 piasters
                "eta_estimate_min": [7.0, 11.0],
                "service_level": ["economy", "comfort"],
            }
        )
        self.zones_df = pd.DataFrame(
            {
                "zone_id": ["Z01", "Z07", "Z11", "Z13"],
                "zone_name": ["Downtown", "Maadi", "Dokki District", "New Cairo District"],
                "legacy_name": ["Downtown", "Maadi", "Dokki", "New Cairo"],
                "zone_type": ["downtown", "midtown", "midtown", "new_city"],
                "has_metro": [1, 1, 0, 0],
            }
        )

    def test_transform_before_fit_raises(self) -> None:
        cleaner = UnitShiftAndConfounderCleaner()
        with self.assertRaises(ValueError):
            cleaner.transform(self.train_df)

    def test_fit_transform_preserves_input_immutability(self) -> None:
        train_copy = self.train_df.copy(deep=True)
        shifted_copy = self.shifted_df.copy(deep=True)

        cleaner = UnitShiftAndConfounderCleaner().fit(self.train_df)
        _ = cleaner.transform(self.shifted_df, zones_df=self.zones_df)

        pd.testing.assert_frame_equal(self.train_df, train_copy)
        pd.testing.assert_frame_equal(self.shifted_df, shifted_copy)

    def test_est_fare_unit_fix_normalizes_piasters_and_keeps_egp_untouched(self) -> None:
        cleaner = UnitShiftAndConfounderCleaner().fit(self.train_df)

        clean_train = cleaner.transform(self.train_df)
        self.assertEqual(cleaner.last_transform_stats_["rows_unit_corrected"], 0)
        np.testing.assert_allclose(clean_train["est_fare"], [55.0, 95.0, 110.0, 105.0])

        clean_shifted = cleaner.transform(self.shifted_df)
        self.assertEqual(cleaner.last_transform_stats_["rows_unit_corrected"], 2)
        np.testing.assert_allclose(clean_shifted["est_fare"], [56.7, 112.0])

    def test_unit_fix_is_idempotent(self) -> None:
        cleaner = UnitShiftAndConfounderCleaner().fit(self.train_df)
        once = cleaner.transform(self.shifted_df, zones_df=self.zones_df)
        twice = cleaner.transform(once, zones_df=self.zones_df)
        pd.testing.assert_frame_equal(once, twice)

    def test_temporal_extraction_and_dtype_coercion(self) -> None:
        dirty = pd.DataFrame(
            {
                "request_ts": ["2026-08-31 09:30:00", "not-a-date"],
                "distance_km": ["5.0", "10.0"],
                "surge_multiplier": [1.0, 1.5],
                "est_fare": ["4500.0", "9000.0"],
                "eta_estimate_min": [6.0, 8.0],
            }
        )
        cleaned = clean_unit_shift_and_confounders(dirty, train_df=self.train_df)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(cleaned["request_ts"]))
        self.assertEqual(cleaned.loc[0, "hour"], 9.0)
        self.assertEqual(cleaned.loc[0, "month"], 8.0)
        self.assertTrue(pd.isna(cleaned.loc[1, "hour"]))
        np.testing.assert_allclose(cleaned["est_fare"], [45.0, 90.0])

    def test_attach_zone_confounders_handles_legacy_and_standard_names(self) -> None:
        enriched = attach_zone_confounders(self.shifted_df, self.zones_df)
        self.assertEqual(enriched["pickup_zone_type"].tolist(), ["midtown", "downtown"])
        self.assertEqual(enriched["pickup_has_metro"].tolist(), [0, 1])
        # Does not alter original pickup_zone column (Person A handles that explicitly)
        self.assertEqual(enriched["pickup_zone"].tolist(), ["Dokki", "Downtown"])

    def test_fix_est_fare_fallback_when_distance_zero_or_missing(self) -> None:
        edge = pd.DataFrame(
            {
                "distance_km": [0.0, np.nan, 4.0],
                "est_fare": [5500.0, 6200.0, 48.0],
            }
        )
        fixed = fix_est_fare_unit_shift(edge, add_flag=True)
        np.testing.assert_allclose(fixed["est_fare"], [55.0, 62.0, 48.0])
        self.assertEqual(fixed["est_fare_unit_corrected"].tolist(), [1, 1, 0])

    def test_detect_unit_shift_onset_and_bounds(self) -> None:
        onset = detect_unit_shift_onset(self.train_df, self.shifted_df)
        self.assertEqual(onset["field"], "est_fare")
        self.assertEqual(onset["day_estimate"], "2026-08-31")
        bounds = validate_numerical_bounds(self.train_df)
        self.assertTrue(all(info["passed"] for info in bounds.values()))

    def test_extract_temporal_features_clean_int_types(self) -> None:
        out = extract_temporal_features(self.train_df)
        self.assertEqual(out["hour"].tolist(), [8, 14, 19, 23])
        self.assertEqual(out["month"].tolist(), [5, 6, 7, 8])
        self.assertTrue(pd.api.types.is_integer_dtype(out["hour"]))


@unittest.skipUnless(
    (RAW_PACK_DIR / "trips.csv").exists()
    and (RAW_PACK_DIR / "recent_labelled.csv").exists()
    and (RAW_PACK_DIR / "holdout_inputs.csv").exists()
    and (RAW_PACK_DIR / "zones.csv").exists(),
    "Raw Pack v17 CSV files not found.",
)
class TestUnitShiftAndConfounderIntegration(unittest.TestCase):
    """Integration tests verifying Person B cleaning across actual CairoGo Pack v17 files."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.trips_df = pd.read_csv(RAW_PACK_DIR / "trips.csv")
        cls.recent_df = pd.read_csv(RAW_PACK_DIR / "recent_labelled.csv")
        cls.holdout_df = pd.read_csv(RAW_PACK_DIR / "holdout_inputs.csv")
        cls.zones_df = pd.read_csv(RAW_PACK_DIR / "zones.csv")
        cls.cleaner = UnitShiftAndConfounderCleaner().fit(cls.trips_df)

    def test_pack_v17_unit_shift_onset_matches_aug_31(self) -> None:
        onset = detect_unit_shift_onset(self.trips_df, self.recent_df)
        self.assertEqual(onset["field"], "est_fare")
        self.assertEqual(onset["day_estimate"], "2026-08-31")
        self.assertGreater(onset["scale_factor_estimate"], 90.0)
        self.assertLess(onset["scale_factor_estimate"], 110.0)

    def test_trips_unchanged_recent_and_holdout_fully_repaired(self) -> None:
        trips_clean = self.cleaner.transform(self.trips_df, zones_df=self.zones_df)
        self.assertEqual(self.cleaner.last_transform_stats_["rows_unit_corrected"], 0)
        np.testing.assert_allclose(trips_clean["est_fare"], self.trips_df["est_fare"])
        self.assertEqual(trips_clean["pickup_zone_type"].isna().sum(), 0)

        recent_clean = self.cleaner.transform(self.recent_df, zones_df=self.zones_df)
        self.assertEqual(
            self.cleaner.last_transform_stats_["rows_unit_corrected"],
            len(self.recent_df),
        )
        np.testing.assert_allclose(recent_clean["est_fare"], self.recent_df["est_fare"] / 100.0)
        self.assertEqual(recent_clean["pickup_zone_type"].isna().sum(), 0)

        holdout_clean = self.cleaner.transform(self.holdout_df, zones_df=self.zones_df)
        self.assertEqual(
            self.cleaner.last_transform_stats_["rows_unit_corrected"],
            len(self.holdout_df),
        )
        np.testing.assert_allclose(holdout_clean["est_fare"], self.holdout_df["est_fare"] / 100.0)
        self.assertEqual(holdout_clean["pickup_zone_type"].isna().sum(), 0)

        # Idempotent on real post-shift data
        holdout_twice = self.cleaner.transform(holdout_clean, zones_df=self.zones_df)
        self.assertEqual(self.cleaner.last_transform_stats_["rows_unit_corrected"], 0)
        pd.testing.assert_frame_equal(holdout_clean, holdout_twice)

    def test_pack_v17_confounding_simpsons_paradox_verified(self) -> None:
        summary = compute_confounding_slopes(self.trips_df, self.zones_df)
        self.assertLess(summary["global_slope"], -0.15)
        self.assertGreater(summary["within_slope"], 0.45)
        self.assertTrue(all(slope > 0.35 for slope in summary["group_slopes"].values()))
        self.assertEqual(summary["n_completed_trips"], 23221)


if __name__ == "__main__":
    unittest.main()
