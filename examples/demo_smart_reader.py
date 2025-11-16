"""
Smart Reader Demo - wlibrary
=============================

Demonstrates intelligent structure detection and multi-sheet processing.
"""

import wlibrary as w
from pathlib import Path
import json


def demo_smart_read():
    """Demonstrate smart reading of a single sheet."""
    print("\n" + "=" * 80)
    print("DEMO 1: Smart Reading - Single Sheet")
    print("=" * 80)

    file_path = "A-Frame.xlsx"  # Replace with your file

    if not Path(file_path).exists():
        print(f"File not found: {file_path}")
        print("Please update the file_path variable.")
        return

    print(f"\nReading file: {file_path}")

    # Smart read - automatically detects structure
    structure = w.smart(file_path)

    # Display metadata
    print("\nMetadata (Project Information):")
    print("-" * 80)
    for key, value in structure.metadata.items():
        print(f"  {key}: {value}")

    # Display categories
    print(f"\nCategories Found: {len(structure.categories)}")
    print("-" * 80)
    for i, category in enumerate(structure.categories, 1):
        print(f"  {i}. {category}")

    # Display table info
    if structure.table_data is not None:
        print(f"\nData Table:")
        print("-" * 80)
        print(f"  Rows: {len(structure.table_data)}")
        print(f"  Columns: {len(structure.table_data.columns)}")
        print(f"\n  Column names:")
        for col in structure.table_data.columns:
            print(f"    - {col}")

        print(f"\n  Preview (first 5 rows):")
        print(structure.table_data.head())

    # Display items
    print(f"\nTotal Items: {len(structure.items)}")
    if structure.items:
        print("\n  First item example:")
        first_item = structure.items[0]
        for key, value in first_item.items():
            print(f"    {key}: {value}")

    # Export structure
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / "structure.json", 'w', encoding='utf-8') as f:
        json.dump(structure.to_dict(), f, indent=2, ensure_ascii=False, default=str)

    print(f"\nExported structure to: {output_dir / 'structure.json'}")


def demo_smart_read_dataframe():
    """Demonstrate smart reading with DataFrame output only."""
    print("\n" + "=" * 80)
    print("DEMO 2: Smart Reading - DataFrame Only")
    print("=" * 80)

    file_path = "A-Frame.xlsx"

    if not Path(file_path).exists():
        print(f"File not found: {file_path}")
        return

    # Read only the data table
    df = w.read_smart(file_path)

    print(f"\nDataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    print("\nFirst 10 rows:")
    print(df.head(10))

    # Can now use with regular wlibrary functions
    df_clean = w.clean(df)
    print(f"\nAfter cleaning: {df_clean.shape}")

    # Export
    w.save(df_clean, "output/smart_data.json")
    print("\nExported to: output/smart_data.json")


def demo_multi_sheet_read():
    """Demonstrate reading all sheets at once."""
    print("\n" + "=" * 80)
    print("DEMO 3: Multi-Sheet Reading")
    print("=" * 80)

    file_path = "Закриті об'єкти.xlsx"  # File with multiple projects

    if not Path(file_path).exists():
        print(f"File not found: {file_path}")
        print("This demo requires a file with multiple sheets.")
        return

    print(f"\nReading all sheets from: {file_path}")

    # Read all sheets
    multi = w.smart_all(file_path)

    print(f"\nFound {len(multi.sheets)} sheets with data:")
    print("-" * 80)

    # Display each sheet
    for i, (sheet_name, structure) in enumerate(multi.sheets.items(), 1):
        print(f"\n{i}. Sheet: {sheet_name}")
        print(f"   Project: {structure.metadata.get('project_name', 'N/A')}")
        print(f"   Client: {structure.metadata.get('client', 'N/A')}")
        print(f"   Items: {len(structure.items)}")
        print(f"   Categories: {len(structure.categories)}")
        if structure.categories:
            print(f"   Categories: {', '.join(structure.categories[:3])}")
            if len(structure.categories) > 3:
                print(f"                ... and {len(structure.categories) - 3} more")

    # Get summary
    summary = multi.get_summary()

    print(f"\nSummary:")
    print("-" * 80)
    print(f"  Total projects: {summary['total_projects']}")
    print(f"  Total items: {summary['total_items']}")
    print(f"  Total cost: {summary['total_cost']}")
    print(f"  Total advance: {summary['total_advance']}")
    print(f"  Total remaining: {summary['total_remaining']}")

    # Export summary
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    from wlibrary.multi_sheet_reader import export_multi_sheet_summary, export_multi_sheet_to_excel

    # Export summary JSON
    export_multi_sheet_summary(multi, output_dir / "multi_sheet_summary.json")
    print(f"\nExported summary to: {output_dir / 'multi_sheet_summary.json'}")

    # Export to Excel
    export_multi_sheet_to_excel(multi, output_dir / "multi_sheet_export.xlsx")
    print(f"Exported to Excel: {output_dir / 'multi_sheet_export.xlsx'}")


def demo_compare_projects():
    """Demonstrate project comparison."""
    print("\n" + "=" * 80)
    print("DEMO 4: Compare Projects")
    print("=" * 80)

    file_path = "Закриті об'єкти.xlsx"

    if not Path(file_path).exists():
        print(f"File not found: {file_path}")
        return

    # Read all sheets
    multi = w.smart_all(file_path)

    # Compare projects
    from wlibrary.multi_sheet_reader import compare_projects
    comparison = compare_projects(multi)

    print("\nProject Comparison:")
    print("-" * 80)
    print(comparison.to_string(index=False))

    # Export comparison
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    comparison.to_csv(output_dir / "project_comparison.csv", index=False)
    print(f"\nExported comparison to: {output_dir / 'project_comparison.csv'}")


def demo_specific_sheet():
    """Demonstrate accessing a specific sheet from multi-sheet structure."""
    print("\n" + "=" * 80)
    print("DEMO 5: Access Specific Sheet")
    print("=" * 80)

    file_path = "Закриті об'єкти.xlsx"

    if not Path(file_path).exists():
        print(f"File not found: {file_path}")
        return

    # Read all sheets
    multi = w.smart_all(file_path)

    # List available sheets
    print(f"\nAvailable sheets:")
    for i, sheet_name in enumerate(multi.sheet_names, 1):
        print(f"  {i}. {sheet_name}")

    # Access first sheet
    if multi.sheet_names:
        first_sheet_name = multi.sheet_names[0]
        first_sheet = multi.get_sheet(first_sheet_name)

        print(f"\nAccessing sheet: {first_sheet_name}")
        print(f"  Project: {first_sheet.metadata.get('project_name', 'N/A')}")
        print(f"  Items: {len(first_sheet.items)}")

        # Work with this specific sheet's data
        if first_sheet.table_data is not None:
            print(f"\n  Data preview:")
            print(first_sheet.table_data.head(3))


def main():
    """Run all demos."""
    print("=" * 80)
    print("wlibrary - Smart Reader Demo")
    print("=" * 80)

    try:
        demo_smart_read()
    except Exception as e:
        print(f"Demo 1 error: {e}")

    try:
        demo_smart_read_dataframe()
    except Exception as e:
        print(f"Demo 2 error: {e}")

    try:
        demo_multi_sheet_read()
    except Exception as e:
        print(f"Demo 3 error: {e}")

    try:
        demo_compare_projects()
    except Exception as e:
        print(f"Demo 4 error: {e}")

    try:
        demo_specific_sheet()
    except Exception as e:
        print(f"Demo 5 error: {e}")

    print("\n" + "=" * 80)
    print("Smart Reader demos completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()