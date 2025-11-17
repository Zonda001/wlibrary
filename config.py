"""
Configuration Module - Centralized Settings
============================================

Centralized configuration for wlibrary with ability to load custom settings.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict


@dataclass
class CleanerConfig:
    """Configuration for data cleaning operations."""

    # Empty data thresholds
    empty_row_threshold: float = 0.5
    empty_col_threshold: float = 0.5

    # Whitespace handling
    strip_whitespace: bool = True
    normalize_whitespace: bool = True  # Replace multiple spaces with single

    # Numeric normalization
    remove_currency_symbols: bool = True
    currency_symbols: List[str] = field(default_factory=lambda: ['$', '€', '£', '₴', '₽'])
    decimal_separator: str = '.'
    thousands_separator: str = ','

    # Date normalization
    date_formats: List[str] = field(default_factory=lambda: [
        '%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y',
        '%m/%d/%Y', '%Y/%m/%d', '%d-%m-%Y'
    ])

    # Column name normalization
    transliterate_cyrillic: bool = True
    max_column_name_length: int = 64

    # Translation dictionary for common terms
    column_translations: Dict[str, str] = field(default_factory=lambda: {
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
        'кількість': 'quantity',
        'ціна': 'price',
        'замовник': 'client',
        'клієнт': 'client',
    })


@dataclass
class AnalyzerConfig:
    """Configuration for data analysis operations."""

    # Type inference thresholds
    categorical_unique_ratio: float = 0.05  # Max unique ratio for categorical
    categorical_max_unique: int = 50  # Max unique values for categorical
    text_min_length: int = 100  # Min average length to consider as text
    id_column_patterns: List[str] = field(default_factory=lambda: [
        'id', '_id', 'key', '_key', 'code', 'number', 'num', '№'
    ])

    # Header detection
    header_keywords: List[str] = field(default_factory=lambda: [
        '№', 'number', 'num', '#', 'name', 'title', 'description', 'item',
        'unit', 'measure', 'uom', 'quantity', 'qty', 'amount',
        'price', 'cost', 'value', 'total',
        # Ukrainian/Russian
        'номер', 'найменування', 'назва', 'наименование',
        'од.вим', 'одиниця', 'ед.изм',
        'кількість', 'количество',
        'ціна', 'цена', 'вартість', 'стоимость'
    ])

    # Metadata keywords
    metadata_keywords: Dict[str, str] = field(default_factory=lambda: {
        'object': 'project_name',
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
        # Ukrainian/Russian
        "об'єкт": 'project_name',
        'проект': 'project_name',
        'замовник': 'client',
        'клієнт': 'client',
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

    # Quality scoring weights
    completeness_weight: float = 0.5
    column_count_weight: float = 0.25
    data_size_weight: float = 0.25

    # Duplicate detection
    duplicate_subset_auto: bool = True  # Auto-detect key columns for duplicates


@dataclass
class SmartReaderConfig:
    """Configuration for smart reading operations."""

    # Header detection
    header_search_rows: int = 20
    min_header_score: int = 5

    # Category detection
    category_min_columns: int = 3  # Min columns with same value
    category_exclude_keywords: List[str] = field(default_factory=lambda: [
        '№', 'name', 'quantity', 'price', 'найменування', 'кількість', 'ціна'
    ])

    # Structure confidence
    min_confidence: float = 0.7

    # Table extraction
    skip_empty_rows: bool = True
    skip_single_value_rows: bool = True


@dataclass
class PerformanceConfig:
    """Configuration for performance optimization."""

    # Caching
    enable_cache: bool = True
    cache_max_size: int = 10
    cache_ttl: int = 3600  # seconds

    # Parallel processing
    enable_parallel: bool = True
    max_workers: int = 4
    parallel_threshold: int = 3  # Min sheets to use parallel

    # Memory management
    chunk_size: int = 10000  # Rows per chunk for large files
    use_chunks_threshold: int = 100000  # Min rows to use chunking

    # Read optimization
    read_engine: str = 'auto'  # 'openpyxl', 'xlrd', 'pyxlsb', 'auto'
    data_only: bool = True  # Read only values, not formulas


@dataclass
class ExtendedTypesConfig:
    """Configuration for extended data type detection."""

    enable_extended_types: bool = True

    # Pattern-based types
    email_pattern: str = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    phone_pattern: str = r'^\+?\d[\d\s\-\(\)]{8,20}$'
    url_pattern: str = r'^https?://[^\s]+$'
    uuid_pattern: str = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
    ipv4_pattern: str = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'

    # Currency detection
    detect_currency: bool = True
    currency_patterns: Dict[str, str] = field(default_factory=lambda: {
        'USD': r'\$\s*\d',
        'EUR': r'€\s*\d',
        'GBP': r'£\s*\d',
        'UAH': r'₴\s*\d',
        'RUB': r'₽\s*\d',
    })

    # JSON detection
    detect_json: bool = True
    json_min_confidence: float = 0.8

    # Address detection
    detect_address: bool = True
    address_keywords: List[str] = field(default_factory=lambda: [
        'street', 'st', 'avenue', 'ave', 'road', 'rd', 'boulevard', 'blvd',
        'вул', 'вулиця', 'проспект', 'пр', 'площа', 'пл'
    ])


@dataclass
class Config:
    """Main configuration class combining all settings."""

    cleaner: CleanerConfig = field(default_factory=CleanerConfig)
    analyzer: AnalyzerConfig = field(default_factory=AnalyzerConfig)
    smart_reader: SmartReaderConfig = field(default_factory=SmartReaderConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    extended_types: ExtendedTypesConfig = field(default_factory=ExtendedTypesConfig)

    # Global settings
    log_level: str = 'INFO'
    verbose: bool = False

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """Create Config from dictionary."""
        return cls(
            cleaner=CleanerConfig(**config_dict.get('cleaner', {})),
            analyzer=AnalyzerConfig(**config_dict.get('analyzer', {})),
            smart_reader=SmartReaderConfig(**config_dict.get('smart_reader', {})),
            performance=PerformanceConfig(**config_dict.get('performance', {})),
            extended_types=ExtendedTypesConfig(**config_dict.get('extended_types', {})),
            log_level=config_dict.get('log_level', 'INFO'),
            verbose=config_dict.get('verbose', False),
        )

    @classmethod
    def from_json(cls, json_path: str) -> 'Config':
        """Load configuration from JSON file."""
        with open(json_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)

    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'Config':
        """Load configuration from YAML file."""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert Config to dictionary."""
        return asdict(self)

    def to_json(self, json_path: str) -> None:
        """Save configuration to JSON file."""
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def to_yaml(self, yaml_path: str) -> None:
        """Save configuration to YAML file."""
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, allow_unicode=True)


# Global default configuration instance
_default_config = Config()


def get_config() -> Config:
    """Get current global configuration."""
    return _default_config


def set_config(config: Config) -> None:
    """Set global configuration."""
    global _default_config
    _default_config = config


def load_config(path: str) -> Config:
    """Load configuration from file and set as global."""
    path = Path(path)

    if path.suffix == '.json':
        config = Config.from_json(str(path))
    elif path.suffix in ['.yml', '.yaml']:
        config = Config.from_yaml(str(path))
    else:
        raise ValueError(f"Unsupported config format: {path.suffix}")

    set_config(config)
    return config


def reset_config() -> None:
    """Reset configuration to defaults."""
    global _default_config
    _default_config = Config()


# Example usage:
if __name__ == "__main__":
    # Default config
    config = get_config()
    print("Default cleaner config:")
    print(f"  Empty row threshold: {config.cleaner.empty_row_threshold}")
    print(f"  Transliterate cyrillic: {config.cleaner.transliterate_cyrillic}")

    # Save default config
    config.to_json("wlibrary_config.json")
    print("\nSaved default config to wlibrary_config.json")

    # Load and modify
    config.cleaner.empty_row_threshold = 0.7
    config.performance.max_workers = 8

    print("\nModified config:")
    print(f"  Empty row threshold: {config.cleaner.empty_row_threshold}")
    print(f"  Max workers: {config.performance.max_workers}")