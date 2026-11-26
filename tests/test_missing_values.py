"""
Unit tests for src/missing_values.py
"""

import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.missing_values import MissingValuesHandler, clean_missing_values


def test_missing_values_handler_fit_transform():
    train_data = pd.DataFrame({
        "weather": ["clear", "rain", np.nan, "dust", "clear"],
        "rating_avg": [4.8, np.nan, 4.2, 4.6, np.nan],
        "distance_km": [5.0, 10.0, 15.0, 20.0, 25.0],
        "request_failed": [0, 1, 1, 0, 0]
    })
    
    test_data = pd.DataFrame({
        "weather": [np.nan, "clear", "rain"],
        "rating_avg": [np.nan, 5.0, 3.8],
        "distance_km": [7.0, 12.0, 18.0]
    })

    handler = MissingValuesHandler()
    cleaned_train = handler.fit_transform(train_data)

    # 1. Check no missing values in feature columns
    assert cleaned_train["weather"].isna().sum() == 0
    assert cleaned_train["rating_avg"].isna().sum() == 0

    # 2. Check indicator columns were created
    assert "weather_was_missing" in cleaned_train.columns
    assert "rating_avg_was_missing" in cleaned_train.columns
    assert cleaned_train["weather_was_missing"].tolist() == [0, 0, 1, 0, 0]
    assert cleaned_train["rating_avg_was_missing"].tolist() == [0, 1, 0, 0, 1]

    # 3. Check train median was applied (median of [4.8, 4.2, 4.6] is 4.6)
    expected_median = 4.6
    assert np.isclose(handler.stats_["rating_avg_median"], expected_median)
    assert np.isclose(cleaned_train.loc[1, "rating_avg"], expected_median)

    # 4. Check test transformation preserves train statistics
    cleaned_test = handler.transform(test_data)
    assert cleaned_test["weather"].isna().sum() == 0
    assert cleaned_test["rating_avg"].isna().sum() == 0
    assert cleaned_test.loc[0, "weather"] == "missing"
    assert np.isclose(cleaned_test.loc[0, "rating_avg"], expected_median)
    assert cleaned_test["weather_was_missing"].tolist() == [1, 0, 0]
    assert cleaned_test["rating_avg_was_missing"].tolist() == [1, 0, 0]


def test_clean_missing_values_functional():
    df = pd.DataFrame({
        "weather": ["clear", np.nan],
        "rating_avg": [4.5, np.nan],
        "actual_trip_time_min": [25.0, np.nan]
    })
    
    cleaned = clean_missing_values(df, drop_leakage=True)
    assert "actual_trip_time_min" not in cleaned.columns
    assert cleaned["weather"].isna().sum() == 0
    assert cleaned["rating_avg"].isna().sum() == 0
    assert "weather_was_missing" in cleaned.columns
