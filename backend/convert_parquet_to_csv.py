"""
Parquet to CSV Converter for Deepset Prompt Injection Dataset
Converts Parquet files to CSV format for AgentShield
Uses pyarrow for reliable Parquet handling
"""

import sys
from pathlib import Path
import json
import csv

# Try to import pyarrow or pandas
try:
    import pyarrow.parquet as pq
    HAS_PYARROW = True
    print("✅ pyarrow imported successfully")
except ImportError:
    HAS_PYARROW = False
    print("⚠️  pyarrow not available, trying pandas...")
    try:
        import pandas as pd
        HAS_PANDAS = True
        print("✅ pandas imported successfully")
    except ImportError:
        HAS_PANDAS = False
        print("❌ Neither pyarrow nor pandas available")
        print("Please install: python -m pip install pandas pyarrow")
        sys.exit(1)

# Correct paths - datasets are in backend/routes/datasets/
BASE_DIR = Path(__file__).parent
DATASETS_DIR = BASE_DIR / "routes" / "datasets"

PARQUET_TRAIN = DATASETS_DIR / "train-00000-of-00001-9564e8b05b4757ab.parquet"
PARQUET_TEST = DATASETS_DIR / "test-00000-of-00001-701d16158af87368.parquet"

CSV_TRAIN = DATASETS_DIR / "train.csv"
CSV_TEST = DATASETS_DIR / "test.csv"


def print_separator(title=""):
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)


def check_files():
    """Check if Parquet files exist"""
    print_separator("📁 Checking Files")
    
    if PARQUET_TRAIN.exists():
        size_mb = PARQUET_TRAIN.stat().st_size / (1024*1024)
        print(f"✅ {PARQUET_TRAIN.name} ({size_mb:.2f} MB)")
    else:
        print(f"❌ {PARQUET_TRAIN.name} NOT FOUND")
        return False
    
    if PARQUET_TEST.exists():
        size_mb = PARQUET_TEST.stat().st_size / (1024*1024)
        print(f"✅ {PARQUET_TEST.name} ({size_mb:.2f} MB)")
    else:
        print(f"❌ {PARQUET_TEST.name} NOT FOUND")
        return False
    
    return True


def load_and_convert_pyarrow(parquet_file, csv_file, dataset_name):
    """Load Parquet with pyarrow and convert to CSV"""
    print(f"\n🔄 Processing {dataset_name} Dataset (using pyarrow)...")
    
    try:
        # Load Parquet
        print(f"   Reading: {parquet_file.name}")
        table = pq.read_table(parquet_file)
        df_dict = table.to_pydict()
        
        num_records = len(next(iter(df_dict.values())))
        print(f"   ✅ Loaded {num_records:,} records")
        print(f"   📋 Columns: {list(df_dict.keys())}")
        
        # Save as CSV
        print(f"   Writing: {csv_file.name}")
        
        # Write CSV with pyarrow data
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if not df_dict:
                print(f"   ❌ No data to write")
                return None, False
            
            fieldnames = list(df_dict.keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write rows
            for i in range(num_records):
                row = {key: df_dict[key][i] for key in fieldnames}
                writer.writerow(row)
        
        print(f"   ✅ Saved to CSV")
        return df_dict, num_records, True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None, False


def load_and_convert_pandas(parquet_file, csv_file, dataset_name):
    """Load Parquet with pandas and convert to CSV"""
    print(f"\n🔄 Processing {dataset_name} Dataset (using pandas)...")
    
    try:
        # Load Parquet
        print(f"   Reading: {parquet_file.name}")
        df = pd.read_parquet(parquet_file)
        print(f"   ✅ Loaded {len(df):,} records")
        print(f"   📋 Columns: {list(df.columns)}")
        
        # Save as CSV
        print(f"   Writing: {csv_file.name}")
        df.to_csv(csv_file, index=False)
        print(f"   ✅ Saved to CSV")
        
        return df, len(df), True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None, False


def display_dataset_info_pyarrow(data_dict, num_records, name):
    """Display dataset statistics for pyarrow dict"""
    print(f"\n📊 {name} Dataset Information:")
    print(f"   Total Records: {num_records:,}")
    print(f"   Total Columns: {len(data_dict)}")
    print(f"   Columns: {list(data_dict.keys())}")
    
    # Display first 3 rows
    print(f"\n   First 3 Records:")
    for i in range(min(3, num_records)):
        print(f"   Row {i + 1}:")
        for col in data_dict.keys():
            value = data_dict[col][i]
            if isinstance(value, str) and len(value) > 70:
                print(f"      {col}: {value[:70]}...")
            else:
                print(f"      {col}: {value}")
    
    # Label distribution
    for col in data_dict.keys():
        if col.lower() in ['label', 'labels', 'is_prompt_injection', 'target']:
            print(f"\n   Label Distribution ({col}):")
            label_counts = {}
            for val in data_dict[col]:
                label_counts[val] = label_counts.get(val, 0) + 1
            
            for label in sorted(label_counts.keys()):
                count = label_counts[label]
                percentage = (count / num_records) * 100
                bar = "█" * int(percentage / 5)
                print(f"      {label}: {count:,} ({percentage:6.2f}%) {bar}")
            break


def display_dataset_info_pandas(df, name):
    """Display dataset statistics for pandas dataframe"""
    print(f"\n📊 {name} Dataset Information:")
    print(f"   Total Records: {len(df):,}")
    print(f"   Total Columns: {len(df.columns)}")
    print(f"   Columns: {list(df.columns)}")
    
    # Display first few rows
    print(f"\n   First 3 Records:")
    for idx, row in df.head(3).iterrows():
        print(f"   Row {idx + 1}:")
        for col in df.columns:
            value = row[col]
            if isinstance(value, str) and len(value) > 70:
                print(f"      {col}: {value[:70]}...")
            else:
                print(f"      {col}: {value}")
    
    # Label distribution
    for col in df.columns:
        if col.lower() in ['label', 'labels', 'is_prompt_injection', 'target']:
            print(f"\n   Label Distribution ({col}):")
            dist = df[col].value_counts().sort_index()
            for label, count in dist.items():
                percentage = (count / len(df)) * 100
                bar = "█" * int(percentage / 5)
                print(f"      {label}: {count:,} ({percentage:6.2f}%) {bar}")
            break


def verify_csv(csv_file):
    """Verify CSV file"""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
        
        num_rows = len(rows)
        num_cols = len(header)
        file_size = csv_file.stat().st_size / 1024
        
        print(f"\n✅ CSV Verification:")
        print(f"   File: {csv_file.name}")
        print(f"   Records: {num_rows:,}")
        print(f"   Columns: {num_cols}")
        print(f"   Size: {file_size:.2f} KB")
        return True, num_rows, num_cols
    except Exception as e:
        print(f"\n❌ CSV Verification Failed: {e}")
        return False, 0, 0


def main():
    print_separator("🔄 Parquet to CSV Converter")
    
    # Step 1: Check files
    if not check_files():
        print("\n❌ Cannot proceed - Parquet files not found")
        return False
    
    # Choose conversion method
    if HAS_PYARROW:
        load_func = load_and_convert_pyarrow
        display_func = display_dataset_info_pyarrow
        print("\n✅ Using pyarrow for conversion")
    else:
        load_func = load_and_convert_pandas
        display_func = display_dataset_info_pandas
        print("\n✅ Using pandas for conversion")
    
    # Step 2: Convert training dataset
    print_separator("Converting Training Dataset")
    df_train, num_train, train_success = load_func(
        PARQUET_TRAIN, CSV_TRAIN, "Training"
    )
    
    if not train_success or df_train is None:
        print("\n❌ Failed to convert training dataset")
        return False
    
    display_func(df_train, num_train, "Training")
    
    # Step 3: Convert test dataset
    print_separator("Converting Test Dataset")
    df_test, num_test, test_success = load_func(
        PARQUET_TEST, CSV_TEST, "Test"
    )
    
    if not test_success or df_test is None:
        print("\n❌ Failed to convert test dataset")
        return False
    
    display_func(df_test, num_test, "Test")
    
    # Step 4: Verify converted files
    print_separator("Verifying CSV Files")
    
    train_verified, train_rows, train_cols = verify_csv(CSV_TRAIN)
    test_verified, test_rows, test_cols = verify_csv(CSV_TEST)
    
    if not (train_verified and test_verified):
        print("\n❌ Verification failed")
        return False
    
    # Final summary
    print_separator("✅ CONVERSION COMPLETE")
    
    print(f"\n📊 Final Statistics:")
    print(f"   Training Records: {num_train:,}")
    print(f"   Test Records: {num_test:,}")
    print(f"   Total Records: {num_train + num_test:,}")
    print(f"   Total Columns: {train_cols}")
    
    print(f"\n📁 Output Files Created:")
    print(f"   ✅ {CSV_TRAIN}")
    print(f"   ✅ {CSV_TEST}")
    
    print(f"\n💡 Next Steps:")
    print(f"   • Use these CSVs to train/test AgentShield")
    print(f"   • Location: {DATASETS_DIR}")
    print(f"   • Load with Python:")
    print(f"     - pandas: pd.read_csv('{CSV_TRAIN.name}')")
    print(f"     - csv: import csv; open('{CSV_TRAIN.name}')")
    
    return True


if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 70 + "\n")
    sys.exit(0 if success else 1)
