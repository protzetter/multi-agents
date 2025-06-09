"""
Verification script to check that the data catalog matches the actual CSV files
"""

import sys
import os
import pandas as pd

# Add the src directory to the path so we can import our tools
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.data_catalog_tool import DATA_CATALOG


def verify_csv_files():
    """Verify that the data catalog matches the actual CSV files."""
    
    print("=== Data Catalog Verification ===\n")
    
    # Base path to docs folder
    docs_path = os.path.join(os.path.dirname(__file__), '..', 'docs')
    
    for product_id, metadata in DATA_CATALOG.items():
        print(f"Verifying: {product_id}")
        print("-" * 40)
        
        # Get the file path
        file_path = os.path.join(docs_path, os.path.basename(metadata['location']))
        
        if not os.path.exists(file_path):
            print(f"❌ ERROR: File not found: {file_path}")
            continue
        
        try:
            # Read the CSV file to get actual columns
            df = pd.read_csv(file_path, nrows=1)  # Just read header
            actual_columns = list(df.columns)
            
            # Get expected columns from catalog
            expected_columns = metadata['attributes']
            
            print(f"📁 File: {metadata['location']}")
            print(f"📊 Expected columns: {len(expected_columns)}")
            print(f"📊 Actual columns: {len(actual_columns)}")
            
            # Check if columns match
            if actual_columns == expected_columns:
                print("✅ Column names match perfectly!")
            else:
                print("❌ Column mismatch detected:")
                
                # Show missing columns
                missing = set(expected_columns) - set(actual_columns)
                if missing:
                    print(f"   Missing from file: {missing}")
                
                # Show extra columns
                extra = set(actual_columns) - set(expected_columns)
                if extra:
                    print(f"   Extra in file: {extra}")
                
                print(f"   Expected: {expected_columns}")
                print(f"   Actual:   {actual_columns}")
            
            # Verify record count (approximate)
            try:
                actual_count = len(pd.read_csv(file_path)) 
                expected_count = metadata['record_count']
                print(f"📈 Expected records: {expected_count:,}")
                print(f"📈 Actual records: {actual_count:,}")
                
                if actual_count == expected_count:
                    print("✅ Record count matches!")
                else:
                    print(f"⚠️  Record count differs by {abs(actual_count - expected_count):,}")
            except Exception as e:
                print(f"⚠️  Could not verify record count: {e}")
            
        except Exception as e:
            print(f"❌ ERROR reading file: {e}")
        
        print()


def show_sample_data():
    """Show sample data from each CSV file."""
    
    print("=== Sample Data ===\n")
    
    docs_path = os.path.join(os.path.dirname(__file__), '..', 'docs')
    
    for product_id, metadata in DATA_CATALOG.items():
        print(f"Sample from: {metadata['name']}")
        print("-" * 50)
        
        file_path = os.path.join(docs_path, os.path.basename(metadata['location']))
        
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path, nrows=3)
                print(df.to_string(index=False))
            except Exception as e:
                print(f"Error reading file: {e}")
        else:
            print("File not found")
        
        print("\n")


if __name__ == "__main__":
    print("Data Catalog Verification Tool")
    print("Choose an option:")
    print("1. Verify catalog against CSV files")
    print("2. Show sample data from CSV files")
    print("3. Both")
    
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    
    if choice == "1":
        verify_csv_files()
    elif choice == "2":
        show_sample_data()
    elif choice == "3":
        verify_csv_files()
        show_sample_data()
    else:
        print("Invalid choice. Running verification...")
        verify_csv_files()
