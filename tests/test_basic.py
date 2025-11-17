"""
Simple test without config dependencies
"""

import wlibrary as w
import pandas as pd
import numpy as np

print("Testing wlibrary v2.0")
print("="*60)

# Test 1: Help
print("\n1. Testing help()...")
try:
    w.help()
    print("OK: help() works")
except Exception as e:
    print(f"ERROR: {e}")

# Test 2: Create sample data
print("\n2. Creating sample data...")
try:
    df = pd.DataFrame({
        'id': range(1, 11),
        'name': [f'Item {i}' for i in range(1, 11)],
        'email': [f'user{i}@test.com' for i in range(1, 11)],
        'price': [f'${np.random.randint(100, 1000)}' for _ in range(10)],
    })
    df.to_excel("test.xlsx", index=False)
    print("OK: Sample data created")
except Exception as e:
    print(f"ERROR: {e}")

# Test 3: Read
print("\n3. Testing read()...")
try:
    df = w.read("test.xlsx")
    print(f"OK: Read {len(df)} rows")
except Exception as e:
    print(f"ERROR: {e}")

# Test 4: Types
print("\n4. Testing types()...")
try:
    types = w.types(df, extended=True)
    print(f"OK: Detected {len(types)} column types")
    for col, info in types.items():
        print(f"   {col}: {info['type']}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 5: Clean
print("\n5. Testing clean()...")
try:
    df_clean = w.clean(df)
    print(f"OK: Cleaned {len(df_clean)} rows")
except Exception as e:
    print(f"ERROR: {e}")

# Test 6: Analyze
print("\n6. Testing analyze()...")
try:
    info = w.analyze(df)
    print(f"OK: Quality score: {info['quality_metrics']['score']}/100")
except Exception as e:
    print(f"ERROR: {e}")

# Test 7: Save
print("\n7. Testing save()...")
try:
    w.save(df_clean, "test_output.json")
    print("OK: Saved to test_output.json")
except Exception as e:
    print(f"ERROR: {e}")

# Test 8: Cache
print("\n8. Testing cache()...")
try:
    cache_info = w.cache()
    print(f"OK: Cache has {cache_info['size']} items")
except Exception as e:
    print(f"ERROR: {e}")

# Test 9: Quick report
print("\n9. Testing quick()...")
try:
    report = w.quick("test.xlsx")
    print(f"OK: Generated report ({len(report)} chars)")
except Exception as e:
    print(f"ERROR: {e}")

# Cleanup
print("\n10. Cleanup...")
try:
    import os
    w.clear()
    for file in ['test.xlsx', 'test_output.json']:
        if os.path.exists(file):
            os.remove(file)
    print("OK: Cleanup complete")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*60)
print("All tests completed!")
print("="*60)