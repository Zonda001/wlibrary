"""
Basic Usage Demo - wlibrary
============================

This script demonstrates basic import, cleaning, and export operations.
"""

import wlibrary as w
from pathlib import Path


def main():
    """Run basic wlibrary demo."""

    print("=" * 80)
    print("wlibrary - Basic Usage Demo")
    print("=" * 80)
    print()

    # Example file path - adjust to your actual file
    file_path = "data/sample.xlsx"  # Replace with your Excel file

    # Check if file exists
    if not Path(file_path).exists():
        print(f"File not found: {file_path}")
        print("Please update the file_path variable with your Excel file.")
        return

    # 1. List available sheets
    print("Step 1: Listing available sheets...")
    sheets = w.sheets(file_path)
    print(f"Found {len(sheets)} sheets: {sheets}")
    print()

    # 2. Preview data
    print("Step 2: Previewing first 5 rows...")
    preview = w.preview(file_path, rows=5)
    print(preview)
    print()

    # 3. Import full data
    print("Step 3: Importing Excel file...")
    df = w.read(file_path, sheet_name=sheets[0])
    print(f"Imported {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")
    print()

    # 4. Clean data
    print("Step 4: Cleaning data...")
    df_clean = w.clean(df)
    print(f"Cleaned data: {len(df_clean)} rows, {len(df_clean.columns)} columns")
    print(f"Normalized columns: {list(df_clean.columns)}")
    print()

    # 5. Analyze structure
    print("Step 5: Analyzing data structure...")
    structure = w.analyze(df_clean)
    print(f"Entity type: {structure['entity_type']}")
    print(f"Key columns: {structure['key_columns']}")
    print(f"Has coordinates: {structure['has_coordinates']}")
    print(f"Has dates: {structure['has_dates']}")
    print(f"Has costs: {structure['has_costs']}")
    print()

    # 6. Get metadata
    print("Step 6: Getting metadata...")
    metadata = w.meta(df_clean)
    print(f"Quality score: {metadata['quality_score']}/100")
    print(f"Completeness: {metadata['completeness']:.1%}")
    print(f"Memory usage: {metadata['memory_usage_mb']:.2f} MB")
    print()

    # 7. Infer column types
    print("Step 7: Inferring column types...")
    types = w.types(df_clean)
    for col, col_type in types.items():
        print(f"  - {col}: {col_type}")
    print()

    # 8. Export to different formats
    print("Step 8: Exporting data...")

    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Export to JSON
    w.save(df_clean, output_dir / "data.json")
    print(f"Exported to {output_dir / 'data.json'}")

    # Export to CSV
    w.save(df_clean, output_dir / "data.csv")
    print(f"Exported to {output_dir / 'data.csv'}")

    # Export to Excel
    w.save(df_clean, output_dir / "data_clean.xlsx", sheet_name="Clean Data")
    print(f"Exported to {output_dir / 'data_clean.xlsx'}")

    # Export to Markdown
    w.save(df_clean, output_dir / "data.md", max_rows=20)
    print(f"Exported to {output_dir / 'data.md'}")

    print()
    print("=" * 80)
    print("Demo completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()