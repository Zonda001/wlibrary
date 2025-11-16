"""
Utils Module - Helper Functions and Utilities
=============================================

Provides utility functions for common operations and data transformations.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def split_coordinates(
        df: pd.DataFrame,
        coord_column: str,
        lat_col: str = 'latitude',
        lon_col: str = 'longitude',
        drop_original: bool = True
) -> pd.DataFrame:
    """
    Split a coordinate column into separate latitude and longitude columns.

    Handles various coordinate formats:
    - "50.4501, 30.5234"
    - "50.4501,30.5234"
    - "50.4501 30.5234"

    Args:
        df: Input DataFrame
        coord_column: Name of the column containing coordinates
        lat_col: Name for the new latitude column
        lon_col: Name for the new longitude column
        drop_original: Whether to drop the original coordinate column

    Returns:
        DataFrame with split coordinates

    Example:
        >>> df = split_coordinates(df, 'coordinates')
        >>> print(df[['latitude', 'longitude']].head())
    """
    df = df.copy()

    if coord_column not in df.columns:
        raise ValueError(f"Column '{coord_column}' not found in DataFrame")

    def parse_coords(coord_str):
        if pd.isna(coord_str):
            return pd.Series([np.nan, np.nan])

        coord_str = str(coord_str).strip()

        # Try various separators
        for sep in [',', ' ', ';']:
            if sep in coord_str:
                parts = [p.strip() for p in coord_str.split(sep)]
                if len(parts) >= 2:
                    try:
                        lat = float(parts[0])
                        lon = float(parts[1])
                        return pd.Series([lat, lon])
                    except ValueError:
                        continue

        return pd.Series([np.nan, np.nan])

    df[[lat_col, lon_col]] = df[coord_column].apply(parse_coords)

    if drop_original:
        df = df.drop(columns=[coord_column])

    logger.info(f"Split coordinates from '{coord_column}' into '{lat_col}' and '{lon_col}'")

    return df


def merge_columns(
        df: pd.DataFrame,
        columns: List[str],
        new_column: str,
        separator: str = ' ',
        drop_original: bool = True
) -> pd.DataFrame:
    """
    Merge multiple columns into a single column.

    Args:
        df: Input DataFrame
        columns: List of column names to merge
        new_column: Name for the new merged column
        separator: Separator to use between values
        drop_original: Whether to drop the original columns

    Returns:
        DataFrame with merged column

    Example:
        >>> df = merge_columns(df, ['first_name', 'last_name'], 'full_name')
    """
    df = df.copy()

    # Check all columns exist
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"Columns not found: {missing}")

    # Merge columns
    df[new_column] = df[columns].apply(
        lambda row: separator.join(str(val) for val in row if pd.notna(val)),
        axis=1
    )

    if drop_original:
        df = df.drop(columns=columns)

    logger.info(f"Merged columns {columns} into '{new_column}'")

    return df


def fill_missing(
        df: pd.DataFrame,
        strategy: str = 'forward',
        columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Fill missing values using various strategies.

    Strategies:
    - 'forward': Forward fill (use previous value)
    - 'backward': Backward fill (use next value)
    - 'mean': Fill with column mean (numeric only)
    - 'median': Fill with column median (numeric only)
    - 'mode': Fill with most common value
    - 'zero': Fill with 0
    - 'empty': Fill with empty string

    Args:
        df: Input DataFrame
        strategy: Fill strategy
        columns: Columns to fill (None for all)

    Returns:
        DataFrame with filled values

    Example:
        >>> df = fill_missing(df, strategy='forward')
    """
    df = df.copy()

    if columns is None:
        columns = df.columns

    for col in columns:
        if col not in df.columns:
            logger.warning(f"Column '{col}' not found, skipping")
            continue

        if strategy == 'forward':
            # Fixed: Use ffill() instead of deprecated fillna(method='ffill')
            df[col] = df[col].ffill()
        elif strategy == 'backward':
            # Fixed: Use bfill() instead of deprecated fillna(method='bfill')
            df[col] = df[col].bfill()
        elif strategy == 'mean' and pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].mean())
        elif strategy == 'median' and pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
        elif strategy == 'mode':
            mode_val = df[col].mode()
            if len(mode_val) > 0:
                df[col] = df[col].fillna(mode_val[0])
        elif strategy == 'zero':
            df[col] = df[col].fillna(0)
        elif strategy == 'empty':
            df[col] = df[col].fillna('')
        else:
            logger.warning(f"Unknown strategy '{strategy}', skipping column '{col}'")

    logger.info(f"Filled missing values using '{strategy}' strategy")

    return df


def filter_by_value(
        df: pd.DataFrame,
        filters: Dict[str, Any]
) -> pd.DataFrame:
    """
    Filter DataFrame by column values.

    Args:
        df: Input DataFrame
        filters: Dictionary mapping column names to filter values
                Can use operators: '>', '<', '>=', '<=', '!=', 'contains', 'startswith'
                Example: {'cost': '>1000', 'status': 'active', 'name': 'contains:test'}

    Returns:
        Filtered DataFrame

    Example:
        >>> df_filtered = filter_by_value(df, {
        ...     'cost': '>1000',
        ...     'status': 'active',
        ...     'name': 'contains:project'
        ... })
    """
    df = df.copy()

    for col, condition in filters.items():
        if col not in df.columns:
            logger.warning(f"Column '{col}' not found, skipping filter")
            continue

        condition_str = str(condition)

        # Parse operator conditions
        if condition_str.startswith('>='):
            value = float(condition_str[2:])
            df = df[df[col] >= value]
        elif condition_str.startswith('<='):
            value = float(condition_str[2:])
            df = df[df[col] <= value]
        elif condition_str.startswith('!='):
            value = condition_str[2:].strip()
            df = df[df[col] != value]
        elif condition_str.startswith('>'):
            value = float(condition_str[1:])
            df = df[df[col] > value]
        elif condition_str.startswith('<'):
            value = float(condition_str[1:])
            df = df[df[col] < value]
        elif condition_str.startswith('contains:'):
            value = condition_str[9:]
            df = df[df[col].astype(str).str.contains(value, na=False, case=False)]
        elif condition_str.startswith('startswith:'):
            value = condition_str[11:]
            df = df[df[col].astype(str).str.startswith(value, na=False)]
        elif condition_str.startswith('endswith:'):
            value = condition_str[9:]
            df = df[df[col].astype(str).str.endswith(value, na=False)]
        else:
            # Exact match
            df = df[df[col] == condition]

    logger.info(f"Filtered DataFrame: {len(df)} rows remaining")

    return df


def rename_columns(
        df: pd.DataFrame,
        mapping: Dict[str, str],
        inplace: bool = False
) -> pd.DataFrame:
    """
    Rename columns using a mapping dictionary.

    Args:
        df: Input DataFrame
        mapping: Dictionary mapping old names to new names
        inplace: Whether to modify DataFrame in place

    Returns:
        DataFrame with renamed columns

    Example:
        >>> df = rename_columns(df, {
        ...     'old_name_1': 'new_name_1',
        ...     'old_name_2': 'new_name_2'
        ... })
    """
    if not inplace:
        df = df.copy()

    df.rename(columns=mapping, inplace=True)

    logger.info(f"Renamed {len(mapping)} columns")

    return df


def reorder_columns(
        df: pd.DataFrame,
        column_order: List[str],
        keep_others: bool = True
) -> pd.DataFrame:
    """
    Reorder columns in a DataFrame.

    Args:
        df: Input DataFrame
        column_order: Desired order of columns
        keep_others: Whether to keep columns not in column_order at the end

    Returns:
        DataFrame with reordered columns

    Example:
        >>> df = reorder_columns(df, ['id', 'name', 'date', 'cost'])
    """
    df = df.copy()

    # Filter to existing columns
    existing_order = [col for col in column_order if col in df.columns]

    if keep_others:
        # Add remaining columns
        remaining = [col for col in df.columns if col not in existing_order]
        final_order = existing_order + remaining
    else:
        final_order = existing_order

    df = df[final_order]

    logger.info(f"Reordered columns: {len(final_order)} columns")

    return df


def group_and_aggregate(
        df: pd.DataFrame,
        group_by: Union[str, List[str]],
        aggregations: Dict[str, Union[str, List[str]]]
) -> pd.DataFrame:
    """
    Group DataFrame and apply aggregations.

    Args:
        df: Input DataFrame
        group_by: Column(s) to group by
        aggregations: Dictionary mapping column names to aggregation functions
                     Functions: 'sum', 'mean', 'median', 'min', 'max', 'count', 'first', 'last'

    Returns:
        Aggregated DataFrame

    Example:
        >>> df_agg = group_and_aggregate(
        ...     df,
        ...     group_by='category',
        ...     aggregations={'cost': ['sum', 'mean'], 'count': 'count'}
        ... )
    """
    logger.info(f"Grouping by {group_by}")

    grouped = df.groupby(group_by)
    result = grouped.agg(aggregations).reset_index()

    # Flatten multi-level columns if necessary
    if isinstance(result.columns, pd.MultiIndex):
        result.columns = ['_'.join(col).strip('_') for col in result.columns.values]

    logger.info(f"Aggregation complete: {len(result)} groups")

    return result


def sample_data(
        df: pd.DataFrame,
        n: Optional[int] = None,
        frac: Optional[float] = None,
        random_state: Optional[int] = None
) -> pd.DataFrame:
    """
    Sample random rows from DataFrame.

    Args:
        df: Input DataFrame
        n: Number of rows to sample (use either n or frac, not both)
        frac: Fraction of rows to sample (0.0 to 1.0)
        random_state: Random seed for reproducibility

    Returns:
        Sampled DataFrame

    Example:
        >>> df_sample = sample_data(df, n=100, random_state=42)
        >>> df_sample = sample_data(df, frac=0.1)
    """
    if n is None and frac is None:
        raise ValueError("Must specify either 'n' or 'frac'")

    if n is not None and frac is not None:
        raise ValueError("Cannot specify both 'n' and 'frac'")

    sample = df.sample(n=n, frac=frac, random_state=random_state)

    logger.info(f"Sampled {len(sample)} rows from DataFrame")

    return sample


def compare_dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> Dict[str, Any]:
    """
    Compare two DataFrames and return differences.

    Args:
        df1: First DataFrame
        df2: Second DataFrame

    Returns:
        Dictionary containing comparison results

    Example:
        >>> comparison = compare_dataframes(df_old, df_new)
        >>> print(comparison['shape_changed'])
    """
    comparison = {
        'shape_changed': df1.shape != df2.shape,
        'shape_df1': df1.shape,
        'shape_df2': df2.shape,
        'columns_changed': set(df1.columns) != set(df2.columns),
        'columns_added': list(set(df2.columns) - set(df1.columns)),
        'columns_removed': list(set(df1.columns) - set(df2.columns)),
        'dtypes_changed': {},
    }

    # Check dtype changes for common columns
    common_cols = set(df1.columns) & set(df2.columns)
    for col in common_cols:
        if df1[col].dtype != df2[col].dtype:
            comparison['dtypes_changed'][col] = {
                'df1': str(df1[col].dtype),
                'df2': str(df2[col].dtype)
            }

    return comparison