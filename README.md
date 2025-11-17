# wlibrary

Python library for intelligent Excel file processing with automatic data cleaning and type detection.

```python
import wlibrary as w

df = w.read("data.xlsx")
df = w.clean(df)
w.save(df, "clean.json")
```

## Installation

```bash
pip install wlibrary
```

## Quick Start

```python
import wlibrary as w

# Read Excel file
df = w.read("file.xlsx")

# Clean and normalize data
df = w.clean(df)

# Save to any format
w.save(df, "output.json")
```

## Features

- **Smart Reading**: Automatically handles merged cells and complex structures
- **Extended Type Detection**: Detects emails, phone numbers, URLs, currency, coordinates, and more
- **Quality Analysis**: Provides quality scores and identifies data issues
- **Auto-Cleaning**: Normalizes column names, removes empty rows, cleans whitespace
- **Fast Performance**: 3x faster with built-in caching
- **Memory Efficient**: 30% memory reduction with automatic optimization

## Core Functions

### Reading Files
```python
w.read("file.xlsx")              # Read Excel file with caching
w.sheets("file.xlsx")            # Get list of sheet names
w.preview("file.xlsx", rows=10)  # Preview first N rows
w.info("file.xlsx")              # Get file information
```

### Data Analysis
```python
w.types(df, extended=True)       # Detect column types
w.analyze(df)                    # Full structure analysis
w.suggest(df)                    # Get improvement suggestions
w.dups(df)                       # Find duplicate rows
```

### Data Cleaning
```python
w.clean(df)                      # Complete cleaning pipeline
w.normalize(df)                  # Normalize column names only
```

### Exporting Data
```python
w.save(df, "output.json")        # JSON
w.save(df, "output.csv")         # CSV
w.save(df, "output.xlsx")        # Excel
```

### Quick Operations
```python
w.quick("file.xlsx")             # Generate quality report
w.pipeline("file.xlsx")          # Complete processing pipeline
```

## Type Detection

Automatically detects 17+ data types:

**Basic Types:**
- numeric, date, categorical, text, boolean, id

**Extended Types:**
- email, phone, url, uuid, ipv4, currency, coordinate, postal_code, address, json

Example:
```python
types = w.types(df, extended=True)
for col, info in types.items():
    print(f"{col}: {info['type']} (confidence: {info['confidence']:.0%})")
```

## Quality Analysis

Get comprehensive quality metrics:

```python
info = w.analyze(df)
print(f"Quality Score: {info['quality_metrics']['score']}/100")
print(f"Completeness: {info['quality_metrics']['avg_completeness']:.0%}")
```

Automatically detects issues:
- Duplicate rows
- High null rates (>50% missing)
- Outliers (>3 IQR)
- Single-value columns
- Inconsistent formats

## Examples

### Basic Cleaning
```python
import wlibrary as w

df = w.read("messy_data.xlsx")
df = w.clean(df)
w.save(df, "cleaned_data.xlsx")
```

### Quality Report
```python
import wlibrary as w

report = w.quick("data.xlsx")
print(report)
```

Output:
```
FILE: data.xlsx
Quality: 85/100
Issues: 3
  - duplicates: 5 rows (5%)
  - high_nulls: column1 (60%)
Suggestions:
  - [HIGH] Remove duplicate rows
  - [MEDIUM] Fill or remove high-null columns
```

### Finding Specific Data
```python
import wlibrary as w

df = w.read("contacts.xlsx")
types = w.types(df, extended=True)

# Find email columns
email_cols = [col for col, info in types.items() if info['type'] == 'email']
print(f"Email columns: {email_cols}")
```

### Batch Processing
```python
import wlibrary as w
from pathlib import Path

for file in Path("data").glob("*.xlsx"):
    result = w.pipeline(str(file))
    print(f"{file.name}: Quality {result['score']}/100")
    w.save(result['df'], f"clean/{file.stem}.json")
```

## Performance

Built-in caching makes repeat operations 3x faster:

```python
# First read: normal speed
df = w.read("large_file.xlsx")  # 2.5 seconds

# Cached read: very fast
df = w.read("large_file.xlsx")  # 0.1 seconds
```

Memory optimization reduces usage by 30%:

```python
df = w.read("file.xlsx", optimize=True)  # Automatically downcast types
```

## Cache Management

```python
w.cache()        # Show cache info
w.clear()        # Clear cache
```

## Configuration

Customize behavior:

```python
from wlibrary.config import get_config, set_config

config = get_config()
config.performance.max_workers = 8
config.cleaner.empty_row_threshold = 0.7
set_config(config)
```

Or use a config file:

```json
{
  "performance": {
    "enable_cache": true,
    "max_workers": 4
  },
  "extended_types": {
    "detect_currency": true,
    "detect_email": true
  }
}
```

```python
from wlibrary.config import load_config
load_config("config.json")
```

## Smart Reading

Automatically detect complex Excel structures:

```python
structure = w.smart("complex_file.xlsx")

# Access different parts
print(structure.metadata)      # {'project': 'Name', 'client': 'ACME'}
print(structure.categories)    # ['Category1', 'Category2']
print(structure.table_data)    # Clean DataFrame
```

Or just get the clean table:

```python
df = w.smart_df("complex_file.xlsx")
```

## Help

Built-in documentation:

```python
import wlibrary as w
w.help()
```


## Requirements

- Python 3.10+
- pandas
- openpyxl
- numpy

## License

MIT License

