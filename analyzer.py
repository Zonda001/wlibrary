"""
Analyzer Module - Advanced Structure Detection and Type Inference
==================================================================

Intelligent analysis with:
- Extended type detection (email, phone, URL, currency, etc.)
- Quality metrics and scoring
- Anomaly detection
- Actionable suggestions
- Relationship detection
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


# ============================================================================
# Extended Type Detection
# ============================================================================

class TypeDetector:
    """Detects specialized data types."""

    # Regex patterns
    _patterns = {
        'email': re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$', re.I),
        'phone': re.compile(r'^\+?\d[\d\s\-\(\)]{8,20}$'),
        'url': re.compile(r'^https?://[^\s]+$', re.I),
        'uuid': re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', re.I),
        'ipv4': re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'),
        'coordinate': re.compile(r'^-?\d+\.\d+[,\s]+-?\d+\.\d+$'),
    }

    _currency_symbols = ['$', '€', '£', '₴', '₽']

    @classmethod
    def detect(cls, series: pd.Series, extended: bool = True) -> Tuple[str, float, Dict]:
        """
        Detect column type with confidence score.

        Returns:
            (type, confidence, metadata)

        Types:
            Basic: numeric, date, categorical, text, boolean, id, empty
            Extended: email, phone, url, uuid, ipv4, currency, coordinate
        """
        non_null = series.dropna()
        if len(non_null) == 0:
            return 'empty', 1.0, {}

        # Check datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return 'date', 1.0, {}

        # Check numeric
        if pd.api.types.is_numeric_dtype(series):
            # Check if ID
            if pd.api.types.is_integer_dtype(series):
                if series.is_unique and series.min() >= 0:
                    return 'id', 1.0, {}
            return 'numeric', 1.0, {}

        # Check boolean
        if pd.api.types.is_bool_dtype(series):
            return 'boolean', 1.0, {}

        # For object dtype, analyze content
        if series.dtype == 'object' and extended:
            # Try extended types
            ext_type, conf, meta = cls._detect_extended(non_null)
            if conf > 0.7:
                return ext_type, conf, meta

        # Default categorization
        unique_ratio = len(non_null.unique()) / len(non_null)

        if unique_ratio < 0.05 and len(non_null.unique()) < 50:
            return 'categorical', 0.9, {}

        sample = non_null.head(100).astype(str)
        avg_len = sample.str.len().mean()

        if avg_len > 100:
            return 'text', 0.9, {}
        elif unique_ratio < 0.5:
            return 'categorical', 0.8, {}

        return 'text', 0.7, {}

    @classmethod
    def _detect_extended(cls, series: pd.Series) -> Tuple[str, float, Dict]:
        """Detect extended types."""
        sample = series.head(100).astype(str)

        # Email
        email_matches = sample.str.match(cls._patterns['email']).sum()
        if email_matches / len(sample) > 0.7:
            return 'email', email_matches / len(sample), {}

        # Phone
        phone_matches = sample.str.match(cls._patterns['phone']).sum()
        if phone_matches / len(sample) > 0.7:
            return 'phone', phone_matches / len(sample), {}

        # URL
        url_matches = sample.str.match(cls._patterns['url']).sum()
        if url_matches / len(sample) > 0.7:
            return 'url', url_matches / len(sample), {}

        # UUID
        uuid_matches = sample.str.match(cls._patterns['uuid']).sum()
        if uuid_matches / len(sample) > 0.7:
            return 'uuid', uuid_matches / len(sample), {}

        # IPv4
        ipv4_matches = sample.str.match(cls._patterns['ipv4']).sum()
        if ipv4_matches / len(sample) > 0.7:
            return 'ipv4', ipv4_matches / len(sample), {}

        # Currency
        currency_matches = 0
        currency_code = None
        for symbol in cls._currency_symbols:
            matches = sample.str.contains(re.escape(symbol), regex=True).sum()
            if matches > currency_matches:
                currency_matches = matches
                currency_code = {'$': 'USD', '€': 'EUR', '£': 'GBP', '₴': 'UAH', '₽': 'RUB'}.get(symbol)

        if currency_matches / len(sample) > 0.7:
            return 'currency', currency_matches / len(sample), {'currency_code': currency_code}

        # Coordinates
        coord_matches = sample.str.match(cls._patterns['coordinate']).sum()
        if coord_matches / len(sample) > 0.7:
            return 'coordinate', coord_matches / len(sample), {}

        return 'unknown', 0.0, {}


def infer_column_type(series: pd.Series) -> str:
    """
    Infer column type (basic types only).

    Example:
        >>> col_type = infer_column_type(df['column'])
        >>> print(col_type)  # 'numeric'
    """
    type_name, _, _ = TypeDetector.detect(series, extended=False)
    return type_name


def infer_types(df: pd.DataFrame, extended: bool = True) -> Dict[str, Any]:
    """
    Infer types for all columns.

    Args:
        df: Input DataFrame
        extended: Use extended type detection (email, phone, etc.)

    Returns:
        Dictionary with type info for each column

    Example:
        >>> types = infer_types(df, extended=True)
        >>> for col, info in types.items():
        ...     print(f"{col}: {info['type']} ({info['confidence']:.0%})")
    """
    logger.info("Analyzing column types...")

    types = {}
    for col in df.columns:
        type_name, conf, meta = TypeDetector.detect(df[col], extended=extended)
        types[col] = {
            'type': type_name,
            'confidence': conf,
            'metadata': meta
        }
        logger.debug(f"  {col}: {type_name} ({conf:.0%})")

    return types


# ============================================================================
# Structure Detection
# ============================================================================

def detect_primary_key(df: pd.DataFrame) -> Optional[str]:
    """
    Detect primary key column.

    Example:
        >>> pk = detect_primary_key(df)
        >>> print(f"Primary key: {pk}")
    """
    for col in df.columns:
        if df[col].is_unique and df[col].notna().all():
            if 'id' in col.lower():
                return col
            if pd.api.types.is_integer_dtype(df[col]) and df[col].min() >= 0:
                return col
    return None


def detect_structure(df: pd.DataFrame, extended: bool = True) -> Dict[str, Any]:
    """
    Detect DataFrame structure.

    Args:
        df: Input DataFrame
        extended: Use extended analysis

    Returns:
        Dictionary with structure info:
        - entity_type: Type of data (objects, products, people, etc.)
        - column_types: Types for each column
        - primary_key: Detected primary key
        - key_columns: Important identifier columns
        - has_emails, has_phones, etc.: Feature flags
        - quality_metrics: Quality scores (if extended=True)
        - anomalies: Detected issues (if extended=True)
        - suggestions: Improvement suggestions (if extended=True)

    Example:
        >>> structure = detect_structure(df)
        >>> print(f"Entity: {structure['entity_type']}")
        >>> print(f"Quality: {structure['quality_metrics']['score']}/100")
    """
    logger.info("Detecting structure...")

    structure = {
        'row_count': len(df),
        'column_count': len(df.columns),
        'memory_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
    }

    # Type detection
    types = infer_types(df, extended=extended)
    structure['column_types'] = types

    # Primary key
    structure['primary_key'] = detect_primary_key(df)

    # Key columns
    key_cols = []
    for col in df.columns:
        if any(kw in col.lower() for kw in ['name', 'title', 'назва', 'об\'єкт']):
            key_cols.append(col)
    structure['key_columns'] = key_cols

    # Entity type detection
    all_cols = ' '.join(df.columns).lower()

    entity_patterns = {
        'objects': ['object', 'об\'єкт', 'building'],
        'products': ['product', 'товар', 'item', 'sku'],
        'people': ['person', 'employee', 'user'],
        'transactions': ['transaction', 'payment'],
        'locations': ['location', 'address', 'city'],
    }

    scores = {e: sum(1 for kw in kws if kw in all_cols)
              for e, kws in entity_patterns.items()}

    best_entity = max(scores, key=scores.get)
    structure['entity_type'] = best_entity if scores[best_entity] > 0 else 'unknown'

    # Feature flags
    structure['has_emails'] = any(t['type'] == 'email' for t in types.values())
    structure['has_phones'] = any(t['type'] == 'phone' for t in types.values())
    structure['has_urls'] = any(t['type'] == 'url' for t in types.values())
    structure['has_coordinates'] = any(t['type'] == 'coordinate' for t in types.values())
    structure['has_dates'] = any(t['type'] == 'date' for t in types.values())
    structure['has_currency'] = any(t['type'] == 'currency' for t in types.values())

    # Extended analysis
    if extended:
        structure['quality_metrics'] = _calc_quality(df)
        structure['anomalies'] = _detect_anomalies(df)
        structure['suggestions'] = _suggest_fixes(df, structure)

    return structure


# ============================================================================
# Quality Analysis
# ============================================================================

def _calc_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate quality metrics."""
    metrics = {}

    # Completeness (% non-null)
    completeness = {}
    for col in df.columns:
        completeness[col] = 1 - (df[col].isnull().sum() / len(df))

    metrics['completeness'] = completeness
    metrics['avg_completeness'] = sum(completeness.values()) / len(df.columns)

    # Uniqueness (% unique values)
    uniqueness = {}
    for col in df.columns:
        uniqueness[col] = df[col].nunique() / len(df) if len(df) > 0 else 0

    metrics['uniqueness'] = uniqueness
    metrics['avg_uniqueness'] = sum(uniqueness.values()) / len(df.columns)

    # Overall score (0-100)
    score = (
        metrics['avg_completeness'] * 50 +
        min(metrics['avg_uniqueness'], 0.5) * 100 +
        (min(len(df), 10000) / 10000) * 25
    )

    metrics['score'] = round(min(score, 100), 1)

    return metrics


def _detect_anomalies(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Detect data anomalies."""
    anomalies = []

    # High null rate
    for col in df.columns:
        null_pct = df[col].isnull().sum() / len(df) * 100
        if null_pct > 50:
            anomalies.append({
                'type': 'high_nulls',
                'column': col,
                'severity': 'high',
                'value': f"{null_pct:.1f}%"
            })

    # Duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        anomalies.append({
            'type': 'duplicates',
            'severity': 'medium',
            'count': dup_count,
            'value': f"{dup_count / len(df) * 100:.1f}%"
        })

    # Single value columns
    for col in df.columns:
        if df[col].nunique() == 1:
            anomalies.append({
                'type': 'single_value',
                'column': col,
                'severity': 'low',
                'value': str(df[col].iloc[0])
            })

    # Outliers in numeric columns
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1, Q3 = df[col].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        outliers = df[(df[col] < Q1 - 3*IQR) | (df[col] > Q3 + 3*IQR)]

        if len(outliers) > 0:
            anomalies.append({
                'type': 'outliers',
                'column': col,
                'severity': 'medium',
                'count': len(outliers),
                'value': f"{len(outliers) / len(df) * 100:.1f}%"
            })

    return anomalies


def _suggest_fixes(df: pd.DataFrame, structure: Dict) -> List[Dict[str, Any]]:
    """Generate improvement suggestions."""
    suggestions = []

    metrics = structure['quality_metrics']
    anomalies = structure['anomalies']

    # Low completeness
    if metrics['avg_completeness'] < 0.9:
        high_null_cols = [col for col, comp in metrics['completeness'].items() if comp < 0.7]
        suggestions.append({
            'priority': 'HIGH',
            'issue': f"Low completeness ({metrics['avg_completeness']:.0%})",
            'action': "Fill or remove columns with high null rates",
            'columns': high_null_cols
        })

    # Duplicates
    dup_anoms = [a for a in anomalies if a['type'] == 'duplicates']
    if dup_anoms:
        suggestions.append({
            'priority': 'MEDIUM',
            'issue': f"Found {dup_anoms[0]['count']} duplicate rows",
            'action': "Use df.drop_duplicates() to remove"
        })

    # Single value columns
    single_cols = [a['column'] for a in anomalies if a['type'] == 'single_value']
    if single_cols:
        suggestions.append({
            'priority': 'LOW',
            'issue': f"{len(single_cols)} columns with single value",
            'action': "Consider removing these columns",
            'columns': single_cols
        })

    # Outliers
    outlier_cols = [a['column'] for a in anomalies if a['type'] == 'outliers']
    if outlier_cols:
        suggestions.append({
            'priority': 'MEDIUM',
            'issue': f"Outliers in {len(outlier_cols)} columns",
            'action': "Review and handle outliers",
            'columns': outlier_cols
        })

    return suggestions


# ============================================================================
# Utility Functions
# ============================================================================

def get_metadata(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get DataFrame metadata.

    Example:
        >>> meta = get_metadata(df)
        >>> print(f"Quality: {meta['quality_score']}/100")
    """
    return {
        'shape': df.shape,
        'memory_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
        'columns': list(df.columns),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'null_counts': df.isnull().sum().to_dict(),
        'completeness': 1 - (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])),
        'quality_score': _calc_quality(df)['score']
    }


def find_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Find duplicate rows.

    Example:
        >>> dups = find_duplicates(df)
        >>> print(f"Found {len(dups)} duplicates")
    """
    return df[df.duplicated(subset=subset, keep=False)]


def suggest_improvements(df: pd.DataFrame) -> List[str]:
    """
    Get improvement suggestions (simple format).

    Example:
        >>> suggestions = suggest_improvements(df)
        >>> for s in suggestions:
        ...     print(f"• {s}")
    """
    structure = detect_structure(df, extended=True)
    suggestions = structure['suggestions']

    return [
        f"[{s['priority']}] {s['issue']} → {s['action']}"
        for s in suggestions
    ]


# ============================================================================
# Short Aliases
# ============================================================================

types = infer_types              # w.types(df)
analyze = detect_structure       # w.analyze(df)
meta = get_metadata             # w.meta(df)
suggest = suggest_improvements  # w.suggest(df)


# Example usage
if __name__ == "__main__":
    print("Analyzer - Enhanced Version")
    print("=" * 60)

    # Create sample data
    df = pd.DataFrame({
        'id': [1, 2, 3, 3, 5],  # Duplicate
        'email': ['a@test.com', 'b@test.com', 'invalid', None, 'c@test.com'],
        'phone': ['+380501234567', '+380501234568', '123', None, '+380501234569'],
        'price': ['$100', '$200', '$10000', '$150', '$250'],
        'constant': ['X'] * 5,  # Single value
        'mostly_null': [1, None, None, None, None],
    })

    # Test 1: Type detection
    print("\n1. Type Detection (Extended):")
    col_types = types(df, extended=True)
    for col, info in col_types.items():
        print(f"   {col:15s}: {info['type']:12s} ({info['confidence']:.0%})")

    # Test 2: Structure analysis
    print("\n2. Structure Analysis:")
    structure = analyze(df)
    print(f"   Entity type: {structure['entity_type']}")
    print(f"   Quality score: {structure['quality_metrics']['score']}/100")
    print(f"   Has emails: {structure['has_emails']}")
    print(f"   Has phones: {structure['has_phones']}")

    # Test 3: Anomalies
    print("\n3. Detected Anomalies:")
    for anom in structure['anomalies']:
        print(f"   [{anom['severity'].upper()}] {anom['type']}: ", end='')
        if 'column' in anom:
            print(f"{anom['column']} ({anom['value']})")
        else:
            print(f"{anom.get('count', '')} ({anom['value']})")

    # Test 4: Suggestions
    print("\n4. Suggestions:")
    for sug in suggest(df):
        print(f"   • {sug}")

    print("\n" + "=" * 60)
    print("✓ Analysis complete!")