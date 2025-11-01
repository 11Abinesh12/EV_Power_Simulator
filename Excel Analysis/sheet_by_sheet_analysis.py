import pandas as pd
import numpy as np

excel_file = 'GPM_Performance Analysis.xlsx'

print("=" * 120)
print(" " * 35 + "DETAILED ANALYSIS OF ALL 3 SHEETS")
print("=" * 120)

# ============================================================================
# SHEET 1: EV Performance Analysis (Configuration/Parameters)
# ============================================================================
print("\n" + "=" * 120)
print("SHEET 1: EV Performance Analysis (Configuration/Parameters Sheet)")
print("=" * 120)

df_config = pd.read_excel(excel_file, sheet_name='EV Performance Analysis')
print(f"\nShape: {df_config.shape[0]} rows × {df_config.shape[1]} columns")

print("\n📋 Full Sheet Content:")
print(df_config.to_string())

print("\n🔍 Extracting Vehicle Parameters from Row 2-3:")
# Row 2 contains headers, Row 3 contains values
if df_config.shape[0] > 3:
    headers = df_config.iloc[2].dropna()
    values = df_config.iloc[3].dropna()
    
    print("\n   Vehicle Configuration Parameters:")
    print("   " + "-" * 80)
    for idx in headers.index:
        if idx in values.index:
            print(f"   {headers[idx]}: {values[idx]}")

print("\n📊 Data Types:")
print(df_config.dtypes)

print("\n💡 Sheet Purpose:")
print("   This sheet contains vehicle configuration parameters used in the simulations:")
print("   - Cd (Drag Coefficient)")
print("   - Cr (Rolling Resistance Coefficient)")
print("   - ρ (Air Density)")
print("   - Af (Frontal Area)")
print("   - Wheel Radius")
print("   - Gear Ratio")

# ============================================================================
# SHEET 2: m-LEV4000-37Nm-2000W (Flat Terrain Simulation)
# ============================================================================
print("\n\n" + "=" * 120)
print("SHEET 2: m-LEV4000-37Nm-2000W (Flat Terrain - 0° Gradient)")
print("=" * 120)

df_flat = pd.read_excel(excel_file, sheet_name='m-LEV4000-37Nm-2000W')
# Remove unnamed columns
unnamed_cols = [col for col in df_flat.columns if 'Unnamed' in str(col)]
df_flat_clean = df_flat.drop(columns=unnamed_cols)

print(f"\nShape: {df_flat_clean.shape[0]} rows × {df_flat_clean.shape[1]} columns")
print(f"Time Range: {df_flat_clean['Time'].min():.1f} to {df_flat_clean['Time'].max():.1f} seconds")

print("\n📋 All Columns:")
for i, col in enumerate(df_flat_clean.columns, 1):
    print(f"   {i:2d}. {col}")

print("\n📊 Statistical Summary:")
print(df_flat_clean.describe().to_string())

print("\n🔍 First 10 Rows:")
print(df_flat_clean.head(10).to_string())

print("\n🔍 Last 5 Rows:")
print(df_flat_clean.tail(5).to_string())

print("\n📈 Key Metrics:")
print(f"   Gradient: {df_flat_clean['Gradient (Degree)'].iloc[0]:.0f}°")
print(f"   Mode: {'Boost' if df_flat_clean['Mode, Eco-1, Boost-2'].iloc[0] == 2 else 'Eco'}")
print(f"   Max Speed: {df_flat_clean['Vehicle Speed (Kmph)'].max():.2f} km/h")
print(f"   Max Acceleration: {df_flat_clean['Vehicle Acceleration (m/s)'].max():.2f} m/s²")
print(f"   Max Motor Torque: {df_flat_clean['Total Motor Torque (Nm)'].max():.2f} Nm")
print(f"   Max Motor Speed: {df_flat_clean['Motor Speed (RPM)'].max():.2f} RPM")

# Calculate power
df_flat_clean['Motor Power (kW)'] = (df_flat_clean['Total Motor Torque (Nm)'] * 
                                      df_flat_clean['Motor Speed (RPM)'] * 2 * np.pi / 60) / 1000
print(f"   Max Motor Power: {df_flat_clean['Motor Power (kW)'].max():.2f} kW")

# Energy and distance
energy = np.trapz(df_flat_clean['Motor Power (kW)'], df_flat_clean['Time']) / 3600
distance = np.trapz(df_flat_clean['Vehicle Speed (m/s)'], df_flat_clean['Time']) / 1000
print(f"   Total Energy: {energy:.4f} kWh ({energy*1000:.2f} Wh)")
print(f"   Distance: {distance:.3f} km")
print(f"   Energy/km: {energy/distance*1000:.2f} Wh/km")

print("\n🔬 Force Analysis:")
print(f"   Max Tractive Force: {df_flat_clean['Motoring Tractive Force F_Tractive (N)'].max():.2f} N")
print(f"   Rolling Resistance: {df_flat_clean['Froll (N)'].iloc[0]:.2f} N")
print(f"   Max Drag Force: {df_flat_clean['Fdrag (N)'].max():.2f} N")
print(f"   Climbing Force: {df_flat_clean['Fclimb (N)'].iloc[0]:.2f} N")
print(f"   Max Net Force: {df_flat_clean['Net Force F_Net(N)'].max():.2f} N")

# ============================================================================
# SHEET 3: VehicleSimulation - LEV6000 (2) (Steep Climb Simulation)
# ============================================================================
print("\n\n" + "=" * 120)
print("SHEET 3: VehicleSimulation - LEV6000 (2) (Steep Climb - 60° Gradient)")
print("=" * 120)

df_climb = pd.read_excel(excel_file, sheet_name='VehicleSimulation - LEV6000 (2)')
# Remove unnamed columns
unnamed_cols = [col for col in df_climb.columns if 'Unnamed' in str(col)]
df_climb_clean = df_climb.drop(columns=unnamed_cols)

print(f"\nShape: {df_climb_clean.shape[0]} rows × {df_climb_clean.shape[1]} columns")
print(f"Time Range: {df_climb_clean['Time'].min():.1f} to {df_climb_clean['Time'].max():.1f} seconds")

print("\n📋 All Columns:")
for i, col in enumerate(df_climb_clean.columns, 1):
    print(f"   {i:2d}. {col}")

print("\n📊 Statistical Summary:")
print(df_climb_clean.describe().to_string())

print("\n🔍 First 10 Rows:")
print(df_climb_clean.head(10).to_string())

print("\n🔍 Last 5 Rows:")
print(df_climb_clean.tail(5).to_string())

print("\n📈 Key Metrics:")
print(f"   Gradient: {df_climb_clean['Gradient (Degree)'].iloc[0]:.0f}°")
print(f"   Mode: {'Boost' if df_climb_clean['Mode, Eco-1, Boost-2'].iloc[0] == 2 else 'Eco'}")
print(f"   Max Speed: {df_climb_clean['Vehicle Speed (Kmph)'].max():.2f} km/h")
print(f"   Max Acceleration: {df_climb_clean['Vehicle Acceleration (m/s)'].max():.2f} m/s²")
print(f"   Max Motor Torque: {df_climb_clean['Total Motor Torque (Nm)'].max():.2f} Nm")
print(f"   Max Motor Speed: {df_climb_clean['Motor Speed (RPM)'].max():.2f} RPM")

# Calculate power
df_climb_clean['Motor Power (kW)'] = (df_climb_clean['Total Motor Torque (Nm)'] * 
                                       df_climb_clean['Motor Speed (RPM)'] * 2 * np.pi / 60) / 1000
print(f"   Max Motor Power: {df_climb_clean['Motor Power (kW)'].max():.2f} kW")

# Energy and distance
energy = np.trapz(df_climb_clean['Motor Power (kW)'], df_climb_clean['Time']) / 3600
distance = np.trapz(df_climb_clean['Vehicle Speed (m/s)'], df_climb_clean['Time']) / 1000
print(f"   Total Energy: {energy:.4f} kWh ({energy*1000:.2f} Wh)")
print(f"   Distance: {distance:.3f} km")
print(f"   Energy/km: {energy/distance*1000:.2f} Wh/km")

print("\n🔬 Force Analysis:")
print(f"   Max Tractive Force: {df_climb_clean['Motoring Tractive Force F_Tractive (N)'].max():.2f} N")
print(f"   Rolling Resistance: {df_climb_clean['Froll (N)'].iloc[0]:.2f} N")
print(f"   Max Drag Force: {df_climb_clean['Fdrag (N)'].max():.2f} N")
print(f"   Climbing Force: {df_climb_clean['Fclimb (N)'].iloc[0]:.2f} N")
print(f"   Max Net Force: {df_climb_clean['Net Force F_Net(N)'].max():.2f} N")

# ============================================================================
# COMPARISON ACROSS ALL 3 SHEETS
# ============================================================================
print("\n\n" + "=" * 120)
print(" " * 40 + "COMPARISON ACROSS ALL SHEETS")
print("=" * 120)

print("\n📊 Sheet Overview:")
print(f"   Sheet 1 (Config): {df_config.shape[0]} rows × {df_config.shape[1]} columns - Configuration parameters")
print(f"   Sheet 2 (Flat):   {df_flat_clean.shape[0]} rows × {df_flat_clean.shape[1]} columns - Flat terrain simulation")
print(f"   Sheet 3 (Climb):  {df_climb_clean.shape[0]} rows × {df_climb_clean.shape[1]} columns - Steep climb simulation")

print("\n🔄 Comparison Table:")
print("   " + "-" * 100)
print(f"   {'Metric':<40} {'Sheet 2 (Flat)':<25} {'Sheet 3 (Climb)':<25}")
print("   " + "-" * 100)
print(f"   {'Gradient':<40} {df_flat_clean['Gradient (Degree)'].iloc[0]:>20.0f}° {df_climb_clean['Gradient (Degree)'].iloc[0]:>20.0f}°")
print(f"   {'Simulation Duration':<40} {df_flat_clean['Time'].max():>20.1f}s {df_climb_clean['Time'].max():>20.1f}s")
print(f"   {'Max Speed (km/h)':<40} {df_flat_clean['Vehicle Speed (Kmph)'].max():>20.2f} {df_climb_clean['Vehicle Speed (Kmph)'].max():>20.2f}")
print(f"   {'Max Acceleration (m/s²)':<40} {df_flat_clean['Vehicle Acceleration (m/s)'].max():>20.2f} {df_climb_clean['Vehicle Acceleration (m/s)'].max():>20.2f}")
print(f"   {'Max Motor Torque (Nm)':<40} {df_flat_clean['Total Motor Torque (Nm)'].max():>20.2f} {df_climb_clean['Total Motor Torque (Nm)'].max():>20.2f}")
print(f"   {'Max Motor Power (kW)':<40} {df_flat_clean['Motor Power (kW)'].max():>20.2f} {df_climb_clean['Motor Power (kW)'].max():>20.2f}")

# Recalculate for comparison
energy_flat = np.trapz(df_flat_clean['Motor Power (kW)'], df_flat_clean['Time']) / 3600
distance_flat = np.trapz(df_flat_clean['Vehicle Speed (m/s)'], df_flat_clean['Time']) / 1000
energy_climb = np.trapz(df_climb_clean['Motor Power (kW)'], df_climb_clean['Time']) / 3600
distance_climb = np.trapz(df_climb_clean['Vehicle Speed (m/s)'], df_climb_clean['Time']) / 1000

print(f"   {'Total Energy (kWh)':<40} {energy_flat:>20.4f} {energy_climb:>20.4f}")
print(f"   {'Distance (km)':<40} {distance_flat:>20.3f} {distance_climb:>20.3f}")
print(f"   {'Energy/km (Wh/km)':<40} {energy_flat/distance_flat*1000:>20.2f} {energy_climb/distance_climb*1000:>20.2f}")
print(f"   {'Max Tractive Force (N)':<40} {df_flat_clean['Motoring Tractive Force F_Tractive (N)'].max():>20.2f} {df_climb_clean['Motoring Tractive Force F_Tractive (N)'].max():>20.2f}")
print(f"   {'Rolling Resistance (N)':<40} {df_flat_clean['Froll (N)'].iloc[0]:>20.2f} {df_climb_clean['Froll (N)'].iloc[0]:>20.2f}")
print(f"   {'Max Drag Force (N)':<40} {df_flat_clean['Fdrag (N)'].max():>20.2f} {df_climb_clean['Fdrag (N)'].max():>20.2f}")
print(f"   {'Climbing Force (N)':<40} {df_flat_clean['Fclimb (N)'].iloc[0]:>20.2f} {df_climb_clean['Fclimb (N)'].iloc[0]:>20.2f}")
print("   " + "-" * 100)

print("\n💡 Key Differences:")
print(f"   • Gradient: {df_climb_clean['Gradient (Degree)'].iloc[0] - df_flat_clean['Gradient (Degree)'].iloc[0]:.0f}° steeper in Sheet 3")
print(f"   • Energy Consumption: {(energy_climb/distance_climb)/(energy_flat/distance_flat):.1f}x higher on climb")
print(f"   • Acceleration: {(1 - df_climb_clean['Vehicle Acceleration (m/s)'].max()/df_flat_clean['Vehicle Acceleration (m/s)'].max())*100:.1f}% lower on climb")
print(f"   • Climbing Force: {df_climb_clean['Fclimb (N)'].iloc[0]:.0f} N on climb vs {df_flat_clean['Fclimb (N)'].iloc[0]:.0f} N on flat")

print("\n" + "=" * 120)
print(" " * 45 + "ANALYSIS COMPLETE")
print("=" * 120)
