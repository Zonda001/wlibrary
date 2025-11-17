import wlibrary as w
import pandas as pd
import numpy as np
from pathlib import Path


def create_sample():
    """Create sample data with various issues."""
    np.random.seed(42)

    df = pd.DataFrame({
        # Basic types
        'id': range(1, 101),
        'name': [f'Product {i}' for i in range(1, 101)],
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'quantity': np.random.randint(1, 100, 100),
        'price': np.random.uniform(10, 1000, 100).round(2),

        # Extended types
        'email': [f'user{i}@test.com' if i % 10 != 0 else None for i in range(1, 101)],
        'phone': [f'+38050{str(i).zfill(7)}' if i % 15 != 0 else None for i in range(1, 101)],
        'website': [f'https://shop{i}.com' if i % 20 != 0 else None for i in range(1, 101)],
        'price_str': [f'${np.random.uniform(100, 1000):.2f}' for _ in range(100)],

        # Issues
        'with_nulls': [i if i % 3 != 0 else None for i in range(100)],
        'constant': ['SAME'] * 100,
    })

    # Add duplicates
    df = pd.concat([df, df.iloc[:3]], ignore_index=True)

    return df


def demo_1_basic():
    """Demo 1: Basic Usage."""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Usage")
    print("=" * 70)

    # Create test file
    df = create_sample()
    df.to_excel("test.xlsx", index=False)

    # Read
    print("\n1. Read file:")
    df = w.read("test.xlsx")
    print(f"   ✓ Loaded {len(df)} rows × {len(df.columns)} cols")

    # Clean
    print("\n2. Clean data:")
    df_clean = w.clean(df)
    print(f"   ✓ Cleaned: {len(df_clean)} rows × {len(df_clean.columns)} cols")

    # Analyze
    print("\n3. Analyze:")
    info = w.analyze(df_clean)
    print(f"   ✓ Entity: {info['entity_type']}")
    print(f"   ✓ Quality: {info['quality_metrics']['score']}/100")

    # Save
    print("\n4. Save:")
    w.save(df_clean, "output.json")
    print(f"   ✓ Saved to output.json")

    # Cleanup
    Path("test.xlsx").unlink()
    Path("output.json").unlink()


def demo_2_smart():
    """Demo 2: Smart Reading."""
    print("\n" + "=" * 70)
    print("DEMO 2: Smart Reading")
    print("=" * 70)

    df = create_sample()
    df.to_excel("test.xlsx", index=False)

    # Smart read
    print("\n1. Smart read (auto-detect structure):")
    s = w.smart("test.xlsx")
    print(f"   ✓ Found {len(s.items)} items")
    print(f"   ✓ Categories: {s.categories}")
    print(f"   ✓ Metadata: {list(s.metadata.keys())}")

    # Or just get table
    print("\n2. Smart read (table only):")
    df = w.smart_df("test.xlsx")
    print(f"   ✓ Table: {len(df)} rows × {len(df.columns)} cols")

    Path("test.xlsx").unlink()


def demo_3_extended_types():
    """Demo 3: Extended Type Detection."""
    print("\n" + "=" * 70)
    print("DEMO 3: Extended Type Detection")
    print("=" * 70)

    df = create_sample()

    print("\n1. Basic types:")
    types_basic = w.types(df, extended=False)
    for col in ['email', 'phone', 'website', 'price_str']:
        print(f"   {col:15s}: {types_basic[col]['type']}")

    print("\n2. Extended types:")
    types_ext = w.types(df, extended=True)
    for col in ['email', 'phone', 'website', 'price_str']:
        info = types_ext[col]
        print(f"   {col:15s}: {info['type']:12s} ({info['confidence']:.0%})")


def demo_4_quality():
    """Demo 4: Quality Analysis."""
    print("\n" + "=" * 70)
    print("DEMO 4: Quality Analysis")
    print("=" * 70)

    df = create_sample()

    # Analyze
    info = w.analyze(df)

    print("\n1. Quality Metrics:")
    metrics = info['quality_metrics']
    print(f"   Overall Score: {metrics['score']}/100")
    print(f"   Completeness: {metrics['avg_completeness']:.0%}")
    print(f"   Uniqueness: {metrics['avg_uniqueness']:.0%}")

    print("\n2. Detected Issues:")
    for anom in info['anomalies'][:5]:
        print(f"   [{anom['severity'].upper()}] {anom['type']}: ", end='')
        if 'column' in anom:
            print(f"{anom['column']} ({anom['value']})")
        else:
            print(f"{anom.get('count', '')} ({anom['value']})")

    print("\n3. Suggestions:")
    suggestions = w.suggest(df)
    for s in suggestions[:3]:
        print(f"   • {s}")


def demo_5_cache():
    """Demo 5: Caching & Performance."""
    print("\n" + "=" * 70)
    print("DEMO 5: Caching & Performance")
    print("=" * 70)

    df = create_sample()
    df.to_excel("test.xlsx", index=False)

    import time

    # First read (no cache)
    print("\n1. First read (no cache):")
    start = time.time()
    df1 = w.read("test.xlsx", cache=True)
    t1 = time.time() - start
    print(f"   Time: {t1:.3f}s")

    # Second read (from cache)
    print("\n2. Second read (cached):")
    start = time.time()
    df2 = w.read("test.xlsx", cache=True)
    t2 = time.time() - start
    print(f"   Time: {t2:.3f}s")
    print(f"   Speedup: {t1 / t2:.1f}x faster")

    # Cache info
    print("\n3. Cache info:")
    ci = w.cache()
    print(f"   Cached files: {ci['size']}/{ci['max_size']}")

    # Memory optimization
    print("\n4. Memory optimization:")
    df3 = w.read("test.xlsx", optimize=True)
    mem_before = df1.memory_usage(deep=True).sum() / 1024 ** 2
    mem_after = df3.memory_usage(deep=True).sum() / 1024 ** 2
    print(f"   Before: {mem_before:.2f} MB")
    print(f"   After: {mem_after:.2f} MB")
    print(f"   Saved: {mem_before - mem_after:.2f} MB ({(mem_before - mem_after) / mem_before * 100:.0f}%)")

    # Clear cache
    w.clear()
    Path("test.xlsx").unlink()


def demo_6_pipeline():
    """Demo 6: Pipeline & Quick Report."""
    print("\n" + "=" * 70)
    print("DEMO 6: Pipeline & Quick Report")
    print("=" * 70)

    df = create_sample()
    df.to_excel("test.xlsx", index=False)

    # Full pipeline
    print("\n1. Full pipeline:")
    result = w.pipeline("test.xlsx")
    print(f"   ✓ Quality: {result['score']}/100")
    print(f"   ✓ Suggestions: {len(result['suggestions'])}")
    print(f"   ✓ DataFrame ready: {result['df'].shape}")

    # Quick report
    print("\n2. Quick report:")
    print(w.quick("test.xlsx"))

    Path("test.xlsx").unlink()


def demo_7_utilities():
    """Demo 7: Utility Functions."""
    print("\n" + "=" * 70)
    print("DEMO 7: Utility Functions")
    print("=" * 70)

    df = create_sample()
    df.to_excel("test.xlsx", index=False)

    # File info
    print("\n1. File info:")
    info = w.info("test.xlsx")
    print(f"   Size: {info['file_size_mb']:.2f} MB")
    print(f"   Sheets: {info['sheet_names']}")

    # Sheets
    print("\n2. List sheets:")
    sheets = w.sheets("test.xlsx")
    print(f"   Found: {sheets}")

    # Preview
    print("\n3. Preview:")
    preview = w.preview("test.xlsx", rows=3)
    print(f"   First 3 rows:")
    print(preview.head(3))

    # Metadata
    print("\n4. Metadata:")
    df = w.read("test.xlsx")
    meta = w.meta(df)
    print(f"   Shape: {meta['shape']}")
    print(f"   Memory: {meta['memory_mb']:.2f} MB")
    print(f"   Quality: {meta['quality_score']}/100")

    # Duplicates
    print("\n5. Find duplicates:")
    dups = w.dups(df)
    print(f"   Found: {len(dups)} duplicate rows")

    Path("test.xlsx").unlink()


def demo_8_cheatsheet():
    """Demo 8: Cheatsheet."""
    print("\n" + "=" * 70)
    print("DEMO 8: Command Cheatsheet")
    print("=" * 70)

    print("""
READING:
  df = w.read("file.xlsx")              # Read with cache
  df = w.read("file.xlsx", cache=False) # No cache
  df = w.read("file.xlsx", optimize=True) # Optimize memory

  w.sheets("file.xlsx")                 # List sheets
  w.preview("file.xlsx", rows=10)       # Preview
  w.info("file.xlsx")                   # File info

SMART READING:
  s = w.smart("file.xlsx")              # Full structure
  df = w.smart_df("file.xlsx")          # Just table
  multi = w.smart_all("file.xlsx")      # All sheets

CLEANING:
  df = w.clean(df)                      # Clean & normalize
  df = w.normalize(df)                  # Just normalize columns

ANALYSIS:
  types = w.types(df, extended=True)    # Detect types
  info = w.analyze(df)                  # Full analysis
  meta = w.meta(df)                     # Metadata
  suggestions = w.suggest(df)           # Suggestions
  dups = w.dups(df)                     # Duplicates

EXPORT:
  w.save(df, "out.json")                # JSON
  w.save(df, "out.csv")                 # CSV
  w.save(df, "out.xlsx")                # Excel

CACHE:
  w.cache()                             # Info
  w.clear()                             # Clear

PIPELINES:
  result = w.pipeline("file.xlsx")      # Complete
  print(w.quick("file.xlsx"))           # Quick report

HELP:
  w.help()                              # Show help
    """)


def main():
    """Run all demos."""
    print("=" * 70)
    print("wlibrary v2.0 - Complete Demo")
    print("=" * 70)
    print("\nShowing all features with minimal code.")

    demos = [
        demo_1_basic,
        demo_2_smart,
        demo_3_extended_types,
        demo_4_quality,
        demo_5_cache,
        demo_6_pipeline,
        demo_7_utilities,
        demo_8_cheatsheet,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("✓ All demos completed!")
    print("=" * 70)
    print("\nTry it yourself:")
    print("  import wlibrary as w")
    print("  w.help()  # For quick reference")


if __name__ == "__main__":
    main()