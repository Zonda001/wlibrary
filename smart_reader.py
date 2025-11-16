"""
Smart Reader Module - Intelligent Excel Structure Detection
============================================================

Automatically detects and processes complex Excel structures:
- Headers and metadata blocks
- Category sections
- Data tables with proper column names
- Merged cells and complex layouts
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class SmartStructure:
    """Smart structure for storing recognized data."""

    def __init__(self):
        self.metadata = {}  # Header (Object, Client, Cost, etc.)
        self.categories = []  # Categories (Pile foundation, Wooden frame, etc.)
        self.items = []  # Material/work items
        self.table_data = None  # Main data table
        self.summary = {}  # Totals

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'metadata': self.metadata,
            'categories': self.categories,
            'items': self.items,
            'summary': self.summary,
            'table_data': self.table_data.to_dict('records') if self.table_data is not None else None
        }


def detect_header_row(df: pd.DataFrame) -> Optional[int]:
    """
    Find the row with column headers.

    Searches for a row that most resembles headers:
    - Contains keywords (number, name, quantity, price, cost)
    - Has fewest empty values
    - Contains text values

    Args:
        df: DataFrame to analyze

    Returns:
        Header row index or None
    """
    header_keywords = [
        '№', 'number', 'num', '#',
        'name', 'title', 'description', 'item',
        'unit', 'measure', 'uom',
        'quantity', 'qty', 'amount',
        'price', 'cost', 'value', 'total'
    ]

    # Add Ukrainian/Russian keywords
    header_keywords.extend([
        'номер', 'найменування', 'назва', 'наименование',
        'од.вим', 'одиниця', 'ед.изм',
        'кількість', 'количество',
        'ціна', 'цена', 'вартість', 'стоимость'
    ])

    best_row = None
    best_score = 0

    for idx in range(min(20, len(df))):  # Search in first 20 rows
        row = df.iloc[idx]
        score = 0

        # Count keyword matches
        for val in row:
            if pd.notna(val):
                val_lower = str(val).lower().strip()
                if any(kw in val_lower for kw in header_keywords):
                    score += 10

        # Count non-empty cells
        non_empty = row.notna().sum()
        score += non_empty

        # Prefer text values
        text_values = sum(1 for val in row if pd.notna(val) and isinstance(val, str))
        score += text_values * 2

        if score > best_score:
            best_score = score
            best_row = idx

    if best_score > 5:  # Minimum threshold
        logger.info(f"Detected header row at index {best_row} (score: {best_score})")
        return best_row

    return None


def extract_metadata_block(df: pd.DataFrame, header_row: int) -> Dict[str, Any]:
    """
    Extract metadata block before the table (Object, Client, Cost, etc.).

    Args:
        df: DataFrame
        header_row: Header row index

    Returns:
        Dictionary with metadata
    """
    metadata = {}

    # Keywords to search for
    metadata_keywords = {
        "object": "project_name",
        'project': 'project_name',
        'client': 'client',
        'customer': 'client',
        'deadline': 'deadline',
        'date': 'date',
        'cost': 'total_cost',
        'total': 'total_cost',
        'advance': 'advance',
        'prepayment': 'advance',
        'remaining': 'remaining',
        'balance': 'remaining',
        'address': 'address',
        'location': 'address',
    }

    # Add Ukrainian/Russian keywords
    metadata_keywords.update({
        "об'єкт": "project_name",
        'проект': 'project_name',
        'замовник': 'client',
        'клиент': 'client',
        'терміни': 'deadline',
        'термины': 'deadline',
        'дедлайн': 'deadline',
        'вартість': 'total_cost',
        'стоимость': 'total_cost',
        'аванс': 'advance',
        'предоплата': 'advance',
        'залишок': 'remaining',
        'остаток': 'remaining',
        'дата': 'date',
        'адреса': 'address',
        'адрес': 'address',
    })

    # Search in rows before header
    for idx in range(header_row):
        row = df.iloc[idx]

        for col_idx, val in enumerate(row):
            if pd.notna(val):
                val_lower = str(val).lower().strip()

                # Check if this is a keyword
                for keyword, field_name in metadata_keywords.items():
                    if keyword in val_lower:
                        # Look for value in next columns
                        for next_idx in range(col_idx + 1, len(row)):
                            next_val = row.iloc[next_idx]
                            if pd.notna(next_val) and str(next_val).strip():
                                metadata[field_name] = str(next_val).strip()
                                logger.debug(f"Found metadata: {field_name} = {next_val}")
                                break
                        break

    return metadata


def detect_category_rows(df: pd.DataFrame, start_row: int) -> List[Tuple[int, str]]:
    """
    Find rows with categories (Pile foundation, Wooden frame, etc.).

    Categories usually:
    - Are bold (in Excel)
    - Repeat in all columns
    - Don't contain numeric values

    Args:
        df: DataFrame
        start_row: Row to start searching from

    Returns:
        List of tuples (row_index, category_name)
    """
    categories = []

    for idx in range(start_row, len(df)):
        row = df.iloc[idx]

        # Check if all non-empty values are the same
        non_empty_values = [str(v).strip() for v in row if pd.notna(v) and str(v).strip()]

        if len(non_empty_values) >= 3:  # Minimum 3 columns with same value
            unique_values = set(non_empty_values)

            if len(unique_values) == 1:
                category_name = non_empty_values[0]

                # Check that it's not a number
                try:
                    float(category_name.replace(',', '.').replace(' ', ''))
                    continue  # It's a number, not a category
                except:
                    # Check that it's not a header
                    if not any(kw in category_name.lower() for kw in ['№', 'name', 'quantity', 'price', 'найменування', 'кількість', 'ціна']):
                        categories.append((idx, category_name))
                        logger.debug(f"Found category at row {idx}: {category_name}")

    return categories


def extract_data_table(df: pd.DataFrame, header_row: int, categories: List[Tuple[int, str]]) -> pd.DataFrame:
    """
    Extract data table with proper headers.

    Args:
        df: DataFrame
        header_row: Header row index
        categories: List of categories

    Returns:
        Cleaned DataFrame with data
    """
    # Get headers
    headers = df.iloc[header_row].tolist()

    # Normalize headers
    clean_headers = []
    for i, h in enumerate(headers):
        if pd.notna(h) and str(h).strip():
            clean_headers.append(str(h).strip())
        else:
            clean_headers.append(f'column_{i}')

    # Create new DataFrame starting from row after header
    data_df = df.iloc[header_row + 1:].copy()
    data_df.columns = clean_headers

    # Add category column
    data_df['category'] = None

    # Assign categories
    current_category = None
    category_dict = dict(categories)

    rows_to_keep = []

    for idx in data_df.index:
        original_idx = df.index.get_loc(idx)

        # Check if this is a category row
        if original_idx in category_dict:
            current_category = category_dict[original_idx]
            continue

        # Skip empty rows
        if data_df.loc[idx].notna().sum() <= 1:
            continue

        # Add category
        data_df.at[idx, 'category'] = current_category
        rows_to_keep.append(idx)

    # Keep only rows with data
    data_df = data_df.loc[rows_to_keep]

    return data_df.reset_index(drop=True)


def smart_read(file_path: str, **kwargs) -> SmartStructure:
    """
    Smart reading of Excel file with automatic structure recognition.

    Automatically finds:
    - Metadata block (header)
    - Header row
    - Categories
    - Data table

    Args:
        file_path: Path to file
        **kwargs: Additional parameters for import_excel

    Returns:
        SmartStructure with recognized structure

    Example:
        >>> structure = smart_read("A-Frame.xlsx")
        >>> print(structure.metadata['project_name'])
        >>> print(structure.table_data.head())
    """
    from .reader import import_excel

    logger.info(f"Smart reading: {file_path}")

    # Read entire file
    df_raw = import_excel(file_path, handle_merged=True, **kwargs)

    # Create structure
    structure = SmartStructure()

    # 1. Find header row
    header_row = detect_header_row(df_raw)

    if header_row is None:
        logger.warning("Could not detect header row, returning raw data")
        structure.table_data = df_raw
        return structure

    logger.info(f"Header row detected at: {header_row}")

    # 2. Extract metadata
    structure.metadata = extract_metadata_block(df_raw, header_row)
    logger.info(f"Extracted metadata: {list(structure.metadata.keys())}")

    # 3. Find categories
    categories = detect_category_rows(df_raw, header_row + 1)
    structure.categories = [cat[1] for cat in categories]
    logger.info(f"Found {len(categories)} categories: {structure.categories}")

    # 4. Extract data table
    structure.table_data = extract_data_table(df_raw, header_row, categories)
    logger.info(f"Extracted table: {len(structure.table_data)} rows × {len(structure.table_data.columns)} columns")

    # 5. Create structured items
    for _, row in structure.table_data.iterrows():
        item = {
            'category': row.get('category'),
        }
        for col in structure.table_data.columns:
            if col != 'category':
                item[col] = row[col]
        structure.items.append(item)

    return structure


def smart_read_to_dataframe(file_path: str, **kwargs) -> pd.DataFrame:
    """
    Smart reading with return of only the data table.

    Args:
        file_path: Path to file

    Returns:
        DataFrame with cleaned data

    Example:
        >>> df = smart_read_to_dataframe("A-Frame.xlsx")
        >>> print(df.head())
    """
    structure = smart_read(file_path, **kwargs)
    return structure.table_data