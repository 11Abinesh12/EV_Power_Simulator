# 🚗⚡ EV Power Train Simulation Tool

A comprehensive desktop application for simulating and analyzing Electric Vehicle (EV) power train performance under various conditions.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6.1-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [User Guide](#user-guide)
- [Technical Details](#technical-details)
- [Simulation Parameters](#simulation-parameters)
- [Output Metrics](#output-metrics)
- [Examples](#examples)

## ✨ Features

### 🎯 Core Capabilities

- **Real-time Physics Simulation**: Accurate EV power train modeling based on real-world physics
- **Interactive GUI**: Modern, user-friendly desktop interface built with PyQt6
- **Multiple Visualization Modes**: 
  - Speed vs Time
  - Power Consumption
  - Force Analysis
  - Motor Performance
  - Energy Consumption
- **Customizable Parameters**: Adjust vehicle specifications, terrain, and operating modes
- **Quick Scenarios**: Pre-configured scenarios for common use cases
- **Data Export**: Export simulation results to CSV for further analysis

### 📊 Analysis Features

- **Performance Metrics**: Max speed, acceleration, motor RPM, torque, power
- **Energy Efficiency**: Energy consumption per km, total energy usage
- **Force Breakdown**: Tractive force, drag, rolling resistance, climbing force
- **Motor Analysis**: RPM, torque, and power characteristics over time

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Windows 10/11 (tested), macOS, or Linux

### Step 1: Clone or Download

```bash
cd EV_Simulation
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required Packages:**
- PyQt6 (6.6.1) - GUI framework
- PyQt6-Charts (6.6.0) - Charting components
- numpy (1.26.2) - Numerical computations
- pandas (2.1.4) - Data handling
- matplotlib (3.8.2) - Plotting
- openpyxl (3.1.2) - Excel file support
- scipy (1.11.4) - Scientific computing

### Step 3: Run the Application

```bash
python main_app.py
```

## 🎮 Quick Start

### Running Your First Simulation

1. **Launch the application**
   ```bash
   python main_app.py
   ```

2. **Choose a quick scenario** (or customize parameters):
   - Click "Flat Terrain (0°)" for highway driving
   - Click "Moderate Hill (15°)" for typical hills
   - Click "Steep Climb (60°)" for extreme gradients

3. **Click "▶ Run Simulation"**

4. **View results** in the visualization tabs:
   - 📈 Speed - Vehicle speed over time
   - ⚡ Power - Motor power consumption
   - 🔧 Forces - Force analysis breakdown
   - ⚙️ Motor - Motor RPM and torque
   - 🔋 Energy - Cumulative energy consumption

5. **Export data** (optional):
   - Click "💾 Export Results"
   - Save as CSV file

## 📖 User Guide

### Control Panel (Left Side)

#### 1. Simulation Parameters

| Parameter | Description | Range | Default |
|-----------|-------------|-------|---------|
| **Duration** | Simulation time in seconds | 10-600s | 90s |
| **Target Speed** | Desired cruising speed | 0-120 km/h | 85 km/h |
| **Gradient** | Road slope angle | -30° to 60° | 0° |
| **Mode** | Motor operating mode | eco/boost | boost |

#### 2. Vehicle Parameters

| Parameter | Description | Range | Default |
|-----------|-------------|-------|---------|
| **Drag Coefficient (Cd)** | Aerodynamic drag | 0.1-2.0 | 0.8 |
| **Rolling Resistance (Cr)** | Tire resistance | 0.001-0.1 | 0.02 |
| **Mass** | Vehicle weight | 50-500 kg | 150 kg |
| **Frontal Area** | Cross-sectional area | 0.1-5.0 m² | 0.5 m² |

#### 3. Quick Scenarios

- **Flat Terrain (0°)**: Highway/city driving simulation
  - Duration: 90s
  - Target Speed: 85 km/h
  - Gradient: 0°

- **Moderate Hill (15°)**: Typical hill climbing
  - Duration: 120s
  - Target Speed: 60 km/h
  - Gradient: 15°

- **Steep Climb (60°)**: Extreme gradient testing
  - Duration: 180s
  - Target Speed: 55 km/h
  - Gradient: 60°

### Visualization Panel (Right Side)

#### 📈 Speed Tab
Shows vehicle speed progression over time. Key insights:
- Acceleration phase
- Steady-state cruising speed
- Time to reach target speed

#### ⚡ Power Tab
Displays motor power consumption. Useful for:
- Peak power requirements
- Average power consumption
- Power profile analysis

#### 🔧 Forces Tab
Comprehensive force analysis showing:
- **Tractive Force** (green): Driving force from motor
- **Total Resistance** (red): Combined resistance forces
- **Drag Force** (blue dashed): Aerodynamic resistance
- **Rolling Resistance** (yellow dashed): Tire friction
- **Climbing Force** (magenta dashed): Gravity component on slopes

#### ⚙️ Motor Tab
Two-panel motor performance view:
- **Top panel**: Motor RPM over time
- **Bottom panel**: Motor torque over time

#### 🔋 Energy Tab
Cumulative energy consumption throughout the simulation.

## 🔬 Technical Details

### Physics Model

The simulation uses accurate physics equations:

#### 1. **Aerodynamic Drag**
```
F_drag = 0.5 × Cd × ρ × A × v²
```
- Cd: Drag coefficient
- ρ: Air density (1.164 kg/m³)
- A: Frontal area
- v: Vehicle speed

#### 2. **Rolling Resistance**
```
F_roll = Cr × m × g × cos(θ)
```
- Cr: Rolling resistance coefficient
- m: Vehicle mass
- g: Gravity (9.81 m/s²)
- θ: Road gradient

#### 3. **Climbing Force**
```
F_climb = m × g × sin(θ)
```

#### 4. **Tractive Force**
```
F_tractive = (T_motor × G) / r
```
- T_motor: Motor torque
- G: Gear ratio (5.221)
- r: Wheel radius (0.2795 m)

#### 5. **Net Force & Acceleration**
```
F_net = F_tractive - (F_drag + F_roll + F_climb)
a = F_net / m
```

#### 6. **Motor Power**
```
P = T × ω
```
- T: Motor torque
- ω: Angular velocity (rad/s)

### Motor Specifications

| Parameter | Eco Mode | Boost Mode |
|-----------|----------|------------|
| Max Torque per Motor | 37 Nm | 52 Nm |
| Total Torque (2 motors) | 74 Nm | 104 Nm |
| Max Power | 4 kW | 22 kW |
| Max RPM | 2746 RPM | 2746 RPM |

## 📊 Output Metrics

### Performance Metrics
- **Max Speed**: Highest speed achieved (km/h)
- **Avg Speed**: Average speed throughout simulation (km/h)
- **Max Acceleration**: Peak acceleration (m/s²)

### Motor Performance
- **Max Motor RPM**: Highest rotational speed
- **Max Motor Torque**: Peak torque output (Nm)
- **Max Motor Power**: Peak power consumption (kW)
- **Avg Motor Power**: Average power draw (kW)

### Energy & Efficiency
- **Total Distance**: Distance traveled (km)
- **Total Energy**: Energy consumed (kWh)
- **Energy per km**: Efficiency metric (Wh/km)

## 💡 Examples

### Example 1: Flat Terrain Analysis

**Scenario**: Highway driving at 85 km/h

**Settings**:
- Duration: 90s
- Target Speed: 85 km/h
- Gradient: 0°
- Mode: Boost

**Expected Results**:
- Max Speed: ~85 km/h
- Energy Consumption: ~50 Wh/km
- Max Acceleration: ~8.5 m/s²
- Dominant Force: Aerodynamic drag (81%)

**Use Case**: Ideal for range estimation on highways

---

### Example 2: Hill Climbing

**Scenario**: Climbing a steep 60° slope

**Settings**:
- Duration: 180s
- Target Speed: 55 km/h
- Gradient: 60°
- Mode: Boost

**Expected Results**:
- Max Speed: ~55 km/h
- Energy Consumption: ~400 Wh/km (8x higher!)
- Max Power: ~22 kW
- Dominant Force: Climbing force (94%)

**Use Case**: Worst-case scenario for battery sizing

---

### Example 3: Efficiency Optimization

**Goal**: Find optimal speed for minimum energy consumption

**Method**:
1. Run simulations at different target speeds (30, 50, 70, 90 km/h)
2. Compare "Energy per km" values
3. Identify sweet spot

**Typical Finding**: 
- Lower speeds (30-50 km/h) minimize drag
- Higher speeds increase energy consumption exponentially

---

### Example 4: Custom Vehicle Testing

**Scenario**: Testing a more aerodynamic design

**Modifications**:
- Reduce Cd from 0.8 to 0.3
- Reduce frontal area to 0.4 m²

**Expected Impact**:
- Significant reduction in drag force
- Lower energy consumption at high speeds
- Higher top speed achievable

## 🛠️ Customization

### Modifying Vehicle Parameters

Edit `simulation_engine.py` to change default values:

```python
@dataclass
class VehicleParameters:
    drag_coefficient: float = 0.8  # Change this
    rolling_resistance: float = 0.02
    vehicle_mass: float = 150.0
    # ... etc
```

### Adding New Scenarios

In `main_app.py`, add to `load_scenario()`:

```python
elif scenario_type == 'custom':
    self.gradient_input.setValue(10)
    self.speed_input.setValue(70)
    self.duration_input.setValue(150)
```

## 📁 Project Structure

```
EV_Simulation/
├── main_app.py                 # Main GUI application
├── simulation_engine.py        # Physics simulation engine
├── requirements.txt            # Python dependencies
├── APP_README.md              # This file
├── DETAILED_SHEET_ANALYSIS.md # Data analysis reference
├── GPM_Performance Analysis.xlsx  # Original data
└── [exported results].csv     # Generated simulation data
```

## 🐛 Troubleshooting

### Issue: Application won't start

**Solution**: Ensure all dependencies are installed
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Plots not displaying

**Solution**: Check matplotlib backend
```bash
pip uninstall matplotlib
pip install matplotlib
```

### Issue: Simulation runs slowly

**Solution**: Reduce duration or increase time step in `simulation_engine.py`

## 📝 Data Export Format

Exported CSV files contain the following columns:

| Column | Description | Unit |
|--------|-------------|------|
| time | Simulation time | seconds |
| speed_ms | Vehicle speed | m/s |
| speed_kmh | Vehicle speed | km/h |
| motor_rpm | Motor rotational speed | RPM |
| motor_torque | Total motor torque | Nm |
| motor_power | Motor power | kW |
| tractive_force | Driving force | N |
| rolling_resistance | Rolling friction | N |
| drag_force | Aerodynamic drag | N |
| climbing_force | Gravity component | N |
| total_resistance | Sum of resistances | N |
| net_force | Accelerating force | N |
| acceleration | Vehicle acceleration | m/s² |
| distance | Cumulative distance | km |
| energy | Cumulative energy | kWh |

## 🔮 Future Enhancements

- [ ] Battery state-of-charge simulation
- [ ] Regenerative braking modeling
- [ ] Multi-segment route simulation
- [ ] Temperature effects on performance
- [ ] Real-time comparison mode
- [ ] 3D terrain visualization
- [ ] Drive cycle analysis (WLTP, NEDC)

## 📄 License

MIT License - Feel free to use and modify for your projects

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional physics models
- UI/UX enhancements
- Performance optimizations
- Documentation improvements

## 📧 Support

For issues or questions:
1. Check this README
2. Review `DETAILED_SHEET_ANALYSIS.md` for data insights
3. Examine the source code comments

## 🙏 Acknowledgments

Based on real EV performance data from GPM Performance Analysis.

---

**Built with ❤️ for EV enthusiasts and engineers**

*Last updated: October 29, 2025*
