# EV Power Train Simulation Tool

## 📋 Overview

A comprehensive **PyQt6-based desktop application** for simulating and analyzing Electric Vehicle (EV) and Unmanned Ground Vehicle (UGV) power train performance. Features real-time physics simulation, multi-graph visualization, and detailed output analysis.

---

## 🚀 Key Features

### Dual Vehicle Support
- **EV Mode**: Full electric vehicle simulation with battery analysis
- **UGV Mode**: Unmanned ground vehicle with specialized terrain capabilities

### Real-Time Simulation
- **120-second physics simulation** using iterative Euler integration
- **241 data points** with 0.5-second time steps
- **Verified calculation engine** with locked physics algorithms

### Multi-Graph Visualization (4 Tabs)
1. **Speed Tab**: Vehicle speed progression (km/h) - Orange line
2. **Power Tab**: Per-motor power consumption (Watts) - Orange line
3. **Forces Tab**: 4-force analysis with color coding
   - Tractive Force (Orange)
   - Rolling Resistance (Blue)
   - Drag Force (Yellow)
   - Load Resistance (Gray)
4. **Motor Tab**: Dual subplots
   - Motor Speed (RPM) - Blue line
   - Total Motor Torque (Nm) - Blue line

### Output Value Simulation
- Force calculations (Fdrag, Froll, Fclimb)
- Acceleration analysis (Term1, Term2, Term3)
- Battery capacity analysis
- Vehicle range estimation

### Data Export
- **Excel export** with complete simulation data
- **241 rows × 17 columns** per simulation
- Single sheet: "Simulation Data"

---

## 🎯 Quick Start

### Installation

1. **Install Python 3.8+** (if not already installed)

2. **Install Dependencies**
```bash
pip install PyQt6 matplotlib numpy pandas openpyxl
```

3. **Run the Application**
```bash
python main_app.py
```

### Basic Workflow

1. **Select Vehicle Type**: Choose EV or UGV from dropdown
2. **Set Parameters**: Adjust vehicle parameters in left panel
3. **Configure Simulation**: Set gradient and mode (Eco/Boost)
4. **Run Simulation**: Click "▶ Run Simulation" button
5. **View Results**: Check all 4 graph tabs + data table
6. **Export Data**: Click "💾 Export Results" for Excel file

---

## 📁 Project Structure

### Main Application
- **main_app.py** - Main PyQt6 application (3,000+ lines)
  - GUI layout and components
  - Physics simulation engine
  - Graph plotting with matplotlib
  - Excel export functionality

### Documentation
- **README.md** - This file (project overview)
- **FORCES_TAB_UPDATE.md** - Forces tab implementation details
- **POWER_TAB_UPDATE.md** - Power tab implementation details
- **SPEED_TAB_UPDATE.md** - Speed tab implementation details
- **UNIFIED_SIMULATION_WORKFLOW.md** - Workflow documentation

---

## 🔧 Technical Specifications

### Physics Engine
- **Integration Method**: Iterative Euler integration
- **Time Step**: 0.5 seconds (dt = 0.5)
- **Duration**: 120 seconds total
- **Data Points**: 241 rows (including t=0)
- **Initial Conditions**: v₀ = 0 m/s (start from rest)

### Force Calculations
```
F_tractive = (Motor_Torque × Gear_Ratio) / Wheel_Radius
F_roll = Cr × Mass × g
F_drag = 0.5 × Cd × ρ × Area × v²
F_climb = Mass × g × sin(gradient)
F_net = F_tractive - (F_roll + F_drag + F_climb)
a = F_net / Mass
```

### Motor Torque Curve
```
IF RPM ≤ Base_RPM:
    Torque = Constant_Torque × Num_Motors
ELSE:
    Torque = (Power × 60) / (2π × RPM)
```

### Default EV Parameters
- **Drag Coefficient (Cd)**: 0.8
- **Rolling Resistance (Cr)**: 0.0214
- **Vehicle Mass**: 160.4 kg
- **Frontal Area**: 0.5 m²
- **Wheel Radius**: 0.2795 m
- **Gear Ratio**: 5.268
- **Motors**: 2 × 52 Nm (Boost mode)
- **Max Power**: 22 kW (Boost) / 4 kW (Eco)

### Default UGV Parameters
- Similar to EV with additional tracked vehicle parameters
- **Track Width**: 0.5 m
- **Skid Coefficient**: 0.5
- **Step Height**: 0.1 m
- **Wheels**: 4 total, 4 powered

---

## 📊 Graph Tabs Explained

### 1. Speed Tab (Orange)
- **X-axis**: Time (seconds, 0-120)
- **Y-axis**: Vehicle Speed (km/h)
- **Shows**: Acceleration from 0 to max speed
- **Pattern**: S-curve (rapid acceleration → plateau)

### 2. Power Tab (Orange)
- **X-axis**: Time (seconds, 0-120)
- **Y-axis**: Per-Motor Power (Watts)
- **Shows**: Power consumption per motor
- **Pattern**: Constant power region (Boost: 2000W per motor)

### 3. Forces Tab (Multi-color)
- **X-axis**: Time (seconds, 0-120)
- **Y-axis**: Force (Newtons)
- **4 Lines**:
  - Orange: Tractive Force (decreases as speed increases)
  - Blue: Rolling Resistance (constant ~31N)
  - Yellow: Drag Force (increases with v²)
  - Gray: Load Resistance (total resistance)

### 4. Motor Tab (Blue, Dual Subplots)
- **Top Plot**: Motor Speed (RPM)
  - Shows RPM increase from 0 to ~4200 RPM
  - Legend: lower right
- **Bottom Plot**: Total Motor Torque (Nm)
  - Shows torque decrease from ~74 Nm to ~9 Nm
  - Legend: upper right
  - **Pattern**: Inverse relationship (constant power = torque × RPM)

---

## 📊 Data Table (17 Columns)

The simulation generates a complete data table with 241 rows:

| Column Name | Unit | Description |
|-------------|------|-------------|
| Time | s | Simulation time (0-120 seconds) |
| Vehicle Speed (m/s) | m/s | Speed in meters per second |
| Vehicle Speed (Kmph) | km/h | Speed in kilometers per hour |
| Motor Speed (RPM) | RPM | Motor rotational speed |
| Gradient (Degree) | ° | Road gradient angle |
| Mode, Eco-1, Boost-2 | - | Operating mode (1=Eco, 2=Boost) |
| Total Motor Torque (Nm) | Nm | Combined torque from all motors |
| Total Number of Power Wheel (No) | - | Number of driven wheels |
| PerMotor Torque (Nm) | Nm | Torque per motor |
| PerMotor Power (Watts) | W | Power per motor |
| Motoring Tractive Force F_Tractive (N) | N | Forward driving force |
| Froll (N) | N | Rolling resistance force |
| Fdrag (N) | N | Aerodynamic drag force |
| Fclimb (N) | N | Climbing resistance force |
| F_Load Resitance (N) | N | Total resistance force |
| Net Force F_Net (N) | N | Net accelerating force |
| Vehicle Acceleration (m/s) | m/s² | Vehicle acceleration |

---

## 🎮 User Interface Layout

### Left Panel: Vehicle Parameters
- **Vehicle Type Selector**: EV / UGV dropdown
- **Parameter Groups** (collapsible):
  - Physical Parameters
  - Drivetrain Parameters
  - Weight Parameters
  - Battery Parameters
  - Performance Parameters
  - UGV-Specific (tracked vehicles)
- **Buttons**:
  - 🔄 Reset to Default Values
  - 💡 Compute Output Values

### Right Panel: Output & Results
- **Output Value Simulation Results** (top)
  - Shows calculated forces, terms, and battery analysis
  - Cleared when reset button is clicked

### Bottom Panel: Simulation & Graphs
- **Simulation Controls**:
  - Gradient Input (degrees)
  - Mode Selection (Eco / Boost)
  - ▶ Run Simulation button
  - 💾 Export Results button
  - 🔄 Reset Simulation button
- **Tab Widget**:
  - Speed Tab (graph)
  - Power Tab (graph)
  - Forces Tab (graph)
  - Motor Tab (graph)
  - Data Table Tab (241 rows)

---

## 🎯 Key Use Cases

### 1. Design Optimization
- Adjust parameters (Cd, Cr, mass, etc.)
- Run simulation to see impact
- Compare results across configurations

### 2. Performance Analysis
- Test different gradients (flat, hills, steep)
- Compare Eco vs Boost modes
- Analyze force distribution

### 3. Battery Sizing
- Calculate required power for acceleration
- Estimate battery capacity from drive cycles
- Analyze energy consumption patterns

### 4. Motor Selection
- Verify torque requirements
- Check RPM operating range
- Validate power ratings

### 5. Education & Training
- Visualize physics concepts
- Understand force interactions
- Learn EV/UGV fundamentals

---

## 🔬 Recent Updates (Version 9.0)

### Major Architectural Simplification (Nov 7, 2025)
- ✅ **Removed simulation_engine.py** - Single source of truth
- ✅ **Eliminated background threading** - Fast execution (<0.1s)
- ✅ **Simplified export** - Single Excel sheet
- ✅ **Unified simulation workflow** - Direct table generation
- ✅ **Code reduction** - Removed ~497 lines

### All Graph Tabs Unified (Nov 7, 2025)
- ✅ **Speed Tab** - Updated to plot from Data Table
- ✅ **Power Tab** - Updated to plot from Data Table
- ✅ **Forces Tab** - Updated to plot from Data Table
- ✅ **Motor Tab** - Updated to plot from Data Table (dual subplots)

### UI Improvements
- ✅ **Removed Results Summary panel** - Cleaner interface
- ✅ **Removed Generate Graph Data button** - Automatic on simulation
- ✅ **Output area clear on reset** - EV and UGV modes
- ✅ **Unified export** - Single "Export Results" button

---

## 📚 Documentation Files

- **FORCES_TAB_UPDATE.md** - Forces tab color coding and implementation
- **POWER_TAB_UPDATE.md** - Power tab update details
- **SPEED_TAB_DATA_SOURCE.md** - Speed tab data source verification
- **SPEED_TAB_UPDATE.md** - Speed tab orange styling
- **UNIFIED_SIMULATION_WORKFLOW.md** - Complete workflow documentation
- **EXPORT_UNIFIED.md** - Export functionality details
- **RESULTS_SUMMARY_REMOVED.md** - UI simplification notes

---

## 🛠️ Technology Stack

- **Python 3.8+**
- **PyQt6** - GUI framework
- **Matplotlib** - Graph plotting
- **NumPy** - Numerical computations
- **Pandas** - Data handling
- **OpenPyXL** - Excel export

---

## 📝 License & Credits

**EV Power Train Simulation Tool**  
Version 9.0 - Single Source of Truth Architecture  
Last Updated: November 7, 2025

Developed for electric vehicle and unmanned ground vehicle power train analysis and design optimization.

---

## 📞 Support

For detailed documentation, see the markdown files in this directory.

For physics algorithms, review the **locked code sections** in `main_app.py`.

For technical issues, check the inline comments and docstrings.

---

*"Simplicity is the ultimate sophistication."* - Leonardo da Vinci
