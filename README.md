# EV Simulation Analysis - Quick Start Guide

## 📋 What's in this folder?

This folder contains a complete analysis of the **GPM_Performance Analysis.xlsx** file, which includes Electric Vehicle (EV) performance simulation data for two different terrain scenarios.

---

## 🚀 Quick Summary

### Two Simulations Analyzed:

1. **Flat Terrain (0° gradient)** - `m-LEV4000-37Nm-2000W`
   - Max Speed: 55.42 km/h
   - Energy: 49.92 Wh/km
   - Max Acceleration: 8.56 m/s²
   - Main resistance: Aerodynamic drag (81.6%)

2. **Steep Climb (60° gradient)** - `VehicleSimulation - LEV6000 (2)`
   - Max Speed: 55.42 km/h
   - Energy: 398.35 Wh/km (8x higher!)
   - Max Acceleration: 3.62 m/s²
   - Main resistance: Climbing force (93.8%)

---

## 📁 Files Generated

### 📊 Visualizations (PNG files)
- **GPM_Analysis_m_LEV4000_37Nm_2000W.png** - 12 detailed charts for flat terrain
- **GPM_Analysis_VehicleSimulation___LEV6000_(2).png** - 12 detailed charts for steep climb
- **GPM_Comparison_All_Simulations.png** - Side-by-side comparison

### 📄 Data Files (CSV)
- **GPM_Data_m_LEV4000_37Nm_2000W.csv** - Clean data for flat terrain (181 rows)
- **GPM_Data_VehicleSimulation___LEV6000_(2).csv** - Clean data for steep climb (181 rows)

### 📖 Documentation
- **ANALYSIS_SUMMARY.md** - Complete detailed analysis report
- **README.md** - This file (quick start guide)

### 🐍 Python Scripts
- **comprehensive_analysis.py** - Main analysis script (run this to regenerate everything)
- **analyze_excel.py** - Initial exploration script
- **check_columns.py** - Column verification script

---

## 🎯 Key Findings

### 1. Energy Consumption Impact
- **Flat terrain**: 49.92 Wh/km (excellent efficiency)
- **60° climb**: 398.35 Wh/km (8x increase)
- **Implication**: Battery range is drastically reduced on steep hills

### 2. Performance Characteristics
- Both scenarios reach the same max speed (55.42 km/h)
- Acceleration is 57.7% lower on steep climbs
- Motor operates at 22 kW max power in both cases

### 3. Resistance Forces
- **Flat**: 81.6% aerodynamic drag, 18.4% rolling resistance
- **Climb**: 93.8% climbing force, 4.1% drag, 2.2% rolling

### 4. Motor Specifications
- 2 motors × 52 Nm = 104 Nm total torque
- Max speed: 2746 RPM
- Max power: 22 kW
- Gear ratio: 5.221
- Wheel radius: 0.2795 m

---

## 📊 How to View the Analysis

### Option 1: View the Visualizations
Open any of the PNG files to see comprehensive charts showing:
- Speed vs Time
- Motor Speed vs Time
- Motor Torque vs Time
- Acceleration vs Time
- Force Analysis
- Resistance Breakdown
- Power Consumption
- Torque-Speed Characteristics
- And more...

### Option 2: Read the Summary
Open **ANALYSIS_SUMMARY.md** for a complete written analysis with:
- Detailed metrics for both simulations
- Comparative analysis
- Technical observations
- Recommendations

### Option 3: Explore the Data
Open the CSV files in Excel or any spreadsheet software to:
- See all 181 data points
- Create custom charts
- Perform your own analysis

### Option 4: Re-run the Analysis
```bash
python comprehensive_analysis.py
```
This will regenerate all visualizations and CSV files.

---

## 🔍 What Each Visualization Shows

### Individual Simulation Charts (12 panels each)
1. **Speed vs Time** - How vehicle speed changes
2. **Motor Speed vs Time** - RPM progression
3. **Motor Torque vs Time** - Torque demand
4. **Acceleration vs Time** - Acceleration profile
5. **Forces vs Time** - Tractive, resistance, and net forces
6. **Resistance Forces** - Rolling, drag, and climbing forces
7. **Motor Power vs Time** - Power consumption
8. **Torque-Speed Characteristic** - Motor operating curve
9. **Power vs Speed** - Power demand at different speeds
10. **Resistance Breakdown** - Pie chart of resistance sources
11. **Speed & Acceleration** - Combined view
12. **Cumulative Energy** - Total energy consumed over time

### Comparison Chart (4 panels)
- Speed comparison between scenarios
- Acceleration comparison
- Motor torque comparison
- Net force comparison

---

## 💡 Insights for Design

### Battery Sizing
- For flat terrain: ~50 Wh/km
- For hilly terrain: ~400 Wh/km
- Plan battery capacity based on expected terrain

### Motor Selection
- Current 22 kW motor handles both scenarios
- Torque is adequate for 60° climbs
- Consider higher torque for better hill acceleration

### Aerodynamics
- Critical on flat terrain (81.6% of resistance)
- Less important on steep climbs (4.1% of resistance)
- Optimize body shape for flat/highway driving

### Rolling Resistance
- Minimal impact (2.2-18.4%)
- Current tire selection is appropriate
- Low-hanging fruit for efficiency gains

---

## 📈 Data Structure

Each CSV file contains these columns:
- `Time` - Simulation time (seconds)
- `Vehicle Speed (m/s)` - Speed in meters per second
- `Vehicle Speed (Kmph)` - Speed in kilometers per hour
- `Motor Speed (RPM)` - Motor rotational speed
- `Gradient (Degree)` - Road gradient
- `Mode, Eco-1, Boost-2` - Operating mode (2 = Boost)
- `Total Motor Torque (Nm)` - Combined torque from all motors
- `Total Number of Power Wheel (No)` - Number of driven wheels
- `PerMotor Torque (Nm)` - Torque per motor
- `Motoring Tractive Force F_Tractive (N)` - Forward driving force
- `Froll (N)` - Rolling resistance force
- `Fdrag (N)` - Aerodynamic drag force
- `Fclimb (N)` - Climbing resistance force
- `F_Load Resitance (N)` - Total resistance
- `Net Force F_Net(N)` - Net accelerating force
- `Vehicle Acceleration (m/s)` - Acceleration
- `Motor Power (kW)` - Calculated motor power
- `Total Power (kW)` - Total power (where applicable)

---

## 🎓 Understanding the Results

### Why is energy consumption 8x higher on climbs?
- Gravity requires constant work to lift the vehicle
- On a 60° slope, 93.8% of energy goes to fighting gravity
- Aerodynamic drag becomes negligible on steep climbs

### Why is acceleration lower on climbs?
- Same motor power, but more force needed to overcome gravity
- Net force (tractive - resistance) is lower
- F = ma, so lower net force = lower acceleration

### Why does drag decrease on climbs?
- Vehicle speed is similar, but relative wind speed may differ
- More importantly, drag becomes a smaller percentage of total resistance
- Climbing force dominates the resistance profile

---

## 🔧 Technical Specifications Extracted

### Vehicle Parameters
- **Drag Coefficient (Cd)**: 0.8
- **Rolling Resistance Coefficient (Cr)**: 0.02
- **Air Density (ρ)**: 1.164 kg/m³
- **Frontal Area (Af)**: 0.5 m²
- **Wheel Radius**: 0.2795 m
- **Gear Ratio**: 5.221

### Motor System
- **Number of Motors**: 2
- **Max Torque per Motor**: 52 Nm
- **Total Max Torque**: 104 Nm
- **Max Power**: 22 kW
- **Max RPM**: 2746

### Operating Conditions
- **Mode**: Boost (Mode 2)
- **Simulation Time**: 90-180 seconds
- **Target Speed**: 55.42 km/h

---

## 📞 Questions?

For detailed technical analysis, see **ANALYSIS_SUMMARY.md**

For visual insights, open the PNG files

For raw data exploration, use the CSV files

---

*Analysis Date: October 29, 2025*
*Source: GPM_Performance Analysis.xlsx*
*Analysis Tool: Python (pandas, numpy, matplotlib, seaborn)*
