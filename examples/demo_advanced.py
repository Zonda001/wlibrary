"""
Advanced Features Demo - wlibrary
==================================

Demonstrates advanced data processing, filtering, grouping, and utilities.
"""

import wlibrary as w
from wlibrary.utils import (
    split_coordinates,
    merge_columns,
    filter_by_value,
    group_and_aggregate,
    fill_missing,
    reorder_columns,
    compare_dataframes
)
from wlibrary.analyzer import suggest_improvements, find_duplicates
from pathlib import Path
import pandas as pd


def demo_coordinate_handling():
    """Demonstrate coordinate splitting."""
    print("\n" + "=" * 80)
    print(" Coordinate Handling")
    print("=" * 80)

    # Create sample data with coordinates
    df = pd.DataFrame({
        'name': ['Location A', 'Location B', 'Location C'],
        'coordinates': ['50.4501, 30.5234', '49.8397,24.0297', '48.4647 35.0462']
    })

    print("\nOriginal data:")
    print(df)

    # Split coordinates
    df = split_coordinates(df, 'coordinates', lat_col='latitude', lon_col='longitude')

    print("\nAfter splitting coordinates:")
    print(df)


def demo_column_operations():
    """Demonstrate column merging and renaming."""
    print("\n" + "=" * 80)
    print(" Column Operations")
    print("=" * 80)

    # Create sample data
    df = pd.DataFrame({
        'first_name': ['John', 'Jane', 'Bob'],
        'last_name': ['Doe', 'Smith', 'Johnson'],
        'age': [30, 25, 35]
    })

    print("\nOriginal data:")
    print(df)

    # Merge columns
    df = merge_columns(df, ['first_name', 'last_name'], 'full_name', separator=' ')

    print("\nAfter merging first_name and last_name:")
    print(df)

    # Reorder columns
    df = reorder_columns(df, ['full_name', 'age'])

    print("\nAfter reordering columns:")
    print(df)


def demo_filtering():
    """Demonstrate advanced filtering."""
    print("\n" + "=" * 80)
    print(" Advanced Filtering")
    print("=" * 80)

    # Create sample data
    df = pd.DataFrame({
        'product': ['Laptop', 'Phone', 'Tablet', 'Monitor', 'Keyboard'],
        'price': [1200, 800, 500, 300, 50],
        'category': ['Electronics', 'Electronics', 'Electronics', 'Accessories', 'Accessories'],
        'status': ['active', 'active', 'discontinued', 'active', 'active']
    })

    print("\nOriginal data:")
    print(df)

    # Filter: price > 400 AND status = 'active'
    df_filtered = filter_by_value(df, {
        'price': '>400',
        'status': 'active'
    })

    print("\nFiltered (price > 400 AND status = 'active'):")
    print(df_filtered)

    # Filter: product contains 'top'
    df_filtered2 = filter_by_value(df, {
        'product': 'contains:top'
    })

    print("\nFiltered (product contains 'top'):")
    print(df_filtered2)


def demo_grouping():
    """Demonstrate grouping and aggregation."""
    print("\n" + "=" * 80)
    print(" Grouping and Aggregation")
    print("=" * 80)

    # Create sample data
    df = pd.DataFrame({
        'category': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C'],
        'sales': [100, 150, 200, 300, 250, 400, 500, 600],
        'quantity': [10, 15, 20, 30, 25, 40, 50, 60]
    })

    print("\nOriginal data:")
    print(df)

    # Group by category and aggregate
    df_agg = group_and_aggregate(
        df,
        group_by='category',
        aggregations={
            'sales': ['sum', 'mean', 'max'],
            'quantity': ['sum', 'mean']
        }
    )

    print("\nGrouped by category with aggregations:")
    print(df_agg)


def demo_missing_values():
    """Demonstrate missing value handling."""
    print("\n" + "=" * 80)
    print(" Missing Value Handling")
    print("=" * 80)

    # Create sample data with missing values
    df = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'value': [10, None, 30, None, 50],
        'category': ['A', None, 'B', 'B', None]
    })

    print("\nOriginal data with missing values:")
    print(df)

    # Forward fill
    df_ffill = fill_missing(df.copy(), strategy='forward')
    print("\nForward fill strategy:")
    print(df_ffill)

    # Fill with mean (numeric columns only)
    df_mean = fill_missing(df.copy(), strategy='mean', columns=['value'])
    print("\nFill 'value' with mean:")
    print(df_mean)


def demo_data_quality():
    """Demonstrate data quality analysis."""
    print("\n" + "=" * 80)
    print(" Data Quality Analysis")
    print("=" * 80)

    # Create sample data with issues
    df = pd.DataFrame({
        'id': [1, 2, 3, 3, 5],  # Duplicate ID
        'name': ['Item A', None, 'Item C', 'Item C', 'Item E'],
        'price': [100, 200, None, 300, 400],
        'constant': ['X', 'X', 'X', 'X', 'X']  # Single value column
    })

    print("\nSample data:")
    print(df)

    # Get improvement suggestions
    suggestions = suggest_improvements(df)

    print("\n Data Quality Suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")

    # Find duplicates
    duplicates = find_duplicates(df, subset=['id'])

    if len(duplicates) > 0:
        print(f"\n️  Found {len(duplicates)} duplicate rows:")
        print(duplicates)


def demo_comparison():
    """Demonstrate DataFrame comparison."""
    print("\n" + "=" * 80)
    print(" DataFrame Comparison")
    print("=" * 80)

    # Create two versions of data
    df1 = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['A', 'B', 'C'],
        'value': [10, 20, 30]
    })

    df2 = pd.DataFrame({
        'id': [1, 2, 3, 4],
        'name': ['A', 'B', 'C', 'D'],
        'value': [10, 25, 30, 40],
        'new_column': ['X', 'Y', 'Z', 'W']
    })

    print("\nDataFrame 1:")
    print(df1)

    print("\nDataFrame 2:")
    print(df2)

    # Compare
    comparison = compare_dataframes(df1, df2)

    print("\n Comparison Results:")
    print(f"Shape changed: {comparison['shape_changed']}")
    print(f"  DF1: {comparison['shape_df1']}")
    print(f"  DF2: {comparison['shape_df2']}")
    print(f"Columns added: {comparison['columns_added']}")
    print(f"Columns removed: {comparison['columns_removed']}")
    if comparison['dtypes_changed']:
        print(f"Data types changed: {comparison['dtypes_changed']}")


def main():
    """Run all advanced demos."""
    print("=" * 80)
    print("wlibrary - Advanced Features Demo")
    print("=" * 80)

    demo_coordinate_handling()
    demo_column_operations()
    demo_filtering()
    demo_grouping()
    demo_missing_values()
    demo_data_quality()
    demo_comparison()

    print("\n" + "=" * 80)
    print(" All advanced demos completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()