"""
Analyzer Module - Structure Detection and Type Inference
========================================================

Provides intelligent analysis of DataFrame structure, automatic type
detection, and metadata extraction.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def infer_column_type(series: pd.Series) -> str:
    """
    Infer the semantic type of a column.

    Returns one of: 'numeric', 'date', 'categorical', 'text', 'boolean', 'coordinate', 'id'

    Args:
        series: Pandas Series to analyze

    Returns:
        String representing the inferred type

    Example:
        >>> col_type = infer_column_type(df['column_name'])
        >>> print(col_type)  # 'numeric'
    """
    # Remove null values for analysis
    non_null = series.dropna()

    if len(non_null) == 0:
        return 'empty'

    # Check if already datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return 'date'

    # Check if numeric
    if pd.api.types.is_numeric_dtype(series):
        # Check if it looks like an ID (integers in sequence)
        if pd.api.types.is_integer_dtype(series):
            if series.is_unique and series.min() >= 0:
                return 'id'
        return 'numeric'

    # Check if boolean
    if pd.api.types.is_bool_dtype(series):
        return 'boolean'

    # For object dtype, analyze content
    if series.dtype == 'object':
        sample = non_null.head(100).astype(str)

        # Check for coordinates (lat/lon patterns)
        coord_pattern = r'-?\d+\.\d+[,\s]+-?\d+\.\d+'
        if sample.str.match(coord_pattern).mean() > 0.7:
            return 'coordinate'

        # Check for dates
        date_keywords = ['date', 'дата', 'time', 'час']
        if any(kw in series.name.lower() for kw in date_keywords):
            try:
                pd.to_datetime(sample.head(10), errors='coerce')
                return 'date'
            except:
                pass

        # Check for categorical (low cardinality)
        unique_ratio = len(non_null.unique()) / len(non_null)
        if unique_ratio < 0.05 and len(non_null.unique()) < 50:
            return 'categorical'

        # Check average length for text vs categorical
        avg_length = sample.str.len().mean()
        if avg_length > 100:
            return 'text'
        elif unique_ratio < 0.5:
            return 'categorical'
        else:
            return 'text'

    return 'unknown'


def infer_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Infer semantic types for all columns in a DataFrame.

    Args:
        df: Input DataFrame

    Returns:
        Dictionary mapping column names to inferred types

    Example:
        >>> types = infer_types(df)
        >>> print(types)
        {'object_name': 'text', 'cost': 'numeric', 'status': 'categorical'}
    """
    logger.info("Inferring column types...")

    types = {}
    for col in df.columns:
        col_type = infer_column_type(df[col])
        types[col] = col_type
        logger.debug(f"  {col}: {col_type}")

    return types


def detect_primary_key(df: pd.DataFrame) -> Optional[str]:
    """
    Attempt to detect a primary key column.

    Args:
        df: Input DataFrame

    Returns:
        Name of the likely primary key column, or None
    """
    for col in df.columns:
        # Check if column is unique and non-null
        if df[col].is_unique and df[col].notna().all():
            # Prefer columns with 'id' in name
            if 'id' in col.lower():
                logger.info(f"Detected primary key: {col}")
                return col
            # Or numeric columns that look like IDs
            if pd.api.types.is_integer_dtype(df[col]) and df[col].min() >= 0:
                logger.info(f"Detected possible primary key: {col}")
                return col

    logger.info("No primary key detected")
    return None


def detect_structure(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Automatically detect the logical structure of a DataFrame.

    Analyzes:
    - Column types
    - Primary keys
    - Relationships
    - Data quality metrics
    - Common patterns (objects, locations, costs, etc.)

    Args:
        df: Input DataFrame

    Returns:
        Dictionary containing structure analysis

    Example:
        >>> structure = detect_structure(df)
        >>> print(structure['entity_type'])
        'objects'
        >>> print(structure['key_columns'])
        ['object_name', 'address']
    """
    logger.info("Detecting DataFrame structure...")

    structure = {
        'row_count': len(df),
        'column_count': len(df.columns),
        'column_types': infer_types(df),
        'primary_key': detect_primary_key(df),
        'key_columns': [],
        'entity_type': 'unknown',
        'has_coordinates': False,
        'has_dates': False,
        'has_costs': False,
    }

    # Detect key columns (likely identifiers)
    for col in df.columns:
        col_lower = col.lower()
        if any(kw in col_lower for kw in ['name', 'назва', 'title', 'об']):
            structure['key_columns'].append(col)

    # Detect entity type based on column names
    all_columns = ' '.join(df.columns).lower()

    if any(kw in all_columns for kw in ['object', 'об\'єкт', 'building', 'будівля']):
        structure['entity_type'] = 'objects'
    elif any(kw in all_columns for kw in ['product', 'товар', 'item']):
        structure['entity_type'] = 'products'
    elif any(kw in all_columns for kw in ['person', 'people', 'employee', 'користувач']):
        structure['entity_type'] = 'people'
    elif any(kw in all_columns for kw in ['transaction', 'payment', 'платіж']):
        structure['entity_type'] = 'transactions'

    # Check for specific data types
    for col, col_type in structure['column_types'].items():
        if col_type == 'coordinate':
            structure['has_coordinates'] = True
        elif col_type == 'date':
            structure['has_dates'] = True
        elif col_type == 'numeric' and any(kw in col.lower() for kw in ['cost', 'price', 'вартість', 'ціна']):
            structure['has_costs'] = True

    logger.info(f"Detected entity type: {structure['entity_type']}")
    logger.info(f"Key columns: {structure['key_columns']}")

    return structure


def get_metadata(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extract comprehensive metadata about a DataFrame.

    Args:
        df: Input DataFrame

    Returns:
        Dictionary containing metadata

    Example:
        >>> metadata = get_metadata(df)
        >>> print(metadata['completeness'])
        0.95
    """
    logger.info("Extracting metadata...")

    metadata = {
        'shape': df.shape,
        'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
        'columns': list(df.columns),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'null_counts': df.isnull().sum().to_dict(),
        'completeness': (1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])),
    }

    # Column-level statistics
    col_stats = {}
    for col in df.columns:
        stats = {
            'dtype': str(df[col].dtype),
            'null_count': int(df[col].isnull().sum()),
            'unique_count': int(df[col].nunique()),
            'completeness': float(1 - df[col].isnull().sum() / len(df)),
        }

        # Add numeric statistics
        if pd.api.types.is_numeric_dtype(df[col]):
            stats.update({
                'mean': float(df[col].mean()) if df[col].notna().any() else None,
                'median': float(df[col].median()) if df[col].notna().any() else None,
                'min': float(df[col].min()) if df[col].notna().any() else None,
                'max': float(df[col].max()) if df[col].notna().any() else None,
                'std': float(df[col].std()) if df[col].notna().any() else None,
            })

        # Add categorical statistics
        elif df[col].dtype == 'object' or pd.api.types.is_categorical_dtype(df[col]):
            value_counts = df[col].value_counts()
            if len(value_counts) > 0:
                stats.update({
                    'most_common': str(value_counts.index[0]),
                    'most_common_count': int(value_counts.iloc[0]),
                })

        col_stats[col] = stats

    metadata['column_statistics'] = col_stats

    # Data quality score (0-100)
    quality_score = (
            metadata['completeness'] * 50 +  # Completeness: 50 points
            (1 - min(len(df.columns) / 100, 1)) * 25 +  # Not too many columns: 25 points
            (min(len(df) / 10000, 1)) * 25  # Sufficient data: 25 points
    )
    metadata['quality_score'] = round(quality_score, 2)

    logger.info(f"Metadata extraction complete. Quality score: {metadata['quality_score']}/100")

    return metadata


def find_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Find duplicate rows in a DataFrame.

    Args:
        df: Input DataFrame
        subset: Columns to consider for duplicates (None for all columns)

    Returns:
        DataFrame containing only duplicate rows

    Example:
        >>> duplicates = find_duplicates(df, subset=['object_name'])
        >>> print(f"Found {len(duplicates)} duplicates")
    """
    duplicates = df[df.duplicated(subset=subset, keep=False)]

    if len(duplicates) > 0:
        logger.info(f"Found {len(duplicates)} duplicate rows")
    else:
        logger.info("No duplicates found")

    return duplicates


def suggest_improvements(df: pd.DataFrame) -> List[str]:
    """
    Suggest improvements for data quality.

    Args:
        df: Input DataFrame

    Returns:
        List of improvement suggestions

    Example:
        >>> suggestions = suggest_improvements(df)
        >>> for suggestion in suggestions:
        >>>     print(f"- {suggestion}")
    """
    suggestions = []
    metadata = get_metadata(df)
    types = infer_types(df)

    # Check completeness
    if metadata['completeness'] < 0.9:
        suggestions.append(
            f"Low data completeness ({metadata['completeness']:.1%}). "
            "Consider handling missing values."
        )

    # Check for columns with high null rates
    for col, stats in metadata['column_statistics'].items():
        if stats['completeness'] < 0.5:
            suggestions.append(
                f"Column '{col}' has {stats['null_count']} missing values "
                f"({stats['completeness']:.1%} complete). Consider removing or imputing."
            )

    # Check for potential ID columns that aren't unique
    for col in df.columns:
        if 'id' in col.lower() and not df[col].is_unique:
            suggestions.append(
                f"Column '{col}' looks like an ID but contains duplicates. "
                "Verify data integrity."
            )

    # Check for columns with single value
    for col in df.columns:
        if df[col].nunique() == 1:
            suggestions.append(
                f"Column '{col}' has only one unique value. Consider removing."
            )

    # Check for very wide DataFrames
    if len(df.columns) > 50:
        suggestions.append(
            f"DataFrame has {len(df.columns)} columns. "
            "Consider whether all columns are necessary."
        )

    # Check for duplicates
    duplicates = find_duplicates(df)
    if len(duplicates) > 0:
        suggestions.append(
            f"Found {len(duplicates)} duplicate rows. Consider deduplication."
        )

    if not suggestions:
        suggestions.append("Data quality looks good! No major issues detected.")

    return suggestions