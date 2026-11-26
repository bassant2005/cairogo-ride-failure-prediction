"""
CairoGo — Missing Values Cleaning Module
Phase 1: Data Cleaning Pipeline
Author: Rawda Raafat (Person D - ID: 20231067)

This module handles missing values across all tables according to the team's
agreed Phase 1 Missingness Analysis findings:
- weather: Informative missingness (MNAR, +4.06% failure rate). Imputed with 'missing' category
  and creates an indicator 'weather_was_missing'.
- driver rating_avg: Informative missingness (MNAR, +5.04% failure rate). Imputed with training set median
  and creates an indicator 'rating_avg_was_missing'.
- Leakage columns (actual_trip_time_min, cancel_reason, driver_arrival_min, support_ticket_flag):
  Flagged as post-request leakage and protected from erroneous imputation.
- Strict train-only fitting: Fit on training data (trips.csv), transform on validation/holdout.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


class MissingValuesHandler:
    """
    Fits imputation parameters on the training dataset and applies
    reproducible missingness handling across training, validation, and holdout datasets.
    """

    def __init__(self):
        self.fitted_: bool = False
        self.stats_: Dict[str, Any] = {}

    def fit(self, df: pd.DataFrame) -> "MissingValuesHandler":
        """
        Fit imputation parameters strictly on training data.
        """
        # 1. Driver rating median from training data
        if "rating_avg" in df.columns:
            valid_ratings = df["rating_avg"].dropna()
            self.stats_["rating_avg_median"] = float(valid_ratings.median()) if len(valid_ratings) > 0 else 4.55
        else:
            self.stats_["rating_avg_median"] = 4.55

        # 2. General numeric feature medians (in case of future edge cases in holdout)
        numeric_candidates = ["distance_km", "est_fare", "eta_estimate_min", "surge_multiplier"]
        for col in numeric_candidates:
            if col in df.columns:
                self.stats_[f"{col}_median"] = float(df[col].median())

        self.stats_["weather_fill_value"] = "missing"
        self.fitted_ = True
        return self

    def transform(self, df: pd.DataFrame, drop_leakage: bool = False) -> pd.DataFrame:
        """
        Apply missing value transformations.
        
        Parameters:
        -----------
        df : pd.DataFrame
            The input dataframe (working copy).
        drop_leakage : bool, default False
            If True, drops post-decision leakage columns (actual_trip_time_min, cancel_reason,
            driver_arrival_min, support_ticket_flag) so they cannot leak into features.
        
        Returns:
        --------
        pd.DataFrame
            Cleaned dataframe with missing indicators and imputed values.
        """
        if not self.fitted_:
            raise ValueError("MissingValuesHandler must be fitted on training data before calling transform()!")

        df_out = df.copy()

        # 1. Handle weather missingness (Categorical — Informative MNAR)
        if "weather" in df_out.columns:
            # Indicator flag: 1 if missing, 0 if present
            df_out["weather_was_missing"] = df_out["weather"].isna().astype(int)
            # Impute NaN as explicit category 'missing'
            df_out["weather"] = df_out["weather"].fillna(self.stats_["weather_fill_value"])

        # 2. Handle driver rating_avg missingness (Numerical — Informative MNAR)
        if "rating_avg" in df_out.columns:
            # Indicator flag: 1 if missing, 0 if present
            df_out["rating_avg_was_missing"] = df_out["rating_avg"].isna().astype(int)
            # Impute NaN with training set median
            df_out["rating_avg"] = df_out["rating_avg"].fillna(self.stats_["rating_avg_median"])

        # 3. Handle any other at-request numeric columns (safety fallback for holdout data)
        numeric_features = ["distance_km", "est_fare", "eta_estimate_min", "surge_multiplier"]
        for col in numeric_features:
            if col in df_out.columns and df_out[col].isna().sum() > 0:
                df_out[f"{col}_was_missing"] = df_out[col].isna().astype(int)
                median_val = self.stats_.get(f"{col}_median", df_out[col].median())
                df_out[col] = df_out[col].fillna(median_val)

        # 4. Handle target leakage columns (if requested)
        leakage_cols = ["actual_trip_time_min", "cancel_reason", "driver_arrival_min", "support_ticket_flag"]
        if drop_leakage:
            existing_leakage = [c for c in leakage_cols if c in df_out.columns]
            df_out = df_out.drop(columns=existing_leakage)

        return df_out

    def fit_transform(self, df: pd.DataFrame, drop_leakage: bool = False) -> pd.DataFrame:
        """Fit on df and return transformed df."""
        return self.fit(df).transform(df, drop_leakage=drop_leakage)


def clean_missing_values(df: pd.DataFrame, 
                         train_df: Optional[pd.DataFrame] = None, 
                         drop_leakage: bool = False) -> pd.DataFrame:
    """
    Convenience functional interface matching the team's data cleaning pipeline.
    
    If train_df is provided, statistics are learned from train_df.
    If train_df is None, statistics are learned directly from df (assuming df is the training set).
    """
    handler = MissingValuesHandler()
    if train_df is not None:
        handler.fit(train_df)
    else:
        handler.fit(df)
    return handler.transform(df, drop_leakage=drop_leakage)
