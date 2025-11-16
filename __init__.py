"""
wlibrary - Universal Excel File Processing Library
===================================================

A production-grade Python library for intelligent Excel file processing,
designed to handle real-world messy data with automatic structure detection,
cleaning, and normalization.

Main Features:
- Import Excel files of any structure
- Automatic data cleaning and normalization
- Intelligent structure detection and type inference
- Multi-format export (JSON, CSV, XLSX)
- Full Unicode support for multilingual data

Author: Denys Sidorov
Version: 1.0.0
Python: 3.10+
"""

from .reader import import_excel, get_sheets, preview_data
from .cleaner import clean_data, normalize_columns
from .analyzer import detect_structure, infer_types, get_metadata
from .exporter import export_data
from .smart_reader import smart_read, smart_read_to_dataframe, SmartStructure
from .multi_sheet_reader import (
    smart_read_all_sheets,
    MultiSheetStructure,
    export_multi_sheet_summary,
    export_multi_sheet_to_excel,
    compare_projects
)

# Short aliases for practical usage
read = import_excel      # w.read("file.xlsx")
clean = clean_data       # w.clean(df)
analyze = detect_structure  # w.analyze(df)
save = export_data       # w.save(df, "output.json")
preview = preview_data   # w.preview("file.xlsx")
sheets = get_sheets      # w.sheets("file.xlsx")
meta = get_metadata      # w.meta(df)
types = infer_types      # w.types(df)

# Smart reading with structure detection
smart = smart_read       # w.smart("file.xlsx") - full structure
read_smart = smart_read_to_dataframe  # w.read_smart("file.xlsx") - table only

# Multi-sheet reading
smart_all = smart_read_all_sheets  # w.smart_all("file.xlsx") - all sheets

__version__ = "1.0.0"
__author__ = "Woodcom Project"
__all__ = [
    # Full names
    "import_excel",
    "get_sheets",
    "preview_data",
    "clean_data",
    "normalize_columns",
    "detect_structure",
    "infer_types",
    "get_metadata",
    "export_data",
    # Smart reading
    "smart_read",
    "smart_read_to_dataframe",
    "SmartStructure",
    # Multi-sheet reading
    "smart_read_all_sheets",
    "MultiSheetStructure",
    "export_multi_sheet_summary",
    "export_multi_sheet_to_excel",
    "compare_projects",
    # Short aliases
    "read",
    "clean",
    "analyze",
    "save",
    "preview",
    "sheets",
    "meta",
    "types",
    "smart",
    "read_smart",
    "smart_all",
]