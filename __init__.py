"""
wlibrary v1.0 - Excel Processing Library
=========================================

Quick Start:
    import wlibrary as w

    # Read
    df = w.read("file.xlsx")              # With cache
    df = w.read("file.xlsx", cache=False) # No cache

    # Clean
    df = w.clean(df)

    # Analyze
    info = w.analyze(df)
    print(f"Quality: {info['quality_metrics']['score']}/100")

    # Save
    w.save(df, "output.json")

Smart Reading:
    # Auto-detect structure
    s = w.smart("file.xlsx")
    print(s.metadata)      # Project info
    print(s.table_data)    # Clean data

    # Just get the table
    df = w.smart_df("file.xlsx")

Extended Types:
    # Detects: email, phone, url, currency, etc.
    types = w.types(df, extended=True)

Performance:
    # Cache info
    w.cache_info()
    w.clear_cache()

    # Memory optimization
    df = w.read("file.xlsx", optimize=True)

Quality:
    # Get suggestions
    suggestions = w.suggest(df)

    # Find issues
    info = w.analyze(df)
    print(info['anomalies'])

Author: Denys Sidorov
Version: 1.0.0
"""

# Core imports
from .reader import (
    import_excel,
    get_sheets,
    preview_data,
    get_file_info,
    clear_cache,
    cache_info,
)

from .cleaner import (
    clean_data,
    normalize_columns,
)

from .analyzer import (
    infer_types,
    detect_structure,
    get_metadata,
    find_duplicates,
    suggest_improvements,
)

from .exporter import (
    export_data,
)

from .smart_reader import (
    smart_read,
    smart_read_to_dataframe,
    SmartStructure,
)

from .multi_sheet_reader import (
    smart_read_all_sheets,
    MultiSheetStructure,
)


# ============================================================================
# Short & Sweet API
# ============================================================================

# Reading
read = import_excel                    # w.read("file.xlsx")
sheets = get_sheets                    # w.sheets("file.xlsx")
preview = preview_data                 # w.preview("file.xlsx", rows=10)
info = get_file_info                  # w.info("file.xlsx")

# Smart reading
smart = smart_read                     # w.smart("file.xlsx") → full structure
smart_df = smart_read_to_dataframe    # w.smart_df("file.xlsx") → just table
smart_all = smart_read_all_sheets     # w.smart_all("file.xlsx") → all sheets

# Cleaning
clean = clean_data                     # w.clean(df)
normalize = normalize_columns          # w.normalize(df)

# Analysis
types = infer_types                    # w.types(df, extended=True)
analyze = detect_structure            # w.analyze(df)
meta = get_metadata                   # w.meta(df)
suggest = suggest_improvements        # w.suggest(df)
dups = find_duplicates               # w.dups(df)

# Export
save = export_data                     # w.save(df, "output.json")

# Cache
cache = cache_info                     # w.cache()
clear = clear_cache                    # w.clear()


# ============================================================================
# Pipeline Functions (Chainable)
# ============================================================================

def pipeline(file_path: str, **kwargs) -> dict:
    """
    Complete analysis pipeline.

    Args:
        file_path: Path to Excel file
        **kwargs: Options (cache, optimize, extended)

    Returns:
        Dict with: df, structure, suggestions

    Example:
        >>> result = w.pipeline("data.xlsx")
        >>> df = result['df']
        >>> print(f"Quality: {result['structure']['quality_metrics']['score']}")
        >>> for s in result['suggestions']:
        ...     print(s)
    """
    # Read
    df = read(
        file_path,
        cache=kwargs.get('cache', True),
        optimize=kwargs.get('optimize', False)
    )

    # Clean
    df_clean = clean(df)

    # Analyze
    structure = analyze(df_clean, extended=kwargs.get('extended', True))

    # Suggestions
    suggestions = suggest(df_clean)

    return {
        'df': df_clean,
        'structure': structure,
        'suggestions': suggestions,
        'score': structure['quality_metrics']['score']
    }


def quick(file_path: str) -> str:
    """
    Quick quality check.

    Returns formatted report.

    Example:
        >>> print(w.quick("data.xlsx"))
    """
    result = pipeline(file_path)

    s = result['structure']

    report = f"""
{'='*60}
FILE: {file_path}
{'='*60}
Shape: {s['row_count']} rows × {s['column_count']} cols
Size: {s['memory_mb']:.1f} MB
Entity: {s['entity_type']}
Quality: {s['quality_metrics']['score']}/100

FEATURES:
  Emails: {'✓' if s['has_emails'] else '✗'}
  Phones: {'✓' if s['has_phones'] else '✗'}
  URLs: {'✓' if s['has_urls'] else '✗'}
  Dates: {'✓' if s['has_dates'] else '✗'}
  Coordinates: {'✓' if s['has_coordinates'] else '✗'}

ISSUES: {len(s['anomalies'])}
"""

    if s['anomalies']:
        report += "\nTop Issues:\n"
        for anom in s['anomalies'][:3]:
            report += f"  • {anom['type']}: {anom.get('column', 'multiple')} "
            report += f"({anom['value']})\n"

    if result['suggestions']:
        report += "\nSuggestions:\n"
        for sug in result['suggestions'][:3]:
            report += f"  • {sug}\n"

    report += "=" * 60

    return report


# ============================================================================
# Version Info
# ============================================================================

__version__ = "2.0.0"
__author__ = "Denys Sidorov"

__all__ = [
    # Reading
    'read', 'sheets', 'preview', 'info',
    'smart', 'smart_df', 'smart_all',

    # Cleaning
    'clean', 'normalize',

    # Analysis
    'types', 'analyze', 'meta', 'suggest', 'dups',

    # Export
    'save',

    # Cache
    'cache', 'clear',

    # Pipelines
    'pipeline', 'quick',

    # Classes
    'SmartStructure', 'MultiSheetStructure',

    # Full names (for clarity)
    'import_excel', 'clean_data', 'infer_types',
    'detect_structure', 'export_data',
    'smart_read', 'smart_read_all_sheets',
]


# ============================================================================
# Quick Help
# ============================================================================

def help():
    """Show quick help."""
    print("""
wlibrary v2.0 - Quick Reference
================================

READING:
  w.read("file.xlsx")              # Read with cache
  w.sheets("file.xlsx")            # List sheets
  w.preview("file.xlsx", rows=10)  # Preview data
  w.info("file.xlsx")              # File info

SMART READING:
  w.smart("file.xlsx")             # Auto-detect structure
  w.smart_df("file.xlsx")          # Just get table
  w.smart_all("file.xlsx")         # All sheets

CLEANING:
  w.clean(df)                      # Clean & normalize
  w.normalize(df)                  # Just normalize columns

ANALYSIS:
  w.types(df, extended=True)       # Detect types
  w.analyze(df)                    # Full analysis
  w.meta(df)                       # Metadata
  w.suggest(df)                    # Improvement tips
  w.dups(df)                       # Find duplicates

EXPORT:
  w.save(df, "out.json")           # Auto-detect format
  w.save(df, "out.csv")            # CSV
  w.save(df, "out.xlsx")           # Excel

CACHE:
  w.cache()                        # Cache info
  w.clear()                        # Clear cache

PIPELINES:
  w.pipeline("file.xlsx")          # Complete analysis
  print(w.quick("file.xlsx"))      # Quick report

OPTIONS:
  w.read("file.xlsx", cache=False)     # No cache
  w.read("file.xlsx", optimize=True)   # Optimize memory
  w.types(df, extended=True)           # Extended types
  w.analyze(df, extended=True)         # Full analysis

    """)


if __name__ == "__main__":
    help()