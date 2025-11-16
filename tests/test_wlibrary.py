"""
Comprehensive Test Suite for wlibrary
======================================

Tests all major functionality of the library.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import json

# Import wlibrary modules
from wlibrary import (
    import_excel, get_sheets, preview_data,
    clean_data, normalize_columns,
    detect_structure, infer_types, get_metadata,
    export_data
)
from wlibrary.cleaner import (
    normalize_column_name,
    remove_empty_rows,
    remove_empty_columns,
    clean_whitespace,
    normalize_dates,
    normalize_numeric
)
from wlibrary.analyzer import (
    infer_column_type,
    detect_primary_key,
    find_duplicates,
    suggest_improvements
)
from wlibrary.utils import (
    split_coordinates,
    merge_columns,
    filter_by_value,
    fill_missing,
    group_and_aggregate
)


# ============================================================================
# Test Cleaner Module
# ============================================================================

class TestCleaner:
    """Tests for cleaner.py module."""

    def test_normalize_column_name_english(self):
        """Test English column name normalization."""
        assert normalize_column_name("Object Name") == "object_name"
        assert normalize_column_name("Cost / Price") == "cost_price"
        assert normalize_column_name("Date-Time") == "date_time"

    def test_normalize_column_name_cyrillic(self):
        """Test Cyrillic column name normalization."""
        assert normalize_column_name("Назва об'єкта") == "object_name"
        assert normalize_column_name("Адреса") == "address"
        assert normalize_column_name("Вартість") == "cost"

    def test_normalize_column_name_mixed(self):
        """Test mixed language column names."""
        result = normalize_column_name("Object Назва")
        assert result in ["object_nazva", "object_name"]  # Either is acceptable

    def test_normalize_columns_dataframe(self):
        """Test normalizing all DataFrame columns."""
        df = pd.DataFrame({
            'Object Name': [1, 2],
            'Cost / Price': [100, 200],
            'Назва': ['A', 'B']
        })

        df_norm = normalize_columns(df)

        assert 'object_name' in df_norm.columns
        assert 'cost_price' in df_norm.columns
        assert len(df_norm.columns) == 3

    def test_remove_empty_rows(self):
        """Test removing empty rows."""
        df = pd.DataFrame({
            'a': [1, None, 3, None],
            'b': [2, None, 4, None],
            'c': [3, None, 5, 6]
        })

        df_clean = remove_empty_rows(df, threshold=0.5)

        # Rows with less than 50% data should be removed
        assert len(df_clean) == 3  # Keep rows 0, 2, 3

    def test_remove_empty_columns(self):
        """Test removing empty columns."""
        df = pd.DataFrame({
            'a': [1, 2, 3],
            'b': [None, None, None],
            'c': [4, 5, 6]
        })

        df_clean = remove_empty_columns(df, threshold=0.5)

        assert 'a' in df_clean.columns
        assert 'b' not in df_clean.columns
        assert 'c' in df_clean.columns

    def test_clean_whitespace(self):
        """Test whitespace cleaning."""
        df = pd.DataFrame({
            'name': ['  John  ', ' Jane ', 'Bob  ']
        })

        df_clean = clean_whitespace(df)

        assert df_clean['name'].iloc[0] == 'John'
        assert df_clean['name'].iloc[1] == 'Jane'
        assert df_clean['name'].iloc[2] == 'Bob'

    def test_normalize_numeric(self):
        """Test numeric normalization."""
        df = pd.DataFrame({
            'cost': ['$1,000', '2000', '3,500.50']
        })

        df_norm = normalize_numeric(df, numeric_columns=['cost'])

        assert df_norm['cost'].dtype in [np.float64, float]
        assert df_norm['cost'].iloc[0] == 1000.0
        assert df_norm['cost'].iloc[2] == 3500.50

    def test_clean_data_pipeline(self):
        """Test full cleaning pipeline."""
        df = pd.DataFrame({
            'Object Name': ['  Item A  ', None, 'Item C'],
            'Cost': ['$100', '200', None],
            'Empty': [None, None, None]
        })

        df_clean = clean_data(df, empty_threshold=0.9)

        # Should normalize columns, clean whitespace, remove empty column
        assert 'object_name' in df_clean.columns
        assert 'Empty' not in df_clean.columns or 'empty' not in df_clean.columns
        assert len(df_clean) > 0


# ============================================================================
# Test Analyzer Module
# ============================================================================

class TestAnalyzer:
    """Tests for analyzer.py module."""

    def test_infer_column_type_numeric(self):
        """Test numeric type inference."""
        series = pd.Series([1, 2, 3, 4, 5])
        assert infer_column_type(series) == 'numeric'

    def test_infer_column_type_text(self):
        """Test text type inference."""
        series = pd.Series(['This is a long text description'] * 5)
        assert infer_column_type(series) == 'text'

    def test_infer_column_type_categorical(self):
        """Test categorical type inference."""
        series = pd.Series(['A', 'B', 'A', 'B', 'C'] * 10)
        assert infer_column_type(series) == 'categorical'

    def test_infer_column_type_date(self):
        """Test date type inference."""
        series = pd.Series(pd.date_range('2020-01-01', periods=5))
        assert infer_column_type(series) == 'date'

    def test_infer_column_type_boolean(self):
        """Test boolean type inference."""
        series = pd.Series([True, False, True, False])
        assert infer_column_type(series) == 'boolean'

    def test_infer_column_type_id(self):
        """Test ID type inference."""
        series = pd.Series([1, 2, 3, 4, 5], name='id')
        assert infer_column_type(series) == 'id'

    def test_infer_types_dataframe(self):
        """Test inferring types for entire DataFrame."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['A', 'B', 'C'],
            'count': [10, 20, 30],
            'active': [True, False, True]
        })

        types = infer_types(df)

        assert types['id'] == 'id'
        assert types['name'] in ['categorical', 'text']
        assert types['count'] == 'numeric'
        assert types['active'] == 'boolean'

    def test_detect_primary_key(self):
        """Test primary key detection."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['A', 'B', 'C']
        })

        pk = detect_primary_key(df)

        assert pk == 'id'

    def test_detect_primary_key_none(self):
        """Test when no primary key exists."""
        df = pd.DataFrame({
            'name': ['A', 'A', 'B'],
            'value': [1, 2, 3]
        })

        pk = detect_primary_key(df)

        assert pk is None

    def test_detect_structure(self):
        """Test structure detection."""
        df = pd.DataFrame({
            'object_name': ['Building A', 'Building B'],
            'address': ['123 St', '456 Ave'],
            'cost': [1000, 2000],
            'date': pd.date_range('2020-01-01', periods=2)
        })

        structure = detect_structure(df)

        assert structure['entity_type'] == 'objects'
        assert structure['has_costs'] == True
        assert structure['has_dates'] == True
        assert len(structure['key_columns']) > 0

    def test_get_metadata(self):
        """Test metadata extraction."""
        df = pd.DataFrame({
            'a': [1, 2, None, 4],
            'b': ['x', 'y', 'z', 'w']
        })

        metadata = get_metadata(df)

        assert metadata['shape'] == (4, 2)
        assert 0 <= metadata['completeness'] <= 1
        assert 0 <= metadata['quality_score'] <= 100
        assert 'column_statistics' in metadata

    def test_find_duplicates(self):
        """Test duplicate detection."""
        df = pd.DataFrame({
            'id': [1, 2, 2, 3],
            'value': ['a', 'b', 'b', 'c']
        })

        duplicates = find_duplicates(df, subset=['id'])

        assert len(duplicates) == 2  # Rows with id=2

    def test_suggest_improvements(self):
        """Test improvement suggestions."""
        df = pd.DataFrame({
            'id': [1, 1, 2],  # Duplicate ID
            'constant': ['X', 'X', 'X'],  # Single value
            'mostly_empty': [1, None, None]  # High null rate
        })

        suggestions = suggest_improvements(df)

        assert len(suggestions) > 0
        assert any('duplicate' in s.lower() for s in suggestions)


# ============================================================================
# Test Utils Module
# ============================================================================

class TestUtils:
    """Tests for utils.py module."""

    def test_split_coordinates(self):
        """Test coordinate splitting."""
        df = pd.DataFrame({
            'location': ['50.4501, 30.5234', '49.8397,24.0297']
        })

        df_split = split_coordinates(df, 'location')

        assert 'latitude' in df_split.columns
        assert 'longitude' in df_split.columns
        assert df_split['latitude'].iloc[0] == 50.4501
        assert df_split['longitude'].iloc[0] == 30.5234

    def test_merge_columns(self):
        """Test column merging."""
        df = pd.DataFrame({
            'first': ['John', 'Jane'],
            'last': ['Doe', 'Smith']
        })

        df_merged = merge_columns(df, ['first', 'last'], 'full_name', separator=' ')

        assert 'full_name' in df_merged.columns
        assert df_merged['full_name'].iloc[0] == 'John Doe'
        assert 'first' not in df_merged.columns

    def test_filter_by_value_greater_than(self):
        """Test filtering with greater than operator."""
        df = pd.DataFrame({
            'value': [10, 20, 30, 40]
        })

        df_filtered = filter_by_value(df, {'value': '>25'})

        assert len(df_filtered) == 2
        assert df_filtered['value'].min() == 30

    def test_filter_by_value_contains(self):
        """Test filtering with contains operator."""
        df = pd.DataFrame({
            'name': ['apple', 'banana', 'grape', 'pineapple']
        })

        df_filtered = filter_by_value(df, {'name': 'contains:apple'})

        assert len(df_filtered) == 2

    def test_fill_missing_forward(self):
        """Test forward fill strategy."""
        df = pd.DataFrame({
            'value': [1, None, None, 4]
        })

        df_filled = fill_missing(df, strategy='forward')

        assert df_filled['value'].iloc[1] == 1
        assert df_filled['value'].iloc[2] == 1

    def test_fill_missing_mean(self):
        """Test mean fill strategy."""
        df = pd.DataFrame({
            'value': [10, None, 30, None]
        })

        df_filled = fill_missing(df, strategy='mean', columns=['value'])

        assert df_filled['value'].iloc[1] == 20.0
        assert df_filled['value'].iloc[3] == 20.0

    def test_group_and_aggregate(self):
        """Test grouping and aggregation."""
        df = pd.DataFrame({
            'category': ['A', 'A', 'B', 'B'],
            'value': [10, 20, 30, 40]
        })

        df_agg = group_and_aggregate(
            df,
            group_by='category',
            aggregations={'value': ['sum', 'mean']}
        )

        assert len(df_agg) == 2
        assert 'category' in df_agg.columns


# ============================================================================
# Test Exporter Module
# ============================================================================

class TestExporter:
    """Tests for exporter.py module."""

    def test_export_to_json(self):
        """Test JSON export."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['A', 'B', 'C']
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.json"
            export_data(df, output_path)

            assert output_path.exists()

            # Verify content
            with open(output_path, 'r') as f:
                data = json.load(f)
                assert len(data) == 3

    def test_export_to_csv(self):
        """Test CSV export."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['A', 'B', 'C']
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.csv"
            export_data(df, output_path)

            assert output_path.exists()

            # Verify content
            df_read = pd.read_csv(output_path)
            assert len(df_read) == 3

    def test_export_to_excel(self):
        """Test Excel export."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['A', 'B', 'C']
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.xlsx"
            export_data(df, output_path)

            assert output_path.exists()

            # Verify content
            df_read = pd.read_excel(output_path)
            assert len(df_read) == 3

    def test_export_auto_detect_format(self):
        """Test automatic format detection from extension."""
        df = pd.DataFrame({'a': [1, 2]})

        with tempfile.TemporaryDirectory() as tmpdir:
            # Test different extensions
            for ext in ['.json', '.csv', '.xlsx']:
                output_path = Path(tmpdir) / f"test{ext}"
                export_data(df, output_path)
                assert output_path.exists()


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_pipeline(self):
        """Test complete import -> clean -> analyze -> export pipeline."""
        # Create sample DataFrame
        df = pd.DataFrame({
            'Object Name': ['  Building A  ', 'Building B', None],
            'Cost': ['$1,000', '2000', '3000'],
            'Status': ['Active', 'Active', 'Inactive']
        })

        # Clean
        df_clean = clean_data(df)

        # Analyze
        structure = detect_structure(df_clean)
        types = infer_types(df_clean)
        metadata = get_metadata(df_clean)

        # Verify results
        assert len(df_clean.columns) > 0
        assert structure is not None
        assert len(types) == len(df_clean.columns)
        assert metadata['quality_score'] >= 0

        # Export
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.json"
            export_data(df_clean, output_path)
            assert output_path.exists()


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])