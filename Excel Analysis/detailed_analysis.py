import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)

# Load the Excel file
excel_file = 'GPM_Performance Analysis.xlsx'
xl_file = pd.ExcelFile(excel_file)
sheet_name = xl_file.sheet_names[0]  # Get the first sheet name
df = pd.read_excel(excel_file, sheet_name=sheet_name)

# Clean up: Remove unnamed columns that are mostly empty
df_clean = df.drop(columns=['Unnamed: 16', 'Unnamed: 17', 'Unnamed: 18', 'Unnamed: 19'])

print("=" * 100)
print("DETAILED GPM PERFORMANCE ANALYSIS")
print("=" * 100)

print("\n1. DATASET OVERVIEW")
print("-" * 100)
print(f"Total Records: {len(df_clean)}")
print(f"Time Range: {df_clean['Time'].min()} to {df_clean['Time'].max()} seconds")
print(f"Simulation Duration: {df_clean['Time'].max()} seconds ({df_clean['Time'].max()/60:.2f} minutes)")

print("\n2. VEHICLE PERFORMANCE METRICS")
print("-" * 100)
print(f"Maximum Speed: {df_clean['Vehicle Speed (Kmph)'].max():.2f} km/h ({df_clean['Vehicle Speed (m/s)'].max():.2f} m/s)")
print(f"Average Speed: {df_clean['Vehicle Speed (Kmph)'].mean():.2f} km/h")
print(f"Final Speed: {df_clean['Vehicle Speed (Kmph)'].iloc[-1]:.2f} km/h")
print(f"Time to reach max speed: {df_clean[df_clean['Vehicle Speed (Kmph)'] >= df_clean['Vehicle Speed (Kmph)'].max() * 0.99]['Time'].min():.2f} seconds")

print("\n3. MOTOR PERFORMANCE")
print("-" * 100)
print(f"Maximum Motor Speed: {df_clean['Motor Speed (RPM)'].max():.2f} RPM")
print(f"Average Motor Speed: {df_clean['Motor Speed (RPM)'].mean():.2f} RPM")
print(f"Maximum Motor Torque: {df_clean['Total Motor Torque (Nm)'].max():.2f} Nm")
print(f"Average Motor Torque: {df_clean['Total Motor Torque (Nm)'].mean():.2f} Nm")
print(f"Maximum Per-Motor Torque: {df_clean['PerMotor Torque (Nm)'].max():.2f} Nm")

print("\n4. FORCE ANALYSIS")
print("-" * 100)
print(f"Maximum Tractive Force: {df_clean['Motoring Tractive Force F_Tractive (N)'].max():.2f} N")
print(f"Rolling Resistance Force: {df_clean['Froll (N)'].iloc[0]:.2f} N (constant)")
print(f"Maximum Drag Force: {df_clean['Fdrag (N)'].max():.2f} N")
print(f"Climbing Force: {df_clean['Fclimb (N)'].iloc[0]:.2f} N (constant)")
print(f"Maximum Load Resistance: {df_clean['F_Load Resitance  (N)'].max():.2f} N")
print(f"Maximum Net Force: {df_clean['Net Force F_Net(N)'].max():.2f} N")

print("\n5. ACCELERATION ANALYSIS")
print("-" * 100)
print(f"Maximum Acceleration: {df_clean['Vehicle Acceleration (m/s)'].max():.2f} m/s²")
print(f"Average Acceleration (first 10s): {df_clean[df_clean['Time'] <= 10]['Vehicle Acceleration (m/s)'].mean():.2f} m/s²")
print(f"Final Acceleration: {df_clean['Vehicle Acceleration (m/s)'].iloc[-1]:.2f} m/s²")

print("\n6. OPERATING CONDITIONS")
print("-" * 100)
print(f"Gradient: {df_clean['Gradient (Degree)'].iloc[0]:.0f} degrees")
print(f"Mode: {'Boost' if df_clean['Mode, Eco-1, Boost-2'].iloc[0] == 2 else 'Eco'}")
print(f"Number of Power Wheels: {df_clean['Total Number of Power Wheel (No)'].mode()[0]:.0f}")

print("\n7. KEY PERFORMANCE PHASES")
print("-" * 100)

# Acceleration phase (when acceleration > 0.1 m/s²)
accel_phase = df_clean[df_clean['Vehicle Acceleration (m/s)'] > 0.1]
if len(accel_phase) > 0:
    print(f"Acceleration Phase: 0 to {accel_phase['Time'].max():.2f} seconds")
    print(f"  - Speed increase: 0 to {accel_phase['Vehicle Speed (Kmph)'].iloc[-1]:.2f} km/h")
    print(f"  - Average acceleration: {accel_phase['Vehicle Acceleration (m/s)'].mean():.2f} m/s²")

# Steady state phase
steady_phase = df_clean[df_clean['Vehicle Acceleration (m/s)'] <= 0.1]
if len(steady_phase) > 0:
    print(f"Steady State Phase: {steady_phase['Time'].min():.2f} to {steady_phase['Time'].max():.2f} seconds")
    print(f"  - Cruise speed: {steady_phase['Vehicle Speed (Kmph)'].mean():.2f} km/h")
    print(f"  - Speed variation: ±{steady_phase['Vehicle Speed (Kmph)'].std():.4f} km/h")

print("\n8. ENERGY AND POWER INSIGHTS")
print("-" * 100)
# Calculate power (P = T × ω, where ω = RPM × 2π/60)
df_clean['Motor Power (kW)'] = (df_clean['Total Motor Torque (Nm)'] * df_clean['Motor Speed (RPM)'] * 2 * np.pi / 60) / 1000
print(f"Maximum Motor Power: {df_clean['Motor Power (kW)'].max():.2f} kW")
print(f"Average Motor Power: {df_clean['Motor Power (kW)'].mean():.2f} kW")
print(f"Power at steady state: {df_clean[df_clean['Time'] > 15]['Motor Power (kW)'].mean():.2f} kW")

# Calculate work done (integrate power over time)
work_done = np.trapz(df_clean['Motor Power (kW)'], df_clean['Time']) / 3600  # kWh
print(f"Total Energy Consumed: {work_done:.4f} kWh")

print("\n9. EFFICIENCY METRICS")
print("-" * 100)
# Tractive efficiency = Net Force / Tractive Force
df_clean['Tractive Efficiency (%)'] = (df_clean['Net Force F_Net(N)'] / df_clean['Motoring Tractive Force F_Tractive (N)']) * 100
df_clean['Tractive Efficiency (%)'].replace([np.inf, -np.inf], np.nan, inplace=True)
print(f"Average Tractive Efficiency: {df_clean['Tractive Efficiency (%)'].mean():.2f}%")
print(f"Tractive Efficiency at steady state: {df_clean[df_clean['Time'] > 15]['Tractive Efficiency (%)'].mean():.2f}%")

print("\n10. RESISTANCE BREAKDOWN AT STEADY STATE (Time > 15s)")
print("-" * 100)
steady_df = df_clean[df_clean['Time'] > 15]
avg_froll = steady_df['Froll (N)'].mean()
avg_fdrag = steady_df['Fdrag (N)'].mean()
avg_fclimb = steady_df['Fclimb (N)'].mean()
total_resistance = avg_froll + avg_fdrag + avg_fclimb

print(f"Rolling Resistance: {avg_froll:.2f} N ({avg_froll/total_resistance*100:.1f}%)")
print(f"Aerodynamic Drag: {avg_fdrag:.2f} N ({avg_fdrag/total_resistance*100:.1f}%)")
print(f"Climbing Resistance: {avg_fclimb:.2f} N ({avg_fclimb/total_resistance*100:.1f}%)")
print(f"Total Resistance: {total_resistance:.2f} N")

print("\n" + "=" * 100)
print("CREATING VISUALIZATIONS...")
print("=" * 100)

# Create comprehensive visualizations
fig = plt.figure(figsize=(20, 24))

# 1. Speed vs Time
ax1 = plt.subplot(5, 2, 1)
ax1.plot(df_clean['Time'], df_clean['Vehicle Speed (Kmph)'], 'b-', linewidth=2)
ax1.set_xlabel('Time (s)', fontsize=10)
ax1.set_ylabel('Vehicle Speed (km/h)', fontsize=10)
ax1.set_title('Vehicle Speed vs Time', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)

# 2. Motor Speed vs Time
ax2 = plt.subplot(5, 2, 2)
ax2.plot(df_clean['Time'], df_clean['Motor Speed (RPM)'], 'r-', linewidth=2)
ax2.set_xlabel('Time (s)', fontsize=10)
ax2.set_ylabel('Motor Speed (RPM)', fontsize=10)
ax2.set_title('Motor Speed vs Time', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)

# 3. Motor Torque vs Time
ax3 = plt.subplot(5, 2, 3)
ax3.plot(df_clean['Time'], df_clean['Total Motor Torque (Nm)'], 'g-', linewidth=2)
ax3.set_xlabel('Time (s)', fontsize=10)
ax3.set_ylabel('Total Motor Torque (Nm)', fontsize=10)
ax3.set_title('Motor Torque vs Time', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3)

# 4. Acceleration vs Time
ax4 = plt.subplot(5, 2, 4)
ax4.plot(df_clean['Time'], df_clean['Vehicle Acceleration (m/s)'], 'm-', linewidth=2)
ax4.set_xlabel('Time (s)', fontsize=10)
ax4.set_ylabel('Acceleration (m/s²)', fontsize=10)
ax4.set_title('Vehicle Acceleration vs Time', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3)

# 5. Forces vs Time
ax5 = plt.subplot(5, 2, 5)
ax5.plot(df_clean['Time'], df_clean['Motoring Tractive Force F_Tractive (N)'], label='Tractive Force', linewidth=2)
ax5.plot(df_clean['Time'], df_clean['F_Load Resitance  (N)'], label='Load Resistance', linewidth=2)
ax5.plot(df_clean['Time'], df_clean['Net Force F_Net(N)'], label='Net Force', linewidth=2)
ax5.set_xlabel('Time (s)', fontsize=10)
ax5.set_ylabel('Force (N)', fontsize=10)
ax5.set_title('Forces vs Time', fontsize=12, fontweight='bold')
ax5.legend(fontsize=8)
ax5.grid(True, alpha=0.3)

# 6. Resistance Forces vs Time
ax6 = plt.subplot(5, 2, 6)
ax6.plot(df_clean['Time'], df_clean['Froll (N)'], label='Rolling Resistance', linewidth=2)
ax6.plot(df_clean['Time'], df_clean['Fdrag (N)'], label='Aerodynamic Drag', linewidth=2)
ax6.plot(df_clean['Time'], df_clean['Fclimb (N)'], label='Climbing Resistance', linewidth=2)
ax6.set_xlabel('Time (s)', fontsize=10)
ax6.set_ylabel('Resistance Force (N)', fontsize=10)
ax6.set_title('Resistance Forces vs Time', fontsize=12, fontweight='bold')
ax6.legend(fontsize=8)
ax6.grid(True, alpha=0.3)

# 7. Motor Power vs Time
ax7 = plt.subplot(5, 2, 7)
ax7.plot(df_clean['Time'], df_clean['Motor Power (kW)'], 'c-', linewidth=2)
ax7.set_xlabel('Time (s)', fontsize=10)
ax7.set_ylabel('Motor Power (kW)', fontsize=10)
ax7.set_title('Motor Power vs Time', fontsize=12, fontweight='bold')
ax7.grid(True, alpha=0.3)

# 8. Torque vs Speed (Motor Characteristic)
ax8 = plt.subplot(5, 2, 8)
ax8.scatter(df_clean['Motor Speed (RPM)'], df_clean['Total Motor Torque (Nm)'], c=df_clean['Time'], cmap='viridis', s=20)
ax8.set_xlabel('Motor Speed (RPM)', fontsize=10)
ax8.set_ylabel('Motor Torque (Nm)', fontsize=10)
ax8.set_title('Motor Torque-Speed Characteristic', fontsize=12, fontweight='bold')
cbar = plt.colorbar(ax8.collections[0], ax=ax8)
cbar.set_label('Time (s)', fontsize=8)
ax8.grid(True, alpha=0.3)

# 9. Power vs Speed
ax9 = plt.subplot(5, 2, 9)
ax9.scatter(df_clean['Vehicle Speed (Kmph)'], df_clean['Motor Power (kW)'], c=df_clean['Time'], cmap='plasma', s=20)
ax9.set_xlabel('Vehicle Speed (km/h)', fontsize=10)
ax9.set_ylabel('Motor Power (kW)', fontsize=10)
ax9.set_title('Power vs Vehicle Speed', fontsize=12, fontweight='bold')
cbar = plt.colorbar(ax9.collections[0], ax=ax9)
cbar.set_label('Time (s)', fontsize=8)
ax9.grid(True, alpha=0.3)

# 10. Resistance Breakdown Pie Chart
ax10 = plt.subplot(5, 2, 10)
resistance_data = [avg_froll, avg_fdrag, avg_fclimb]
resistance_labels = ['Rolling\nResistance', 'Aerodynamic\nDrag', 'Climbing\nResistance']
colors = ['#ff9999', '#66b3ff', '#99ff99']
ax10.pie(resistance_data, labels=resistance_labels, autopct='%1.1f%%', colors=colors, startangle=90)
ax10.set_title('Resistance Force Breakdown\n(Steady State)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('GPM_Performance_Analysis.png', dpi=300, bbox_inches='tight')
print("\n✅ Visualization saved as 'GPM_Performance_Analysis.png'")

# Save cleaned data to CSV
df_clean.to_csv('GPM_Performance_Data_Clean.csv', index=False)
print("✅ Cleaned data saved as 'GPM_Performance_Data_Clean.csv'")

# Create summary statistics file
with open('GPM_Analysis_Summary.txt', 'w') as f:
    f.write("=" * 100 + "\n")
    f.write("GPM PERFORMANCE ANALYSIS SUMMARY\n")
    f.write("=" * 100 + "\n\n")
    
    f.write("DATASET OVERVIEW\n")
    f.write("-" * 100 + "\n")
    f.write(f"Total Records: {len(df_clean)}\n")
    f.write(f"Simulation Duration: {df_clean['Time'].max()} seconds ({df_clean['Time'].max()/60:.2f} minutes)\n\n")
    
    f.write("KEY PERFORMANCE METRICS\n")
    f.write("-" * 100 + "\n")
    f.write(f"Maximum Speed: {df_clean['Vehicle Speed (Kmph)'].max():.2f} km/h\n")
    f.write(f"Maximum Acceleration: {df_clean['Vehicle Acceleration (m/s)'].max():.2f} m/s²\n")
    f.write(f"Maximum Motor Power: {df_clean['Motor Power (kW)'].max():.2f} kW\n")
    f.write(f"Total Energy Consumed: {work_done:.4f} kWh\n")
    f.write(f"Gradient: {df_clean['Gradient (Degree)'].iloc[0]:.0f} degrees\n")
    f.write(f"Operating Mode: {'Boost' if df_clean['Mode, Eco-1, Boost-2'].iloc[0] == 2 else 'Eco'}\n")

print("✅ Summary saved as 'GPM_Analysis_Summary.txt'")

print("\n" + "=" * 100)
print("ANALYSIS COMPLETE!")
print("=" * 100)
print("\nGenerated Files:")
print("  1. GPM_Performance_Analysis.png - Comprehensive visualization")
print("  2. GPM_Performance_Data_Clean.csv - Cleaned dataset")
print("  3. GPM_Analysis_Summary.txt - Summary statistics")
