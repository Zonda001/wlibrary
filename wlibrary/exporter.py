"""
Exporter Module - Data Export Functionality
===========================================

Provides flexible data export to various formats with intelligent
formatting and optimization.
"""

import logging
import json
from pathlib import Path
from typing import Union, Optional, Dict, Any, List

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for NumPy types."""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif pd.isna(obj):
            return None
        return super().default(obj)


def export_to_json(
        df: pd.DataFrame,
        output_path: Union[str, Path],
        orient: str = 'records',
        indent: int = 2,
        ensure_ascii: bool = False
) -> None:
    """
    Export DataFrame to JSON format.

    Args:
        df: DataFrame to export
        output_path: Path for output file
        orient: JSON orientation ('records', 'index', 'columns', 'values', 'split', 'table')
        indent: JSON indentation level
        ensure_ascii: Whether to escape non-ASCII characters

    Example:
        >>> export_to_json(df, "output.json", orient='records')
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Exporting to JSON: {output_path}")

    try:
        # Convert to dict
        data = df.to_dict(orient=orient)

        # Write with custom encoder
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii, cls=NumpyEncoder)

        logger.info(f"Successfully exported {len(df)} rows to {output_path}")

    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        raise


def export_to_csv(
        df: pd.DataFrame,
        output_path: Union[str, Path],
        sep: str = ',',
        encoding: str = 'utf-8',
        index: bool = False,
        **kwargs
) -> None:
    """
    Export DataFrame to CSV format.

    Args:
        df: DataFrame to export
        output_path: Path for output file
        sep: Column separator
        encoding: File encoding
        index: Whether to include index
        **kwargs: Additional arguments for pandas.to_csv

    Example:
        >>> export_to_csv(df, "output.csv")
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Exporting to CSV: {output_path}")

    try:
        df.to_csv(output_path, sep=sep, encoding=encoding, index=index, **kwargs)
        logger.info(f"Successfully exported {len(df)} rows to {output_path}")

    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        raise


def export_to_excel(
        df: pd.DataFrame,
        output_path: Union[str, Path],
        sheet_name: str = 'Sheet1',
        index: bool = False,
        freeze_panes: Optional[tuple] = (1, 0),
        **kwargs
) -> None:
    """
    Export DataFrame to Excel format with formatting.

    Args:
        df: DataFrame to export
        output_path: Path for output file
        sheet_name: Name of the Excel sheet
        index: Whether to include index
        freeze_panes: Tuple (row, col) to freeze panes at (None to disable)
        **kwargs: Additional arguments for pandas.to_excel

    Example:
        >>> export_to_excel(df, "output.xlsx", sheet_name="Data")
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Exporting to Excel: {output_path}")

    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=index, **kwargs)

            # Apply formatting if freeze_panes is specified
            if freeze_panes:
                worksheet = writer.sheets[sheet_name]
                worksheet.freeze_panes = worksheet.cell(
                    row=freeze_panes[0] + 1,
                    column=freeze_panes[1] + 1
                )

        logger.info(f"Successfully exported {len(df)} rows to {output_path}")

    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")
        raise


def export_to_markdown(
        df: pd.DataFrame,
        output_path: Union[str, Path],
        max_rows: Optional[int] = None,
        tablefmt: str = 'pipe'
) -> None:
    """
    Export DataFrame to Markdown table format.

    Args:
        df: DataFrame to export
        output_path: Path for output file
        max_rows: Maximum number of rows to export (None for all)
        tablefmt: Table format ('pipe', 'grid', 'simple', etc.)

    Example:
        >>> export_to_markdown(df, "output.md", max_rows=100)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Exporting to Markdown: {output_path}")

    try:
        export_df = df.head(max_rows) if max_rows else df
        markdown_table = export_df.to_markdown(index=False, tablefmt=tablefmt)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_table)

        logger.info(f"Successfully exported {len(export_df)} rows to {output_path}")

    except Exception as e:
        logger.error(f"Error exporting to Markdown: {e}")
        raise


def export_data(
        df: pd.DataFrame,
        output_path: Union[str, Path],
        format: Optional[str] = None,
        **kwargs
) -> None:
    """
    Export DataFrame to specified format (auto-detect from extension if not specified).

    Supported formats:
    - JSON (.json)
    - CSV (.csv, .tsv)
    - Excel (.xlsx, .xls)
    - Markdown (.md)

    Args:
        df: DataFrame to export
        output_path: Path for output file
        format: Export format ('json', 'csv', 'excel', 'markdown'). Auto-detected if None.
        **kwargs: Additional arguments passed to specific export function

    Raises:
        ValueError: If format is unsupported or cannot be detected

    Example:
        >>> export_data(df, "output.json")  # Auto-detects JSON
        >>> export_data(df, "output.csv", sep=';')  # CSV with custom separator
        >>> export_data(df, "data.xlsx", sheet_name="Results")  # Excel
    """
    output_path = Path(output_path)

    # Auto-detect format from extension if not specified
    if format is None:
        ext = output_path.suffix.lower()
        format_map = {
            '.json': 'json',
            '.csv': 'csv',
            '.tsv': 'csv',
            '.xlsx': 'excel',
            '.xls': 'excel',
            '.md': 'markdown',
            '.markdown': 'markdown',
        }
        format = format_map.get(ext)

        if format is None:
            raise ValueError(
                f"Cannot detect format from extension '{ext}'. "
                f"Supported: {list(format_map.keys())}"
            )

    format = format.lower()

    # Route to appropriate export function
    if format == 'json':
        export_to_json(df, output_path, **kwargs)
    elif format == 'csv':
        if output_path.suffix.lower() == '.tsv':
            kwargs.setdefault('sep', '\t')
        export_to_csv(df, output_path, **kwargs)
    elif format == 'excel':
        export_to_excel(df, output_path, **kwargs)
    elif format == 'markdown':
        export_to_markdown(df, output_path, **kwargs)
    else:
        raise ValueError(
            f"Unsupported format: '{format}'. "
            "Supported formats: json, csv, excel, markdown"
        )


def export_summary(
        df: pd.DataFrame,
        output_path: Union[str, Path],
        include_stats: bool = True,
        include_sample: bool = True,
        sample_rows: int = 5
) -> None:
    """
    Export a comprehensive summary of the DataFrame.

    Creates a text file with:
    - Basic info (shape, columns, dtypes)
    - Statistical summary
    - Sample data

    Args:
        df: DataFrame to summarize
        output_path: Path for output file
        include_stats: Include statistical summary
        include_sample: Include sample data
        sample_rows: Number of sample rows to include

    Example:
        >>> export_summary(df, "summary.txt")
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Exporting summary to: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        # Basic info
        f.write("=" * 80 + "\n")
        f.write("DATAFRAME SUMMARY\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n\n")

        f.write("Columns:\n")
        for col in df.columns:
            f.write(f"  - {col} ({df[col].dtype})\n")
        f.write("\n")

        # Data types
        f.write("Data Types:\n")
        f.write(df.dtypes.to_string())
        f.write("\n\n")

        # Missing values
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            f.write("Missing Values:\n")
            for col, count in null_counts[null_counts > 0].items():
                pct = (count / len(df)) * 100
                f.write(f"  - {col}: {count} ({pct:.1f}%)\n")
            f.write("\n")

        # Statistical summary
        if include_stats:
            f.write("-" * 80 + "\n")
            f.write("STATISTICAL SUMMARY\n")
            f.write("-" * 80 + "\n\n")
            f.write(df.describe(include='all').to_string())
            f.write("\n\n")

        # Sample data
        if include_sample:
            f.write("-" * 80 + "\n")
            f.write(f"SAMPLE DATA (first {sample_rows} rows)\n")
            f.write("-" * 80 + "\n\n")
            f.write(df.head(sample_rows).to_string())
            f.write("\n")

    logger.info(f"Successfully exported summary to {output_path}")