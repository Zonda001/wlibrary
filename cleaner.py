"""
Cleaner Module - Data Cleaning and Normalization
================================================

Provides intelligent data cleaning, normalization, and standardization
for messy Excel data.
"""

import logging
import re
from typing import Dict, List, Optional, Union

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def normalize_column_name(name: str) -> str:
    """
    Normalize a column name to snake_case format.

    Handles:
    - Cyrillic and Latin characters
    - Spaces, dashes, and special characters
    - Multiple languages

    Args:
        name: Original column name

    Returns:
        Normalized column name in snake_case

    Example:
        >>> normalize_column_name("Назва об'єкта")
        'nazva_ob_iekta'
        >>> normalize_column_name("Object Name / Description")
        'object_name_description'
    """
    if not isinstance(name, str):
        return str(name)

    # Common translations for Ukrainian/Russian columns
    translations = {
        'назва': 'name',
        "об'єкт": 'object',
        "об'єкта": 'object',
        'адреса': 'address',
        'координати': 'coordinates',
        'вартість': 'cost',
        'дата': 'date',
        'статус': 'status',
        'примітка': 'note',
        'коментар': 'comment',
        'тип': 'type',
        'категорія': 'category',
    }

    # Convert to lowercase
    name = name.lower().strip()

    # Apply translations
    for uk, en in translations.items():
        name = name.replace(uk, en)

    # Transliterate remaining Cyrillic characters
    cyrillic_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'ґ': 'g', 'д': 'd',
        'е': 'e', 'є': 'ie', 'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i',
        'ї': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ь': '', 'ю': 'iu', 'я': 'ia', 'ы': 'y', 'э': 'e', 'ъ': ''
    }

    for cyr, lat in cyrillic_map.items():
        name = name.replace(cyr, lat)

    # Replace special characters with underscores
    name = re.sub(r'[^\w\s]', '_', name)

    # Replace whitespace with underscores
    name = re.sub(r'\s+', '_', name)

    # Remove multiple consecutive underscores
    name = re.sub(r'_+', '_', name)

    # Remove leading/trailing underscores
    name = name.strip('_')

    # If empty, return default
    if not name:
        return 'column'

    return name


def normalize_columns(df: pd.DataFrame, inplace: bool = False) -> pd.DataFrame:
    """
    Normalize all column names in a DataFrame to snake_case.

    Args:
        df: Input DataFrame
        inplace: Whether to modify the DataFrame in place

    Returns:
        DataFrame with normalized column names

    Example:
        >>> df = normalize_columns(df)
        >>> print(df.columns)
        Index(['object_name', 'address', 'cost', 'date'])
    """
    if not inplace:
        df = df.copy()

    # Create mapping of old to new names
    column_mapping = {}
    new_columns = []
    seen = set()

    for col in df.columns:
        normalized = normalize_column_name(str(col))

        # Handle duplicate column names
        if normalized in seen:
            counter = 1
            while f"{normalized}_{counter}" in seen:
                counter += 1
            normalized = f"{normalized}_{counter}"

        seen.add(normalized)
        new_columns.append(normalized)
        column_mapping[col] = normalized

    df.columns = new_columns

    logger.info(f"Normalized {len(df.columns)} column names")
    if len(column_mapping) <= 10:
        logger.debug(f"Column mapping: {column_mapping}")

    return df


def remove_empty_rows(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """
    Remove rows that are mostly empty.

    Args:
        df: Input DataFrame
        threshold: Fraction of non-null values required to keep a row (0.0 to 1.0)

    Returns:
        DataFrame with empty rows removed

    Example:
        >>> df = remove_empty_rows(df, threshold=0.3)
    """
    initial_rows = len(df)

    # Calculate non-null fraction for each row
    non_null_fraction = df.notna().sum(axis=1) / len(df.columns)

    # Keep rows above threshold
    df = df[non_null_fraction >= threshold].copy()

    removed = initial_rows - len(df)
    if removed > 0:
        logger.info(f"Removed {removed} empty rows (threshold={threshold})")

    return df.reset_index(drop=True)


def remove_empty_columns(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """
    Remove columns that are mostly empty.

    Args:
        df: Input DataFrame
        threshold: Fraction of non-null values required to keep a column (0.0 to 1.0)

    Returns:
        DataFrame with empty columns removed
    """
    initial_cols = len(df.columns)

    # Calculate non-null fraction for each column
    non_null_fraction = df.notna().sum() / len(df)

    # Keep columns above threshold
    keep_cols = non_null_fraction[non_null_fraction >= threshold].index
    df = df[keep_cols].copy()

    removed = initial_cols - len(df.columns)
    if removed > 0:
        logger.info(f"Removed {removed} empty columns (threshold={threshold})")

    return df


def clean_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean whitespace from all string columns.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with cleaned whitespace
    """
    df = df.copy()

    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(
                lambda x: x.strip() if isinstance(x, str) else x
            )

    logger.info("Cleaned whitespace from string columns")
    return df


def normalize_dates(df: pd.DataFrame, date_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Normalize date columns to datetime format.

    Args:
        df: Input DataFrame
        date_columns: List of column names containing dates (auto-detect if None)

    Returns:
        DataFrame with normalized dates
    """
    df = df.copy()

    if date_columns is None:
        # Auto-detect date columns
        date_columns = []
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['date', 'дата', 'time', 'час']):
                date_columns.append(col)

    for col in date_columns:
        if col not in df.columns:
            logger.warning(f"Date column '{col}' not found in DataFrame")
            continue

        try:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            logger.info(f"Normalized date column: {col}")
        except Exception as e:
            logger.warning(f"Could not normalize date column '{col}': {e}")

    return df


def normalize_numeric(df: pd.DataFrame, numeric_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Normalize numeric columns by removing non-numeric characters and converting to numbers.

    Args:
        df: Input DataFrame
        numeric_columns: List of column names containing numbers (auto-detect if None)

    Returns:
        DataFrame with normalized numeric columns
    """
    df = df.copy()

    if numeric_columns is None:
        # Auto-detect numeric columns
        numeric_columns = []
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['cost', 'price', 'вартість', 'ціна', 'sum', 'сума', 'amount']):
                numeric_columns.append(col)

    for col in numeric_columns:
        if col not in df.columns:
            logger.warning(f"Numeric column '{col}' not found in DataFrame")
            continue

        try:
            # Remove non-numeric characters except decimal point and minus
            df[col] = df[col].apply(
                lambda x: re.sub(r'[^\d\.\-]', '', str(x)) if pd.notna(x) else x
            )
            df[col] = pd.to_numeric(df[col], errors='coerce')
            logger.info(f"Normalized numeric column: {col}")
        except Exception as e:
            logger.warning(f"Could not normalize numeric column '{col}': {e}")

    return df


def clean_data(
    df: pd.DataFrame,
    remove_empty: bool = True,
    normalize_cols: bool = True,
    clean_ws: bool = True,
    normalize_nums: bool = True,
    normalize_dt: bool = True,
    empty_threshold: float = 0.5
) -> pd.DataFrame:
    """
    Comprehensive data cleaning pipeline.

    Performs:
    - Column name normalization
    - Empty row/column removal
    - Whitespace cleaning
    - Date normalization
    - Numeric normalization

    Args:
        df: Input DataFrame
        remove_empty: Remove empty rows and columns
        normalize_cols: Normalize column names to snake_case
        clean_ws: Clean whitespace from strings
        normalize_nums: Normalize numeric columns
        normalize_dt: Normalize date columns
        empty_threshold: Threshold for removing empty rows/columns

    Returns:
        Cleaned DataFrame

    Example:
        >>> df = clean_data(df)
        >>> print(df.info())
    """
    logger.info(f"Starting data cleaning pipeline on DataFrame with {len(df)} rows, {len(df.columns)} columns")

    original_shape = df.shape

    # Normalize column names
    if normalize_cols:
        df = normalize_columns(df)

    # Remove empty rows and columns
    if remove_empty:
        df = remove_empty_rows(df, threshold=empty_threshold)
        df = remove_empty_columns(df, threshold=empty_threshold)

    # Clean whitespace
    if clean_ws:
        df = clean_whitespace(df)

    # Normalize dates
    if normalize_dt:
        df = normalize_dates(df)

    # Normalize numeric columns
    if normalize_nums:
        df = normalize_numeric(df)

    logger.info(f"Data cleaning complete. Shape: {original_shape} -> {df.shape}")

    return df