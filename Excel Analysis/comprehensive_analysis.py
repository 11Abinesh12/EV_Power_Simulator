import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec

# Set style
sns.set_style("whitegrid")

# Load the Excel file
excel_file = 'GPM_Performance Analysis.xlsx'
xl_file = pd.ExcelFile(excel_file)

print("=" * 120)
print(" " * 40 + "COMPREHENSIVE GPM PERFORMANCE ANALYSIS")
print("=" * 120)

print(f"\n📁 Excel File: {excel_file}")
print(f"📊 Total Sheets: {len(xl_file.sheet_names)}")
print(f"📋 Sheet Names: {xl_file.sheet_names}\n")

# Dictionary to store all dataframes
dfs = {}

# Analyze each sheet
for idx, sheet_name in enumerate(xl_file.sheet_names, 1):
    print("\n" + "=" * 120)
    print(f"SHEET {idx}: {sheet_name}")
    print("=" * 120)
    
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    if sheet_name == 'EV Performance Analysis':
        print("\n📌 This appears to be a configuration/parameters sheet")
        print(f"   Shape: {df.shape}")
        print("\n   Extracting vehicle parameters...")
        
        # Try to extract parameters from row 2-3
        if df.shape[0] > 3:
            print(f"\n   Row 2 (Headers): {df.iloc[2].dropna().to_dict()}")
            print(f"   Row 3 (Values): {df.iloc[3].dropna().to_dict()}")
        
        dfs[sheet_name] = df
        continue
    
    # For simulation sheets
    # Clean up unnamed columns
    unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
    df_clean = df.drop(columns=unnamed_cols)
    
    dfs[sheet_name] = df_clean
    
    print(f"\n📏 Dimensions: {df_clean.shape[0]} rows × {df_clean.shape[1]} columns")
    print(f"⏱️  Time Range: {df_clean['Time'].min():.1f} to {df_clean['Time'].max():.1f} seconds")
    print(f"📊 Simulation Duration: {df_clean['Time'].max():.1f} seconds ({df_clean['Time'].max()/60:.2f} minutes)")
    
    print(f"\n📋 Columns: {list(df_clean.columns)}")
    
    # Calculate additional metrics
    if 'Total Motor Torque (Nm)' in df_clean.columns and 'Motor Speed (RPM)' in df_clean.columns:
        df_clean['Motor Power (kW)'] = (df_clean['Total Motor Torque (Nm)'] * df_clean['Motor Speed (RPM)'] * 2 * np.pi / 60) / 1000
    
    if 'PerMotor Power (Watts)' in df_clean.columns and 'Total Number of Power Wheel (No)' in df_clean.columns:
        df_clean['Total Power (kW)'] = (df_clean['PerMotor Power (Watts)'] * df_clean['Total Number of Power Wheel (No)']) / 1000
    
    print("\n" + "-" * 120)
    print("VEHICLE PERFORMANCE METRICS")
    print("-" * 120)
    print(f"🚗 Maximum Speed: {df_clean['Vehicle Speed (Kmph)'].max():.2f} km/h ({df_clean['Vehicle Speed (m/s)'].max():.2f} m/s)")
    print(f"🚗 Average Speed: {df_clean['Vehicle Speed (Kmph)'].mean():.2f} km/h")
    print(f"🚗 Final Speed: {df_clean['Vehicle Speed (Kmph)'].iloc[-1]:.2f} km/h")
    
    # Time to reach 90% of max speed
    max_speed = df_clean['Vehicle Speed (Kmph)'].max()
    time_to_90 = df_clean[df_clean['Vehicle Speed (Kmph)'] >= max_speed * 0.9]['Time'].min()
    print(f"⏱️  Time to 90% max speed: {time_to_90:.2f} seconds")
    
    print("\n" + "-" * 120)
    print("MOTOR PERFORMANCE")
    print("-" * 120)
    print(f"⚡ Maximum Motor Speed: {df_clean['Motor Speed (RPM)'].max():.2f} RPM")
    print(f"⚡ Average Motor Speed: {df_clean['Motor Speed (RPM)'].mean():.2f} RPM")
    print(f"⚡ Maximum Motor Torque: {df_clean['Total Motor Torque (Nm)'].max():.2f} Nm")
    print(f"⚡ Average Motor Torque: {df_clean['Total Motor Torque (Nm)'].mean():.2f} Nm")
    
    if 'PerMotor Torque (Nm)' in df_clean.columns:
        print(f"⚡ Maximum Per-Motor Torque: {df_clean['PerMotor Torque (Nm)'].max():.2f} Nm")
    
    if 'Motor Power (kW)' in df_clean.columns:
        print(f"⚡ Maximum Motor Power: {df_clean['Motor Power (kW)'].max():.2f} kW")
        print(f"⚡ Average Motor Power: {df_clean['Motor Power (kW)'].mean():.2f} kW")
    
    if 'Total Power (kW)' in df_clean.columns:
        print(f"⚡ Maximum Total Power: {df_clean['Total Power (kW)'].max():.2f} kW")
    
    print("\n" + "-" * 120)
    print("FORCE ANALYSIS")
    print("-" * 120)
    print(f"💪 Maximum Tractive Force: {df_clean['Motoring Tractive Force F_Tractive (N)'].max():.2f} N")
    print(f"💪 Rolling Resistance: {df_clean['Froll (N)'].iloc[0]:.2f} N (constant)")
    print(f"💪 Maximum Drag Force: {df_clean['Fdrag (N)'].max():.2f} N")
    print(f"💪 Climbing Force: {df_clean['Fclimb (N)'].iloc[0]:.2f} N (constant)")
    print(f"💪 Maximum Load Resistance: {df_clean['F_Load Resitance  (N)'].max():.2f} N")
    print(f"💪 Maximum Net Force: {df_clean['Net Force F_Net(N)'].max():.2f} N")
    
    print("\n" + "-" * 120)
    print("ACCELERATION ANALYSIS")
    print("-" * 120)
    print(f"🏁 Maximum Acceleration: {df_clean['Vehicle Acceleration (m/s)'].max():.2f} m/s²")
    print(f"🏁 Average Acceleration (first 10s): {df_clean[df_clean['Time'] <= 10]['Vehicle Acceleration (m/s)'].mean():.2f} m/s²")
    print(f"🏁 Final Acceleration: {df_clean['Vehicle Acceleration (m/s)'].iloc[-1]:.2f} m/s²")
    
    print("\n" + "-" * 120)
    print("OPERATING CONDITIONS")
    print("-" * 120)
    print(f"🏔️  Gradient: {df_clean['Gradient (Degree)'].iloc[0]:.0f} degrees")
    mode_val = df_clean['Mode, Eco-1, Boost-2'].iloc[0]
    mode_name = 'Boost' if mode_val == 2 else 'Eco'
    print(f"⚙️  Mode: {mode_name} (value: {mode_val})")
    print(f"🔧 Number of Power Wheels: {df_clean['Total Number of Power Wheel (No)'].mode()[0]:.0f}")
    
    # Energy calculation
    if 'Motor Power (kW)' in df_clean.columns:
        energy_consumed = np.trapz(df_clean['Motor Power (kW)'], df_clean['Time']) / 3600  # kWh
        print(f"🔋 Total Energy Consumed: {energy_consumed:.4f} kWh")
        
        # Distance traveled
        distance_m = np.trapz(df_clean['Vehicle Speed (m/s)'], df_clean['Time'])
        distance_km = distance_m / 1000
        print(f"📏 Distance Traveled: {distance_km:.3f} km ({distance_m:.1f} m)")
        
        if distance_km > 0:
            energy_per_km = energy_consumed / distance_km
            print(f"⚡ Energy Consumption: {energy_per_km:.4f} kWh/km ({energy_per_km*1000:.2f} Wh/km)")
    
    elif 'Total Power (kW)' in df_clean.columns:
        energy_consumed = np.trapz(df_clean['Total Power (kW)'], df_clean['Time']) / 3600  # kWh
        print(f"🔋 Total Energy Consumed: {energy_consumed:.4f} kWh")
        
        distance_m = np.trapz(df_clean['Vehicle Speed (m/s)'], df_clean['Time'])
        distance_km = distance_m / 1000
        print(f"📏 Distance Traveled: {distance_km:.3f} km ({distance_m:.1f} m)")
        
        if distance_km > 0:
            energy_per_km = energy_consumed / distance_km
            print(f"⚡ Energy Consumption: {energy_per_km:.4f} kWh/km ({energy_per_km*1000:.2f} Wh/km)")
    
    # Resistance breakdown at steady state
    steady_state = df_clean[df_clean['Time'] > df_clean['Time'].max() * 0.5]
    if len(steady_state) > 0:
        print("\n" + "-" * 120)
        print("RESISTANCE BREAKDOWN (Steady State - Last 50% of simulation)")
        print("-" * 120)
        avg_froll = steady_state['Froll (N)'].mean()
        avg_fdrag = steady_state['Fdrag (N)'].mean()
        avg_fclimb = steady_state['Fclimb (N)'].mean()
        total_resistance = avg_froll + avg_fdrag + avg_fclimb
        
        print(f"   Rolling Resistance: {avg_froll:.2f} N ({avg_froll/total_resistance*100:.1f}%)")
        print(f"   Aerodynamic Drag:   {avg_fdrag:.2f} N ({avg_fdrag/total_resistance*100:.1f}%)")
        print(f"   Climbing Resistance: {avg_fclimb:.2f} N ({avg_fclimb/total_resistance*100:.1f}%)")
        print(f"   Total Resistance:    {total_resistance:.2f} N")

# Now create visualizations for the simulation sheets
simulation_sheets = [s for s in xl_file.sheet_names if s != 'EV Performance Analysis']

print("\n\n" + "=" * 120)
print(" " * 40 + "CREATING VISUALIZATIONS")
print("=" * 120)

for sheet_name in simulation_sheets:
    df_clean = dfs[sheet_name]
    
    print(f"\n📊 Creating plots for: {sheet_name}")
    
    # Create a comprehensive figure
    fig = plt.figure(figsize=(20, 16))
    fig.suptitle(f'GPM Performance Analysis - {sheet_name}', fontsize=16, fontweight='bold', y=0.995)
    
    gs = GridSpec(4, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    # 1. Speed vs Time
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(df_clean['Time'], df_clean['Vehicle Speed (Kmph)'], 'b-', linewidth=2)
    ax1.set_xlabel('Time (s)', fontsize=10)
    ax1.set_ylabel('Vehicle Speed (km/h)', fontsize=10)
    ax1.set_title('Vehicle Speed vs Time', fontsize=11, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 2. Motor Speed vs Time
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(df_clean['Time'], df_clean['Motor Speed (RPM)'], 'r-', linewidth=2)
    ax2.set_xlabel('Time (s)', fontsize=10)
    ax2.set_ylabel('Motor Speed (RPM)', fontsize=10)
    ax2.set_title('Motor Speed vs Time', fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. Motor Torque vs Time
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(df_clean['Time'], df_clean['Total Motor Torque (Nm)'], 'g-', linewidth=2)
    ax3.set_xlabel('Time (s)', fontsize=10)
    ax3.set_ylabel('Total Motor Torque (Nm)', fontsize=10)
    ax3.set_title('Motor Torque vs Time', fontsize=11, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. Acceleration vs Time
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.plot(df_clean['Time'], df_clean['Vehicle Acceleration (m/s)'], 'm-', linewidth=2)
    ax4.set_xlabel('Time (s)', fontsize=10)
    ax4.set_ylabel('Acceleration (m/s²)', fontsize=10)
    ax4.set_title('Vehicle Acceleration vs Time', fontsize=11, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # 5. Forces vs Time
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot(df_clean['Time'], df_clean['Motoring Tractive Force F_Tractive (N)'], label='Tractive Force', linewidth=2)
    ax5.plot(df_clean['Time'], df_clean['F_Load Resitance  (N)'], label='Load Resistance', linewidth=2)
    ax5.plot(df_clean['Time'], df_clean['Net Force F_Net(N)'], label='Net Force', linewidth=2)
    ax5.set_xlabel('Time (s)', fontsize=10)
    ax5.set_ylabel('Force (N)', fontsize=10)
    ax5.set_title('Forces vs Time', fontsize=11, fontweight='bold')
    ax5.legend(fontsize=8)
    ax5.grid(True, alpha=0.3)
    
    # 6. Resistance Forces vs Time
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.plot(df_clean['Time'], df_clean['Froll (N)'], label='Rolling Resistance', linewidth=2)
    ax6.plot(df_clean['Time'], df_clean['Fdrag (N)'], label='Aerodynamic Drag', linewidth=2)
    ax6.plot(df_clean['Time'], df_clean['Fclimb (N)'], label='Climbing Resistance', linewidth=2)
    ax6.set_xlabel('Time (s)', fontsize=10)
    ax6.set_ylabel('Resistance Force (N)', fontsize=10)
    ax6.set_title('Resistance Forces vs Time', fontsize=11, fontweight='bold')
    ax6.legend(fontsize=8)
    ax6.grid(True, alpha=0.3)
    
    # 7. Motor Power vs Time
    if 'Motor Power (kW)' in df_clean.columns:
        ax7 = fig.add_subplot(gs[2, 0])
        ax7.plot(df_clean['Time'], df_clean['Motor Power (kW)'], 'c-', linewidth=2)
        ax7.set_xlabel('Time (s)', fontsize=10)
        ax7.set_ylabel('Motor Power (kW)', fontsize=10)
        ax7.set_title('Motor Power vs Time', fontsize=11, fontweight='bold')
        ax7.grid(True, alpha=0.3)
    elif 'Total Power (kW)' in df_clean.columns:
        ax7 = fig.add_subplot(gs[2, 0])
        ax7.plot(df_clean['Time'], df_clean['Total Power (kW)'], 'c-', linewidth=2)
        ax7.set_xlabel('Time (s)', fontsize=10)
        ax7.set_ylabel('Total Power (kW)', fontsize=10)
        ax7.set_title('Total Power vs Time', fontsize=11, fontweight='bold')
        ax7.grid(True, alpha=0.3)
    
    # 8. Torque-Speed Characteristic
    ax8 = fig.add_subplot(gs[2, 1])
    scatter = ax8.scatter(df_clean['Motor Speed (RPM)'], df_clean['Total Motor Torque (Nm)'], 
                         c=df_clean['Time'], cmap='viridis', s=30, alpha=0.6)
    ax8.set_xlabel('Motor Speed (RPM)', fontsize=10)
    ax8.set_ylabel('Motor Torque (Nm)', fontsize=10)
    ax8.set_title('Motor Torque-Speed Characteristic', fontsize=11, fontweight='bold')
    cbar = plt.colorbar(scatter, ax=ax8)
    cbar.set_label('Time (s)', fontsize=8)
    ax8.grid(True, alpha=0.3)
    
    # 9. Power vs Speed
    if 'Motor Power (kW)' in df_clean.columns:
        ax9 = fig.add_subplot(gs[2, 2])
        scatter = ax9.scatter(df_clean['Vehicle Speed (Kmph)'], df_clean['Motor Power (kW)'], 
                             c=df_clean['Time'], cmap='plasma', s=30, alpha=0.6)
        ax9.set_xlabel('Vehicle Speed (km/h)', fontsize=10)
        ax9.set_ylabel('Motor Power (kW)', fontsize=10)
        ax9.set_title('Power vs Vehicle Speed', fontsize=11, fontweight='bold')
        cbar = plt.colorbar(scatter, ax=ax9)
        cbar.set_label('Time (s)', fontsize=8)
        ax9.grid(True, alpha=0.3)
    
    # 10. Resistance Breakdown Pie Chart
    steady_state = df_clean[df_clean['Time'] > df_clean['Time'].max() * 0.5]
    ax10 = fig.add_subplot(gs[3, 0])
    resistance_data = [
        steady_state['Froll (N)'].mean(),
        steady_state['Fdrag (N)'].mean(),
        steady_state['Fclimb (N)'].mean()
    ]
    resistance_labels = ['Rolling\nResistance', 'Aerodynamic\nDrag', 'Climbing\nResistance']
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    ax10.pie(resistance_data, labels=resistance_labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax10.set_title('Resistance Force Breakdown\n(Steady State)', fontsize=11, fontweight='bold')
    
    # 11. Speed and Acceleration together
    ax11 = fig.add_subplot(gs[3, 1])
    ax11_twin = ax11.twinx()
    line1 = ax11.plot(df_clean['Time'], df_clean['Vehicle Speed (Kmph)'], 'b-', linewidth=2, label='Speed')
    line2 = ax11_twin.plot(df_clean['Time'], df_clean['Vehicle Acceleration (m/s)'], 'r-', linewidth=2, label='Acceleration')
    ax11.set_xlabel('Time (s)', fontsize=10)
    ax11.set_ylabel('Speed (km/h)', fontsize=10, color='b')
    ax11_twin.set_ylabel('Acceleration (m/s²)', fontsize=10, color='r')
    ax11.set_title('Speed & Acceleration vs Time', fontsize=11, fontweight='bold')
    ax11.tick_params(axis='y', labelcolor='b')
    ax11_twin.tick_params(axis='y', labelcolor='r')
    ax11.grid(True, alpha=0.3)
    
    # 12. Energy consumption over time
    if 'Motor Power (kW)' in df_clean.columns:
        ax12 = fig.add_subplot(gs[3, 2])
        cumulative_energy = np.cumsum(df_clean['Motor Power (kW)'] * (df_clean['Time'].diff().fillna(0))) / 3600
        ax12.plot(df_clean['Time'], cumulative_energy * 1000, 'orange', linewidth=2)  # Convert to Wh
        ax12.set_xlabel('Time (s)', fontsize=10)
        ax12.set_ylabel('Cumulative Energy (Wh)', fontsize=10)
        ax12.set_title('Cumulative Energy Consumption', fontsize=11, fontweight='bold')
        ax12.grid(True, alpha=0.3)
    
    # Save figure
    filename = f'GPM_Analysis_{sheet_name.replace(" ", "_").replace("-", "_")}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved: {filename}")
    plt.close()
    
    # Save cleaned data
    csv_filename = f'GPM_Data_{sheet_name.replace(" ", "_").replace("-", "_")}.csv'
    df_clean.to_csv(csv_filename, index=False)
    print(f"   ✅ Saved: {csv_filename}")

# Create comparison plot if we have multiple simulation sheets
if len(simulation_sheets) > 1:
    print(f"\n📊 Creating comparison plot for all simulations")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Comparison of All Simulations', fontsize=16, fontweight='bold')
    
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    for idx, sheet_name in enumerate(simulation_sheets):
        df = dfs[sheet_name]
        color = colors[idx % len(colors)]
        
        # Speed comparison
        axes[0, 0].plot(df['Time'], df['Vehicle Speed (Kmph)'], label=sheet_name, linewidth=2, color=color)
        
        # Acceleration comparison
        axes[0, 1].plot(df['Time'], df['Vehicle Acceleration (m/s)'], label=sheet_name, linewidth=2, color=color)
        
        # Motor Torque comparison
        axes[1, 0].plot(df['Time'], df['Total Motor Torque (Nm)'], label=sheet_name, linewidth=2, color=color)
        
        # Net Force comparison
        axes[1, 1].plot(df['Time'], df['Net Force F_Net(N)'], label=sheet_name, linewidth=2, color=color)
    
    axes[0, 0].set_xlabel('Time (s)')
    axes[0, 0].set_ylabel('Vehicle Speed (km/h)')
    axes[0, 0].set_title('Speed Comparison')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].set_xlabel('Time (s)')
    axes[0, 1].set_ylabel('Acceleration (m/s²)')
    axes[0, 1].set_title('Acceleration Comparison')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    axes[1, 0].set_xlabel('Time (s)')
    axes[1, 0].set_ylabel('Motor Torque (Nm)')
    axes[1, 0].set_title('Motor Torque Comparison')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].set_xlabel('Time (s)')
    axes[1, 1].set_ylabel('Net Force (N)')
    axes[1, 1].set_title('Net Force Comparison')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('GPM_Comparison_All_Simulations.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved: GPM_Comparison_All_Simulations.png")
    plt.close()

print("\n" + "=" * 120)
print(" " * 45 + "ANALYSIS COMPLETE!")
print("=" * 120)
print("\n📁 Generated Files:")
for sheet_name in simulation_sheets:
    safe_name = sheet_name.replace(" ", "_").replace("-", "_")
    print(f"   • GPM_Analysis_{safe_name}.png - Comprehensive visualization")
    print(f"   • GPM_Data_{safe_name}.csv - Cleaned dataset")
if len(simulation_sheets) > 1:
    print(f"   • GPM_Comparison_All_Simulations.png - Comparison of all simulations")

print("\n" + "=" * 120)
