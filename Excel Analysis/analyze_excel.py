import pandas as pd
import openpyxl
import sys

# Load the Excel file
excel_file = 'GPM_Performance Analysis.xlsx'

print("=" * 80)
print("EXCEL FILE ANALYSIS: GPM_Performance Analysis.xlsx")
print("=" * 80)

# Get all sheet names
xl_file = pd.ExcelFile(excel_file)
sheet_names = xl_file.sheet_names

print(f"\n📊 Number of sheets: {len(sheet_names)}")
print(f"Sheet names: {sheet_names}\n")

# Analyze each sheet
for sheet_name in sheet_names:
    print("\n" + "=" * 80)
    print(f"SHEET: {sheet_name}")
    print("=" * 80)
    
    # Read the sheet
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    print(f"\n📏 Dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
    
    print(f"\n📋 Column names:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    print(f"\n📊 Data types:")
    print(df.dtypes)
    
    print(f"\n📈 Basic statistics:")
    print(df.describe(include='all'))
    
    print(f"\n🔍 First 10 rows:")
    print(df.head(10))
    
    print(f"\n🔍 Last 5 rows:")
    print(df.tail(5))
    
    print(f"\n❓ Missing values:")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(missing[missing > 0])
    else:
        print("  No missing values")
    
    print(f"\n🔢 Unique value counts for each column:")
    for col in df.columns:
        unique_count = df[col].nunique()
        print(f"  {col}: {unique_count} unique values")
        if unique_count <= 20 and df[col].dtype == 'object':
            print(f"    Values: {df[col].unique().tolist()}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
