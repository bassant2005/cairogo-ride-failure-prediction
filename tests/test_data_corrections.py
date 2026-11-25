"""Unit and integration tests for src/data_corrections.py (Person A)."""

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_corrections import (
    apply_all_corrections,
    build_legacy_zone_mapping,
    fix_zone_names,
    verify_zone_fix,
)

RAW_PACK_DIR = ROOT / "data" / "raw" / "CairoGo_pack_v17"


class TestZoneCorrectionsUnit(unittest.TestCase):
    """Unit tests using synthetic DataFrames and edge cases."""

    def setUp(self) -> None:
        self.zones_df = pd.DataFrame(
            {
                "zone_id": ["Z01", "Z11", "Z13", "Z21"],
                "zone_name": [
                    "Downtown",
                    "Dokki District",
                    "New Cairo District",
                    "Badr City District",
                ],
                "legacy_name": ["Downtown", "Dokki", "New Cairo", "Badr City"],
            }
        )

    def test_build_legacy_zone_mapping_returns_expected_dict(self) -> None:
        mapping = build_legacy_zone_mapping(self.zones_df)
        self.assertEqual(
            mapping,
            {
                "Downtown": "Downtown",
                "Dokki": "Dokki District",
                "New Cairo": "New Cairo District",
                "Badr City": "Badr City District",
            },
        )

    def test_build_legacy_zone_mapping_missing_columns_raises(self) -> None:
        bad_zones = pd.DataFrame({"zone_name": ["Downtown"]})
        with self.assertRaises(ValueError):
            build_legacy_zone_mapping(bad_zones)

    def test_fix_zone_names_remaps_both_columns_without_mutating_input(self) -> None:
        raw_df = pd.DataFrame(
            {
                "trip_id": [1, 2, 3],
                "pickup_zone": ["Dokki", "Downtown", "Badr City"],
                "dropoff_zone": ["New Cairo", "Dokki", "Dokki District"],
            }
        )
        raw_copy = raw_df.copy(deep=True)

        fixed_df = fix_zone_names(raw_df, self.zones_df)

        # Input must remain untouched
        pd.testing.assert_frame_equal(raw_df, raw_copy)
        self.assertEqual(
            fixed_df["pickup_zone"].tolist(),
            ["Dokki District", "Downtown", "Badr City District"],
        )
        self.assertEqual(
            fixed_df["dropoff_zone"].tolist(),
            ["New Cairo District", "Dokki District", "Dokki District"],
        )

    def test_fix_zone_names_preserves_nan_and_missing_column(self) -> None:
        partial_df = pd.DataFrame({"pickup_zone": ["Dokki", np.nan, "Downtown"]})
        fixed_df = fix_zone_names(partial_df, self.zones_df)

        self.assertEqual(fixed_df.loc[0, "pickup_zone"], "Dokki District")
        self.assertTrue(pd.isna(fixed_df.loc[1, "pickup_zone"]))
        self.assertEqual(fixed_df.loc[2, "pickup_zone"], "Downtown")

    def test_fix_zone_names_supports_custom_column_names(self) -> None:
        custom_df = pd.DataFrame(
            {"start_area": ["New Cairo"], "end_area": ["Badr City"]}
        )
        fixed_df = fix_zone_names(
            custom_df,
            self.zones_df,
            pickup_col="start_area",
            dropoff_col="end_area",
        )
        self.assertEqual(fixed_df["start_area"].tolist(), ["New Cairo District"])
        self.assertEqual(fixed_df["end_area"].tolist(), ["Badr City District"])

    def test_verify_zone_fix_passes_when_valid(self) -> None:
        valid_df = pd.DataFrame(
            {
                "pickup_zone": ["Downtown", "Dokki District", None],
                "dropoff_zone": ["New Cairo District", "Badr City District", "Downtown"],
            }
        )
        verify_zone_fix(valid_df, self.zones_df)

    def test_verify_zone_fix_raises_on_unmatched_zone(self) -> None:
        bad_pickup = pd.DataFrame(
            {"pickup_zone": ["UnknownZone"], "dropoff_zone": ["Downtown"]}
        )
        with self.assertRaises(AssertionError) as ctx:
            verify_zone_fix(bad_pickup, self.zones_df)
        self.assertIn("UnknownZone", str(ctx.exception))

        bad_dropoff = pd.DataFrame(
            {"pickup_zone": ["Downtown"], "dropoff_zone": ["Dokki"]}
        )
        with self.assertRaises(AssertionError) as ctx2:
            verify_zone_fix(bad_dropoff, self.zones_df)
        self.assertIn("Dokki", str(ctx2.exception))

    def test_apply_all_corrections_is_idempotent(self) -> None:
        df = pd.DataFrame(
            {
                "trip_id": [10, 20],
                "pickup_zone": ["Dokki", "New Cairo"],
                "dropoff_zone": ["Badr City", "Downtown"],
            }
        )
        once = apply_all_corrections(df, self.zones_df)
        twice = apply_all_corrections(once, self.zones_df)
        pd.testing.assert_frame_equal(once, twice)


@unittest.skipUnless(
    (RAW_PACK_DIR / "trips.csv").exists() and (RAW_PACK_DIR / "zones.csv").exists(),
    "Raw Pack v17 CSV files not found.",
)
class TestZoneCorrectionsIntegration(unittest.TestCase):
    """Integration and data-invariant tests on the actual CairoGo Pack v17 dataset."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.trips_df = pd.read_csv(RAW_PACK_DIR / "trips.csv")
        cls.zones_df = pd.read_csv(RAW_PACK_DIR / "zones.csv")
        cls.fixed_df = apply_all_corrections(cls.trips_df, cls.zones_df)

    def test_unmatched_zones_before_and_zero_after_fix(self) -> None:
        valid_zones = set(self.zones_df["zone_name"].dropna())

        unmatched_before = set(self.trips_df["pickup_zone"].dropna()) - valid_zones
        self.assertEqual(unmatched_before, {"Dokki", "New Cairo", "Badr City"})

        frac_before = (
            ~self.trips_df["pickup_zone"].isin(valid_zones)
        ).mean()
        self.assertAlmostEqual(frac_before, 0.1148, places=4)

        for col in ("pickup_zone", "dropoff_zone"):
            unmatched_after = set(self.fixed_df[col].dropna()) - valid_zones
            self.assertEqual(unmatched_after, set())

    def test_zero_records_lost_and_other_columns_unchanged(self) -> None:
        self.assertEqual(self.fixed_df.shape, self.trips_df.shape)
        self.assertEqual(list(self.fixed_df.columns), list(self.trips_df.columns))

        other_cols = [
            c for c in self.trips_df.columns if c not in ("pickup_zone", "dropoff_zone")
        ]
        pd.testing.assert_frame_equal(
            self.fixed_df[other_cols], self.trips_df[other_cols]
        )

    def test_zero_join_loss_when_merging_with_zones(self) -> None:
        pickup_joined = self.fixed_df.merge(
            self.zones_df[["zone_name", "zone_id"]],
            left_on="pickup_zone",
            right_on="zone_name",
            how="left",
        )
        self.assertEqual(len(pickup_joined), len(self.trips_df))
        self.assertEqual(pickup_joined["zone_id"].isna().sum(), 0)

        dropoff_joined = self.fixed_df.merge(
            self.zones_df[["zone_name", "zone_id"]],
            left_on="dropoff_zone",
            right_on="zone_name",
            how="left",
        )
        self.assertEqual(len(dropoff_joined), len(self.trips_df))
        self.assertEqual(dropoff_joined["zone_id"].isna().sum(), 0)
