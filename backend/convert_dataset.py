"""
Deepset Prompt Injection Dataset Converter
Converts Parquet files to CSV format for AgentShield

This script:
1. Reads train and test Parquet files (if they exist)
2. Converts them to CSV format
3. Displays statistics (records, columns, label distribution)
4. Validates the converted files
"""

import os
import sys
from pathlib import Path
from typing import Dict, Tuple

# Try to import pandas and pyarrow
try:
    import pandas as pd
    import pyarrow.parquet as pq
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️  pandas/pyarrow not available. Install with:")
    print("   pip install pandas pyarrow")

# Configuration
DATASETS_DIR = Path(__file__).parent / "datasets"
PARQUET_TRAIN = DATASETS_DIR / "train-00000-of-00001-9564e8b05b4757ab.parquet"
PARQUET_TEST = DATASETS_DIR / "test-00000-of-00001-701d16158af87368.parquet"
CSV_TRAIN = DATASETS_DIR / "train.csv"
CSV_TEST = DATASETS_DIR / "test.csv"


def check_dependencies() -> bool:
    """Check if required dependencies are installed"""
    if not PANDAS_AVAILABLE:
        print("❌ Missing pandas/pyarrow")
        print("\nInstall with:")
        print("  pip install pandas==2.1.3 pyarrow==13.0.0")
        return False
    
    print("✅ pandas is installed")
    print("✅ pyarrow is installed")
    return True


def load_parquet(parquet_file: Path) -> pd.DataFrame:
    """Load a Parquet file and return as DataFrame"""
    if not PANDAS_AVAILABLE:
        return None
    
    try:
        df = pd.read_parquet(parquet_file)
        print(f"✅ Loaded: {parquet_file.name}")
        return df
    except FileNotFoundError:
        print(f"⚠️  File not found: {parquet_file.name}")
        return None
    except Exception as e:
        print(f"❌ Error loading {parquet_file.name}: {e}")
        return None


def display_dataframe_info(df: pd.DataFrame, name: str) -> None:
    """Display information about a DataFrame"""
    if df is None:
        return
    
    print(f"\n📊 {name} Dataset Information:")
    print(f"  Total Records: {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Shape: {df.shape}")
    
    # Show sample row
    if len(df) > 0:
        print(f"\n  Sample Row:")
        for col in df.columns:
            value = df[col].iloc[0]
            # Truncate long strings
            if isinstance(value, str) and len(value) > 80:
                print(f"    {col}: {value[:80]}...")
            else:
                print(f"    {col}: {value}")


def get_label_distribution(df: pd.DataFrame) -> Dict:
    """Get label distribution from DataFrame"""
    if df is None:
        return {}
    
    # Try common label column names
    label_cols = ['label', 'labels', 'is_prompt_injection', 'target', 'y']
    
    for col in label_cols:
        if col in df.columns:
            distribution = df[col].value_counts().to_dict()
            return {col: distribution}
    
    return {}


def display_label_distribution(df: pd.DataFrame, name: str) -> None:
    """Display label distribution"""
    if df is None:
        return
    
    dist = get_label_distribution(df)
    
    if not dist:
        print(f"  No standard label column found")
        return
    
    for col, values in dist.items():
        print(f"\n  Label Distribution ({col}):")
        for label, count in sorted(values.items()):
            percentage = (count / len(df)) * 100
            bar_length = int(percentage / 5)
            bar = "█" * bar_length
            print(f"    {label}: {count:4d} ({percentage:5.1f}%) {bar}")


def convert_to_csv(parquet_file: Path, csv_file: Path, name: str) -> bool:
    """Convert Parquet to CSV"""
    if not PANDAS_AVAILABLE:
        return False
    
    df = load_parquet(parquet_file)
    
    if df is None:
        return False
    
    try:
        df.to_csv(csv_file, index=False)
        print(f"✅ Converted to CSV: {csv_file.name}")
        
        # Display statistics
        display_dataframe_info(df, name)
        display_label_distribution(df, name)
        
        return True
    except Exception as e:
        print(f"❌ Error converting to CSV: {e}")
        return False


def verify_csv(csv_file: Path) -> bool:
    """Verify the converted CSV file"""
    if not csv_file.exists():
        print(f"❌ File not found: {csv_file}")
        return False
    
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ Verified CSV: {csv_file.name}")
        print(f"   Records: {len(df):,}")
        print(f"   Columns: {len(df.columns)}")
        file_size = csv_file.stat().st_size
        if file_size > 1024*1024:
            print(f"   File size: {file_size / (1024*1024):.2f} MB")
        else:
            print(f"   File size: {file_size / 1024:.2f} KB")
        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def compare_parquet_csv(parquet_file: Path, csv_file: Path) -> bool:
    """Compare Parquet and CSV to ensure data integrity"""
    if not PANDAS_AVAILABLE or not parquet_file.exists():
        return True
    
    try:
        df_parquet = pd.read_parquet(parquet_file)
        df_csv = pd.read_csv(csv_file)
        
        if len(df_parquet) != len(df_csv):
            print(f"❌ Record count mismatch: {len(df_parquet)} vs {len(df_csv)}")
            return False
        
        if len(df_parquet.columns) != len(df_csv.columns):
            print(f"❌ Column count mismatch")
            return False
        
        print(f"✅ Data integrity verified for {csv_file.name}")
        return True
    except Exception as e:
        print(f"⚠️  Comparison skipped: {e}")
        return True


def main():
    """Main conversion workflow"""
    print("=" * 70)
    print("🔄 Deepset Prompt Injection Dataset Converter")
    print("=" * 70)
    
    # Check dependencies
    print("\n1️⃣  Checking dependencies...")
    if not check_dependencies():
        print("\n⚠️  Continuing with existing CSV files (if any)...")
    
    # Create datasets directory if it doesn't exist
    print("\n2️⃣  Checking datasets directory...")
    if not DATASETS_DIR.exists():
        DATASETS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {DATASETS_DIR}")
    else:
        print(f"✅ Found: {DATASETS_DIR}")
    
    # Check for Parquet files and convert if found
    parquet_files_found = False
    if PARQUET_TRAIN.exists() and PARQUET_TEST.exists():
        parquet_files_found = True
        print("\n3️⃣  Converting Parquet Files to CSV...")
        
        print("\nTraining Dataset:")
        train_success = convert_to_csv(PARQUET_TRAIN, CSV_TRAIN, "Training")
        
        print("\nTest Dataset:")
        test_success = convert_to_csv(PARQUET_TEST, CSV_TEST, "Test")
        
        if not (train_success and test_success):
            return False
    else:
        print("\n3️⃣  Parquet files not found")
        if PARQUET_TRAIN.exists():
            print(f"✅ Found: {PARQUET_TRAIN.name}")
        else:
            print(f"⚠️  Missing: {PARQUET_TRAIN.name}")
        
        if PARQUET_TEST.exists():
            print(f"✅ Found: {PARQUET_TEST.name}")
        else:
            print(f"⚠️  Missing: {PARQUET_TEST.name}")
        
        print("\nTo use this script, download datasets from:")
        print("  https://huggingface.co/datasets/deepset/prompt-injection")
    
    # Verify existing or converted CSV files
    print("\n4️⃣  Verifying CSV Files...")
    
    csv_train_exists = CSV_TRAIN.exists()
    csv_test_exists = CSV_TEST.exists()
    
    if csv_train_exists:
        print("\nTraining CSV Verification:")
        verify_csv(CSV_TRAIN)
    else:
        print(f"⚠️  {CSV_TRAIN.name} not found")
    
    if csv_test_exists:
        print("\nTest CSV Verification:")
        verify_csv(CSV_TEST)
    else:
        print(f"⚠️  {CSV_TEST.name} not found")
    
    # Compare data integrity if Parquet files exist
    if parquet_files_found:
        print("\n5️⃣  Comparing Data Integrity...")
        print("\nTraining Data Integrity:")
        compare_parquet_csv(PARQUET_TRAIN, CSV_TRAIN)
        
        print("\nTest Data Integrity:")
        compare_parquet_csv(PARQUET_TEST, CSV_TEST)
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 CONVERSION SUMMARY")
    print("=" * 70)
    
    # Load and display final stats
    if CSV_TRAIN.exists() and CSV_TEST.exists():
        try:
            df_train = pd.read_csv(CSV_TRAIN)
            df_test = pd.read_csv(CSV_TEST)
            
            total_records = len(df_train) + len(df_test)
            total_columns = len(df_train.columns)
            
            print(f"\n✅ CSV Files Ready!")
            print(f"\nDataset Statistics:")
            print(f"  Training Records: {len(df_train):,}")
            print(f"  Test Records: {len(df_test):,}")
            print(f"  Total Records: {total_records:,}")
            print(f"  Total Columns: {total_columns}")
            print(f"  Column Names: {list(df_train.columns)}")
            
            # Overall label distribution
            all_dist = get_label_distribution(df_train)
            if all_dist:
                for col, values in all_dist.items():
                    print(f"\nTraining Label Distribution ({col}):")
                    for label, count in sorted(values.items()):
                        percentage = (count / len(df_train)) * 100
                        bar_length = int(percentage / 5)
                        bar = "█" * bar_length
                        print(f"  {label}: {count:4d} ({percentage:5.1f}%) {bar}")
            
            print(f"\n📁 Output Files:")
            print(f"  Training: {CSV_TRAIN}")
            print(f"  Test: {CSV_TEST}")
            
            # Check if files are being used by AgentShield
            print(f"\n💡 These datasets can be used by AgentShield for:")
            print(f"  • Training prompt injection detection models")
            print(f"  • Evaluating security engine performance")
            print(f"  • Validating threat detection accuracy")
            
            return True
        except Exception as e:
            print(f"\n❌ Error reading CSV files: {e}")
            return False
    else:
        print(f"\n❌ CSV files not available")
        if not parquet_files_found:
            print(f"\n📥 To complete conversion:")
            print(f"  1. Download Deepset Prompt Injection dataset")
            print(f"  2. Place Parquet files in: {DATASETS_DIR}")
            print(f"  3. Run this script again")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

