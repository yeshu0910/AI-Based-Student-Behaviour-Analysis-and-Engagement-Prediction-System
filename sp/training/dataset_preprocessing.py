"""
Dataset Preprocessing Module.
Handles data cleaning, normalization, missing-value imputation,
and multimodal feature alignment for classroom and public engagement datasets (e.g. DAiSEE).
"""
import pandas as pd
import numpy as np

class DatasetPreprocessor:
    @staticmethod
    def preprocess_multimodal_records(df: pd.DataFrame) -> pd.DataFrame:
        clean_df = df.copy()

        # Handle missing visual signals with conservative median imputation
        numeric_cols = clean_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if clean_df[col].isnull().any():
                clean_df[col] = clean_df[col].fillna(clean_df[col].median())

        return clean_df

