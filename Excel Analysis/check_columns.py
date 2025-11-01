import pandas as pd

excel_file = 'GPM_Performance Analysis.xlsx'
xl_file = pd.ExcelFile(excel_file)
print(f"Sheet names: {xl_file.sheet_names}")

for sheet in xl_file.sheet_names:
    print(f"\n{'='*80}")
    print(f"Sheet: {sheet}")
    print(f"{'='*80}")
    df = pd.read_excel(excel_file, sheet_name=sheet)
    print(f"Shape: {df.shape}")
    print(f"\nColumn names:")
    for i, col in enumerate(df.columns):
        print(f"  {i}: '{col}'")
    print(f"\nFirst 5 rows:")
    print(df.head())
