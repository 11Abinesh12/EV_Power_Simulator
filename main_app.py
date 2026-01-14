"""
================================================================================
EV POWER TRAIN SIMULATION TOOL
================================================================================

Description:
    Comprehensive desktop application for simulating and analyzing Electric 
    Vehicle (EV) and Unmanned Ground Vehicle (UGV) power train performance.
    Features real-time physics simulation with iterative Euler integration,
    multi-graph visualization, and detailed output analysis.

Version:        9.0 - Single Source of Truth Architecture
Last Updated:   November 7, 2025
Author:         [Your Name/Organization]
License:        [Your License]

================================================================================
FEATURES
================================================================================

✓ Dual Vehicle Support: EV and UGV modes with specialized parameters
✓ Real-Time Simulation: 120-second physics with 241 data points
✓ Multi-Graph Visualization: 4 interactive tabs (Speed, Power, Forces, Motor)
✓ Data Table: Complete 17-column dataset with all simulation values
✓ Excel Export: Single-sheet export with all simulation data
✓ Output Analysis: Force calculations, battery sizing, range estimation
✓ Parameter Management: Default values, reset functionality, terrain scenarios

================================================================================
TECHNICAL SPECIFICATIONS
================================================================================

Physics Engine:
    - Integration Method: Iterative Euler integration
    - Time Step: 0.5 seconds
    - Duration: 120 seconds
    - Data Points: 241 rows (including t=0)
    - Initial Conditions: v₀ = 0 m/s (start from rest)

Graph Tabs:
    1. Speed Tab (Orange): Vehicle speed vs time
    2. Power Tab (Orange): Per-motor power consumption
    3. Forces Tab (Multi-color): 4-force analysis
       - Tractive Force (Orange)
       - Rolling Resistance (Blue)
       - Drag Force (Yellow)
       - Load Resistance (Gray)
    4. Motor Tab (Blue): Dual subplots
       - Motor Speed (RPM)
       - Total Motor Torque (Nm)

Technology Stack:
    - Python 3.8+
    - PyQt6 (GUI framework)
    - Matplotlib (Graph plotting)
    - NumPy (Numerical computations)
    - Pandas (Data handling)
    - OpenPyXL (Excel export)

================================================================================
VERSION HISTORY
================================================================================

Version 9.0 (Nov 7, 2025) - Major Architectural Simplification
    ✓ Removed simulation_engine.py - Single source of truth
    ✓ Eliminated background threading - Fast execution (<0.1s)
    ✓ Simplified export - Single Excel sheet
    ✓ Unified simulation workflow - Direct table generation
    ✓ Code reduction - Removed ~497 lines

Version 8.0 (Nov 7, 2025) - Motor Tab Update
    ✓ Updated Motor tab with dual subplots
    ✓ All 4 graph tabs now plot from Data Table

Version 7.0 (Nov 7, 2025) - Forces Tab Update
    ✓ Updated Forces tab with 4 color-coded lines
    ✓ Multi-line force visualization

Version 6.0 (Nov 7, 2025) - Power Tab Update
    ✓ Updated Power tab to plot from Data Table
    ✓ Orange line styling with Watts units

Version 5.0 (Nov 7, 2025) - Streamlined Interface
    ✓ Removed Results Summary panel
    ✓ Cleaner UI with more space

================================================================================
CREDITS & ACKNOWLEDGMENTS
================================================================================

Development Team:
    - Lead Developer: [Your Name]
    - Project Supervisor: [Supervisor Name]
    - Organization: [Your Organization]

Special Thanks:
    - Physics calculations based on standard vehicle dynamics equations
    - UI design inspired by modern engineering simulation tools
    - PyQt6 and Matplotlib communities for excellent frameworks

Contact:
    - Email: [Your Email]
    - GitHub: [Your GitHub]
    - Documentation: See README.md and *.md files in project directory

================================================================================
USAGE
================================================================================

Quick Start:
    1. Install dependencies: pip install PyQt6 matplotlib numpy pandas openpyxl
    2. Run application: python main_app.py
    3. Select vehicle type (EV or UGV)
    4. Adjust parameters in left panel
    5. Set gradient and mode
    6. Click "▶ Run Simulation"
    7. View results in graph tabs and data table
    8. Export data with "💾 Export Results"

Key Workflows:
    - Design Optimization: Adjust parameters and compare results
    - Performance Analysis: Test different gradients and modes
    - Battery Sizing: Calculate power requirements
    - Motor Selection: Verify torque and RPM specifications
    - Education: Visualize physics concepts

================================================================================
LICENSE
================================================================================

[Insert your license text here - MIT, GPL, Proprietary, etc.]

Copyright (c) 2025 [Your Name/Organization]
All rights reserved.

================================================================================
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QGroupBox, QGridLayout, QTabWidget,
                             QTextEdit, QFileDialog, QMessageBox, QProgressBar,
                             QDoubleSpinBox, QSpinBox, QMenuBar, QMenu, QSplitter,
                             QStackedWidget, QScrollArea, QTableWidget, QTableWidgetItem,
                             QHeaderView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Set matplotlib to use light theme
plt.style.use('default')
matplotlib.rcParams['figure.facecolor'] = 'white'
matplotlib.rcParams['axes.facecolor'] = 'white'
matplotlib.rcParams['savefig.facecolor'] = 'white'
matplotlib.rcParams['axes.edgecolor'] = 'black'
matplotlib.rcParams['axes.labelcolor'] = 'black'
matplotlib.rcParams['xtick.color'] = 'black'
matplotlib.rcParams['ytick.color'] = 'black'
matplotlib.rcParams['text.color'] = 'black'
matplotlib.rcParams['grid.color'] = 'gray'
import pandas as pd
import json


# ========== EV DEFAULT CONSTANTS ==========
EV_DEFAULTS = {
    # Physical Parameters
    'wheel_radius': 0.559/2,        # m
    'cd': 0.8,                     # Drag coefficient
    'cr': 0.02,                    # Rolling resistance coefficient
    'frontal_area': 0.5,           # m²
    'air_density': 1.164,          # kg/m³
    
    # Drivetrain Parameters
    'gear_ratio': 5.221,
    'gear_efficiency': 95.0,       # %
    'motor_efficiency': 85.0,      # %
    'motor_base_rpm': 500,
    
    # Weight Parameters (base values)
    'battery_weight_input': 10.5,   # kg
    'vehicle_weight': 150.0,       # kg
    'passenger_weight': 0.0,       # kg
    'motor_controller_weight': 0.0, # kg
    'other_weights': 0.0,          # kg
    'generator_weight': 0.0,       # kg
    
    # Battery Parameters
    'battery_requirements': 'Lithium',
    'battery_chemistry': 'NCM',
    'battery_voltage': 24.0,       # V
    'weight_per_wh': 0.0065,       # kg/Wh (approx. 154 Wh/kg)
    'peukert_coeff': 1.05,
    'discharge_hr': 2.0,           # Hr
    'dod_pct': 100.0,              # %
    'battery_current': 55.0,       # A
    'true_capacity_wh': 1839.0,    # Wh
    'true_capacity_ah': 77.0,      # Ah
    'tentative_ah': 78.0,          # Ah
    'tentative_wh': 1870.0,        # Wh
    'battery_weight_total': 12,  # kg
    
    # Performance Parameters
    'rotary_inertia': 1.06,
    'max_speed': 50.0,             # km/h
    'slope_speed': 5.0,            # km/h
    'gradeability': 30.0,          # degrees
    'accel_end_speed': 50.0,       # km/h
    'accel_period': 5.0,           # seconds
    'vehicle_range': 70.0,         # km
}

# Calculated Weight Parameters (derived from base values)
EV_DEFAULTS['kerb_weight'] = EV_DEFAULTS['battery_weight_input'] + EV_DEFAULTS['vehicle_weight']
EV_DEFAULTS['gvw'] = EV_DEFAULTS['kerb_weight'] + EV_DEFAULTS['passenger_weight']

# UGV Default Parameters (Unmanned Ground Vehicle)
UGV_DEFAULTS = {
    # Physical Parameters
    'wheel_radius': 0.559/2,            # m
    'cd': 0.8,                         # Drag coefficient
    'cr': 0.02,                        # Rolling resistance coefficient
    'frontal_area': 0.5,               # m²
    'air_density': 1.164,              # kg/m³
    
    # Drivetrain Parameters
    'gear_ratio': 5.221,
    'gear_efficiency': 95.0,           # %
    'motor_efficiency': 85.0,          # %
    'motor_base_rpm': 500,
    
    # Weight Parameters
    'battery_weight_input': 10.5,   # kg
    'vehicle_weight': 150.0,       # kg
    'passenger_weight': 0.0,       # kg
    'motor_controller_weight': 0.0, # kg
    'other_weights': 0.0,          # kg
    'generator_weight': 0.0,       # kg       
    
    # Battery Parameters
    'battery_requirements': 'Lithium',
    'battery_chemistry': 'NCM',
    'battery_voltage': 24.0,       # V
    'weight_per_wh': 0.0065,       # kg/Wh (approx. 154 Wh/kg)
    'peukert_coeff': 1.05,
    'discharge_hr': 2.0,           # Hr
    'dod_pct': 100.0,              # %
    'battery_current': 55.0,       # A
    'true_capacity_wh': 1839.0,    # Wh
    'true_capacity_ah': 77.0,      # Ah
    'tentative_ah': 78.0,          # Ah
    'tentative_wh': 1870.0,        # Wh
    'battery_weight_total': 12,  # kg    
    
    # Performance Parameters
    'rotary_inertia': 1.06,
    'max_speed': 50.0,             # km/h
    'slope_speed': 5.0,            # km/h
    'gradeability': 30.0,          # degrees
    'accel_end_speed': 50.0,       # km/h
    'accel_period': 5.0,           # seconds
    'vehicle_range': 70.0,         # km
    
    # UGV-Specific Parameters
    'step_height': 0.1,                # m
    'num_wheels': 4,                   # Total number of wheels
    'num_powered_wheels': 2,           # Number of powered wheels
    'track_width': 0.6,                # m (distance between left and right wheels)
    'skid_coefficient': 0.7,           # Coefficient of friction for skid turning
    'spin_angular_rad': 0.5,           # rad/s (angular velocity during spin)
}

# Calculated UGV Weight Parameters (derived from base values)
UGV_DEFAULTS['kerb_weight'] = UGV_DEFAULTS['battery_weight_input'] + UGV_DEFAULTS['vehicle_weight']
UGV_DEFAULTS['gvw'] = UGV_DEFAULTS['kerb_weight'] + UGV_DEFAULTS['passenger_weight']

# Calculated UGV-Specific Parameters (derived from base values)
UGV_DEFAULTS['load_per_wheel'] = UGV_DEFAULTS['gvw'] / UGV_DEFAULTS['num_wheels']  # kg per wheel
UGV_DEFAULTS['torque_climb'] = UGV_DEFAULTS['step_height'] * 9.81 * UGV_DEFAULTS['load_per_wheel']  # Nm
UGV_DEFAULTS['spin_angular_deg'] = UGV_DEFAULTS['spin_angular_rad'] * 57.2958  # rad/s to deg/s

# ========== GPM MOTOR SPECIFICATIONS (ePropelled Rhino Series) ==========
GPM_MOTORS = {
    'Default': {
        'name': 'Default (Original)',
        'continuous_power_w': 1000,     # Watts per motor (eco mode)
        'peak_power_w': 2000,           # Watts per motor (boost mode)
        'peak_torque_nm': 37,           # Nm per motor (boost constant torque)
        'continuous_torque_nm': 19,     # Nm per motor (eco constant torque)
        'base_rpm': 500,                # RPM threshold for constant torque region
        'max_rpm': 7500,
        'efficiency': 0.90,
        'weight_kg': 0                  # No additional weight (already included)
    },
    'GPM35': {
        'name': 'GPM35 (4kW/8kW)',
        'continuous_power_w': 4000,     # Watts per motor
        'peak_power_w': 8000,           # Watts per motor
        'peak_torque_nm': 35,           # Nm per motor
        'continuous_torque_nm': 17.5,   # Nm per motor (estimated: half of peak)
        'base_rpm': 500,                # RPM threshold
        'max_rpm': 7500,
        'efficiency': 0.90,
        'weight_kg': 13.5
    },
    'GPM50': {
        'name': 'GPM50 (6kW/11kW)',
        'continuous_power_w': 6000,
        'peak_power_w': 11000,
        'peak_torque_nm': 52,
        'continuous_torque_nm': 26,     # Nm per motor (estimated)
        'base_rpm': 500,
        'max_rpm': 7500,
        'efficiency': 0.90,
        'weight_kg': 14.5
    },
    'GPM70': {
        'name': 'GPM70 (8kW/16kW)',
        'continuous_power_w': 8000,
        'peak_power_w': 16000,
        'peak_torque_nm': 70,
        'continuous_torque_nm': 35,     # Nm per motor (estimated)
        'base_rpm': 500,
        'max_rpm': 7500,
        'efficiency': 0.90,
        'weight_kg': 18
    }
}

# ========== GRAPH SIMULATION DEFAULT CONSTANTS ==========

GRAPH_SIM_DEFAULTS = {
    # Simulation Environment Parameters
    'gradient_deg': 0.0,               # degrees - Road slope angle
    'mode': 'boost',                   # 'boost' or 'eco' - Operating mode

    # Initial Time and Speed Parameters
    'init_time': 0.0,                  # s - Starting time
    'init_vehicle_speed_ms': 0.0,      # m/s - Initial vehicle speed
    'init_vehicle_speed_kmph': 0.0,    # km/h - Initial vehicle speed (display)
    
    # Initial Motor Parameters
    'init_motor_speed_rpm': 0.0,     # RPM - Initial motor speed
    'init_num_power_wheels': 2,                   # count - Number of powered wheels
    'init_total_motor_torque': 74.0,   # Nm - Total torque from all motors
    'init_per_motor_torque': 50.0,     # Nm - Torque per individual motor
    'init_per_motor_power': 2000.0,    # W - Power per individual motor
    
    # Initial Force Parameters
    'init_tractive_force': 500.0,      # N - Driving force at wheels
    'init_froll': 30.69,               # N - Rolling resistance force
    'init_fdrag': 0.0,                 # N - Aerodynamic drag force
    'init_fclimb': 0.0,                # N - Climbing force (gradient)
    'init_fload': 30.69,               # N - Total load resistance (Froll + Fdrag + Fclimb)
    'init_fnet': 0.0,                  # N - Net force (Tractive - Load)
    
    # Initial Acceleration Parameter
    'init_vehicle_accel': 0.0,         # m/s² - Vehicle acceleration
    
    # Simulation Control Parameters
    'duration': 120.0,                  # s - Simulation duration (2m)
}

# Calculated Graph Simulation Parameters (derived from base values and EV defaults)
# Calculate init_vehicle_speed_kmph from init_vehicle_speed_ms
GRAPH_SIM_DEFAULTS['init_vehicle_speed_kmph'] = GRAPH_SIM_DEFAULTS['init_vehicle_speed_ms'] * 3.6

# Calculate init_motor_speed_rpm using formula: (speed_kmph * gear_ratio) / (2 * π * wheel_radius * 0.001 * 60)
# Uses EV_DEFAULTS for gear_ratio and wheel_radius
GRAPH_SIM_DEFAULTS['init_motor_speed_rpm'] = (
    GRAPH_SIM_DEFAULTS['init_vehicle_speed_kmph'] * EV_DEFAULTS['gear_ratio']
) / (2 * 3.14159 * EV_DEFAULTS['wheel_radius'] * 0.001 * 60)

# Calculate init_total_motor_torque based on mode and motor RPM
# Formula: IF(mode=boost, IF(RPM<500, 37, (2000*60)/(2*π*RPM)), IF(RPM<500, 19, (1000*60)/(2*π*RPM))) * 2
# When RPM < 500 (including 0), use constant values: 37 for boost, 19 for eco
GRAPH_SIM_DEFAULTS['init_total_motor_torque'] = (
    GRAPH_SIM_DEFAULTS['mode'] == 'boost' and (
        GRAPH_SIM_DEFAULTS['init_motor_speed_rpm'] < 500 and 37 or (
            (2000 * 60) / (2 * 3.14159 * GRAPH_SIM_DEFAULTS['init_motor_speed_rpm'])
        )
    ) or (
        GRAPH_SIM_DEFAULTS['init_motor_speed_rpm'] < 500 and 19 or (
            (1000 * 60) / (2 * 3.14159 * GRAPH_SIM_DEFAULTS['init_motor_speed_rpm'])
        )
    )
) * 2

# Calculate init_per_motor_torque: total torque divided by number of power wheels
GRAPH_SIM_DEFAULTS['init_per_motor_torque'] = (
    GRAPH_SIM_DEFAULTS['init_total_motor_torque'] / GRAPH_SIM_DEFAULTS['init_num_power_wheels']
)

# Calculate init_per_motor_power: (2π × RPM × torque) / 60
GRAPH_SIM_DEFAULTS['init_per_motor_power'] = (
    (2 * 3.14159 * GRAPH_SIM_DEFAULTS['init_motor_speed_rpm'] * GRAPH_SIM_DEFAULTS['init_per_motor_torque']) / 60
)

# Calculate init_tractive_force: (total_torque × gear_efficiency × gear_ratio) / wheel_radius
# Uses EV_DEFAULTS for gear_efficiency, gear_ratio, and wheel_radius
GRAPH_SIM_DEFAULTS['init_tractive_force'] = (
    (GRAPH_SIM_DEFAULTS['init_total_motor_torque'] * (EV_DEFAULTS['gear_efficiency'] / 100.0) * EV_DEFAULTS['gear_ratio']) 
    / EV_DEFAULTS['wheel_radius']
)

# Calculate init_froll: rolling resistance force = cr × mass × g
# Uses EV_DEFAULTS for cr and gvw
GRAPH_SIM_DEFAULTS['init_froll'] = EV_DEFAULTS['cr'] * EV_DEFAULTS['gvw'] * 9.81

# Calculate init_fdrag: aerodynamic drag force = cd × air_density × frontal_area × speed² × 0.03858025308642
# Uses EV_DEFAULTS for cd, air_density, frontal_area
GRAPH_SIM_DEFAULTS['init_fdrag'] = (
    EV_DEFAULTS['cd'] * EV_DEFAULTS['air_density'] * EV_DEFAULTS['frontal_area'] * 
    GRAPH_SIM_DEFAULTS['init_vehicle_speed_kmph'] * GRAPH_SIM_DEFAULTS['init_vehicle_speed_kmph'] * 0.03858025308642
)

# Calculate init_fclimb: climbing force = mass × g × sin(gradient_angle)
# Uses EV_DEFAULTS for gvw
import math
GRAPH_SIM_DEFAULTS['init_fclimb'] = (
    EV_DEFAULTS['gvw'] * 9.81 * math.sin(GRAPH_SIM_DEFAULTS['gradient_deg'] * 0.01745329)
)

# Calculate init_fload: total load resistance = froll + fdrag + fclimb
GRAPH_SIM_DEFAULTS['init_fload'] = (
    GRAPH_SIM_DEFAULTS['init_froll'] + GRAPH_SIM_DEFAULTS['init_fdrag'] + GRAPH_SIM_DEFAULTS['init_fclimb']
)

# Calculate init_fnet: net force = tractive force - load resistance
GRAPH_SIM_DEFAULTS['init_fnet'] = (
    GRAPH_SIM_DEFAULTS['init_tractive_force'] - GRAPH_SIM_DEFAULTS['init_fload']
)

# Calculate init_vehicle_accel: acceleration = net force / mass
# Uses EV_DEFAULTS for gvw (kerb_weight + passenger_weight)
GRAPH_SIM_DEFAULTS['init_vehicle_accel'] = (
    GRAPH_SIM_DEFAULTS['init_fnet'] / EV_DEFAULTS['gvw']
)

# Physical constants
GRAVITY = 9.81  # m/s² 
DEG_TO_RAD = 0.01745329  # degrees to radians conversion
KMH_TO_MS = 0.2777778   # km/h to m/s conversion


class PlotCanvas(FigureCanvas):
    """Canvas for matplotlib plots"""
    
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='white', edgecolor='black')
        super().__init__(self.fig)
        self.setParent(parent)
        self.setStyleSheet("background-color: white;")
    
    def plot_results(self, history, plot_type='speed'):
        """Plot simulation results"""
        self.fig.clear()
        
        if plot_type == 'speed':
            ax = self.fig.add_subplot(111)
            ax.plot(history['time'], history['speed_kmh'], color='orange', linewidth=2.5, label='Vehicle Speed (Kmph)')
            ax.set_xlabel('Time (Sec)', fontsize=10, fontweight='bold')
            ax.set_ylabel('Vehicle Speed (Kmph)', fontsize=10)
            ax.set_title('Vehicle Speed (Kmph)', fontsize=12, fontweight='bold')
            ax.legend(loc='lower right', fontsize=9)
            ax.grid(True, alpha=0.3, linestyle='--')
        
        elif plot_type == 'power':
            ax = self.fig.add_subplot(111)
            ax.plot(history['time'], history['motor_power'], color='orange', linewidth=2.5, label='PerMotor Power (Watts)')
            ax.set_xlabel('Time (Sec)', fontsize=10, fontweight='bold')
            ax.set_ylabel('PerMotor Power (Watts)', fontsize=10)
            ax.set_title('Power', fontsize=12, fontweight='bold')
            ax.legend(loc='upper right', fontsize=9)
            ax.grid(True, alpha=0.3, linestyle='--')
        
        elif plot_type == 'forces':
            ax = self.fig.add_subplot(111)
            ax.plot(history['time'], history['tractive_force'], color='orange', 
                   linewidth=2.5, label='Motoring Tractive Force F_Tractive (N)')
            ax.plot(history['time'], history['rolling_resistance'], color='blue', 
                   linewidth=2.5, label='Froll (N)')
            ax.plot(history['time'], history['drag_force'], color='yellow', 
                   linewidth=2.5, label='Fdrag (N)')
            ax.plot(history['time'], history['total_resistance'], color='gray', 
                   linewidth=2.5, label='F_Load Resistance (N)')
            ax.set_xlabel('Time (Sec)', fontsize=10, fontweight='bold')
            ax.set_ylabel('Force (N)', fontsize=10)
            ax.set_title('Forces', fontsize=12, fontweight='bold')
            ax.legend(fontsize=8, loc='upper right')
            ax.grid(True, alpha=0.3, linestyle='--')
        
        elif plot_type == 'motor':
            ax1 = self.fig.add_subplot(211)
            ax1.plot(history['time'], history['motor_rpm'], color='blue', linewidth=2.5, label='Motor Speed (RPM)')
            ax1.set_ylabel('Motor Speed (RPM)', fontsize=10)
            ax1.set_title('Motor Speed (RPM)', fontsize=12, fontweight='bold')
            ax1.legend(loc='lower right', fontsize=8)
            ax1.grid(True, alpha=0.3, linestyle='--')
            
            ax2 = self.fig.add_subplot(212)
            ax2.plot(history['time'], history['motor_torque'], color='blue', linewidth=2.5, label='Total Motor Torque (Nm)')
            ax2.set_xlabel('Time (Sec)', fontsize=10, fontweight='bold')
            ax2.set_ylabel('Total Motor Torque (Nm)', fontsize=10)
            ax2.set_title('Total Motor Torque (Nm)', fontsize=12, fontweight='bold')
            ax2.legend(loc='upper right', fontsize=8)
            ax2.grid(True, alpha=0.3, linestyle='--')
        
        elif plot_type == 'energy':
            ax = self.fig.add_subplot(111)
            ax.plot(history['time'], history['energy'], 'purple', linewidth=2)
            ax.set_xlabel('Time (s)', fontsize=10)
            ax.set_ylabel('Energy Consumed (kWh)', fontsize=10)
            ax.set_title('Energy Consumption', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        self.draw()


class EVSimulationApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.current_view = 'split'  # split, graphs_only, controls_only
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle('EV Power Train Simulation Tool')
        # Set responsive window size based on screen
        screen = QApplication.primaryScreen().geometry()
        width = min(1400, int(screen.width() * 0.85))
        height = min(900, int(screen.height() * 0.85))
        self.setGeometry(100, 100, width, height)
        self.setMinimumSize(800, 600)

        # Set application icon
        icon_path = 'ePropelled Logo.jpg'
        app_icon = QIcon(icon_path)
        self.setWindowIcon(app_icon)
        
        # Create menu bar
        self.create_menu_bar()
    
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header bar with ePropelled_Text.jpg logo
        header_widget = QWidget()
        header_widget.setStyleSheet('border-bottom: 1px solid #ddd;')
        header_widget.setMaximumHeight(60)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        
        # ePropelled_Text.jpg Logo (200px width, fixed size, centered)
        logo_label = QLabel()
        logo_pixmap = QPixmap('ePropelled_Text.jpg')
        if not logo_pixmap.isNull():
            scaled_logo = logo_pixmap.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
            logo_label.setFixedSize(200, scaled_logo.height())
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(logo_label)
        
        main_layout.addWidget(header_widget)
        
        # Top navbar tabs (global, outside splitter)
        self.nav_tabs = QTabWidget()
        self.nav_tabs.addTab(QWidget(), 'Output Value Simulation')
        self.nav_tabs.addTab(QWidget(), 'Graph Simulation')
        self.nav_tabs.addTab(QWidget(), 'Testing Point')
        self.nav_tabs.currentChanged.connect(self.on_nav_changed)
        self.nav_tabs.setMaximumHeight(40)
        main_layout.addWidget(self.nav_tabs)
        
        # Create splitter for resizable panels
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Controls
        self.left_panel = self.create_control_panel()
        self.splitter.addWidget(self.left_panel)
        
        # Right side uses a stacked widget to switch between Output and Graph views
        self.right_stack = QStackedWidget()
        
        # Page 0: Output values panel (default)
        self.output_panel = self.create_output_panel()
        self.right_stack.addWidget(self.output_panel)
        
        # Page 1: Graph visualization panel
        self.right_panel = self.create_visualization_panel()
        self.right_stack.addWidget(self.right_panel)
        
        # Page 2: Testing Point panel
        self.testing_point_panel = self.create_testing_point_panel()
        self.right_stack.addWidget(self.testing_point_panel)
        
        self.splitter.addWidget(self.right_stack)
        
        # Set initial splitter sizes (1:2 ratio)
        self.splitter.setSizes([400, 800])
        
        main_layout.addWidget(self.splitter)
        
        # Default to Output Value Simulation view
        self.right_stack.setCurrentIndex(0)
        # Trigger initial view setup
        if hasattr(self, 'nav_tabs'):
            self.on_nav_changed(0)  # Initialize Output Value Simulation mode
        
        # Initialize calculated weight fields
        self.update_ev_calculated_weights()
        self.update_ugv_calculated_weights()
        
        # Initialize graph simulation calculated fields
        self.update_graph_sim_calculated_values()

        self.statusBar().showMessage('Ready')
    
    def on_nav_changed(self, index: int):
        """Handle navbar tab changes to switch right view and buttons"""
        if index == 0:  # Output Value Simulation (default first tab)
            # Show output panel with comprehensive EV/UGV parameters
            self.right_stack.setCurrentIndex(0)  # Output panel
            self.left_panel.setVisible(True)
            # Hide graph simulation controls
            self.graph_sim_params_group.setVisible(False)
            self.runtime_params_group.setVisible(False)  # Hide runtime params in Output mode
            self.scenario_group.setVisible(False)
            self.btn_layout_widget.setVisible(False)
            # Show Vehicle Parameters for Output mode
            self.vehicle_group.setVisible(True)
            # Show comprehensive EV/UGV params and compute button
            if self.vehicle_type_combo.currentText() == 'EV':
                self.ev_params_group.setVisible(True)
                self.ugv_params_group.setVisible(False)
                self.reset_ev_defaults()  # Load default values
            else:  # UGV
                self.ev_params_group.setVisible(False)
                self.ugv_params_group.setVisible(True)
                self.reset_ugv_defaults()  # Load default values
            self.output_compute_btn.setVisible(True)
            self.output_compute_btn.setEnabled(True)
            # Give space for comprehensive params
            try:
                self.splitter.setSizes([400, 800])
            except Exception:  
                pass
            self.statusBar().showMessage('Output Value Simulation mode - Comprehensive Parameters')
        elif index == 1:  # Graph Simulation
            # Show graphs with basic simulation controls on the left
            self.right_stack.setCurrentIndex(1)  # Graphs panel
            self.left_panel.setVisible(True)
            # Show only basic simulation controls for running simulations
            self.graph_sim_params_group.setVisible(True)
            self.runtime_params_group.setVisible(True)  # Show runtime params in Graph mode
            self.scenario_group.setVisible(True)
            self.btn_layout_widget.setVisible(True)
            # Hide Vehicle Parameters and comprehensive EV/UGV params
            self.vehicle_group.setVisible(False)
            self.ev_params_group.setVisible(False)
            self.ugv_params_group.setVisible(False)
            self.output_compute_btn.setVisible(False)
            # Give space for basic params and graphs
            try:
                self.splitter.setSizes([400, 800])
            except Exception:
                pass
            self.statusBar().showMessage('Graph Simulation mode')
        else:  # Testing Point (index == 2)
            # Show testing point panel - HIDE left panel completely for full width
            self.right_stack.setCurrentIndex(2)  # Testing Point panel
            self.left_panel.setVisible(False)  # Hide left panel to use full width
            # Hide all controls (they're not needed in Testing Point mode)
            self.graph_sim_params_group.setVisible(False)
            self.runtime_params_group.setVisible(False)
            self.scenario_group.setVisible(False)
            self.btn_layout_widget.setVisible(False)
            self.vehicle_group.setVisible(False)
            self.ev_params_group.setVisible(False)
            self.ugv_params_group.setVisible(False)
            self.output_compute_btn.setVisible(False)
            self.statusBar().showMessage('Testing Point mode')
    
    def on_vehicle_type_changed(self, vehicle_type: str):
        """Handle vehicle type selection change to show/hide appropriate parameter sections"""
        if vehicle_type == 'EV':
            self.ev_params_group.setVisible(True)
            self.ugv_params_group.setVisible(False)
            self.reset_ev_defaults()  # Load default values
            self.statusBar().showMessage('EV parameters displayed')
        else:  # UGV
            self.ev_params_group.setVisible(False)
            self.ugv_params_group.setVisible(True)
            self.reset_ugv_defaults()  # Load default values
            self.statusBar().showMessage('UGV parameters displayed')
    
    def on_motor_selection_changed(self, motor_key: str):
        """Handle motor model selection change to show/hide custom fields and update calculations"""
        is_custom = (motor_key == 'Customize')
        
        # Toggle visibility of custom motor input fields
        self.custom_torque_label.setVisible(is_custom)
        self.custom_peak_torque.setVisible(is_custom)
        self.custom_power_label.setVisible(is_custom)
        self.custom_peak_power.setVisible(is_custom)
        
        # Update calculated values based on selected motor
        self.update_graph_sim_calculated_values()
        
        # Update status bar with motor info
        if motor_key in GPM_MOTORS:
            motor = GPM_MOTORS[motor_key]
            self.statusBar().showMessage(f"Motor: {motor['name']} - Peak: {motor['peak_torque_nm']} Nm, {motor['peak_power_w']/1000:.0f} kW")
        elif is_custom:
            self.statusBar().showMessage('Custom motor mode - Enter peak torque and power values')

    
    def create_menu_bar(self):
        """Create menu bar with view options"""
        menubar = self.menuBar()
        
        # Help Menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = help_menu.addAction('ℹ️ About')
        about_action.triggered.connect(self.show_about)
    
    def switch_view(self, view_mode):
        """Switch between different view modes"""
        self.current_view = view_mode
        
        if view_mode == 'split':
            # Show both panels
            self.left_panel.setVisible(True)
            self.right_panel.setVisible(True)
            self.splitter.setSizes([400, 800])
            self.statusBar().showMessage('Split View: Controls & Graphs')
            
        elif view_mode == 'graphs_only':
            # Hide controls, show only graphs
            self.left_panel.setVisible(False)
            self.right_panel.setVisible(True)
            self.statusBar().showMessage('Graphs Only View')
            
        elif view_mode == 'controls_only':
            # Hide graphs, show only controls
            self.left_panel.setVisible(True)
            self.right_panel.setVisible(False)
            self.statusBar().showMessage('Controls Only View')
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
            self.statusBar().showMessage('Exited Fullscreen')
        else:
            self.showFullScreen()
            self.statusBar().showMessage('Entered Fullscreen Mode')
    
    def create_output_panel(self):
        """Create right-side panel for Output Value Simulation"""
        panel = QWidget()
        v = QVBoxLayout(panel)
        header = QLabel('Output Value Simulation Results')
        header.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        v.addWidget(header)
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        v.addWidget(self.output_text)
        return panel
    
    def create_testing_point_panel(self):
        """Create right-side panel for Testing Point - Motor Efficiency Map with Comprehensive Test Points"""
        panel = QWidget()
        main_layout = QVBoxLayout(panel)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header
        header = QLabel('Motor Efficiency Test Points')
        header.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(header)
        
        # Description label
        desc_label = QLabel('Enter 10 test points with vehicle parameters to analyze motor efficiency across different operating conditions.')
        desc_label.setStyleSheet('color: #666; font-style: italic; margin-bottom: 5px;')
        desc_label.setWordWrap(True)
        main_layout.addWidget(desc_label)
        
        # Left side - Test Points Input Table (scrollable)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_panel.setMinimumWidth(550)
        
        # Create table for test points with all parameters
        self.test_points_table = QTableWidget()
        self.test_points_table.setRowCount(10)
        self.test_points_table.setColumnCount(11)  # Point #, RPM, Torque, GVW, Cd, Cr, Air Density, Frontal Area, Gear Ratio, Wheel Radius, Gradient
        
        # Set column headers
        headers = ['Pt', 'RPM', 'Torque\n(Nm)', 'GVW\n(kg)', 'Cd', 'Cr', 'Air ρ\n(kg/m³)', 'Area\n(m²)', 'Gear\nRatio', 'Wheel R\n(m)', 'Grade\n(°)']
        self.test_points_table.setHorizontalHeaderLabels(headers)
        
        # Make all columns stretch to fill available width
        header = self.test_points_table.horizontalHeader()
        from PyQt6.QtWidgets import QHeaderView
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Store input widgets for each test point
        self.test_point_inputs = []
        
        # Different default values for each of the 10 test points
        # Varying RPM, Torque, Gradient and some vehicle parameters for diverse analysis
        self.test_point_defaults = [
            # Point 1: Low speed, low torque, flat road
            {'rpm': 500, 'torque': 20, 'gvw': EV_DEFAULTS['gvw'], 'cd': EV_DEFAULTS['cd'], 
             'cr': EV_DEFAULTS['cr'], 'air_density': EV_DEFAULTS['air_density'], 
             'frontal_area': EV_DEFAULTS['frontal_area'], 'gear_ratio': EV_DEFAULTS['gear_ratio'], 
             'wheel_radius': EV_DEFAULTS['wheel_radius'], 'gradient': 0.0},
            
            # Point 2: Medium speed, medium torque, flat road
            {'rpm': 1500, 'torque': 50, 'gvw': EV_DEFAULTS['gvw'], 'cd': EV_DEFAULTS['cd'], 
             'cr': EV_DEFAULTS['cr'], 'air_density': EV_DEFAULTS['air_density'], 
             'frontal_area': EV_DEFAULTS['frontal_area'], 'gear_ratio': EV_DEFAULTS['gear_ratio'], 
             'wheel_radius': EV_DEFAULTS['wheel_radius'], 'gradient': 0.0},
            
            # Point 3: Optimal efficiency zone (mid RPM, mid-high torque)
            {'rpm': 2500, 'torque': 75, 'gvw': EV_DEFAULTS['gvw'], 'cd': EV_DEFAULTS['cd'], 
             'cr': EV_DEFAULTS['cr'], 'air_density': EV_DEFAULTS['air_density'], 
             'frontal_area': EV_DEFAULTS['frontal_area'], 'gear_ratio': EV_DEFAULTS['gear_ratio'], 
             'wheel_radius': EV_DEFAULTS['wheel_radius'], 'gradient': 0.0},
            
            # Point 4: High torque climbing - gentle slope
            {'rpm': 2000, 'torque': 100, 'gvw': EV_DEFAULTS['gvw'], 'cd': EV_DEFAULTS['cd'], 
             'cr': EV_DEFAULTS['cr'], 'air_density': EV_DEFAULTS['air_density'], 
             'frontal_area': EV_DEFAULTS['frontal_area'], 'gear_ratio': EV_DEFAULTS['gear_ratio'], 
             'wheel_radius': EV_DEFAULTS['wheel_radius'], 'gradient': 5.0},
            
            # Point 5: High speed cruise
            {'rpm': 4000, 'torque': 40, 'gvw': EV_DEFAULTS['gvw'], 'cd': EV_DEFAULTS['cd'], 
             'cr': EV_DEFAULTS['cr'], 'air_density': EV_DEFAULTS['air_density'], 
             'frontal_area': EV_DEFAULTS['frontal_area'], 'gear_ratio': EV_DEFAULTS['gear_ratio'], 
             'wheel_radius': EV_DEFAULTS['wheel_radius'], 'gradient': 0.0},
            
            # Point 6: Steep climb - high torque
            {'rpm': 1000, 'torque': 120, 'gvw': EV_DEFAULTS['gvw'], 'cd': EV_DEFAULTS['cd'], 
             'cr': EV_DEFAULTS['cr'], 'air_density': EV_DEFAULTS['air_density'], 
             'frontal_area': EV_DEFAULTS['frontal_area'], 'gear_ratio': EV_DEFAULTS['gear_ratio'], 
             'wheel_radius': EV_DEFAULTS['wheel_radius'], 'gradient': 15.0},
            
            # Point 7: Highway speed
            {'rpm': 5000, 'torque': 60, 'gvw': EV_DEFAULTS['gvw'], 'cd': EV_DEFAULTS['cd'], 
             'cr': EV_DEFAULTS['cr'], 'air_density': EV_DEFAULTS['air_density'], 
             'frontal_area': EV_DEFAULTS['frontal_area'], 'gear_ratio': EV_DEFAULTS['gear_ratio'], 
             'wheel_radius': EV_DEFAULTS['wheel_radius'], 'gradient': 0.0},
            
            # Point 8: Very high speed
            {'rpm': 7000, 'torque': 30, 'gvw': EV_DEFAULTS['gvw'], 'cd': EV_DEFAULTS['cd'], 
             'cr': EV_DEFAULTS['cr'], 'air_density': EV_DEFAULTS['air_density'], 
             'frontal_area': EV_DEFAULTS['frontal_area'], 'gear_ratio': EV_DEFAULTS['gear_ratio'], 
             'wheel_radius': EV_DEFAULTS['wheel_radius'], 'gradient': 0.0},
            
            # Point 9: Heavy load condition
            {'rpm': 3000, 'torque': 90, 'gvw': EV_DEFAULTS['gvw'] * 1.3, 'cd': EV_DEFAULTS['cd'], 
             'cr': EV_DEFAULTS['cr'], 'air_density': EV_DEFAULTS['air_density'], 
             'frontal_area': EV_DEFAULTS['frontal_area'], 'gear_ratio': EV_DEFAULTS['gear_ratio'], 
             'wheel_radius': EV_DEFAULTS['wheel_radius'], 'gradient': 3.0},
            
            # Point 10: Downhill regeneration
            {'rpm': 3500, 'torque': 25, 'gvw': EV_DEFAULTS['gvw'], 'cd': EV_DEFAULTS['cd'], 
             'cr': EV_DEFAULTS['cr'], 'air_density': EV_DEFAULTS['air_density'], 
             'frontal_area': EV_DEFAULTS['frontal_area'], 'gear_ratio': EV_DEFAULTS['gear_ratio'], 
             'wheel_radius': EV_DEFAULTS['wheel_radius'], 'gradient': -5.0},
        ]
        
        # Create input widgets for each row
        for i in range(10):
            row_inputs = {}
            defaults = self.test_point_defaults[i]  # Get defaults for this specific test point
            
            # Point number (read-only label)
            point_label = QTableWidgetItem(str(i + 1))
            point_label.setFlags(point_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
            point_label.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.test_points_table.setItem(i, 0, point_label)
            
            # RPM input
            rpm_input = QDoubleSpinBox()
            rpm_input.setRange(0, 10000)
            rpm_input.setDecimals(0)
            rpm_input.setSingleStep(100)
            rpm_input.setValue(defaults['rpm'])
            self.test_points_table.setCellWidget(i, 1, rpm_input)
            row_inputs['rpm'] = rpm_input
            
            # Torque input
            torque_input = QDoubleSpinBox()
            torque_input.setRange(0, 200)
            torque_input.setDecimals(1)
            torque_input.setSingleStep(5)
            torque_input.setValue(defaults['torque'])
            self.test_points_table.setCellWidget(i, 2, torque_input)
            row_inputs['torque'] = torque_input
            
            # GVW input
            gvw_input = QDoubleSpinBox()
            gvw_input.setRange(1, 10000)
            gvw_input.setDecimals(1)
            gvw_input.setSingleStep(10)
            gvw_input.setValue(defaults['gvw'])
            self.test_points_table.setCellWidget(i, 3, gvw_input)
            row_inputs['gvw'] = gvw_input
            
            # Cd input
            cd_input = QDoubleSpinBox()
            cd_input.setRange(0.01, 2.0)
            cd_input.setDecimals(3)
            cd_input.setSingleStep(0.01)
            cd_input.setValue(defaults['cd'])
            self.test_points_table.setCellWidget(i, 4, cd_input)
            row_inputs['cd'] = cd_input
            
            # Cr input
            cr_input = QDoubleSpinBox()
            cr_input.setRange(0.001, 0.5)
            cr_input.setDecimals(4)
            cr_input.setSingleStep(0.001)
            cr_input.setValue(defaults['cr'])
            self.test_points_table.setCellWidget(i, 5, cr_input)
            row_inputs['cr'] = cr_input
            
            # Air Density input
            air_density_input = QDoubleSpinBox()
            air_density_input.setRange(0.5, 2.0)
            air_density_input.setDecimals(3)
            air_density_input.setSingleStep(0.01)
            air_density_input.setValue(defaults['air_density'])
            self.test_points_table.setCellWidget(i, 6, air_density_input)
            row_inputs['air_density'] = air_density_input
            
            # Frontal Area input
            frontal_area_input = QDoubleSpinBox()
            frontal_area_input.setRange(0.1, 10.0)
            frontal_area_input.setDecimals(2)
            frontal_area_input.setSingleStep(0.1)
            frontal_area_input.setValue(defaults['frontal_area'])
            self.test_points_table.setCellWidget(i, 7, frontal_area_input)
            row_inputs['frontal_area'] = frontal_area_input
            
            # Gear Ratio input
            gear_ratio_input = QDoubleSpinBox()
            gear_ratio_input.setRange(0.1, 50.0)
            gear_ratio_input.setDecimals(3)
            gear_ratio_input.setSingleStep(0.1)
            gear_ratio_input.setValue(defaults['gear_ratio'])
            self.test_points_table.setCellWidget(i, 8, gear_ratio_input)
            row_inputs['gear_ratio'] = gear_ratio_input
            
            # Wheel Radius input
            wheel_radius_input = QDoubleSpinBox()
            wheel_radius_input.setRange(0.05, 1.0)
            wheel_radius_input.setDecimals(4)
            wheel_radius_input.setSingleStep(0.01)
            wheel_radius_input.setValue(defaults['wheel_radius'])
            self.test_points_table.setCellWidget(i, 9, wheel_radius_input)
            row_inputs['wheel_radius'] = wheel_radius_input
            
            # Gradient input
            gradient_input = QDoubleSpinBox()
            gradient_input.setRange(-45, 45)
            gradient_input.setDecimals(1)
            gradient_input.setSingleStep(1)
            gradient_input.setValue(defaults['gradient'])
            self.test_points_table.setCellWidget(i, 10, gradient_input)
            row_inputs['gradient'] = gradient_input
            
            self.test_point_inputs.append(row_inputs)
        
        # Set row height
        for i in range(10):
            self.test_points_table.setRowHeight(i, 35)
        
        # Enable scrolling
        self.test_points_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.test_points_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        
        left_layout.addWidget(self.test_points_table)
        
        # Buttons row
        btn_layout = QHBoxLayout()
        
        # Plot button
        self.plot_test_points_btn = QPushButton('📊 Plot Test Points')
        self.plot_test_points_btn.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        ''')
        self.plot_test_points_btn.clicked.connect(self.plot_efficiency_test_points)
        btn_layout.addWidget(self.plot_test_points_btn)
        
        # Reset to Defaults button
        self.reset_test_points_btn = QPushButton('🔄 Reset to Defaults')
        self.reset_test_points_btn.setStyleSheet('''
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        ''')
        self.reset_test_points_btn.clicked.connect(self.reset_test_points_to_defaults)
        btn_layout.addWidget(self.reset_test_points_btn)
        
        # Clear button
        self.clear_test_points_btn = QPushButton('🗑️ Clear All')
        self.clear_test_points_btn.setStyleSheet('''
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c41808;
            }
        ''')
        self.clear_test_points_btn.clicked.connect(self.clear_test_points)
        btn_layout.addWidget(self.clear_test_points_btn)
        
        btn_layout.addStretch()
        left_layout.addLayout(btn_layout)
        
        # Top section - Table on left, Results on right (side by side)
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        top_splitter.addWidget(left_panel)
        
        # Right side - Results panel (at top, next to table)
        results_panel = QWidget()
        results_layout = QVBoxLayout(results_panel)
        results_layout.setContentsMargins(5, 0, 0, 0)
        results_layout.setSpacing(2)
        results_panel.setMinimumWidth(250)  # Minimum width for results table
        
        # Results text area
        results_label = QLabel('Test Point Results:')
        results_label.setFont(QFont('Arial', 11, QFont.Weight.Bold))
        results_layout.addWidget(results_label)
        
        self.testing_point_text = QTextEdit()
        self.testing_point_text.setPlaceholderText('Results will be displayed here after plotting...')
        self.testing_point_text.setReadOnly(True)
        self.testing_point_text.document().setDocumentMargin(0)
        self.testing_point_text.setViewportMargins(0, 0, 0, 0)
        self.testing_point_text.setContentsMargins(0, 0, 0, 0)
        self.testing_point_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.testing_point_text.setStyleSheet('''
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                padding: 0px;
                margin: 0px;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #ccc;
                border-radius: 4px;
            }
        ''')
        results_layout.addWidget(self.testing_point_text)
        
        top_splitter.addWidget(results_panel)
        top_splitter.setSizes([750, 250])  # 3/4 for input table, 1/4 for results
        
        # Bottom section - Two graphs side by side with equal space
        graphs_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left graph - Efficiency Map
        efficiency_panel = QWidget()
        efficiency_layout = QVBoxLayout(efficiency_panel)
        efficiency_layout.setContentsMargins(0, 0, 5, 0)
        
        graph_header = QLabel('Efficiency in Torque-Speed Area')
        graph_header.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        graph_header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        efficiency_layout.addWidget(graph_header)
        
        self.efficiency_canvas = PlotCanvas(efficiency_panel, width=5, height=4, dpi=100)
        efficiency_layout.addWidget(self.efficiency_canvas)
        
        graphs_splitter.addWidget(efficiency_panel)
        
        # Right graph - Motor Suitability Analysis
        motor_panel = QWidget()
        motor_layout = QVBoxLayout(motor_panel)
        motor_layout.setContentsMargins(5, 0, 0, 0)
        
        # Motor selection header row
        motor_header_row = QHBoxLayout()
        
        motor_header = QLabel('Motor Suitability Analysis')
        motor_header.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        motor_header_row.addWidget(motor_header)
        
        motor_header_row.addStretch()
        
        motor_select_label = QLabel('Select Motor:')
        motor_select_label.setFont(QFont('Arial', 10))
        motor_header_row.addWidget(motor_select_label)
        
        self.motor_select_combo = QComboBox()
        self.motor_select_combo.addItems(['GPM35', 'GPM50', 'GPM70'])
        self.motor_select_combo.setCurrentIndex(0)
        self.motor_select_combo.setMinimumWidth(100)
        self.motor_select_combo.setStyleSheet('''
            QComboBox {
                padding: 5px 10px;
                border: 2px solid #2196F3;
                border-radius: 5px;
                background-color: white;
                color: black;
                font-weight: bold;
            }
            QComboBox:hover {
                border-color: #1976D2;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #2196F3;
                selection-color: white;
            }
        ''')
        self.motor_select_combo.currentTextChanged.connect(self.update_motor_suitability_plot)
        motor_header_row.addWidget(self.motor_select_combo)
        
        motor_layout.addLayout(motor_header_row)
        
        # Motor suitability canvas
        self.motor_suitability_canvas = PlotCanvas(motor_panel, width=5, height=4, dpi=100)
        motor_layout.addWidget(self.motor_suitability_canvas)
        
        graphs_splitter.addWidget(motor_panel)
        
        # Set equal sizes for both graphs (50-50 split)
        graphs_splitter.setSizes([500, 500])
        
        # Main vertical splitter - top section and graphs below
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(graphs_splitter)
        main_splitter.setSizes([320, 380])
        
        main_layout.addWidget(main_splitter)
        
        # Initialize plots
        self.plot_efficiency_map()
        self.plot_motor_suitability()
        
        return panel
    
    def plot_motor_suitability(self, test_points=None):
        """Plot motor operating envelope with test points to analyze suitability"""
        import numpy as np
        
        self.motor_suitability_canvas.fig.clear()
        ax = self.motor_suitability_canvas.fig.add_subplot(111)
        
        # Get selected motor
        motor_key = self.motor_select_combo.currentText()
        motor = GPM_MOTORS.get(motor_key, GPM_MOTORS['GPM35'])
        
        # Motor parameters
        peak_torque = motor['peak_torque_nm']
        continuous_torque = motor['continuous_torque_nm']
        peak_power = motor['peak_power_w']
        continuous_power = motor['continuous_power_w']
        base_rpm = motor['base_rpm']
        max_rpm = motor['max_rpm']
        
        # Create RPM range
        rpm_range = np.linspace(0, max_rpm, 500)
        
        # Calculate torque curves (constant torque region + constant power region)
        # Peak torque curve
        peak_torque_curve = np.zeros_like(rpm_range)
        for i, rpm in enumerate(rpm_range):
            if rpm <= base_rpm:
                peak_torque_curve[i] = peak_torque
            else:
                # Constant power region: P = T * omega, so T = P / omega
                omega = rpm * 2 * np.pi / 60
                peak_torque_curve[i] = min(peak_torque, peak_power / omega if omega > 0 else peak_torque)
        
        # Continuous torque curve
        continuous_torque_curve = np.zeros_like(rpm_range)
        for i, rpm in enumerate(rpm_range):
            if rpm <= base_rpm:
                continuous_torque_curve[i] = continuous_torque
            else:
                omega = rpm * 2 * np.pi / 60
                continuous_torque_curve[i] = min(continuous_torque, continuous_power / omega if omega > 0 else continuous_torque)
        
        # Plot motor envelope
        ax.fill_between(rpm_range, 0, continuous_torque_curve, alpha=0.3, color='green', label='Continuous Operation')
        ax.fill_between(rpm_range, continuous_torque_curve, peak_torque_curve, alpha=0.3, color='orange', label='Peak/Boost Operation')
        
        ax.plot(rpm_range, peak_torque_curve, 'r-', linewidth=2, label=f'Peak Torque ({peak_torque} Nm)')
        ax.plot(rpm_range, continuous_torque_curve, 'g-', linewidth=2, label=f'Continuous Torque ({continuous_torque} Nm)')
        
        # Plot test points if provided
        suitable_count = 0
        peak_only_count = 0
        unsuitable_count = 0
        
        if test_points:
            for p in test_points:
                if p['rpm'] > 0 or p['torque'] > 0:
                    rpm = p['rpm']
                    torque = p['torque']
                    point_num = p['point_num']
                    
                    # Determine suitability
                    # Find the torque limits at this RPM
                    if rpm <= base_rpm:
                        peak_limit = peak_torque
                        cont_limit = continuous_torque
                    else:
                        omega = rpm * 2 * np.pi / 60
                        peak_limit = min(peak_torque, peak_power / omega if omega > 0 else peak_torque)
                        cont_limit = min(continuous_torque, continuous_power / omega if omega > 0 else continuous_torque)
                    
                    # Check if within motor capability
                    if torque <= cont_limit and rpm <= max_rpm:
                        # Within continuous operation - GOOD
                        color = 'green'
                        marker = 'o'
                        suitable_count += 1
                    elif torque <= peak_limit and rpm <= max_rpm:
                        # Within peak operation only - WARNING
                        color = 'orange'
                        marker = '^'
                        peak_only_count += 1
                    else:
                        # Outside motor capability - BAD
                        color = 'red'
                        marker = 'x'
                        unsuitable_count += 1
                    
                    # Only use edgecolors for filled markers (not 'x')
                    if marker == 'x':
                        ax.scatter(rpm, torque, c=color, s=120, marker=marker, 
                                  linewidths=2, zorder=10)
                    else:
                        ax.scatter(rpm, torque, c=color, s=120, marker=marker, 
                                  linewidths=2, zorder=10, edgecolors='black')
                    
                    ax.annotate(f'P{point_num}', (rpm, torque), textcoords="offset points", 
                               xytext=(5, 5), fontsize=8, fontweight='bold',
                               color='white', bbox=dict(boxstyle='round,pad=0.2', 
                               facecolor=color, alpha=0.8))
        
        # Add suitability summary
        summary_text = f'{motor_key}: '
        if test_points:
            total = suitable_count + peak_only_count + unsuitable_count
            summary_text += f'✓ {suitable_count}/{total} Suitable'
            if peak_only_count > 0:
                summary_text += f', ⚠ {peak_only_count} Peak Only'
            if unsuitable_count > 0:
                summary_text += f', ✗ {unsuitable_count} Unsuitable'
        else:
            summary_text += 'Plot test points to analyze'
        
        ax.set_title(summary_text, fontsize=11, fontweight='bold')
        ax.set_xlabel('Speed (rpm)', fontsize=10, fontweight='bold')
        ax.set_ylabel('Torque (N.m)', fontsize=10, fontweight='bold')
        ax.set_xlim(0, max_rpm)
        ax.set_ylim(0, peak_torque * 1.2)
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        self.motor_suitability_canvas.fig.tight_layout()
        self.motor_suitability_canvas.draw()
    
    def update_motor_suitability_plot(self):
        """Update motor suitability plot when motor selection changes"""
        # Get current test points if available
        test_points = getattr(self, 'current_test_points', None)
        self.plot_motor_suitability(test_points)
    
    def calculate_motor_efficiency(self, rpm, torque, params=None):
        """
        Calculate motor efficiency based on RPM, Torque and vehicle parameters.
        This model accounts for vehicle-specific factors like GVW, resistance, and gradient.
        """
        import numpy as np
        import math
        
        # Use default params if not provided
        if params is None:
            params = {
                'gvw': EV_DEFAULTS['gvw'],
                'cd': EV_DEFAULTS['cd'],
                'cr': EV_DEFAULTS['cr'],
                'air_density': EV_DEFAULTS['air_density'],
                'frontal_area': EV_DEFAULTS['frontal_area'],
                'gear_ratio': EV_DEFAULTS['gear_ratio'],
                'wheel_radius': EV_DEFAULTS['wheel_radius'],
                'gradient': 0.0
            }
        
        # Motor efficiency model parameters (tuned to match reference image)
        # Peak efficiency occurs around 2000-4000 RPM and 50-150 Nm
        rpm_peak = 2500
        torque_peak = 80
        
        # Efficiency calculation using Gaussian-like distribution
        rpm_factor = np.exp(-((rpm - rpm_peak) ** 2) / (2 * 3000 ** 2))
        torque_factor = np.exp(-((torque - torque_peak) ** 2) / (2 * 60 ** 2))
        
        # Base efficiency with combined factors
        base_efficiency = 0.96 * rpm_factor * torque_factor
        
        # Add penalty for very low RPM and torque (motor losses)
        low_rpm_penalty = np.exp(-(rpm / 500) ** 2) * 0.3
        low_torque_penalty = np.exp(-(torque / 20) ** 2) * 0.2
        
        # Add penalty for very high RPM (windage losses)
        high_rpm_penalty = np.exp(-((10000 - rpm) / 2000) ** 2) * 0.15 if rpm > 7000 else 0
        
        # Add penalty for very high torque at high RPM (thermal limits)
        high_load_penalty = 0
        if rpm > 5000 and torque > 100:
            high_load_penalty = 0.3 * (rpm / 10000) * (torque / 200)
        
        # Vehicle-specific adjustments
        # Heavy vehicles require more torque, affecting efficiency at low torque
        gvw_factor = params['gvw'] / EV_DEFAULTS['gvw']
        if gvw_factor > 1.5:
            base_efficiency *= (1 - 0.02 * (gvw_factor - 1.5))
        
        # Gradient affects required torque
        gradient_rad = math.radians(params['gradient'])
        gradient_penalty = abs(math.sin(gradient_rad)) * 0.05
        
        # Aerodynamic drag penalty at high speed
        drag_factor = params['cd'] * params['frontal_area'] * params['air_density']
        drag_penalty = 0.02 * (drag_factor / (EV_DEFAULTS['cd'] * EV_DEFAULTS['frontal_area'] * EV_DEFAULTS['air_density']) - 1) if drag_factor > 0 else 0
        drag_penalty = max(0, drag_penalty)
        
        # Calculate final efficiency
        efficiency = max(0.0, base_efficiency - low_rpm_penalty - low_torque_penalty - 
                        high_rpm_penalty - high_load_penalty - gradient_penalty - drag_penalty)
        
        # Scale to realistic efficiency range (0 to ~0.96)
        efficiency = efficiency * 0.96 + 0.04 * (1 - low_rpm_penalty - low_torque_penalty)
        efficiency = np.clip(efficiency, 0, 0.96)
        
        return efficiency
    
    def calculate_vehicle_forces(self, params, speed_kmh=0):
        """Calculate vehicle forces based on parameters"""
        import math
        
        # Convert speed to m/s
        speed_ms = speed_kmh / 3.6
        
        # Rolling resistance force: Froll = Cr * m * g
        f_roll = params['cr'] * params['gvw'] * 9.81
        
        # Aerodynamic drag force: Fdrag = 0.5 * Cd * ρ * A * v²
        f_drag = 0.5 * params['cd'] * params['air_density'] * params['frontal_area'] * speed_ms ** 2
        
        # Grade resistance force: Fgrade = m * g * sin(θ)
        gradient_rad = math.radians(params['gradient'])
        f_grade = params['gvw'] * 9.81 * math.sin(gradient_rad)
        
        # Total resistance force
        f_load = f_roll + f_drag + f_grade
        
        return {
            'f_roll': f_roll,
            'f_drag': f_drag,
            'f_grade': f_grade,
            'f_load': f_load
        }
    
    def plot_efficiency_map(self, test_points=None):
        """Plot the motor efficiency contour map with optional test points and hover tooltips"""
        import numpy as np
        
        self.efficiency_canvas.fig.clear()
        ax = self.efficiency_canvas.fig.add_subplot(111)
        
        # Store test points data for hover functionality
        self.current_test_points = test_points
        
        # Create grid for contour plot
        rpm_range = np.linspace(0, 10000, 150)
        torque_range = np.linspace(0, 200, 150)
        RPM, TORQUE = np.meshgrid(rpm_range, torque_range)
        
        # Calculate efficiency for each point (using default params for base map)
        EFFICIENCY = np.zeros_like(RPM)
        for i in range(RPM.shape[0]):
            for j in range(RPM.shape[1]):
                EFFICIENCY[i, j] = self.calculate_motor_efficiency(RPM[i, j], TORQUE[i, j])
        
        # Create contour plot with color map similar to reference
        levels = np.linspace(0, 0.96, 12)
        contour = ax.contourf(RPM, TORQUE, EFFICIENCY, levels=levels, cmap='jet', extend='both')
        
        # Add contour lines
        contour_lines = ax.contour(RPM, TORQUE, EFFICIENCY, levels=levels, colors='black', linewidths=0.5, alpha=0.7)
        ax.clabel(contour_lines, inline=True, fontsize=7, fmt='%.2f')
        
        # Add colorbar
        cbar = self.efficiency_canvas.fig.colorbar(contour, ax=ax, label='Machine Efficiency', pad=0.02)
        cbar.set_ticks(np.linspace(0, 0.96, 11))
        cbar.set_ticklabels([f'{v:.2f}' for v in np.linspace(0, 0.96, 11)])
        
        # Store scatter points for hover detection
        self.scatter_points = None
        self.hover_annotation = None
        
        # Plot test points if provided
        if test_points:
            valid_points = [(p['rpm'], p['torque'], p['efficiency'], p['point_num']) 
                           for p in test_points if p['rpm'] > 0 or p['torque'] > 0]
            
            if valid_points:
                rpm_values = [p[0] for p in valid_points]
                torque_values = [p[1] for p in valid_points]
                efficiencies = [p[2] for p in valid_points]
                point_nums = [p[3] for p in valid_points]
                
                # Plot test points with markers
                self.scatter_points = ax.scatter(rpm_values, torque_values, c='black', s=120, marker='x', 
                          linewidths=2.5, zorder=10, label='Test Points')
                
                # Store point data for hover
                self.scatter_data = list(zip(rpm_values, torque_values, efficiencies, point_nums))
                
                # Add point labels
                for rpm, torque, eff, point_num in valid_points:
                    ax.annotate(f'P{point_num}', (rpm, torque), textcoords="offset points", 
                               xytext=(5, 5), fontsize=8, fontweight='bold',
                               color='white', bbox=dict(boxstyle='round,pad=0.2', 
                               facecolor='black', alpha=0.8))
                
                ax.legend(loc='upper right', fontsize=9)
                
                # Create annotation for hover (initially hidden)
                self.hover_annotation = ax.annotate("", xy=(0, 0), xytext=(20, 20),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.5", fc="#FFFFE0", ec="black", alpha=0.95),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
                    fontsize=10, fontweight='bold', zorder=20)
                self.hover_annotation.set_visible(False)
                
                # Connect hover event
                self.efficiency_canvas.mpl_connect("motion_notify_event", self.on_efficiency_hover)
        
        # Labels and title
        ax.set_xlabel('Speed (rpm)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Mechanical Torque (N.m)', fontsize=11, fontweight='bold')
        ax.set_title('Efficiency in Torque-Speed Area', fontsize=12, fontweight='bold')
        
        # Set axis limits
        ax.set_xlim(0, 10000)
        ax.set_ylim(0, 200)
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        self.efficiency_canvas.fig.tight_layout()
        self.efficiency_canvas.draw()
    
    def on_efficiency_hover(self, event):
        """Handle hover events on the efficiency map to show tooltips"""
        if event.inaxes is None or self.scatter_points is None or not hasattr(self, 'scatter_data'):
            return
        
        # Check if we're near any scatter point
        if self.hover_annotation is None:
            return
            
        visible = False
        for rpm, torque, eff, point_num in self.scatter_data:
            # Calculate distance from mouse to point (in data coordinates)
            # Need to account for different axis scales
            x_scale = 10000  # RPM range
            y_scale = 200    # Torque range
            
            dx = (event.xdata - rpm) / x_scale
            dy = (event.ydata - torque) / y_scale
            distance = (dx**2 + dy**2)**0.5
            
            # If within threshold, show annotation
            if distance < 0.03:  # ~3% of the plot size
                self.hover_annotation.xy = (rpm, torque)
                text = f"Point {point_num}\n─────────\nRPM: {rpm:,.0f}\nTorque: {torque:.1f} N.m\n★ Efficiency: {eff*100:.2f}%"
                self.hover_annotation.set_text(text)
                self.hover_annotation.set_visible(True)
                visible = True
                break
        
        if not visible:
            self.hover_annotation.set_visible(False)
        
        self.efficiency_canvas.draw_idle()
    
    def plot_efficiency_test_points(self):
        """Collect test point data with all parameters and plot on efficiency map"""
        import numpy as np
        
        test_points = []
        results_text = "═" * 80 + "\n"
        results_text += "                    TEST POINT EFFICIENCY ANALYSIS RESULTS\n"
        results_text += "═" * 80 + "\n\n"
        
        valid_points = 0
        for i in range(10):
            inputs = self.test_point_inputs[i]
            
            rpm = inputs['rpm'].value()
            torque = inputs['torque'].value()
            
            if rpm > 0 or torque > 0:
                # Get all parameters for this test point
                params = {
                    'gvw': inputs['gvw'].value(),
                    'cd': inputs['cd'].value(),
                    'cr': inputs['cr'].value(),
                    'air_density': inputs['air_density'].value(),
                    'frontal_area': inputs['frontal_area'].value(),
                    'gear_ratio': inputs['gear_ratio'].value(),
                    'wheel_radius': inputs['wheel_radius'].value(),
                    'gradient': inputs['gradient'].value()
                }
                
                # Calculate efficiency with vehicle parameters
                efficiency = self.calculate_motor_efficiency(rpm, torque, params)
                
                # Calculate vehicle forces
                forces = self.calculate_vehicle_forces(params)
                
                # Calculate vehicle speed from RPM
                speed_kmh = (rpm * 2 * 3.14159 * params['wheel_radius'] * 60) / (params['gear_ratio'] * 1000)
                
                test_points.append({
                    'point_num': i + 1,
                    'rpm': rpm,
                    'torque': torque,
                    'efficiency': efficiency,
                    'params': params,
                    'forces': forces,
                    'speed_kmh': speed_kmh
                })
                valid_points += 1
        
        if valid_points == 0:
            QMessageBox.warning(self, 'No Test Points', 
                               'Please enter at least one test point (RPM > 0 or Torque > 0) to plot.')
            return
        
        # Create HTML formatted results for professional look
        html_results = '''
        <html><body style="margin:0; padding:0; font-family: Arial, sans-serif;">
        <div style="background-color: #1976D2; color: white; padding: 8px; 
                    text-align: center; font-size: 12px; font-weight: bold;">
            MOTOR EFFICIENCY TEST RESULTS
        </div>
        <table style="width:100%; border-collapse: collapse; font-size: 11px; border: 1px solid #ccc; table-layout: fixed;">
            <tr style="background-color: #E3F2FD;">
                <th style="padding:6px; border:1px solid #ccc;">Pt</th>
                <th style="padding:6px; border:1px solid #ccc;">RPM</th>
                <th style="padding:6px; border:1px solid #ccc;">Torque</th>
                <th style="padding:6px; border:1px solid #ccc;">Speed</th>
                <th style="padding:6px; border:1px solid #ccc;">Grade</th>
                <th style="padding:6px; border:1px solid #ccc;">Efficiency</th>
            </tr>
        '''
        
        for i, p in enumerate(test_points):
            eff_pct = p['efficiency'] * 100
            grade = p['params']['gradient']
            grade_str = f"{grade:+.1f}°" if grade != 0 else "0°"
            
            # Row background color
            row_bg = "#ffffff" if i % 2 == 0 else "#f8f9fa"
            
            # Efficiency color and style
            if eff_pct >= 80:
                eff_color = "#28a745"
                eff_bg = "#d4edda"
            elif eff_pct >= 50:
                eff_color = "#fd7e14"
                eff_bg = "#fff3cd"
            else:
                eff_color = "#dc3545"
                eff_bg = "#f8d7da"
            
            html_results += f'''
            <tr style="background-color: {row_bg};">
                <td style="padding:6px; border:1px solid #ddd; text-align:center; font-weight:bold;">{p['point_num']}</td>
                <td style="padding:6px; border:1px solid #ddd; text-align:right;">{p['rpm']:.0f}</td>
                <td style="padding:6px; border:1px solid #ddd; text-align:right;">{p['torque']:.1f}</td>
                <td style="padding:6px; border:1px solid #ddd; text-align:right;">{p['speed_kmh']:.1f}</td>
                <td style="padding:6px; border:1px solid #ddd; text-align:center;">{grade_str}</td>
                <td style="padding:6px; border:1px solid #ddd; text-align:center; background:{eff_bg}; color:{eff_color}; font-weight:bold;">{eff_pct:.1f}%</td>
            </tr>
            '''
        
        html_results += '</table>'
        
        # Calculate statistics
        efficiencies = [p['efficiency'] for p in test_points]
        avg_efficiency = np.mean(efficiencies)
        
        # Find best and worst points
        best_point = max(test_points, key=lambda x: x['efficiency'])
        worst_point = min(test_points, key=lambda x: x['efficiency'])
        
        html_results += f'''
        <div style="margin-top:10px; padding:10px; background:#f5f5f5; border-radius:5px; border:1px solid #ddd;">
            <div style="font-weight:bold; font-size:12px; margin-bottom:8px; color:#1976D2;">📊 SUMMARY</div>
            <table style="width:100%; font-size:11px;">
                <tr>
                    <td style="padding:3px;">Total Points:</td>
                    <td style="padding:3px; font-weight:bold;">{valid_points}</td>
                </tr>
                <tr>
                    <td style="padding:3px;">Average:</td>
                    <td style="padding:3px; font-weight:bold;">{avg_efficiency*100:.1f}%</td>
                </tr>
                <tr>
                    <td style="padding:3px; color:#28a745;">✓ Best:</td>
                    <td style="padding:3px; color:#28a745; font-weight:bold;">P{best_point['point_num']} ({best_point['efficiency']*100:.1f}%)</td>
                </tr>
                <tr>
                    <td style="padding:3px; color:#dc3545;">✗ Worst:</td>
                    <td style="padding:3px; color:#dc3545; font-weight:bold;">P{worst_point['point_num']} ({worst_point['efficiency']*100:.1f}%)</td>
                </tr>
            </table>
        </div>
        </body></html>
        '''
        
        # Update results text with HTML
        self.testing_point_text.setHtml(html_results)
        
        # Store test points for motor selection changes
        self.current_test_points = test_points
        
        # Plot the efficiency map with test points
        self.plot_efficiency_map(test_points=test_points)
        
        # Plot the motor suitability graph with test points
        self.plot_motor_suitability(test_points=test_points)
        
        self.statusBar().showMessage(f'Plotted {valid_points} test points | Avg Efficiency: {avg_efficiency*100:.1f}%')
    
    def reset_test_points_to_defaults(self):
        """Reset all test point parameters to their original default values and clear graphs"""
        for i in range(10):
            inputs = self.test_point_inputs[i]
            defaults = self.test_point_defaults[i]
            inputs['rpm'].setValue(defaults['rpm'])
            inputs['torque'].setValue(defaults['torque'])
            inputs['gvw'].setValue(defaults['gvw'])
            inputs['cd'].setValue(defaults['cd'])
            inputs['cr'].setValue(defaults['cr'])
            inputs['air_density'].setValue(defaults['air_density'])
            inputs['frontal_area'].setValue(defaults['frontal_area'])
            inputs['gear_ratio'].setValue(defaults['gear_ratio'])
            inputs['wheel_radius'].setValue(defaults['wheel_radius'])
            inputs['gradient'].setValue(defaults['gradient'])
        
        # Clear test points data
        self.current_test_points = None
        
        # Clear results text
        self.testing_point_text.clear()
        
        # Reset graphs to initial state (no test points)
        self.plot_efficiency_map()
        self.plot_motor_suitability()
        
        self.statusBar().showMessage('All test points reset to original defaults')
    
    def clear_test_points(self):
        """Clear all test point inputs and reset the graphs"""
        for i in range(10):
            inputs = self.test_point_inputs[i]
            inputs['rpm'].setValue(0)
            inputs['torque'].setValue(0)
            inputs['gvw'].setValue(EV_DEFAULTS['gvw'])
            inputs['cd'].setValue(EV_DEFAULTS['cd'])
            inputs['cr'].setValue(EV_DEFAULTS['cr'])
            inputs['air_density'].setValue(EV_DEFAULTS['air_density'])
            inputs['frontal_area'].setValue(EV_DEFAULTS['frontal_area'])
            inputs['gear_ratio'].setValue(EV_DEFAULTS['gear_ratio'])
            inputs['wheel_radius'].setValue(EV_DEFAULTS['wheel_radius'])
            inputs['gradient'].setValue(0.0)
        
        # Clear test points data
        self.current_test_points = None
        
        # Clear results text
        self.testing_point_text.clear()
        
        # Reset graphs to initial state (no test points)
        self.plot_efficiency_map()
        self.plot_motor_suitability()
        
        self.statusBar().showMessage('All test points cleared')
    
    def compute_output_values(self):
        """Process current inputs and show output values for selected vehicle type"""
        import math
        
        # Read inputs
        vehicle_type = self.vehicle_type_combo.currentText()
        
        # Get EV or UGV parameters based on vehicle type
        if vehicle_type == 'EV':
            # Physical parameters
            wheel_radius = self.ev_wheel_radius_input.value()
            cd = self.ev_cd_input.value()
            cr = self.ev_cr_input.value()
            frontal_area = self.ev_frontal_area_input.value()
            air_density = self.ev_air_density_input.value()
            
            # Drivetrain parameters
            gear_ratio = self.ev_gear_ratio_input.value()
            gear_efficiency = self.ev_gear_efficiency_input.value() / 100.0
            motor_efficiency = self.ev_motor_efficiency_input.value() / 100.0
            motor_base_rpm = self.ev_motor_base_rpm_input.value()
            
            # Weight parameters (ALL components) 
            passenger_weight = self.ev_passenger_weight_input.value()
            motor_controller_weight = self.ev_motor_controller_weight_input.value()
            battery_weight_input = self.ev_battery_weight_input.value()
            vehicle_weight_input = self.ev_vehicle_weight_input.value()
            other_weights = self.ev_other_weights_input.value()
            generator_weight = self.ev_generator_weight_input.value()
            kerb_weight = battery_weight_input + vehicle_weight_input
            gvw_input = kerb_weight + passenger_weight

            # Battery parameters (ALL)
            battery_requirements = self.ev_battery_req_input.currentText()
            battery_chemistry = self.ev_battery_chem_input.currentText()
            battery_voltage = self.ev_battery_voltage_input.value()
            weight_per_wh = self.ev_weight_per_wh_input.value()
            peukert_coeff = self.ev_peukert_input.value()
            discharge_hr = self.ev_discharge_hr_input.value()
            dod_pct = self.ev_dod_input.value()
            battery_current = self.ev_battery_current_input.value()
            true_capacity_wh = self.ev_true_capacity_wh_input.value()
            true_capacity_ah = self.ev_true_capacity_ah_input.value()
            tentative_ah = self.ev_tentative_ah_input.value()
            tentative_wh = self.ev_tentative_wh_input.value()
            battery_weight_total = self.ev_battery_weight_total_input.value()
            
            # Performance parameters
            max_speed = self.ev_max_speed_input.value()
            slope_speed = self.ev_slope_speed_input.value()
            gradeability = self.ev_gradeability_input.value()
            accel_end_speed = self.ev_accel_end_speed_input.value()
            accel_period = self.ev_accel_period_input.value()
            rotary_inertia = self.ev_rotary_inertia_input.value()
            vehicle_range = self.ev_vehicle_range_input.value()
            
            # Calculate total vehicle mass from components
            calculated_vehicle_mass = gvw_input
            
            # Calculate GVW (Gross Vehicle Weight)
            calculated_gvw = calculated_vehicle_mass
            
            # Use calculated mass if vehicle_weight_input is default/zero
            if vehicle_weight_input > 0:
                vehicle_mass = vehicle_weight_input
            else:
                vehicle_mass = calculated_vehicle_mass
            
            # Battery calculations with chemistry
            # Energy density by chemistry (Wh/kg)
            energy_density_map = {
                'NCM': 250,  # Nickel Cobalt Manganese
                'NCA': 260,  # Nickel Cobalt Aluminum
                'LFP': 160,  # Lithium Iron Phosphate
                'LTO': 80    # Lithium Titanate Oxide
            }
            energy_density = energy_density_map.get(battery_chemistry, 200)
            
            # Placeholder for battery calculations - will be calculated after power analysis
            calculated_battery_current = 0
            calculated_true_capacity_wh = 0
            calculated_true_capacity_ah = 0
            calculated_tentative_ah = 0
            calculated_tentative_wh = 0
            calculated_battery_weight = 0
            available_capacity_wh = 0
            available_capacity_ah = 0
            
            # Store all calculated values for display
            ev_weight_breakdown = {
                'kerb_weight': kerb_weight,
                'passenger_weight': passenger_weight,
                'motor_controller_weight': motor_controller_weight,
                'battery_weight_total': battery_weight_total,
                'other_weights': other_weights,
                'generator_weight': generator_weight,
                'calculated_total': calculated_vehicle_mass,
                'calculated_gvw': calculated_gvw,
                'input_vehicle_weight': vehicle_weight_input
            }
            
            # ev_battery_analysis will be created after battery calculations
            
            vehicle_mass = calculated_vehicle_mass if vehicle_weight_input <= 0 else vehicle_weight_input
        else:  # UGV
            wheel_radius = self.ugv_wheel_radius_input.value()
            gear_ratio = self.ugv_gear_ratio_input.value()
            gear_efficiency = self.ugv_gear_efficiency_input.value() / 100.0
            motor_efficiency = self.ugv_motor_efficiency_input.value() / 100.0
            motor_base_rpm = self.ugv_motor_base_rpm_input.value()
            vehicle_weight_input = self.ugv_vehicle_weight_input.value()
            cd = self.ugv_cd_input.value()
            cr = self.ugv_cr_input.value()
            frontal_area = self.ugv_frontal_area_input.value()
            air_density = self.ugv_air_density_input.value()
            max_speed = self.ugv_max_speed_input.value()
            slope_speed = self.ugv_slope_speed_input.value()
            gradeability = self.ugv_gradeability_input.value()
            accel_end_speed = self.ugv_accel_end_speed_input.value()
            accel_period = self.ugv_accel_period_input.value()
            rotary_inertia = self.ugv_rotary_inertia_input.value()
            
            # For UGV, use GVW field (same as EV)
            gvw_input = self.ugv_gvw_input.value()
            calculated_gvw = gvw_input
            vehicle_mass = vehicle_weight_input
        
        # Convert speeds to m/s
        max_speed_ms = max_speed / 3.6
        slope_speed_ms = slope_speed / 3.6
        accel_end_speed_ms = accel_end_speed / 3.6
        
        # Vehicle Speed for Motor Base Speed RPM
        vehicle_speed_motor_base = (motor_base_rpm * 2 * math.pi * wheel_radius) / (60 * gear_ratio)
        
        # --- FORCE CALCULATIONS ---
        # Drag force at max speed (F = 0.5 * Cd * ρ * A * v²)
        F_drag_max = 0.5 * cd * air_density * frontal_area * max_speed_ms * max_speed_ms
        
        # Drag force at slope speed (F = 0.5 * Cd * ρ * A * v²)
        F_drag_slope = 0.5 * cd * air_density * frontal_area * slope_speed_ms * slope_speed_ms
        
        # Rolling resistance (zero gradient)
        F_roll = cr * gvw_input * 9.81
        
        # Climbing force (gradeability in degrees)
        F_climb = gvw_input * 9.81 * math.sin(gradeability * 0.01745329)
        
        # Convert acceleration end speed to m/s
        Vehicle_End_Acc_Speed = accel_end_speed * 0.277777777777777
        
        # --- VEHICLE ACCELERATION POWER ---
        # Term1: ((GVW * rotary_inertia) / (2 * accel_period)) * ((Vehicle_End_Acc_Speed^2) + (vehicle_speed_motor_base^2))
        term1 = ((calculated_gvw * rotary_inertia) / (2 * accel_period)) * ((Vehicle_End_Acc_Speed ** 2) + (vehicle_speed_motor_base ** 2))
        
        # Term2: (Cd * rho * A * Vehicle_End_Acc_Speed^3) / 5
        term2 = (cd * air_density * frontal_area * Vehicle_End_Acc_Speed * Vehicle_End_Acc_Speed * Vehicle_End_Acc_Speed) / 5
        
        # Term3: (2 * Cr * GVW * g * Vehicle_End_Acc_Speed) / 3
        term3 = (2 * cr * calculated_gvw * 9.81 * Vehicle_End_Acc_Speed) / 3
        
        # Required Power for Acceleration
        req_power_accel = (term1 + term2 + term3) / (gear_efficiency * motor_efficiency)
        
        # --- MOTOR INPUT POWER (accounting for efficiencies) ---
        # Zero Gradient Max Speed Power
        motor_input_max = ((F_drag_max + F_roll) * (max_speed * 0.2777778)) / (gear_efficiency * motor_efficiency)
        
        # Max Slope - Max Slope Speed Power
        motor_input_slope = ((F_drag_slope + F_roll + F_climb) * (slope_speed * 0.2777778)) / (gear_efficiency * motor_efficiency)
        
        # Acceleration Power
        motor_input_accel = req_power_accel
        
        # --- TOTAL REQUIRED MOTOR OUTPUT POWER ---
        motor_output_max = ((F_drag_max + F_roll) * (max_speed * 0.2777778)) / gear_efficiency
        motor_output_slope = ((F_drag_slope + F_roll + F_climb) * (slope_speed * 0.2777778)) / gear_efficiency
        motor_output_accel = (term1 + term2 + term3) / gear_efficiency
        
        # --- TOTAL TORQUE AND RPM AT MOTOR OUTPUT ---
        # RPM at max speed
        rpm_motor_max = (max_speed * gear_ratio) / (2 * math.pi * wheel_radius * 0.001 * 60)
        torque_motor_max = (motor_output_max * 60) / (2 * math.pi * rpm_motor_max)
        
        # RPM at slope speed
        rpm_motor_slope = (slope_speed * gear_ratio) / (2 * math.pi * wheel_radius * 0.001 * 60)
        torque_motor_slope = (motor_output_slope * 60) / (2 * math.pi * rpm_motor_slope)
        
        # RPM at acceleration (use motor base RPM)
        rpm_motor_accel = (accel_end_speed * gear_ratio) / (2 * math.pi * wheel_radius * 0.001 * 60)
        torque_motor_accel = (motor_output_accel * 60) / (2 * math.pi * rpm_motor_accel)
        
        # --- TOTAL REQUIRED POWER OUTPUT AT WHEELS ---
        wheel_power_max = motor_output_max * gear_efficiency
        wheel_power_slope = motor_output_slope * gear_efficiency
        wheel_power_accel = motor_output_accel * gear_efficiency
        
        # --- TOTAL TORQUE AND RPM AT WHEELS ---
        # RPM at wheels (max speed)
        rpm_wheel_max = (max_speed_ms* 60) / (2 * math.pi * wheel_radius)
        torque_wheel_max = (wheel_power_max * 60) / (2 * math.pi * rpm_wheel_max) if rpm_wheel_max > 0 else 0
        
        # RPM at wheels (slope speed)
        rpm_wheel_slope = (slope_speed_ms * 60) / (2 * math.pi * wheel_radius)
        torque_wheel_slope = (wheel_power_slope * 60) / (2 * math.pi * rpm_wheel_slope) if rpm_wheel_slope > 0 else 0
        
        # RPM at wheels (acceleration - using motor base RPM)
        rpm_wheel_accel = (accel_end_speed_ms * 60) / (2 * math.pi * wheel_radius)
        torque_wheel_accel = (wheel_power_accel * 60) / (2 * math.pi * rpm_wheel_accel) 
        
        # --- BATTERY CALCULATIONS USING FORMULAS (EV ONLY) ---
        if vehicle_type == 'EV':
            # Get battery voltage and vehicle range
            battery_voltage = self.ev_battery_voltage_input.value()
            vehicle_range_km = self.ev_vehicle_range_input.value()
            
            # Battery parameters from inputs
            battery_chemistry = self.ev_battery_chem_input.currentText()
            battery_requirements = self.ev_battery_req_input.currentText()
            weight_per_wh = self.ev_weight_per_wh_input.value()
            peukert_coeff = self.ev_peukert_input.value()
            discharge_hr = self.ev_discharge_hr_input.value()
            dod_pct = self.ev_dod_input.value()

            
            # Formula 1: Constant Speed Battery Current (A) = (Zero Gradient Max Speed Power (W)) / Battery Voltage
            calculated_battery_current = motor_input_max / battery_voltage 
            
            # Formula 2: True usable Battery Capacity Wh = (Vehicle Range * Zero Gradient Max Speed Power) / (ContSpeed * (DoD% / 100))
            calculated_true_capacity_wh = (vehicle_range_km * motor_input_max) / (max_speed * (dod_pct / 100.0))
            
            # Formula 3: True usable Battery Ah = True Capacity Wh / Battery voltage
            calculated_true_capacity_ah = calculated_true_capacity_wh / battery_voltage 
            
            # Formula 4: Tentative battery Ah for given Discharge Hr (with Peukert correction)
            # Tentative_Ah = (True_Ah * ((Battery_Current * discharge_hr)^(peukert_coeff - 1)))^(1/peukert_coeff)
            calculated_tentative_ah = (calculated_true_capacity_ah * ((calculated_battery_current * discharge_hr) ** (peukert_coeff - 1))) ** (1/peukert_coeff)
            
            # Formula 5: Tentative battery Capacity Wh = Battery_voltage * Tentative_Ah
            calculated_tentative_wh = battery_voltage * calculated_tentative_ah
            
            # Formula 6: Battery Weight = Tentative_Wh * weight_per_wh
            calculated_battery_weight = calculated_tentative_wh * weight_per_wh
            
            # Store battery analysis results
            ev_battery_analysis = {
                'requirements': battery_requirements,
                'chemistry': battery_chemistry,
                'battery_voltage': battery_voltage,
                'weight_per_wh': weight_per_wh,
                'peukert_coeff': peukert_coeff,
                'discharge_hr': discharge_hr,
                'dod_pct': dod_pct,
                'battery_current': calculated_battery_current,
                'nominal_capacity_wh': calculated_true_capacity_wh,
                'nominal_capacity_ah': calculated_true_capacity_ah,
                'peukert_adjusted_ah': calculated_tentative_ah,
                'peukert_adjusted_wh': calculated_tentative_wh,
                'calculated_battery_weight': calculated_battery_weight
            }
            
            # --- BATTERY CAPACITY WITH DRIVE PATTERN ---
            # Define drive pattern slabs (speed, drive%, gradient, distance%)
            slabs = [
                {'name': 'Slab-1 Max Speed', 'speed': max_speed, 'drive_pct': 35, 'gradient': 0.0},
                {'name': 'Slab-2 Speed', 'speed': max_speed * 0.7, 'drive_pct': 40, 'gradient': 0.0},  # 35 km/h
                {'name': 'Slab-3 Speed', 'speed': max_speed * 0.5, 'drive_pct': 20, 'gradient': 0.0},  # 25 km/h
                {'name': 'Slab-4 Speed', 'speed': slope_speed, 'drive_pct': 5, 'gradient': gradeability},
            ]
            
            # Use vehicle_range_km (already defined above) for slab calculations
            vehicle_range_total = vehicle_range_km
            
            slab_data = []
            total_usable_ah = 0
            
            for slab in slabs:
                speed_kmh = slab['speed']
                speed_ms = speed_kmh / 3.6
                gradient_deg = slab['gradient']
                drive_pct = slab['drive_pct']
                distance_km = (vehicle_range_total * drive_pct)/100
                
                # Calculate forces
                F_drag_slab = cd * air_density * frontal_area * speed_kmh * speed_kmh * 0.03858025308642
                F_roll_slab = cr * calculated_gvw * 9.81
                F_climb_slab =  calculated_gvw * 9.81 * math.sin(gradient_deg*0.01745329)
                
                # Power calculations
                power_wheel_slab = (F_drag_slab + F_roll_slab + F_climb_slab)
                motor_output_slab = power_wheel_slab * (speed_kmh * 0.2777778) / gear_efficiency
                motor_input_slab = power_wheel_slab * (speed_kmh * 0.2777778) / (gear_efficiency * motor_efficiency)
                
                # Battery current
                battery_current_slab = motor_input_slab / battery_voltage 
        
                # Energy and capacity
                usable_energy_wh = (motor_input_slab * distance_km) / (speed_kmh * (dod_pct/100))
                true_usable_ah = usable_energy_wh / battery_voltage
                final_ah = (true_usable_ah * ((battery_current_slab * discharge_hr) ** (peukert_coeff - 1))) ** (1/peukert_coeff)
                
                total_usable_ah += true_usable_ah
                
                slab_data.append({
                    'name': slab['name'],
                    'speed': speed_kmh,
                    'drive_pct': drive_pct,
                    'gradient': gradient_deg,
                    'distance': distance_km,
                    'F_climb': F_climb_slab,
                    'F_drag': F_drag_slab,
                    'F_roll': F_roll_slab,
                    'motor_input': motor_input_slab,
                    'motor_output': motor_output_slab,
                    'battery_current': battery_current_slab,
                    'usable_energy': usable_energy_wh,
                    'true_usable_ah': true_usable_ah,
                    'final_ah': final_ah
                })
            
            final_battery_capacity_ah = sum(slab['final_ah'] for slab in slab_data)
        
        # Build HTML output - Only for EV
        if vehicle_type == 'EV':
            html = f"""
            <style>
                table.data {{ width:100%; border-collapse:collapse; margin:5px 0; border:1px solid #999; }}
                table.data th, table.data td {{ padding:8px; text-align:left; border:1px solid #999; font-family:Segoe UI; font-size:15px; }}
                table.data th {{ background-color:#f2f2f2; font-weight:bold; }}
                table.data td.value {{ text-align:right; }}
                table.layout {{ width:100%; border:none; border-collapse:collapse; }}
                table.layout td {{ vertical-align:top; padding:10px; border:none; }}
                table.layout td:first-child {{ border-right: 2px solid #ddd; padding-right:15px; }}
                table.layout td:last-child {{ padding-left:15px; }}
                h3 {{ margin:4px 0; font-family:Segoe UI; font-size:16px; font-weight:bold; }}
                h4 {{ margin:8px 0 4px 0; font-family:Segoe UI; font-size:15px; color:#2c3e50; font-weight:bold; }}
                .category {{ background-color: #dc3545; color: white; padding: 8px; margin: 15px 0 5px 0; font-weight: bold; font-size: 15px; border-radius: 4px; }}
            </style>
            
            <h3>EV Computed Output Values</h3>
            
            <div class='category'>Motor Performance</div>
            <table class='layout'>
                <tr>
                    <td width='50%'>
                        <h4>Motor Input Power</h4>
                        <table class='data'>
                            <tr><th>Scenario</th><th class='value'>Power (W)</th></tr>
                            <tr><td>Zero Gradient Max Speed Power</td><td class='value'>{motor_input_max:.0f}</td></tr>
                            <tr><td>Max Slope- Max Slope Speed Power</td><td class='value'>{motor_input_slope:.0f}</td></tr>
                            <tr><td>Acceleration Power</td><td class='value'>{motor_input_accel:.0f}</td></tr>
                        </table>
                    </td>
                    <td width='50%'>
                        <h4>Total Required Motor Output Power</h4>
                        <table class='data'>
                            <tr><th>Scenario</th><th class='value'>Power (W)</th></tr>
                            <tr><td>Zero Gradient Max Speed Power</td><td class='value'>{motor_output_max:.0f}</td></tr>
                            <tr><td>Max Slope- Max Slope Speed Power</td><td class='value'>{motor_output_slope:.0f}</td></tr>
                            <tr><td>Acceleration Power</td><td class='value'>{motor_output_accel:.0f}</td></tr>
                        </table>
                    </td>
                </tr>
            </table>
            
            <h4>Total Torque and RPM at Motor Output</h4>
            <table class='data'>
                <tr><th>Scenario</th><th class='value'>RPM</th><th class='value'>Torque (Nm)</th></tr>
                <tr><td>Zero Gradient Max Speed</td><td class='value'>{rpm_motor_max:.0f}</td><td class='value'>{torque_motor_max:.2f}</td></tr>
                <tr><td>Acceleration</td><td class='value'>{rpm_motor_accel:.0f}</td><td class='value'>{torque_motor_accel:.0f}</td></tr>
                <tr><td>Max Slope- Max Slope Speed</td><td class='value'>{rpm_motor_slope:.0f}</td><td class='value'>{torque_motor_slope:.0f}</td></tr>
            </table>
            
            <div class='category'>Wheel Performance</div>
            <table class='layout'>
                <tr>
                    <td width='50%'>
                        <h4>Total Required Power Output at Wheels</h4>
                        <table class='data'>
                            <tr><th>Scenario</th><th class='value'>Power (W)</th></tr>
                            <tr><td>Zero Gradient Max Speed Power</td><td class='value'>{wheel_power_max:.0f}</td></tr>
                            <tr><td>Acceleration Power</td><td class='value'>{wheel_power_accel:.0f}</td></tr>
                            <tr><td>Max Slope- Max Slope Speed Power</td><td class='value'>{wheel_power_slope:.0f}</td></tr>
                        </table>
                    </td>
                    <td width='50%'>
                        <h4>Total Torque and RPM at Wheels</h4>
                        <table class='data'>
                            <tr><th>Scenario</th><th class='value'>RPM</th><th class='value'>Torque (Nm)</th></tr>
                            <tr><td>Zero Gradient Max Speed Torque</td><td class='value'>{rpm_wheel_max:.0f}</td><td class='value'>{torque_wheel_max:.0f}</td></tr>
                            <tr><td>Acceleration Torque</td><td class='value'>{rpm_wheel_accel:.0f}</td><td class='value'>{torque_wheel_accel:.0f}</td></tr>
                            <tr><td>Max Slope- Max Slope Speed Torque</td><td class='value'>{rpm_wheel_slope:.0f}</td><td class='value'>{torque_wheel_slope:.0f}</td></tr>
                        </table>
                    </td>
                </tr>
            </table>
            
            <div class='category'>Weight Analysis</div>
            <table class='layout'>
                <tr>
                    <td width='50%'>
                        <h4>Weight Components</h4>
                        <table class='data'>
                            <tr><th>Component</th><th class='value'>Weight (kg)</th></tr>
                            <tr><td>Kerb Weight</td><td class='value'>{ev_weight_breakdown['kerb_weight']:.1f}</td></tr>
                            <tr><td>Passenger/Load Weight</td><td class='value'>{ev_weight_breakdown['passenger_weight']:.1f}</td></tr>
                            <tr><td>Motor & Controller Weight</td><td class='value'>{ev_weight_breakdown['motor_controller_weight']:.1f}</td></tr>
                            <tr><td>Battery Weight</td><td class='value'>{ev_weight_breakdown['battery_weight_total']:.1f}</td></tr>
                            <tr><td>Other Weights</td><td class='value'>{ev_weight_breakdown['other_weights']:.1f}</td></tr>
                            <tr><td>Generator Weight</td><td class='value'>{ev_weight_breakdown['generator_weight']:.1f}</td></tr>
                            <tr style='background-color:#e8f4f8; font-weight:bold;'>
                                <td>Calculated Total Vehicle Weight</td>
                                <td class='value'>{ev_weight_breakdown['calculated_total']:.1f}</td>
                            </tr>
                            <tr style='background-color:#ffeaa7; font-weight:bold;'>
                                <td>Input Vehicle Weight (used in calc)</td>
                                <td class='value'>{ev_weight_breakdown['input_vehicle_weight']:.1f}</td>
                            </tr>
                            <tr style='background-color:#d3f8e2; font-weight:bold;'>
                                <td>Calculated GVW</td>
                                <td class='value'>{ev_weight_breakdown['calculated_gvw']:.1f}</td>
                            </tr>
                        </table>
                    </td>
                    <td width='50%'>
                        <h4>Battery Analysis</h4>
                        <table class='data'>
                            <tr><th>Parameter</th><th class='value'>Value</th></tr>
                            <tr><td>Battery Requirements</td><td class='value'>{ev_battery_analysis['requirements']}</td></tr>
                            <tr><td>Battery Chemistry</td><td class='value'>{ev_battery_analysis['chemistry']}</td></tr>
                            <tr><td>Battery voltage</td><td class='value'>{ev_battery_analysis['battery_voltage']:.0f}</td></tr>
                            <tr><td>Weight per unit Wh</td><td class='value'>{ev_battery_analysis['weight_per_wh']}</td></tr>
                            <tr><td>Peukert's Coefficient</td><td class='value'>{ev_battery_analysis['peukert_coeff']}</td></tr>
                            <tr><td>Battery Discharge hour rating (Hr)</td><td class='value'>{ev_battery_analysis['discharge_hr']:.0f}</td></tr>
                            <tr><td>DepthOfDischarge%</td><td class='value'>{ev_battery_analysis['dod_pct']:.0f}</td></tr>
                            <tr><td>Constant Speed Battery Current (A)</td><td class='value'>{ev_battery_analysis['battery_current']:.0f}</td></tr>
                            <tr><td>True usable Battery Capacity Wh</td><td class='value'>{ev_battery_analysis['nominal_capacity_wh']:.0f}</td></tr>
                            <tr><td>True usable Battery Ah</td><td class='value'>{ev_battery_analysis['nominal_capacity_ah']:.0f}</td></tr>
                            <tr><td>Tentative  battery Ah for given Discharge Hr</td><td class='value'>{ev_battery_analysis['peukert_adjusted_ah']:.0f}</td></tr>
                            <tr><td>Tentative battery Capacity Wh</td><td class='value'>{ev_battery_analysis['peukert_adjusted_wh']:.0f}</td></tr>
                            <tr><td>Battery Weight</td><td class='value'>{ev_battery_analysis['calculated_battery_weight']:.0f}</td></tr>
                        </table>
                    </td>
                </tr>
            </table>
            
            <div class='category'>Force Calculations & Acceleration Analysis</div>
            <table class='layout'>
                <tr>
                    <td width='50%'>
                        <h4>Force Calculations</h4>
                        <table class='data'>
                            <tr><th>Force Type</th><th class='value'>Value (N)</th></tr>
                            <tr><td>F<sub>drag-const</sub></td><td class='value'>{F_drag_max:.2f}</td></tr>
                            <tr><td>F<sub>drag-slope</sub></td><td class='value'>{F_drag_slope:.2f}</td></tr>
                            <tr><td>F<sub>roll</sub></td><td class='value'>{F_roll:.2f}</td></tr>
                            <tr><td>F<sub>climb</sub></td><td class='value'>{F_climb:.2f}</td></tr>
                        </table>
                    </td>
                    <td width='50%'>
                        <h4>Vehicle Acceleration Power</h4>
                        <table class='data'>
                            <tr><th>Parameter</th><th class='value'>Value</th></tr>
                            <tr><td>Vehicle Speed for Motor Base Speed RPM (m/s)</td><td class='value'>{vehicle_speed_motor_base:.3f}</td></tr>
                            <tr><td>Vehicle End of Acc Speed (m/s)</td><td class='value'>{Vehicle_End_Acc_Speed:.3f}</td></tr>
                            <tr><td>Term1</td><td class='value'>{term1:.0f}</td></tr>
                            <tr><td>Term2</td><td class='value'>{term2:.0f}</td></tr>
                            <tr><td>Term3</td><td class='value'>{term3:.0f}</td></tr>
                            <tr><td><b>Required Power for Acceleration</b></td><td class='value'><b>{req_power_accel:.0f}</b></td></tr>
                        </table>
                    </td>
                </tr>
            </table>
            
            <div class='category'>Battery Capacity Analysis</div>
            <h4>Battery Capacity with Respect to Drive Pattern</h4>
            <table class='data'>
                <tr>
                    <th>Speed Slab</th>
                    <th class='value'>Speed (km/h)</th>
                    <th class='value'>Drive %</th>
                    <th class='value'>Gradient (°)</th>
                    <th class='value'>Distance (km)</th>
                    <th class='value'>F<sub>climb</sub> (N)</th>
                    <th class='value'>F<sub>drag</sub> (N)</th>
                    <th class='value'>F<sub>roll</sub> (N)</th>
                    <th class='value'>Motor Input (W)</th>
                    <th class='value'>Motor Output (W)</th>
                    <th class='value'>Battery Current (A)</th>
                    <th class='value'>Useable Energy (Wh)</th>
                    <th class='value'>True Usable Ah</th>
                    <th class='value'>Final Ah</th>
                </tr>
                {''.join([f'''<tr>
                    <td>{s["name"]}</td>
                    <td class='value'>{s["speed"]:.0f}</td>
                    <td class='value'>{s["drive_pct"]}%</td>
                    <td class='value'>{s["gradient"]:.1f}</td>
                    <td class='value'>{s["distance"]:.2f}</td>
                    <td class='value'>{s["F_climb"]:.0f}</td>
                    <td class='value'>{s["F_drag"]:.0f}</td>
                    <td class='value'>{s["F_roll"]:.0f}</td>
                    <td class='value'>{s["motor_input"]:.0f}</td>
                    <td class='value'>{s["motor_output"]:.0f}</td>
                    <td class='value'>{s["battery_current"]:.0f}</td>
                    <td class='value'>{s["usable_energy"]:.0f}</td>
                    <td class='value'>{s["true_usable_ah"]:.0f}</td>
                    <td class='value'>{s["final_ah"]:.0f}</td>
                </tr>''' for s in slab_data])}
                <tr style='background-color:#e8f4f8; font-weight:bold;'>
                    <td colspan='12'>Final Battery Capacity</td>
                    <td class='value' colspan='2'>{final_battery_capacity_ah:.0f} Ah</td>
                </tr>
                <tr style='background-color:#e8f4f8; font-weight:bold;'>
                    <td colspan='12'>Vehicle Range</td>
                    <td class='value' colspan='2'>{vehicle_range_total:.0f} km</td>
                </tr>
            </table>
            """
            self.output_text.setHtml(html)
            self.statusBar().showMessage('EV Output values computed successfully')
        else:
            # UGV - Comprehensive output calculations
            # Get UGV-specific parameters
            num_wheels = self.ugv_num_wheels_input.value()
            num_powered_wheels = self.ugv_num_powered_wheels_input.value()
            track_width = self.ugv_track_width_input.value()
            skid_coefficient = self.ugv_skid_coefficient_input.value()
            spin_angular_rad = self.ugv_spin_angular_rad_input.value()
            spin_angular_deg = self.ugv_spin_angular_deg_input.value()
            
            # --- PER MOTOR OUTPUT POWER ---
            per_motor_output_max = ((F_drag_max + F_roll) * (max_speed * 0.2777778))/(gear_efficiency * num_powered_wheels)
            per_motor_output_slope = ((F_drag_slope + F_roll + F_climb) * (slope_speed * 0.2777778))/(gear_efficiency * num_powered_wheels)
            per_motor_output_accel = (term1 + term2 + term3)/gear_efficiency
            
            # --- PER MOTOR TORQUE AND RPM ---
            per_motor_torque_max = (per_motor_output_max * 60)/(2 * math.pi * rpm_motor_max)
            per_motor_torque_accel = (per_motor_output_accel * 60)/(2 * math.pi * rpm_motor_accel)
            per_motor_torque_slope = (per_motor_output_slope * 60)/(2 * math.pi * rpm_motor_slope)
            
            # --- POWER OUTPUT PER WHEELS (Powered wheels only) ---
            per_wheel_power_max = per_motor_output_max * gear_efficiency
            per_wheel_power_accel = per_motor_output_accel * gear_efficiency
            per_wheel_power_slope = per_motor_output_slope * gear_efficiency
            # --- TORQUE AND RPM PER WHEEL (Powered wheels only) ---
            per_wheel_torque_max = (per_wheel_power_max * 60)/(2 * math.pi * rpm_wheel_max)
            per_wheel_torque_accel = (per_wheel_power_accel * 60)/(2 * math.pi * rpm_wheel_accel)
            per_wheel_torque_slope = (per_wheel_power_slope * 60)/(2 * math.pi * rpm_wheel_slope)
            
            # --- SKID PARAMETERS AND POWER ESTIMATION ---
            # Total Skid Friction Force
            total_skid_friction = calculated_gvw * 9.81 * skid_coefficient
            
            # Per wheel Skid Friction Force
            per_wheel_skid_friction = total_skid_friction / num_powered_wheels 
            
            # Wheel linear speed during turning
            wheel_linear_speed_turn = spin_angular_rad * track_width / 2
            
            # Power for each motor during turn
            power_per_motor_turn = (skid_coefficient * calculated_gvw * 9.81 * spin_angular_rad * track_width)/4
            
            # Total power for all motors
            total_power_turn = (skid_coefficient * calculated_gvw * 9.81 * spin_angular_rad * track_width)/2
            
            # Wheel RPM during turn
            wheel_rpm_turn = spin_angular_rad * 9.549297
            
            # Vehicle rotational degree per second
            vehicle_rot_deg_per_sec = spin_angular_rad * 57.2958
            
            # Total Wheel Torque
            total_wheel_torque = total_skid_friction * wheel_radius
            
            # Total Motor Wheel Torque (accounting for gear efficiency)
            total_motor_wheel_torque = total_wheel_torque / gear_ratio 
            
            # Per Motor Wheel Torque
            per_motor_wheel_torque = total_motor_wheel_torque / num_powered_wheels 
            
            html = f"""
            <style>
                table.data {{ width:100%; border-collapse:collapse; margin:5px 0; border:1px solid #999; }}
                table.data th, table.data td {{ padding:8px; text-align:left; border:1px solid #999; font-family:Segoe UI; font-size:15px; }}
                table.data th {{ background-color:#f2f2f2; font-weight:bold; }}
                table.data td.value {{ text-align:right; }}
                table.layout {{ width:100%; border:none; border-collapse:collapse; }}
                table.layout td {{ vertical-align:top; padding:10px; border:none; }}
                table.layout td:first-child {{ border-right: 2px solid #ddd; padding-right:15px; }}
                table.layout td:last-child {{ padding-left:15px; }}
                h3 {{ margin:4px 0; font-family:Segoe UI; font-size:16px; font-weight:bold; }}
                h4 {{ margin:8px 0 4px 0; font-family:Segoe UI; font-size:15px; color:#2c3e50; font-weight:bold; }}
                .category {{ background-color: #dc3545; color: white; padding: 8px; margin: 15px 0 5px 0; font-weight: bold; font-size: 15px; border-radius: 4px; }}
            </style>
            
            <h3>UGV Computed Output Values</h3>
            
            <div class='category'>Force Calculations & Acceleration Analysis</div>
            <table class='layout'>
                <tr>
                    <td width='50%'>
                        <h4>Force Calculations</h4>
                        <table class='data'>
                            <tr><th>Force Type</th><th class='value'>Value (N)</th></tr>
                            <tr><td>F<sub>drag-const</sub></td><td class='value'>{F_drag_max:.2f}</td></tr>
                            <tr><td>F<sub>drag-slope</sub></td><td class='value'>{F_drag_slope:.2f}</td></tr>
                            <tr><td>F<sub>roll</sub></td><td class='value'>{F_roll:.2f}</td></tr>
                            <tr><td>F<sub>climb</sub></td><td class='value'>{F_climb:.2f}</td></tr>
                        </table>
                    </td>
                    <td width='50%'>
                        <h4>Vehicle Acceleration Power</h4>
                        <table class='data'>
                            <tr><th>Parameter</th><th class='value'>Value</th></tr>
                            <tr><td>Vehicle Speed for Motor Base Speed RPM (m/s)</td><td class='value'>{vehicle_speed_motor_base:.3f}</td></tr>
                            <tr><td>Vehicle End of Acc Speed (m/s)</td><td class='value'>{Vehicle_End_Acc_Speed:.3f}</td></tr>
                            <tr><td>Term1</td><td class='value'>{term1:.0f}</td></tr>
                            <tr><td>Term2</td><td class='value'>{term2:.0f}</td></tr>
                            <tr><td>Term3</td><td class='value'>{term3:.0f}</td></tr>
                            <tr><td><b>Required Power for Acceleration</b></td><td class='value'><b>{req_power_accel:.0f}</b></td></tr>
                        </table>
                    </td>
                </tr>
            </table>
            
            <div class='category'>Motor Performance</div>
            <table class='layout'>
                <tr>
                    <td width='50%'>
                        <h4>Per Motor Output Power</h4>
                        <table class='data'>
                            <tr><th>Scenario</th><th class='value'>Power (W)</th></tr>
                            <tr><td>Zero Gradient Max Speed Power</td><td class='value'>{per_motor_output_max:.0f}</td></tr>
                            <tr><td>Max Slope- Max Slope Speed Power</td><td class='value'>{per_motor_output_slope:.0f}</td></tr>
                            <tr><td>Acceleration Power</td><td class='value'>{per_motor_output_accel:.0f}</td></tr>
                        </table>
                    </td>
                    <td width='50%'>
                        <h4>Per Motor Torque and RPM</h4>
                        <table class='data'>
                            <tr><th>Scenario</th><th class='value'>RPM</th><th class='value'>Torque (Nm)</th></tr>
                            <tr><td>Zero Gradient Max Speed</td><td class='value'>{rpm_motor_max:.0f}</td><td class='value'>{per_motor_torque_max:.2f}</td></tr>
                            <tr><td>Acceleration</td><td class='value'>{rpm_motor_accel:.0f}</td><td class='value'>{per_motor_torque_accel:.2f}</td></tr>
                            <tr><td>Max Slope- Max Slope Speed</td><td class='value'>{rpm_motor_slope:.0f}</td><td class='value'>{per_motor_torque_slope:.2f}</td></tr>
                        </table>
                    </td>
                </tr>
            </table>
            
            <div class='category'>Wheel Performance</div>
            <table class='layout'>
                <tr>
                    <td width='50%'>
                        <h4>Power Output Per Wheels</h4>
                        <table class='data'>
                            <tr><th>Scenario</th><th class='value'>Power (W)</th></tr>
                            <tr><td>Zero Gradient Max Speed Power</td><td class='value'>{per_wheel_power_max:.0f}</td></tr>
                            <tr><td>Acceleration Power</td><td class='value'>{per_wheel_power_accel:.0f}</td></tr>
                            <tr><td>Max Slope- Max Slope Speed Power</td><td class='value'>{per_wheel_power_slope:.0f}</td></tr>
                        </table>
                    </td>
                    <td width='50%'>
                        <h4>Torque and RPM Per Wheel</h4>
                        <table class='data'>
                            <tr><th>Scenario</th><th class='value'>RPM</th><th class='value'>Torque (Nm)</th></tr>
                            <tr><td>Zero Gradient Max Speed Torque</td><td class='value'>{rpm_wheel_max:.0f}</td><td class='value'>{per_wheel_torque_max:.0f}</td></tr>
                            <tr><td>Acceleration Torque</td><td class='value'>{rpm_wheel_accel:.0f}</td><td class='value'>{per_wheel_torque_accel:.0f}</td></tr>
                            <tr><td>Max Slope- Max Slope Speed Torque</td><td class='value'>{rpm_wheel_slope:.0f}</td><td class='value'>{per_wheel_torque_slope:.0f}</td></tr>
                        </table>
                    </td>
                </tr>
            </table>
            
            <div class='category'>Skid Parameters & Power Estimation</div>
            <h4>Skid Parameters and Power Estimation</h4>
            <table class='data'>
                <tr><th>Parameter</th><th class='value'>Value</th><th class='value'>Unit</th></tr>
                <tr><td>Total Skid Friction Force (F<sub>skid</sub>)</td><td class='value'>{total_skid_friction:.0f}</td><td class='value'>N</td></tr>
                <tr><td>Per Wheel Skid Friction Force (F<sub>side</sub>)</td><td class='value'>{per_wheel_skid_friction:.0f}</td><td class='value'>N</td></tr>
                <tr><td>Wheel Linear Speed During Turning (v<sub>wheel</sub>)</td><td class='value'>{wheel_linear_speed_turn:.2f}</td><td class='value'>m/s</td></tr>
                <tr><td>Power for Each Motor (P<sub>turn</sub>)</td><td class='value'>{power_per_motor_turn:.0f}</td><td class='value'>Watts</td></tr>
                <tr><td>Total Power for All Motors (P<sub>total</sub>)</td><td class='value'>{total_power_turn:.0f}</td><td class='value'>Watts</td></tr>
                <tr><td>Wheel RPM</td><td class='value'>{wheel_rpm_turn:.0f}</td><td class='value'>rpm</td></tr>
                <tr><td>Vehicle Rotational Degree per Second</td><td class='value'>{vehicle_rot_deg_per_sec:.0f}</td><td class='value'>degree/sec</td></tr>
                <tr><td>Total Wheel Torque</td><td class='value'>{total_wheel_torque:.0f}</td><td class='value'>Nm</td></tr>
                <tr><td>Total Motor Wheel Torque</td><td class='value'>{total_motor_wheel_torque:.2f}</td><td class='value'>Nm</td></tr>
                <tr><td>Per Motor Wheel Torque</td><td class='value'>{per_motor_wheel_torque:.2f}</td><td class='value'>Nm</td></tr>
            </table>
            """
            self.output_text.setHtml(html)
            self.statusBar().showMessage('UGV Output values computed successfully')
    
    def generate_graph_simulation_data(self):
        """
        ⚠️ LOCKED CODE - VERIFIED ACCURATE ⚠️
        Generate time-series graph simulation data using initial input parameters
        
        This method uses ITERATIVE EULER INTEGRATION for physics-accurate results.
        DO NOT MODIFY the integration logic without verification.
        
        Key Implementation Details:
        - Uses pre-calculated initial values for t=0
        - Each subsequent step (t>0) uses values from PREVIOUS step
        - Integration: v_new = v_old + a_old × dt
        - Forces recalculated at each step based on current speed
        - Produces accurate, physics-based results matching reference data
        
        Last Verified: November 7, 2025 at 12:38 PM IST
        Status: ✅ ACCURATE - Matches reference calculations
        """
        import math
        import numpy as np
        
        # Get simulation parameters
        duration = self.simulation_duration_input.value()  # User customizable duration
        gradient_deg = self.gradient_input.value()
        mode = self.mode_combo.currentText()
        
        # Get initial parameters from input fields
        init_time = self.init_time.value()
        init_speed_ms = self.init_vehicle_speed_ms.value()
        init_speed_kmph = self.init_vehicle_speed_kmph.value()
        init_motor_rpm = self.init_motor_speed_rpm.value()
        init_num_power_wheels = self.init_num_power_wheels.value()
        init_total_torque = self.init_total_motor_torque.value()
        init_per_motor_torque = self.init_per_motor_torque.value()
        init_per_motor_power = self.init_per_motor_power.value()
        init_tractive = self.init_tractive_force.value()
        init_froll = self.init_froll.value()
        init_fdrag = self.init_fdrag.value()
        init_fclimb = self.init_fclimb.value()
        init_fload = self.init_fload.value()
        init_fnet = self.init_fnet.value()
        init_accel = self.init_vehicle_accel.value()
        
        # Mode display (Eco-1, Boost-2)
        mode_value = 2 if mode == 'boost' else 1
        mode_display = f'Eco-{mode_value}' if mode == 'eco' else f'Boost-{mode_value}'
        
        # Get user-defined time step from input field
        dt = self.time_step_input.value()  # Time step in seconds (user customizable)
        
        # Generate time steps starting from init_time
        time_steps = np.arange(init_time, init_time + duration + dt, dt)
        
        # Prepare data storage
        data = []
        
        # Get constants needed for calculations
        gvw = EV_DEFAULTS['gvw']
        gear_efficiency = EV_DEFAULTS['gear_efficiency'] / 100.0
        gear_ratio = EV_DEFAULTS['gear_ratio']
        wheel_radius = EV_DEFAULTS['wheel_radius']
        cr = EV_DEFAULTS['cr']
        cd = EV_DEFAULTS['cd']
        air_density = EV_DEFAULTS['air_density']
        frontal_area = EV_DEFAULTS['frontal_area']
        
        # Get motor parameters from selection
        motor_key = self.motor_combo.currentText()
        if motor_key == 'Customize':
            peak_torque = self.custom_peak_torque.value()
            peak_power = self.custom_peak_power.value()
            continuous_torque = peak_torque / 2
            continuous_power = peak_power / 2
            base_rpm = 500
        else:
            motor = GPM_MOTORS.get(motor_key, GPM_MOTORS['Default'])
            peak_torque = motor['peak_torque_nm']
            peak_power = motor['peak_power_w']
            continuous_torque = motor['continuous_torque_nm']
            continuous_power = motor['continuous_power_w']
            base_rpm = motor['base_rpm']
        
        # Select torque/power based on mode
        if mode == 'boost':
            torque_per_motor = peak_torque
            power_per_motor = peak_power
        else:
            torque_per_motor = continuous_torque
            power_per_motor = continuous_power
        
        # ⚠️ LOCKED: Initialize state variables with initial values
        # These values are used for the first row (t=0) and updated iteratively
        current_speed_ms = init_speed_ms
        current_speed_kmh = init_speed_kmph
        motor_speed_rpm = init_motor_rpm
        total_motor_torque = init_total_torque
        per_motor_torque = init_per_motor_torque
        per_motor_power = init_per_motor_power
        F_tractive = init_tractive
        F_roll = init_froll
        F_drag = init_fdrag
        F_climb = init_fclimb
        F_load = init_fload
        F_net = init_fnet
        acceleration = init_accel
        
        # ⚠️ LOCKED: Iterative integration loop - DO NOT CHANGE
        for i, t in enumerate(time_steps):
            # For t=0, we already have initial values set above
            # For t>0, calculate new values based on previous state
            if i > 0:
                # ⚠️ CRITICAL: Euler integration step
                # Update speed using previous acceleration: v_new = v_old + a * dt
                current_speed_ms = current_speed_ms + (acceleration * dt)
                current_speed_ms = max(0, current_speed_ms)  # Prevent negative
                current_speed_kmh = current_speed_ms * 3.6
                
                # Calculate Motor Speed (RPM) from current vehicle speed
                motor_speed_rpm = (current_speed_kmh * gear_ratio) / (2 * 3.14159 * wheel_radius * 0.001 * 60)
                
                # Calculate Total Motor Torque based on selected motor and RPM
                # Constant torque below base RPM, constant power above
                if motor_speed_rpm < base_rpm:
                    torque = torque_per_motor  # Constant torque region
                else:
                    # Constant power region: T = (P × 60) / (2π × RPM)
                    torque = (power_per_motor * 60) / (2 * 3.14159 * motor_speed_rpm)
                
                total_motor_torque = torque * init_num_power_wheels
                
                # Per motor calculations
                per_motor_torque = total_motor_torque / init_num_power_wheels
                per_motor_power = (2 * 3.14159 * motor_speed_rpm * per_motor_torque) / 60
                
                # Tractive force
                F_tractive = (total_motor_torque * gear_efficiency * gear_ratio) / wheel_radius
                
                # Resistance forces
                F_roll = cr * gvw * 9.81
                F_drag = cd * air_density * frontal_area * current_speed_kmh * current_speed_kmh * 0.03858025308642
                F_climb = gvw * 9.81 * math.sin(gradient_deg * 0.01745329)
                
                # Total load and net force
                F_load = F_roll + F_drag + F_climb
                F_net = F_tractive - F_load
                
                # Acceleration for NEXT step
                acceleration = F_net / gvw
            
            # Store data
            data.append({
                'Time': round(t, 1),
                'Vehicle Speed (m/s)': round(current_speed_ms, 3),
                'Vehicle Speed (Kmph)': round(current_speed_kmh, 2),
                'Motor Speed (RPM)': round(motor_speed_rpm, 1),
                'Gradient (Degree)': gradient_deg,
                'Mode': mode_display,
                'Total Motor Torque (Nm)': round(total_motor_torque, 2),
                'Total Number of Power Wheels': init_num_power_wheels,
                'PerMotor Torque (Nm)': round(per_motor_torque, 2),
                'PerMotor Power (Watts)': round(per_motor_power, 1),
                'Motoring Tractive Force F_Tractive (N)': round(F_tractive, 2),
                'Froll (N)': round(F_roll, 2),
                'Fdrag (N)': round(F_drag, 2),
                'Fclimb (N)': round(F_climb, 2),
                'F_Load Resistance (N)': round(F_load, 2),
                'Net Force F_Net (N)': round(F_net, 2),
                'Vehicle Acceleration (m/s)': round(acceleration, 3)
            })
        
        # Store data for export
        self.graph_simulation_data = data
        
        # Populate table
        self.populate_graph_table(data)
        
        # Plot in Speed, Power, Forces, and Motor tabs
        self.plot_graph_simulation_speed(data)
        self.plot_graph_simulation_power(data)
        self.plot_graph_simulation_forces(data)
        self.plot_graph_simulation_motor(data)
        
        self.statusBar().showMessage(f'Generated {len(data)} data points - All graph tabs updated with table data')
    
    def populate_graph_table(self, data):
        """Populate the graph data table with calculated values"""
        if not data:
            return
        
        # Set up table
        headers = list(data[0].keys())
        self.graph_data_table.setColumnCount(len(headers))
        self.graph_data_table.setRowCount(len(data))
        self.graph_data_table.setHorizontalHeaderLabels(headers)
        
        # Populate data
        for row_idx, row_data in enumerate(data):
            for col_idx, header in enumerate(headers):
                value = row_data[header]
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.graph_data_table.setItem(row_idx, col_idx, item)
        
        # Resize columns to content
        self.graph_data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    
    def plot_graph_simulation_speed(self, data):
        """
        Plot graph simulation speed data in the Speed tab.
        This uses data from the Data Table (generate_graph_simulation_data).
        """
        if not data:
            return
        
        # Extract time and speed data from table
        time = [row['Time'] for row in data]
        speed_kmh = [row['Vehicle Speed (Kmph)'] for row in data]
        
        print(f"DEBUG: Plotting {len(data)} data points from table")
        print(f"DEBUG: Time range: {time[0]} to {time[-1]} seconds")
        print(f"DEBUG: Speed range: {speed_kmh[0]} to {max(speed_kmh)} km/h")
        
        # Clear and plot on speed canvas
        self.speed_canvas.fig.clear()
        ax = self.speed_canvas.fig.add_subplot(111)
        
        # Plot with orange line matching reference
        ax.plot(time, speed_kmh, color='orange', linewidth=2.5, label='Vehicle Speed (Kmph)')
        
        # Set custom X-axis ticks based on user input
        import numpy as np
        xtick_interval = int(self.graph_xtick_interval.value())
        max_time = max(time)
        xticks = np.arange(0, max_time + xtick_interval, xtick_interval)
        ax.set_xticks(xticks)
        
        # Formatting to match reference
        ax.set_xlabel('Time (Sec)', fontsize=10, fontweight='bold')
        ax.set_ylabel('Vehicle Speed (Kmph)', fontsize=10)
        ax.set_title('Vehicle Speed (Kmph)', fontsize=12, fontweight='bold')
        ax.legend(loc='lower right', fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Adjust and draw
        self.speed_canvas.fig.tight_layout()
        self.speed_canvas.draw()
    
    def plot_graph_simulation_power(self, data):
        """
        Plot graph simulation power data in the Power tab.
        This uses data from the Data Table (generate_graph_simulation_data).
        """
        if not data:
            return
        
        # Extract time and power data from table
        time = [row['Time'] for row in data]
        power_watts = [row['PerMotor Power (Watts)'] for row in data]
        
        # Clear and plot on power canvas
        self.power_canvas.fig.clear()
        ax = self.power_canvas.fig.add_subplot(111)
        
        # Plot with orange line matching reference
        ax.plot(time, power_watts, color='orange', linewidth=2.5, label='PerMotor Power (Watts)')
        
        # Set custom X-axis ticks based on user input
        import numpy as np
        xtick_interval = int(self.graph_xtick_interval.value())
        max_time = max(time)
        xticks = np.arange(0, max_time + xtick_interval, xtick_interval)
        ax.set_xticks(xticks)
        
        # Formatting to match reference
        ax.set_xlabel('Time (Sec)', fontsize=10, fontweight='bold')
        ax.set_ylabel('PerMotor Power (Watts)', fontsize=10)
        ax.set_title('Power', fontsize=12, fontweight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Adjust and draw
        self.power_canvas.fig.tight_layout()
        self.power_canvas.draw()
    
    def plot_graph_simulation_forces(self, data):
        """
        Plot graph simulation forces data in the Forces tab.
        This uses data from the Data Table (generate_graph_simulation_data).
        """
        if not data:
            return
        
        # Extract time and force data from table
        time = [row['Time'] for row in data]
        f_tractive = [row['Motoring Tractive Force F_Tractive (N)'] for row in data]
        f_roll = [row['Froll (N)'] for row in data]
        f_drag = [row['Fdrag (N)'] for row in data]
        f_load = [row['F_Load Resistance (N)'] for row in data]
        
        # Clear and plot on forces canvas
        self.forces_canvas.fig.clear()
        ax = self.forces_canvas.fig.add_subplot(111)
        
        # Plot with matching colors from reference
        ax.plot(time, f_tractive, color='orange', linewidth=2.5, label='Motoring Tractive Force F_Tractive (N)')
        ax.plot(time, f_roll, color='blue', linewidth=2.5, label='Froll (N)')
        ax.plot(time, f_drag, color='yellow', linewidth=2.5, label='Fdrag (N)')
        ax.plot(time, f_load, color='gray', linewidth=2.5, label='F_Load Resistance (N)')
        
        # Set custom X-axis ticks based on user input
        import numpy as np
        xtick_interval = int(self.graph_xtick_interval.value())
        max_time = max(time)
        xticks = np.arange(0, max_time + xtick_interval, xtick_interval)
        ax.set_xticks(xticks)
        
        # Formatting to match reference
        ax.set_xlabel('Time (Sec)', fontsize=10, fontweight='bold')
        ax.set_ylabel('Force (N)', fontsize=10)
        ax.set_title('Forces', fontsize=12, fontweight='bold')
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Adjust and draw
        self.forces_canvas.fig.tight_layout()
        self.forces_canvas.draw()
    
    def plot_graph_simulation_motor(self, data):
        """
        Plot graph simulation motor data in the Motor tab.
        This uses data from the Data Table (generate_graph_simulation_data).
        Shows two subplots: Motor Speed (RPM) and Total Motor Torque (Nm).
        """
        if not data:
            return
        
        # Extract time and motor data from table
        time = [row['Time'] for row in data]
        motor_rpm = [row['Motor Speed (RPM)'] for row in data]
        motor_torque = [row['Total Motor Torque (Nm)'] for row in data]
        
        # Clear and plot on motor canvas
        self.motor_canvas.fig.clear()
        
        # Get X-axis tick settings
        import numpy as np
        xtick_interval = int(self.graph_xtick_interval.value())
        max_time = max(time)
        xticks = np.arange(0, max_time + xtick_interval, xtick_interval)
        
        # Top subplot - Motor Speed (RPM)
        ax1 = self.motor_canvas.fig.add_subplot(211)
        ax1.plot(time, motor_rpm, color='blue', linewidth=2.5, label='Motor Speed (RPM)')
        ax1.set_xticks(xticks)
        ax1.set_ylabel('Motor Speed (RPM)', fontsize=10)
        ax1.set_title('Motor Speed (RPM)', fontsize=12, fontweight='bold')
        ax1.legend(loc='lower right', fontsize=8)
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        # Bottom subplot - Total Motor Torque (Nm)
        ax2 = self.motor_canvas.fig.add_subplot(212)
        ax2.plot(time, motor_torque, color='blue', linewidth=2.5, label='Total Motor Torque (Nm)')
        ax2.set_xticks(xticks)
        ax2.set_xlabel('Time (Sec)', fontsize=10, fontweight='bold')
        ax2.set_ylabel('Total Motor Torque (Nm)', fontsize=10)
        ax2.set_title('Total Motor Torque (Nm)', fontsize=12, fontweight='bold')
        ax2.legend(loc='upper right', fontsize=8)
        ax2.grid(True, alpha=0.3, linestyle='--')
        
        # Adjust and draw
        self.motor_canvas.fig.tight_layout()
        self.motor_canvas.draw()
    
    def show_about(self):
        """Show about dialog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
        
        dialog = QDialog(self)
        dialog.setWindowTitle('About EV Simulation Tool')
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # About text
        about_text = """
        <h2 style='text-align:center;'>EV Power Train Simulation Tool</h2>
        <p style='text-align:center;'><b>Version:</b> 1.0</p>
        <p style='text-align:center;'><b>Developed by:</b> ePropelled</p>
        <br>
        <p>A comprehensive tool for simulating electric vehicle power train performance.</p>
        <p><b>Features include:</b></p>
        <ul>
            <li>Real-time performance simulation</li>
            <li>Motor and battery analysis</li>
            <li>Energy efficiency calculations</li>
            <li>Multiple terrain scenarios</li>
            <li>Data export capabilities</li>
        </ul>
        """
        text_label = QLabel(about_text)
        text_label.setWordWrap(True)
        layout.addWidget(text_label)
        
        # Close button
        from PyQt6.QtWidgets import QPushButton
        close_btn = QPushButton('Close')
        close_btn.setStyleSheet('padding: 8px; background-color: #2196F3; color: white; border-radius: 4px;')
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def create_control_panel(self):
        """Create left control panel with scroll area"""
        # Main container
        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(5, 5, 5, 5)
        
        # Vehicle Selection - STICKY at top (outside scroll area)
        self.vehicle_group = QGroupBox('Vehicle Selection')
        vehicle_layout = QGridLayout()
        
        # Vehicle Type
        vehicle_layout.addWidget(QLabel('Vehicle Type:'), 0, 0)
        self.vehicle_type_combo = QComboBox()
        self.vehicle_type_combo.addItems(['EV', 'UGV'])
        self.vehicle_type_combo.currentTextChanged.connect(self.on_vehicle_type_changed)
        vehicle_layout.addWidget(self.vehicle_type_combo, 0, 1)
        
        self.vehicle_group.setLayout(vehicle_layout)
        panel_layout.addWidget(self.vehicle_group)
        
        # Scrollable area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Content widget inside scroll area
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Runtime Parameters - Separate group for simulation control
        self.runtime_params_group = QGroupBox('Runtime Parameters')
        runtime_layout = QGridLayout()
        
        # Time Step (s) - User customizable
        runtime_layout.addWidget(QLabel('Time Step (s):'), 0, 0)
        self.time_step_input = QDoubleSpinBox()
        self.time_step_input.setRange(0.01, 10.0)
        self.time_step_input.setValue(0.5)  # Default 0.5 seconds
        self.time_step_input.setDecimals(2)
        self.time_step_input.setSingleStep(0.1)
        self.time_step_input.setToolTip('Time step for simulation data (smaller = more data points, more accurate)')
        runtime_layout.addWidget(self.time_step_input, 0, 1)
        
        # Graph X-Axis Tick Interval (s) - User customizable
        runtime_layout.addWidget(QLabel('Graph X-Axis Interval (s):'), 1, 0)
        self.graph_xtick_interval = QDoubleSpinBox()
        self.graph_xtick_interval.setRange(1, 60)
        self.graph_xtick_interval.setValue(5)  # Default 5 seconds (0, 5, 10, 15...)
        self.graph_xtick_interval.setDecimals(0)
        self.graph_xtick_interval.setSingleStep(5)
        self.graph_xtick_interval.setToolTip('X-axis tick interval for graphs (e.g., 5 = 0, 5, 10, 15...)')
        runtime_layout.addWidget(self.graph_xtick_interval, 1, 1)
        
        # Simulation Duration (s) - User customizable
        runtime_layout.addWidget(QLabel('Simulation Duration (s):'), 2, 0)
        self.simulation_duration_input = QDoubleSpinBox()
        self.simulation_duration_input.setRange(10, 600)
        self.simulation_duration_input.setValue(120)  # Default 120 seconds (2 minutes)
        self.simulation_duration_input.setDecimals(0)
        self.simulation_duration_input.setSingleStep(10)
        self.simulation_duration_input.setToolTip('Total simulation duration in seconds (10-600)')
        runtime_layout.addWidget(self.simulation_duration_input, 2, 1)
        
        self.runtime_params_group.setLayout(runtime_layout)
        layout.addWidget(self.runtime_params_group)
        
        # Graph Simulation Initial Parameters
        self.graph_sim_params_group = QGroupBox('Graph Simulation Initial Parameters')
        graph_sim_layout = QGridLayout()
        
        # Gradient
        graph_sim_layout.addWidget(QLabel('Gradient (°):'), 0, 0)
        self.gradient_input = QDoubleSpinBox()
        self.gradient_input.setRange(-30, 60)
        self.gradient_input.setValue(GRAPH_SIM_DEFAULTS['gradient_deg'])
        self.gradient_input.valueChanged.connect(self.update_graph_sim_calculated_values)
        graph_sim_layout.addWidget(self.gradient_input, 0, 1)
        
        # Mode
        graph_sim_layout.addWidget(QLabel('Mode:'), 1, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['boost', 'eco'])
        self.mode_combo.currentTextChanged.connect(self.update_graph_sim_calculated_values)
        graph_sim_layout.addWidget(self.mode_combo, 1, 1)
        
        # Motor Model Selection
        graph_sim_layout.addWidget(QLabel('Motor Model:'), 2, 0)
        self.motor_combo = QComboBox()
        self.motor_combo.addItems(['Default', 'GPM35', 'GPM50', 'GPM70', 'Customize'])
        self.motor_combo.currentTextChanged.connect(self.on_motor_selection_changed)
        graph_sim_layout.addWidget(self.motor_combo, 2, 1)
        
        # Custom Motor Parameters (hidden by default, shown when "Customize" is selected)
        graph_sim_layout.addWidget(QLabel('Custom Peak Torque (Nm):'), 3, 0)
        self.custom_peak_torque = QDoubleSpinBox()
        self.custom_peak_torque.setRange(1, 500)
        self.custom_peak_torque.setValue(37)
        self.custom_peak_torque.setDecimals(1)
        self.custom_peak_torque.valueChanged.connect(self.update_graph_sim_calculated_values)
        graph_sim_layout.addWidget(self.custom_peak_torque, 3, 1)
        
        graph_sim_layout.addWidget(QLabel('Custom Peak Power (W):'), 4, 0)
        self.custom_peak_power = QDoubleSpinBox()
        self.custom_peak_power.setRange(100, 50000)
        self.custom_peak_power.setValue(2000)
        self.custom_peak_power.setDecimals(0)
        self.custom_peak_power.valueChanged.connect(self.update_graph_sim_calculated_values)
        graph_sim_layout.addWidget(self.custom_peak_power, 4, 1)
        
        # Store references for visibility toggle
        self.custom_torque_label = graph_sim_layout.itemAtPosition(3, 0).widget()
        self.custom_power_label = graph_sim_layout.itemAtPosition(4, 0).widget()
        
        # Hide custom fields by default
        self.custom_torque_label.setVisible(False)
        self.custom_peak_torque.setVisible(False)
        self.custom_power_label.setVisible(False)
        self.custom_peak_power.setVisible(False)
        
        # Time (s)
        graph_sim_layout.addWidget(QLabel('Time (s):'), 5, 0)
        self.init_time = QDoubleSpinBox()
        self.init_time.setRange(0, 1000)
        self.init_time.setValue(GRAPH_SIM_DEFAULTS['init_time'])
        self.init_time.setDecimals(1)
        self.init_time.setSingleStep(0.5)
        graph_sim_layout.addWidget(self.init_time, 5, 1)

        
        # Initial Vehicle Speed (m/s) - BASE VALUE (controls calculated fields)
        graph_sim_layout.addWidget(QLabel('Initial Vehicle Speed (m/s):'), 6, 0)
        self.init_vehicle_speed_ms = QDoubleSpinBox()
        self.init_vehicle_speed_ms.setRange(0, 100)
        self.init_vehicle_speed_ms.setValue(GRAPH_SIM_DEFAULTS['init_vehicle_speed_ms'])
        self.init_vehicle_speed_ms.setDecimals(3)
        self.init_vehicle_speed_ms.setSingleStep(0.1)
        self.init_vehicle_speed_ms.valueChanged.connect(self.update_graph_sim_calculated_values)
        graph_sim_layout.addWidget(self.init_vehicle_speed_ms, 6, 1)
        
        # Initial Motor Speed (RPM) - CALCULATED from vehicle speed and gear ratio
        graph_sim_layout.addWidget(QLabel('Initial Motor Speed (RPM):'), 7, 0)
        self.init_motor_speed_rpm = QDoubleSpinBox()
        self.init_motor_speed_rpm.setRange(0, 10000)
        self.init_motor_speed_rpm.setValue(GRAPH_SIM_DEFAULTS['init_motor_speed_rpm'])
        self.init_motor_speed_rpm.setDecimals(1)
        self.init_motor_speed_rpm.setSingleStep(10)
        self.init_motor_speed_rpm.setReadOnly(True)
        self.init_motor_speed_rpm.setStyleSheet("QDoubleSpinBox { background-color: #f0f0f0; }")
        graph_sim_layout.addWidget(self.init_motor_speed_rpm, 7, 1)
        
        # Total Number of Power Wheel Motors
        graph_sim_layout.addWidget(QLabel('Number of Power Wheels:'), 8, 0)
        self.init_num_power_wheels = QSpinBox()
        self.init_num_power_wheels.setRange(1, 8)
        self.init_num_power_wheels.setValue(GRAPH_SIM_DEFAULTS['init_num_power_wheels'])
        self.init_num_power_wheels.valueChanged.connect(self.update_graph_sim_calculated_values)
        graph_sim_layout.addWidget(self.init_num_power_wheels, 8, 1)
        
        # Initial Total Motor Torque (Nm) - CALCULATED from mode and motor RPM
        graph_sim_layout.addWidget(QLabel('Initial Total Motor Torque (Nm):'), 9, 0)
        self.init_total_motor_torque = QDoubleSpinBox()
        self.init_total_motor_torque.setRange(0, 10000)
        self.init_total_motor_torque.setValue(GRAPH_SIM_DEFAULTS['init_total_motor_torque'])
        self.init_total_motor_torque.setDecimals(2)
        self.init_total_motor_torque.setSingleStep(1)
        self.init_total_motor_torque.setReadOnly(True)
        self.init_total_motor_torque.setStyleSheet("QDoubleSpinBox { background-color: #f0f0f0; }")
        graph_sim_layout.addWidget(self.init_total_motor_torque, 9, 1)
        
        # Initial PerMotor Power (Watts) - CALCULATED from motor RPM and per-motor torque
        graph_sim_layout.addWidget(QLabel('Initial PerMotor Power (W):'), 10, 0)
        self.init_per_motor_power = QDoubleSpinBox()
        self.init_per_motor_power.setRange(0, 50000)
        self.init_per_motor_power.setValue(GRAPH_SIM_DEFAULTS['init_per_motor_power'])
        self.init_per_motor_power.setDecimals(1)
        self.init_per_motor_power.setSingleStep(100)
        self.init_per_motor_power.setReadOnly(True)
        self.init_per_motor_power.setStyleSheet("QDoubleSpinBox { background-color: #f0f0f0; }")
        graph_sim_layout.addWidget(self.init_per_motor_power, 10, 1)
        
        # Initial Tractive Force (N) - CALCULATED from total torque, gear efficiency, gear ratio, wheel radius
        graph_sim_layout.addWidget(QLabel('Initial Tractive Force (N):'), 11, 0)
        self.init_tractive_force = QDoubleSpinBox()
        self.init_tractive_force.setRange(0, 10000)
        self.init_tractive_force.setValue(GRAPH_SIM_DEFAULTS['init_tractive_force'])
        self.init_tractive_force.setDecimals(2)
        self.init_tractive_force.setSingleStep(10)
        self.init_tractive_force.setReadOnly(True)
        self.init_tractive_force.setStyleSheet("QDoubleSpinBox { background-color: #f0f0f0; }")
        graph_sim_layout.addWidget(self.init_tractive_force, 11, 1)
        
        # Initial Froll (N) - CALCULATED from rolling resistance (cr × mass × g)
        graph_sim_layout.addWidget(QLabel('Initial Froll (N):'), 12, 0)
        self.init_froll = QDoubleSpinBox()
        self.init_froll.setRange(0, 5000)
        self.init_froll.setValue(GRAPH_SIM_DEFAULTS['init_froll'])
        self.init_froll.setDecimals(2)
        self.init_froll.setSingleStep(1)
        self.init_froll.setReadOnly(True)
        self.init_froll.setStyleSheet("QDoubleSpinBox { background-color: #f0f0f0; }")
        graph_sim_layout.addWidget(self.init_froll, 12, 1)
        
        # Initial Fdrag (N) - CALCULATED from aerodynamic drag (cd × ρ × A × v²)
        graph_sim_layout.addWidget(QLabel('Initial Fdrag (N):'), 13, 0)
        self.init_fdrag = QDoubleSpinBox()
        self.init_fdrag.setRange(0, 5000)
        self.init_fdrag.setValue(GRAPH_SIM_DEFAULTS['init_fdrag'])
        self.init_fdrag.setDecimals(2)
        self.init_fdrag.setSingleStep(1)
        self.init_fdrag.setReadOnly(True)
        self.init_fdrag.setStyleSheet("QDoubleSpinBox { background-color: #f0f0f0; }")
        graph_sim_layout.addWidget(self.init_fdrag, 13, 1)
        
        # Initial Fclimb (N) - CALCULATED from climbing force (mass × g × sin(gradient))
        graph_sim_layout.addWidget(QLabel('Initial Fclimb (N):'), 14, 0)
        self.init_fclimb = QDoubleSpinBox()
        self.init_fclimb.setRange(0, 5000)
        self.init_fclimb.setValue(GRAPH_SIM_DEFAULTS['init_fclimb'])
        self.init_fclimb.setDecimals(2)
        self.init_fclimb.setSingleStep(1)
        self.init_fclimb.setReadOnly(True)
        self.init_fclimb.setStyleSheet("QDoubleSpinBox { background-color: #f0f0f0; }")
        graph_sim_layout.addWidget(self.init_fclimb, 14, 1)
        
        # Initial Vehicle Speed (Kmph) - CALCULATED from m/s
        graph_sim_layout.addWidget(QLabel('Initial Vehicle Speed (Kmph):'), 15, 0)
        self.init_vehicle_speed_kmph = QDoubleSpinBox()
        self.init_vehicle_speed_kmph.setRange(0, 300)
        self.init_vehicle_speed_kmph.setValue(GRAPH_SIM_DEFAULTS['init_vehicle_speed_kmph'])
        self.init_vehicle_speed_kmph.setDecimals(2)
        self.init_vehicle_speed_kmph.setSingleStep(1)
        self.init_vehicle_speed_kmph.setReadOnly(True)
        self.init_vehicle_speed_kmph.setStyleSheet("QDoubleSpinBox { background-color: #f0f0f0; }")
        graph_sim_layout.addWidget(self.init_vehicle_speed_kmph, 15, 1)
        
        # Initial PerMotor Torque (Nm) - CALCULATED from total torque and number of wheels
        graph_sim_layout.addWidget(QLabel('Initial PerMotor Torque (Nm):'), 16, 0)
        self.init_per_motor_torque = QDoubleSpinBox()
        self.init_per_motor_torque.setRange(0, 10000)
        self.init_per_motor_torque.setValue(GRAPH_SIM_DEFAULTS['init_per_motor_torque'])
        self.init_per_motor_torque.setDecimals(2)
        self.init_per_motor_torque.setSingleStep(1)
        self.init_per_motor_torque.setReadOnly(True)
        self.init_per_motor_torque.setStyleSheet("QDoubleSpinBox { background-color: #f0f0f0; }")
        graph_sim_layout.addWidget(self.init_per_motor_torque, 16, 1)
        
        # Initial F_Load Resistance (N) - CALCULATED from froll + fdrag + fclimb
        graph_sim_layout.addWidget(QLabel('Initial F_Load Resistance (N):'), 17, 0)
        self.init_fload = QDoubleSpinBox()
        self.init_fload.setRange(0, 10000)
        self.init_fload.setValue(GRAPH_SIM_DEFAULTS['init_fload'])
        self.init_fload.setDecimals(2)
        self.init_fload.setSingleStep(1)
        self.init_fload.setReadOnly(True)
        self.init_fload.setStyleSheet("QDoubleSpinBox { background-color: #f0f0f0; }")
        graph_sim_layout.addWidget(self.init_fload, 17, 1)
        
        # Initial Net Force F_Net (N) - CALCULATED from tractive force - load resistance
        graph_sim_layout.addWidget(QLabel('Initial Net Force F_Net (N):'), 18, 0)
        self.init_fnet = QDoubleSpinBox()
        self.init_fnet.setRange(-10000, 10000)
        self.init_fnet.setValue(GRAPH_SIM_DEFAULTS['init_fnet'])
        self.init_fnet.setDecimals(2)
        self.init_fnet.setSingleStep(1)
        self.init_fnet.setReadOnly(True)
        self.init_fnet.setStyleSheet("QDoubleSpinBox { background-color: #f0f0f0; }")
        graph_sim_layout.addWidget(self.init_fnet, 18, 1)
        
        # Initial Vehicle Acceleration (m/s²) - CALCULATED from net force / mass
        graph_sim_layout.addWidget(QLabel('Initial Acceleration (m/s²):'), 19, 0)
        self.init_vehicle_accel = QDoubleSpinBox()
        self.init_vehicle_accel.setRange(-10, 10)
        self.init_vehicle_accel.setValue(GRAPH_SIM_DEFAULTS['init_vehicle_accel'])
        self.init_vehicle_accel.setDecimals(3)
        self.init_vehicle_accel.setSingleStep(0.1)
        self.init_vehicle_accel.setReadOnly(True)
        self.init_vehicle_accel.setStyleSheet("QDoubleSpinBox { background-color: #f0f0f0; }")
        graph_sim_layout.addWidget(self.init_vehicle_accel, 19, 1)
        
        self.graph_sim_params_group.setLayout(graph_sim_layout)
        layout.addWidget(self.graph_sim_params_group)
        
        # EV-Specific Parameters - Organized into scrollable area
        self.ev_params_group = QGroupBox('EV Parameters')
        ev_main_layout = QVBoxLayout()
        
        # Physical Parameters
        ev_physical_group = QGroupBox('Physical Parameters')
        ev_physical_layout = QGridLayout()
        
        ev_physical_layout.addWidget(QLabel('Cd Drag Coefficient:'), 0, 0)
        self.ev_cd_input = QDoubleSpinBox()
        self.ev_cd_input.setRange(0.1, 2.0)
        self.ev_cd_input.setValue(EV_DEFAULTS['cd'])
        self.ev_cd_input.setDecimals(3)
        self.ev_cd_input.setSingleStep(0.01)
        ev_physical_layout.addWidget(self.ev_cd_input, 0, 1)
        
        ev_physical_layout.addWidget(QLabel('Cr Rolling Resistance:'), 1, 0)
        self.ev_cr_input = QDoubleSpinBox()
        self.ev_cr_input.setRange(0.001, 0.1)
        self.ev_cr_input.setValue(EV_DEFAULTS['cr'])
        self.ev_cr_input.setDecimals(4)
        self.ev_cr_input.setSingleStep(0.001)
        ev_physical_layout.addWidget(self.ev_cr_input, 1, 1)
        
        ev_physical_layout.addWidget(QLabel('Wheel Radius (m):'), 2, 0)
        self.ev_wheel_radius_input = QDoubleSpinBox()
        self.ev_wheel_radius_input.setRange(0.05, 1.0)
        self.ev_wheel_radius_input.setValue(EV_DEFAULTS['wheel_radius'])
        self.ev_wheel_radius_input.setDecimals(4)
        self.ev_wheel_radius_input.setSingleStep(0.001)
        ev_physical_layout.addWidget(self.ev_wheel_radius_input, 2, 1)
        
        ev_physical_layout.addWidget(QLabel('ρ Air Density (kg/m³):'), 3, 0)
        self.ev_air_density_input = QDoubleSpinBox()
        self.ev_air_density_input.setRange(0.5, 2.0)
        self.ev_air_density_input.setValue(EV_DEFAULTS['air_density'])
        self.ev_air_density_input.setDecimals(3)
        self.ev_air_density_input.setSingleStep(0.001)
        ev_physical_layout.addWidget(self.ev_air_density_input, 3, 1)
        
        ev_physical_layout.addWidget(QLabel('Af Frontal Area (m²):'), 4, 0)
        self.ev_frontal_area_input = QDoubleSpinBox()
        self.ev_frontal_area_input.setRange(0.1, 5.0)
        self.ev_frontal_area_input.setValue(EV_DEFAULTS['frontal_area'])
        self.ev_frontal_area_input.setDecimals(2)
        self.ev_frontal_area_input.setSingleStep(0.1)
        ev_physical_layout.addWidget(self.ev_frontal_area_input, 4, 1)
        
        ev_physical_group.setLayout(ev_physical_layout)
        ev_main_layout.addWidget(ev_physical_group)
        
        # Drivetrain Parameters
        ev_drivetrain_group = QGroupBox('Drivetrain Parameters')
        ev_drivetrain_layout = QGridLayout()
        
        ev_drivetrain_layout.addWidget(QLabel('Gear Ratio:'), 0, 0)
        self.ev_gear_ratio_input = QDoubleSpinBox()
        self.ev_gear_ratio_input.setRange(1.0, 20.0)
        self.ev_gear_ratio_input.setValue(5.221)
        self.ev_gear_ratio_input.setDecimals(3)
        self.ev_gear_ratio_input.setSingleStep(0.1)
        ev_drivetrain_layout.addWidget(self.ev_gear_ratio_input, 0, 1)
        
        ev_drivetrain_layout.addWidget(QLabel('Gear Efficiency ηg (%):'), 1, 0)
        self.ev_gear_efficiency_input = QDoubleSpinBox()
        self.ev_gear_efficiency_input.setRange(50.0, 99.0)
        self.ev_gear_efficiency_input.setValue(95.0)
        self.ev_gear_efficiency_input.setDecimals(1)
        self.ev_gear_efficiency_input.setSingleStep(0.5)
        ev_drivetrain_layout.addWidget(self.ev_gear_efficiency_input, 1, 1)
        
        ev_drivetrain_layout.addWidget(QLabel('Motor Efficiency ηm (%):'), 2, 0)
        self.ev_motor_efficiency_input = QDoubleSpinBox()
        self.ev_motor_efficiency_input.setRange(50.0, 99.0)
        self.ev_motor_efficiency_input.setValue(85.0)
        self.ev_motor_efficiency_input.setDecimals(1)
        self.ev_motor_efficiency_input.setSingleStep(0.5)
        ev_drivetrain_layout.addWidget(self.ev_motor_efficiency_input, 2, 1)
        
        ev_drivetrain_layout.addWidget(QLabel('Motor Base RPM:'), 3, 0)
        self.ev_motor_base_rpm_input = QSpinBox()
        self.ev_motor_base_rpm_input.setRange(100, 20000)
        self.ev_motor_base_rpm_input.setValue(1000)
        self.ev_motor_base_rpm_input.setSingleStep(100)
        ev_drivetrain_layout.addWidget(self.ev_motor_base_rpm_input, 3, 1)
        
        ev_drivetrain_group.setLayout(ev_drivetrain_layout)
        ev_main_layout.addWidget(ev_drivetrain_group)
        
        # Weight Parameters
        ev_weight_group = QGroupBox('Weight Parameters')
        ev_weight_layout = QGridLayout()
        
        ev_weight_layout.addWidget(QLabel('Kerb Weight (kg):'), 0, 0)
        self.ev_kerb_weight_input = QDoubleSpinBox()
        self.ev_kerb_weight_input.setRange(0.0, 5000.0)
        self.ev_kerb_weight_input.setValue(150.0)
        self.ev_kerb_weight_input.setSingleStep(5.0)
        self.ev_kerb_weight_input.setReadOnly(True)  # Calculated field
        self.ev_kerb_weight_input.setStyleSheet("QDoubleSpinBox { background-color: #f0f0f0; }")
        ev_weight_layout.addWidget(self.ev_kerb_weight_input, 0, 1)
        
        ev_weight_layout.addWidget(QLabel('Passenger/Load Weight (kg):'), 1, 0)
        self.ev_passenger_weight_input = QDoubleSpinBox()
        self.ev_passenger_weight_input.setRange(0.0, 1000.0)
        self.ev_passenger_weight_input.setValue(0.0)
        self.ev_passenger_weight_input.setSingleStep(5.0)
        ev_weight_layout.addWidget(self.ev_passenger_weight_input, 1, 1)
        
        ev_weight_layout.addWidget(QLabel('GVW (kg):'), 2, 0)
        self.ev_gvw_input = QDoubleSpinBox()
        self.ev_gvw_input.setRange(0.0, 6000.0)
        self.ev_gvw_input.setValue(150.0)
        self.ev_gvw_input.setSingleStep(5.0)
        self.ev_gvw_input.setReadOnly(True)  # Calculated field
        self.ev_gvw_input.setStyleSheet("QDoubleSpinBox { background-color: #f0f0f0; }")
        ev_weight_layout.addWidget(self.ev_gvw_input, 2, 1)
        
        ev_weight_layout.addWidget(QLabel('Motor & Controller Weight (kg):'), 3, 0)
        self.ev_motor_controller_weight_input = QDoubleSpinBox()
        self.ev_motor_controller_weight_input.setRange(0.0, 500.0)
        self.ev_motor_controller_weight_input.setValue(0.0)
        self.ev_motor_controller_weight_input.setSingleStep(1.0)
        ev_weight_layout.addWidget(self.ev_motor_controller_weight_input, 3, 1)
        
        ev_weight_layout.addWidget(QLabel('Battery Weight (kg):'), 4, 0)
        self.ev_battery_weight_input = QDoubleSpinBox()
        self.ev_battery_weight_input.setRange(0.0, 1000.0)
        self.ev_battery_weight_input.setValue(0.0)
        self.ev_battery_weight_input.setSingleStep(1.0)
        ev_weight_layout.addWidget(self.ev_battery_weight_input, 4, 1)
        
        ev_weight_layout.addWidget(QLabel('Vehicle Weight (kg):'), 5, 0)
        self.ev_vehicle_weight_input = QDoubleSpinBox()
        self.ev_vehicle_weight_input.setRange(0.0, 5000.0)
        self.ev_vehicle_weight_input.setValue(150.0)
        self.ev_vehicle_weight_input.setSingleStep(5.0)
        ev_weight_layout.addWidget(self.ev_vehicle_weight_input, 5, 1)
        
        ev_weight_layout.addWidget(QLabel('Other Weights (kg):'), 6, 0)
        self.ev_other_weights_input = QDoubleSpinBox()
        self.ev_other_weights_input.setRange(0.0, 500.0)
        self.ev_other_weights_input.setValue(0.0)
        self.ev_other_weights_input.setSingleStep(1.0)
        ev_weight_layout.addWidget(self.ev_other_weights_input, 6, 1)
        
        ev_weight_layout.addWidget(QLabel('Generator Weight (kg):'), 7, 0)
        self.ev_generator_weight_input = QDoubleSpinBox()
        self.ev_generator_weight_input.setRange(0.0, 200.0)
        self.ev_generator_weight_input.setValue(0.0)
        self.ev_generator_weight_input.setSingleStep(1.0)
        ev_weight_layout.addWidget(self.ev_generator_weight_input, 7, 1)
        
        ev_weight_group.setLayout(ev_weight_layout)
        ev_main_layout.addWidget(ev_weight_group)
        
        # Connect signals for auto-calculation of kerb_weight and gvw
        self.ev_battery_weight_input.valueChanged.connect(self.update_ev_calculated_weights)
        self.ev_vehicle_weight_input.valueChanged.connect(self.update_ev_calculated_weights)
        self.ev_passenger_weight_input.valueChanged.connect(self.update_ev_calculated_weights)
        
        # Battery Parameters
        ev_battery_group = QGroupBox('Battery Parameters')
        ev_battery_layout = QGridLayout()
        
        ev_battery_layout.addWidget(QLabel('Battery Requirements:'), 0, 0)
        self.ev_battery_req_input = QComboBox()
        self.ev_battery_req_input.addItems(['Lithium', 'Lead Acid', 'NiMH'])
        self.ev_battery_req_input.setCurrentText('Lithium')
        ev_battery_layout.addWidget(self.ev_battery_req_input, 0, 1)
        
        ev_battery_layout.addWidget(QLabel('Battery Chemistry:'), 1, 0)
        self.ev_battery_chem_input = QComboBox()
        self.ev_battery_chem_input.addItems(['NCM', 'NCA', 'LFP', 'LTO'])
        self.ev_battery_chem_input.setCurrentText('NCM')
        ev_battery_layout.addWidget(self.ev_battery_chem_input, 1, 1)
        
        ev_battery_layout.addWidget(QLabel('Battery Voltage (V):'), 2, 0)
        self.ev_battery_voltage_input = QDoubleSpinBox()
        self.ev_battery_voltage_input.setRange(0.0, 1000.0)
        self.ev_battery_voltage_input.setValue(24.0)
        self.ev_battery_voltage_input.setDecimals(1)
        self.ev_battery_voltage_input.setSingleStep(1.0)
        ev_battery_layout.addWidget(self.ev_battery_voltage_input, 2, 1)
        
        ev_battery_layout.addWidget(QLabel('Weight per unit Wh (kg/Wh):'), 3, 0)
        self.ev_weight_per_wh_input = QDoubleSpinBox()
        self.ev_weight_per_wh_input.setRange(0.0, 1.0)
        self.ev_weight_per_wh_input.setValue(EV_DEFAULTS['weight_per_wh'])
        self.ev_weight_per_wh_input.setDecimals(4)
        self.ev_weight_per_wh_input.setSingleStep(0.0001)
        ev_battery_layout.addWidget(self.ev_weight_per_wh_input, 3, 1)
        
        ev_battery_layout.addWidget(QLabel('Peukert\'s Coefficient:'), 4, 0)
        self.ev_peukert_input = QDoubleSpinBox()
        self.ev_peukert_input.setRange(1.0, 1.5)
        self.ev_peukert_input.setValue(1.05)
        self.ev_peukert_input.setDecimals(2)
        self.ev_peukert_input.setSingleStep(0.01)
        ev_battery_layout.addWidget(self.ev_peukert_input, 4, 1)
        
        ev_battery_layout.addWidget(QLabel('Discharge Hour Rating (Hr):'), 5, 0)
        self.ev_discharge_hr_input = QDoubleSpinBox()
        self.ev_discharge_hr_input.setRange(0.1, 20.0)
        self.ev_discharge_hr_input.setValue(2.0)
        self.ev_discharge_hr_input.setDecimals(1)
        self.ev_discharge_hr_input.setSingleStep(0.1)
        ev_battery_layout.addWidget(self.ev_discharge_hr_input, 5, 1)
        
        ev_battery_layout.addWidget(QLabel('Depth of Discharge (%):'), 6, 0)
        self.ev_dod_input = QDoubleSpinBox()
        self.ev_dod_input.setRange(0.0, 100.0)
        self.ev_dod_input.setValue(100.0)
        self.ev_dod_input.setDecimals(1)
        self.ev_dod_input.setSingleStep(1.0)
        ev_battery_layout.addWidget(self.ev_dod_input, 6, 1)
        
        ev_battery_layout.addWidget(QLabel('Constant Speed Battery Current (A):'), 7, 0)
        self.ev_battery_current_input = QDoubleSpinBox()
        self.ev_battery_current_input.setRange(0.0, 500.0)
        self.ev_battery_current_input.setValue(53.0)
        self.ev_battery_current_input.setDecimals(1)
        self.ev_battery_current_input.setSingleStep(1.0)
        ev_battery_layout.addWidget(self.ev_battery_current_input, 7, 1)
        
        ev_battery_layout.addWidget(QLabel('True Usable Battery Capacity (Wh):'), 8, 0)
        self.ev_true_capacity_wh_input = QDoubleSpinBox()
        self.ev_true_capacity_wh_input.setRange(0.0, 50000.0)
        self.ev_true_capacity_wh_input.setValue(1789.0)
        self.ev_true_capacity_wh_input.setDecimals(1)
        self.ev_true_capacity_wh_input.setSingleStep(10.0)
        ev_battery_layout.addWidget(self.ev_true_capacity_wh_input, 8, 1)
        
        ev_battery_layout.addWidget(QLabel('True Usable Battery Capacity (Ah):'), 9, 0)
        self.ev_true_capacity_ah_input = QDoubleSpinBox()
        self.ev_true_capacity_ah_input.setRange(0.0, 1000.0)
        self.ev_true_capacity_ah_input.setValue(75.0)
        self.ev_true_capacity_ah_input.setDecimals(1)
        self.ev_true_capacity_ah_input.setSingleStep(1.0)
        ev_battery_layout.addWidget(self.ev_true_capacity_ah_input, 9, 1)
        
        ev_battery_layout.addWidget(QLabel('Tentative Battery Ah (for Discharge Hr):'), 10, 0)
        self.ev_tentative_ah_input = QDoubleSpinBox()
        self.ev_tentative_ah_input.setRange(0.0, 1000.0)
        self.ev_tentative_ah_input.setValue(76.0)
        self.ev_tentative_ah_input.setDecimals(1)
        self.ev_tentative_ah_input.setSingleStep(1.0)
        ev_battery_layout.addWidget(self.ev_tentative_ah_input, 10, 1)
        
        ev_battery_layout.addWidget(QLabel('Tentative Battery Capacity (Wh):'), 11, 0)
        self.ev_tentative_wh_input = QDoubleSpinBox()
        self.ev_tentative_wh_input.setRange(0.0, 50000.0)
        self.ev_tentative_wh_input.setValue(1820.0)
        self.ev_tentative_wh_input.setDecimals(1)
        self.ev_tentative_wh_input.setSingleStep(10.0)
        ev_battery_layout.addWidget(self.ev_tentative_wh_input, 11, 1)
        
        ev_battery_layout.addWidget(QLabel('Battery Weight (kg):'), 12, 0)
        self.ev_battery_weight_total_input = QDoubleSpinBox()
        self.ev_battery_weight_total_input.setRange(0.0, 500.0)
        self.ev_battery_weight_total_input.setValue(12.0)
        self.ev_battery_weight_total_input.setDecimals(1)
        self.ev_battery_weight_total_input.setSingleStep(0.5)
        ev_battery_layout.addWidget(self.ev_battery_weight_total_input, 12, 1)
        
        ev_battery_group.setLayout(ev_battery_layout)
        ev_main_layout.addWidget(ev_battery_group)
        
        # Performance Parameters
        ev_performance_group = QGroupBox('Performance Parameters')
        ev_performance_layout = QGridLayout()
        
        ev_performance_layout.addWidget(QLabel('Rotary Inertia Compensation:'), 0, 0)
        self.ev_rotary_inertia_input = QDoubleSpinBox()
        self.ev_rotary_inertia_input.setRange(0.0, 2.0)
        self.ev_rotary_inertia_input.setValue(1.06)
        self.ev_rotary_inertia_input.setDecimals(3)
        self.ev_rotary_inertia_input.setSingleStep(0.01)
        ev_performance_layout.addWidget(self.ev_rotary_inertia_input, 0, 1)
        
        ev_performance_layout.addWidget(QLabel('Max Speed (Kmph):'), 1, 0)
        self.ev_max_speed_input = QDoubleSpinBox()
        self.ev_max_speed_input.setRange(1.0, 300.0)
        self.ev_max_speed_input.setValue(50.0)
        self.ev_max_speed_input.setSingleStep(1.0)
        ev_performance_layout.addWidget(self.ev_max_speed_input, 1, 1)
        
        ev_performance_layout.addWidget(QLabel('Slope Speed (Kmph):'), 2, 0)
        self.ev_slope_speed_input = QDoubleSpinBox()
        self.ev_slope_speed_input.setRange(1.0, 150.0)
        self.ev_slope_speed_input.setValue(5.0)
        self.ev_slope_speed_input.setSingleStep(1.0)
        ev_performance_layout.addWidget(self.ev_slope_speed_input, 2, 1)
        
        ev_performance_layout.addWidget(QLabel('Gradeability (deg):'), 3, 0)
        self.ev_gradeability_input = QDoubleSpinBox()
        self.ev_gradeability_input.setRange(0.0, 60.0)
        self.ev_gradeability_input.setValue(30.0)
        self.ev_gradeability_input.setSingleStep(0.5)
        ev_performance_layout.addWidget(self.ev_gradeability_input, 3, 1)
        
        ev_performance_layout.addWidget(QLabel('Acceleration End Speed (Kmph):'), 4, 0)
        self.ev_accel_end_speed_input = QDoubleSpinBox()
        self.ev_accel_end_speed_input.setRange(1.0, 200.0)
        self.ev_accel_end_speed_input.setValue(50.0)
        self.ev_accel_end_speed_input.setSingleStep(1.0)
        ev_performance_layout.addWidget(self.ev_accel_end_speed_input, 4, 1)
        
        ev_performance_layout.addWidget(QLabel('Acceleration Period (s):'), 5, 0)
        self.ev_accel_period_input = QDoubleSpinBox()
        self.ev_accel_period_input.setRange(1.0, 60.0)
        self.ev_accel_period_input.setValue(5.0)
        self.ev_accel_period_input.setSingleStep(0.5)
        ev_performance_layout.addWidget(self.ev_accel_period_input, 5, 1)
        
        ev_performance_layout.addWidget(QLabel('Vehicle Range (Km):'), 6, 0)
        self.ev_vehicle_range_input = QDoubleSpinBox()
        self.ev_vehicle_range_input.setRange(1.0, 1000.0)
        self.ev_vehicle_range_input.setValue(70.0)
        self.ev_vehicle_range_input.setSingleStep(5.0)
        ev_performance_layout.addWidget(self.ev_vehicle_range_input, 6, 1)
        
        ev_performance_group.setLayout(ev_performance_layout)
        ev_main_layout.addWidget(ev_performance_group)
        
        # Reset to Defaults button for EV
        ev_reset_btn = QPushButton('🔄 Reset to Default Values')
        ev_reset_btn.setStyleSheet('''
            QPushButton { background-color: #FF5722; color: white; font-weight: bold; padding: 10px; border: none; border-radius: 5px; }
            QPushButton:hover { background-color: #E64A19; }
            QPushButton:pressed { background-color: #BF360C; }
        ''')
        ev_reset_btn.clicked.connect(self.reset_ev_defaults)
        ev_main_layout.addWidget(ev_reset_btn)
        
        self.ev_params_group.setLayout(ev_main_layout)
        layout.addWidget(self.ev_params_group)
        
        # UGV Parameters (Shared + UGV-Specific)
        self.ugv_params_group = QGroupBox('UGV Parameters')
        ugv_main_layout = QVBoxLayout()
        
        # Physical Parameters
        ugv_physical_group = QGroupBox('Physical Parameters')
        ugv_physical_layout = QGridLayout()
        
        ugv_physical_layout.addWidget(QLabel('Cd Drag Coefficient:'), 0, 0)
        self.ugv_cd_input = QDoubleSpinBox()
        self.ugv_cd_input.setRange(0.1, 2.0)
        self.ugv_cd_input.setValue(0.8)
        self.ugv_cd_input.setDecimals(3)
        self.ugv_cd_input.setSingleStep(0.01)
        ugv_physical_layout.addWidget(self.ugv_cd_input, 0, 1)
        
        ugv_physical_layout.addWidget(QLabel('Cr Rolling Resistance:'), 1, 0)
        self.ugv_cr_input = QDoubleSpinBox()
        self.ugv_cr_input.setRange(0.001, 0.1)
        self.ugv_cr_input.setValue(0.02)
        self.ugv_cr_input.setDecimals(4)
        self.ugv_cr_input.setSingleStep(0.001)
        ugv_physical_layout.addWidget(self.ugv_cr_input, 1, 1)
        
        ugv_physical_layout.addWidget(QLabel('Wheel Radius (m):'), 2, 0)
        self.ugv_wheel_radius_input = QDoubleSpinBox()
        self.ugv_wheel_radius_input.setRange(0.05, 1.0)
        self.ugv_wheel_radius_input.setValue(0.2795)
        self.ugv_wheel_radius_input.setDecimals(4)
        self.ugv_wheel_radius_input.setSingleStep(0.001)
        ugv_physical_layout.addWidget(self.ugv_wheel_radius_input, 2, 1)
        
        ugv_physical_layout.addWidget(QLabel('ρ Air Density (kg/m³):'), 3, 0)
        self.ugv_air_density_input = QDoubleSpinBox()
        self.ugv_air_density_input.setRange(0.5, 2.0)
        self.ugv_air_density_input.setValue(1.164)
        self.ugv_air_density_input.setDecimals(3)
        self.ugv_air_density_input.setSingleStep(0.001)
        ugv_physical_layout.addWidget(self.ugv_air_density_input, 3, 1)
        
        ugv_physical_layout.addWidget(QLabel('Af Frontal Area (m²):'), 4, 0)
        self.ugv_frontal_area_input = QDoubleSpinBox()
        self.ugv_frontal_area_input.setRange(0.1, 5.0)
        self.ugv_frontal_area_input.setValue(0.5)
        self.ugv_frontal_area_input.setDecimals(2)
        self.ugv_frontal_area_input.setSingleStep(0.1)
        ugv_physical_layout.addWidget(self.ugv_frontal_area_input, 4, 1)
        
        ugv_physical_group.setLayout(ugv_physical_layout)
        ugv_main_layout.addWidget(ugv_physical_group)
        
        # Drivetrain Parameters
        ugv_drivetrain_group = QGroupBox('Drivetrain Parameters')
        ugv_drivetrain_layout = QGridLayout()
        
        ugv_drivetrain_layout.addWidget(QLabel('Gear Ratio:'), 0, 0)
        self.ugv_gear_ratio_input = QDoubleSpinBox()
        self.ugv_gear_ratio_input.setRange(1.0, 20.0)
        self.ugv_gear_ratio_input.setValue(5.221)
        self.ugv_gear_ratio_input.setDecimals(3)
        self.ugv_gear_ratio_input.setSingleStep(0.1)
        ugv_drivetrain_layout.addWidget(self.ugv_gear_ratio_input, 0, 1)
        
        ugv_drivetrain_layout.addWidget(QLabel('Gear Efficiency ηg (%):'), 1, 0)
        self.ugv_gear_efficiency_input = QDoubleSpinBox()
        self.ugv_gear_efficiency_input.setRange(50.0, 99.0)
        self.ugv_gear_efficiency_input.setValue(95.0)
        self.ugv_gear_efficiency_input.setDecimals(1)
        self.ugv_gear_efficiency_input.setSingleStep(0.5)
        ugv_drivetrain_layout.addWidget(self.ugv_gear_efficiency_input, 1, 1)
        
        ugv_drivetrain_layout.addWidget(QLabel('Motor Efficiency ηm (%):'), 2, 0)
        self.ugv_motor_efficiency_input = QDoubleSpinBox()
        self.ugv_motor_efficiency_input.setRange(50.0, 99.0)
        self.ugv_motor_efficiency_input.setValue(85.0)
        self.ugv_motor_efficiency_input.setDecimals(1)
        self.ugv_motor_efficiency_input.setSingleStep(0.5)
        ugv_drivetrain_layout.addWidget(self.ugv_motor_efficiency_input, 2, 1)
        
        ugv_drivetrain_layout.addWidget(QLabel('Motor Base RPM:'), 3, 0)
        self.ugv_motor_base_rpm_input = QSpinBox()
        self.ugv_motor_base_rpm_input.setRange(100, 20000)
        self.ugv_motor_base_rpm_input.setValue(1000)
        self.ugv_motor_base_rpm_input.setSingleStep(100)
        ugv_drivetrain_layout.addWidget(self.ugv_motor_base_rpm_input, 3, 1)
        
        ugv_drivetrain_group.setLayout(ugv_drivetrain_layout)
        ugv_main_layout.addWidget(ugv_drivetrain_group)
        
        # Weight Parameters
        ugv_weight_group = QGroupBox('Weight Parameters')
        ugv_weight_layout = QGridLayout()
        
        ugv_weight_layout.addWidget(QLabel('Kerb Weight (kg):'), 0, 0)
        self.ugv_kerb_weight_input = QDoubleSpinBox()
        self.ugv_kerb_weight_input.setRange(0.0, 5000.0)
        self.ugv_kerb_weight_input.setValue(150.0)
        self.ugv_kerb_weight_input.setSingleStep(5.0)
        self.ugv_kerb_weight_input.setReadOnly(True)  # Calculated field
        self.ugv_kerb_weight_input.setStyleSheet("QDoubleSpinBox { background-color: #f0f0f0; }")
        ugv_weight_layout.addWidget(self.ugv_kerb_weight_input, 0, 1)
        
        ugv_weight_layout.addWidget(QLabel('Passenger/Load Weight (kg):'), 1, 0)
        self.ugv_passenger_weight_input = QDoubleSpinBox()
        self.ugv_passenger_weight_input.setRange(0.0, 1000.0)
        self.ugv_passenger_weight_input.setValue(0.0)
        self.ugv_passenger_weight_input.setSingleStep(5.0)
        ugv_weight_layout.addWidget(self.ugv_passenger_weight_input, 1, 1)
        
        ugv_weight_layout.addWidget(QLabel('GVW (kg):'), 2, 0)
        self.ugv_gvw_input = QDoubleSpinBox()
        self.ugv_gvw_input.setRange(0.0, 6000.0)
        self.ugv_gvw_input.setValue(150.0)
        self.ugv_gvw_input.setSingleStep(5.0)
        self.ugv_gvw_input.setReadOnly(True)  # Calculated field
        self.ugv_gvw_input.setStyleSheet("QDoubleSpinBox { background-color: #f0f0f0; }")
        ugv_weight_layout.addWidget(self.ugv_gvw_input, 2, 1)
        
        ugv_weight_layout.addWidget(QLabel('Motor & Controller Weight (kg):'), 3, 0)
        self.ugv_motor_controller_weight_input = QDoubleSpinBox()
        self.ugv_motor_controller_weight_input.setRange(0.0, 500.0)
        self.ugv_motor_controller_weight_input.setValue(0.0)
        self.ugv_motor_controller_weight_input.setSingleStep(1.0)
        ugv_weight_layout.addWidget(self.ugv_motor_controller_weight_input, 3, 1)
        
        ugv_weight_layout.addWidget(QLabel('Battery Weight (kg):'), 4, 0)
        self.ugv_battery_weight_input = QDoubleSpinBox()
        self.ugv_battery_weight_input.setRange(0.0, 1000.0)
        self.ugv_battery_weight_input.setValue(0.0)
        self.ugv_battery_weight_input.setSingleStep(1.0)
        ugv_weight_layout.addWidget(self.ugv_battery_weight_input, 4, 1)
        
        ugv_weight_layout.addWidget(QLabel('Vehicle Weight (kg):'), 5, 0)
        self.ugv_vehicle_weight_input = QDoubleSpinBox()
        self.ugv_vehicle_weight_input.setRange(0.0, 5000.0)
        self.ugv_vehicle_weight_input.setValue(150.0)
        self.ugv_vehicle_weight_input.setSingleStep(5.0)
        ugv_weight_layout.addWidget(self.ugv_vehicle_weight_input, 5, 1)
        
        ugv_weight_layout.addWidget(QLabel('Other Weights (kg):'), 6, 0)
        self.ugv_other_weights_input = QDoubleSpinBox()
        self.ugv_other_weights_input.setRange(0.0, 500.0)
        self.ugv_other_weights_input.setValue(0.0)
        self.ugv_other_weights_input.setSingleStep(1.0)
        ugv_weight_layout.addWidget(self.ugv_other_weights_input, 6, 1)
        
        ugv_weight_layout.addWidget(QLabel('Generator Weight (kg):'), 7, 0)
        self.ugv_generator_weight_input = QDoubleSpinBox()
        self.ugv_generator_weight_input.setRange(0.0, 200.0)
        self.ugv_generator_weight_input.setValue(0.0)
        self.ugv_generator_weight_input.setSingleStep(1.0)
        ugv_weight_layout.addWidget(self.ugv_generator_weight_input, 7, 1)
        
        ugv_weight_group.setLayout(ugv_weight_layout)
        ugv_main_layout.addWidget(ugv_weight_group)
        
        # Connect signals for auto-calculation of kerb_weight and gvw
        self.ugv_battery_weight_input.valueChanged.connect(self.update_ugv_calculated_weights)
        self.ugv_vehicle_weight_input.valueChanged.connect(self.update_ugv_calculated_weights)
        self.ugv_passenger_weight_input.valueChanged.connect(self.update_ugv_calculated_weights)
        
        # Battery Parameters
        ugv_battery_group = QGroupBox('Battery Parameters')
        ugv_battery_layout = QGridLayout()
        
        ugv_battery_layout.addWidget(QLabel('Battery Requirements:'), 0, 0)
        self.ugv_battery_req_input = QComboBox()
        self.ugv_battery_req_input.addItems(['Lithium', 'Lead Acid', 'NiMH'])
        self.ugv_battery_req_input.setCurrentText('Lithium')
        ugv_battery_layout.addWidget(self.ugv_battery_req_input, 0, 1)
        
        ugv_battery_layout.addWidget(QLabel('Battery Chemistry:'), 1, 0)
        self.ugv_battery_chem_input = QComboBox()
        self.ugv_battery_chem_input.addItems(['NCM', 'NCA', 'LFP', 'LTO'])
        self.ugv_battery_chem_input.setCurrentText('NCM')
        ugv_battery_layout.addWidget(self.ugv_battery_chem_input, 1, 1)
        
        ugv_battery_layout.addWidget(QLabel('Battery Voltage (V):'), 2, 0)
        self.ugv_battery_voltage_input = QDoubleSpinBox()
        self.ugv_battery_voltage_input.setRange(0.0, 1000.0)
        self.ugv_battery_voltage_input.setValue(24.0)
        self.ugv_battery_voltage_input.setDecimals(1)
        self.ugv_battery_voltage_input.setSingleStep(1.0)
        ugv_battery_layout.addWidget(self.ugv_battery_voltage_input, 2, 1)
        
        ugv_battery_layout.addWidget(QLabel('Weight per unit Wh (kg/Wh):'), 3, 0)
        self.ugv_weight_per_wh_input = QDoubleSpinBox()
        self.ugv_weight_per_wh_input.setRange(0.0, 1.0)
        self.ugv_weight_per_wh_input.setValue(0.0)
        self.ugv_weight_per_wh_input.setDecimals(4)
        self.ugv_weight_per_wh_input.setSingleStep(0.0001)
        ugv_battery_layout.addWidget(self.ugv_weight_per_wh_input, 3, 1)
        
        ugv_battery_layout.addWidget(QLabel('Peukert\'s Coefficient:'), 4, 0)
        self.ugv_peukert_input = QDoubleSpinBox()
        self.ugv_peukert_input.setRange(1.0, 1.5)
        self.ugv_peukert_input.setValue(1.05)
        self.ugv_peukert_input.setDecimals(2)
        self.ugv_peukert_input.setSingleStep(0.01)
        ugv_battery_layout.addWidget(self.ugv_peukert_input, 4, 1)
        
        ugv_battery_layout.addWidget(QLabel('Discharge Hour Rating (Hr):'), 5, 0)
        self.ugv_discharge_hr_input = QDoubleSpinBox()
        self.ugv_discharge_hr_input.setRange(0.1, 20.0)
        self.ugv_discharge_hr_input.setValue(2.0)
        self.ugv_discharge_hr_input.setDecimals(1)
        self.ugv_discharge_hr_input.setSingleStep(0.1)
        ugv_battery_layout.addWidget(self.ugv_discharge_hr_input, 5, 1)
        
        ugv_battery_layout.addWidget(QLabel('Depth of Discharge (%):'), 6, 0)
        self.ugv_dod_input = QDoubleSpinBox()
        self.ugv_dod_input.setRange(0.0, 100.0)
        self.ugv_dod_input.setValue(100.0)
        self.ugv_dod_input.setDecimals(1)
        self.ugv_dod_input.setSingleStep(1.0)
        ugv_battery_layout.addWidget(self.ugv_dod_input, 6, 1)
        
        ugv_battery_layout.addWidget(QLabel('Constant Speed Battery Current (A):'), 7, 0)
        self.ugv_battery_current_input = QDoubleSpinBox()
        self.ugv_battery_current_input.setRange(0.0, 500.0)
        self.ugv_battery_current_input.setValue(53.0)
        self.ugv_battery_current_input.setDecimals(1)
        self.ugv_battery_current_input.setSingleStep(1.0)
        ugv_battery_layout.addWidget(self.ugv_battery_current_input, 7, 1)
        
        ugv_battery_layout.addWidget(QLabel('True Usable Battery Capacity (Wh):'), 8, 0)
        self.ugv_true_capacity_wh_input = QDoubleSpinBox()
        self.ugv_true_capacity_wh_input.setRange(0.0, 50000.0)
        self.ugv_true_capacity_wh_input.setValue(1789.0)
        self.ugv_true_capacity_wh_input.setDecimals(1)
        self.ugv_true_capacity_wh_input.setSingleStep(10.0)
        ugv_battery_layout.addWidget(self.ugv_true_capacity_wh_input, 8, 1)
        
        ugv_battery_layout.addWidget(QLabel('True Usable Battery Capacity (Ah):'), 9, 0)
        self.ugv_true_capacity_ah_input = QDoubleSpinBox()
        self.ugv_true_capacity_ah_input.setRange(0.0, 1000.0)
        self.ugv_true_capacity_ah_input.setValue(75.0)
        self.ugv_true_capacity_ah_input.setDecimals(1)
        self.ugv_true_capacity_ah_input.setSingleStep(1.0)
        ugv_battery_layout.addWidget(self.ugv_true_capacity_ah_input, 9, 1)
        
        ugv_battery_layout.addWidget(QLabel('Tentative Battery Ah (for Discharge Hr):'), 10, 0)
        self.ugv_tentative_ah_input = QDoubleSpinBox()
        self.ugv_tentative_ah_input.setRange(0.0, 1000.0)
        self.ugv_tentative_ah_input.setValue(76.0)
        self.ugv_tentative_ah_input.setDecimals(1)
        self.ugv_tentative_ah_input.setSingleStep(1.0)
        ugv_battery_layout.addWidget(self.ugv_tentative_ah_input, 10, 1)
        
        ugv_battery_layout.addWidget(QLabel('Tentative Battery Capacity (Wh):'), 11, 0)
        self.ugv_tentative_wh_input = QDoubleSpinBox()
        self.ugv_tentative_wh_input.setRange(0.0, 50000.0)
        self.ugv_tentative_wh_input.setValue(1820.0)
        self.ugv_tentative_wh_input.setDecimals(1)
        self.ugv_tentative_wh_input.setSingleStep(10.0)
        ugv_battery_layout.addWidget(self.ugv_tentative_wh_input, 11, 1)
        
        ugv_battery_layout.addWidget(QLabel('Battery Weight (kg):'), 12, 0)
        self.ugv_battery_weight_total_input = QDoubleSpinBox()
        self.ugv_battery_weight_total_input.setRange(0.0, 500.0)
        self.ugv_battery_weight_total_input.setValue(12.0)
        self.ugv_battery_weight_total_input.setDecimals(1)
        self.ugv_battery_weight_total_input.setSingleStep(0.5)
        ugv_battery_layout.addWidget(self.ugv_battery_weight_total_input, 12, 1)
        
        ugv_battery_group.setLayout(ugv_battery_layout)
        ugv_main_layout.addWidget(ugv_battery_group)
        
        # Performance Parameters
        ugv_performance_group = QGroupBox('Performance Parameters')
        ugv_performance_layout = QGridLayout()
        
        ugv_performance_layout.addWidget(QLabel('Rotary Inertia Compensation:'), 0, 0)
        self.ugv_rotary_inertia_input = QDoubleSpinBox()
        self.ugv_rotary_inertia_input.setRange(0.0, 2.0)
        self.ugv_rotary_inertia_input.setValue(1.06)
        self.ugv_rotary_inertia_input.setDecimals(3)
        self.ugv_rotary_inertia_input.setSingleStep(0.01)
        ugv_performance_layout.addWidget(self.ugv_rotary_inertia_input, 0, 1)
        
        ugv_performance_layout.addWidget(QLabel('Max Speed (Kmph):'), 1, 0)
        self.ugv_max_speed_input = QDoubleSpinBox()
        self.ugv_max_speed_input.setRange(1.0, 300.0)
        self.ugv_max_speed_input.setValue(50.0)
        self.ugv_max_speed_input.setSingleStep(1.0)
        ugv_performance_layout.addWidget(self.ugv_max_speed_input, 1, 1)
        
        ugv_performance_layout.addWidget(QLabel('Slope Speed (Kmph):'), 2, 0)
        self.ugv_slope_speed_input = QDoubleSpinBox()
        self.ugv_slope_speed_input.setRange(1.0, 150.0)
        self.ugv_slope_speed_input.setValue(5.0)
        self.ugv_slope_speed_input.setSingleStep(1.0)
        ugv_performance_layout.addWidget(self.ugv_slope_speed_input, 2, 1)
        
        ugv_performance_layout.addWidget(QLabel('Gradeability (deg):'), 3, 0)
        self.ugv_gradeability_input = QDoubleSpinBox()
        self.ugv_gradeability_input.setRange(0.0, 60.0)
        self.ugv_gradeability_input.setValue(30.0)
        self.ugv_gradeability_input.setSingleStep(0.5)
        ugv_performance_layout.addWidget(self.ugv_gradeability_input, 3, 1)
        
        ugv_performance_layout.addWidget(QLabel('Acceleration End Speed (Kmph):'), 4, 0)
        self.ugv_accel_end_speed_input = QDoubleSpinBox()
        self.ugv_accel_end_speed_input.setRange(1.0, 200.0)
        self.ugv_accel_end_speed_input.setValue(50.0)
        self.ugv_accel_end_speed_input.setSingleStep(1.0)
        ugv_performance_layout.addWidget(self.ugv_accel_end_speed_input, 4, 1)
        
        ugv_performance_layout.addWidget(QLabel('Acceleration Period (s):'), 5, 0)
        self.ugv_accel_period_input = QDoubleSpinBox()
        self.ugv_accel_period_input.setRange(1.0, 60.0)
        self.ugv_accel_period_input.setValue(5.0)
        self.ugv_accel_period_input.setSingleStep(0.5)
        ugv_performance_layout.addWidget(self.ugv_accel_period_input, 5, 1)
        
        ugv_performance_layout.addWidget(QLabel('Vehicle Range (Km):'), 6, 0)
        self.ugv_vehicle_range_input = QDoubleSpinBox()
        self.ugv_vehicle_range_input.setRange(1.0, 1000.0)
        self.ugv_vehicle_range_input.setValue(70.0)
        self.ugv_vehicle_range_input.setSingleStep(5.0)
        ugv_performance_layout.addWidget(self.ugv_vehicle_range_input, 6, 1)
        
        ugv_performance_group.setLayout(ugv_performance_layout)
        ugv_main_layout.addWidget(ugv_performance_group)
        
        # UGV-Specific Parameters
        ugv_specific_group = QGroupBox('UGV-Specific Parameters')
        ugv_specific_layout = QGridLayout()
        
        ugv_specific_layout.addWidget(QLabel('Step Height (m):'), 0, 0)
        self.ugv_step_height_input = QDoubleSpinBox()
        self.ugv_step_height_input.setRange(0.0, 1.0)
        self.ugv_step_height_input.setValue(0.1)
        self.ugv_step_height_input.setDecimals(3)
        self.ugv_step_height_input.setSingleStep(0.01)
        ugv_specific_layout.addWidget(self.ugv_step_height_input, 0, 1)
        
        ugv_specific_layout.addWidget(QLabel('Number of Wheels:'), 1, 0)
        self.ugv_num_wheels_input = QSpinBox()
        self.ugv_num_wheels_input.setRange(2, 12)
        self.ugv_num_wheels_input.setValue(4)
        self.ugv_num_wheels_input.setSingleStep(1)
        ugv_specific_layout.addWidget(self.ugv_num_wheels_input, 1, 1)
        
        ugv_specific_layout.addWidget(QLabel('Number of Powered Wheels:'), 2, 0)
        self.ugv_num_powered_wheels_input = QSpinBox()
        self.ugv_num_powered_wheels_input.setRange(1, 12)
        self.ugv_num_powered_wheels_input.setValue(2)
        self.ugv_num_powered_wheels_input.setSingleStep(1)
        ugv_specific_layout.addWidget(self.ugv_num_powered_wheels_input, 2, 1)
        
        ugv_specific_layout.addWidget(QLabel('Load on each Wheel (kg):'), 3, 0)
        self.ugv_load_per_wheel_input = QDoubleSpinBox()
        self.ugv_load_per_wheel_input.setRange(0.0, 1000.0)
        self.ugv_load_per_wheel_input.setValue(37.5)
        self.ugv_load_per_wheel_input.setSingleStep(0.1)
        ugv_specific_layout.addWidget(self.ugv_load_per_wheel_input, 3, 1)
        
        ugv_specific_layout.addWidget(QLabel('Torque Req. Climb/Motor (Nm):'), 4, 0)
        self.ugv_torque_climb_input = QDoubleSpinBox()
        self.ugv_torque_climb_input.setRange(0.0, 500.0)
        self.ugv_torque_climb_input.setValue(36.75)
        self.ugv_torque_climb_input.setSingleStep(0.01)
        ugv_specific_layout.addWidget(self.ugv_torque_climb_input, 4, 1)
        
        ugv_specific_layout.addWidget(QLabel('Track Width (m):'), 5, 0)
        self.ugv_track_width_input = QDoubleSpinBox()
        self.ugv_track_width_input.setRange(0.1, 5.0)
        self.ugv_track_width_input.setValue(0.6)
        self.ugv_track_width_input.setDecimals(3)
        self.ugv_track_width_input.setSingleStep(0.01)
        ugv_specific_layout.addWidget(self.ugv_track_width_input, 5, 1)
        
        ugv_specific_layout.addWidget(QLabel('Skid Coefficient μ:'), 6, 0)
        self.ugv_skid_coefficient_input = QDoubleSpinBox()
        self.ugv_skid_coefficient_input.setRange(0.1, 2.0)
        self.ugv_skid_coefficient_input.setValue(0.7)
        self.ugv_skid_coefficient_input.setDecimals(3)
        self.ugv_skid_coefficient_input.setSingleStep(0.01)
        ugv_specific_layout.addWidget(self.ugv_skid_coefficient_input, 6, 1)
        
        ugv_specific_layout.addWidget(QLabel('Spin Angular Speed ω (rad/s):'), 7, 0)
        self.ugv_spin_angular_rad_input = QDoubleSpinBox()
        self.ugv_spin_angular_rad_input.setRange(0.0, 20.0)
        self.ugv_spin_angular_rad_input.setValue(0.5)
        self.ugv_spin_angular_rad_input.setDecimals(3)
        self.ugv_spin_angular_rad_input.setSingleStep(0.1)
        ugv_specific_layout.addWidget(self.ugv_spin_angular_rad_input, 7, 1)
        
        ugv_specific_layout.addWidget(QLabel('Spin Angular Speed (deg/s):'), 8, 0)
        self.ugv_spin_angular_deg_input = QDoubleSpinBox()
        self.ugv_spin_angular_deg_input.setRange(0.0, 1200.0)
        self.ugv_spin_angular_deg_input.setValue(28.6479)
        self.ugv_spin_angular_deg_input.setDecimals(4)
        self.ugv_spin_angular_deg_input.setSingleStep(0.1)
        ugv_specific_layout.addWidget(self.ugv_spin_angular_deg_input, 8, 1)
        
        ugv_specific_group.setLayout(ugv_specific_layout)
        ugv_main_layout.addWidget(ugv_specific_group)
        
        # Reset to Defaults button for UGV
        ugv_reset_btn = QPushButton('🔄 Reset to Default Values')
        ugv_reset_btn.setStyleSheet('''
            QPushButton { background-color: #FF5722; color: white; font-weight: bold; padding: 10px; border: none; border-radius: 5px; }
            QPushButton:hover { background-color: #E64A19; }
            QPushButton:pressed { background-color: #BF360C; }
        ''')
        ugv_reset_btn.clicked.connect(self.reset_ugv_defaults)
        ugv_main_layout.addWidget(ugv_reset_btn)
        
        self.ugv_params_group.setLayout(ugv_main_layout)
        layout.addWidget(self.ugv_params_group)
        
        # Initially hide comprehensive params (shown only in Output Value Simulation)
        self.ev_params_group.setVisible(False)
        self.ugv_params_group.setVisible(False)
        
        # Quick Scenarios
        self.scenario_group = QGroupBox('Quick Scenarios')
        scenario_layout = QVBoxLayout()
        
        # Create button group for exclusive selection (only one scenario active at a time)
        from PyQt6.QtWidgets import QButtonGroup
        self.scenario_btn_group = QButtonGroup(self)
        self.scenario_btn_group.setExclusive(True)
        
        # Base style for scenario buttons (OFF state)
        flat_off_style = '''
            QPushButton { padding: 6px; background-color: #E3F2FD; border: 2px solid #90CAF9; border-radius: 3px; }
            QPushButton:hover { background-color: #BBDEFB; }
            QPushButton:checked { background-color: #1565C0; color: white; border: 2px solid #0D47A1; font-weight: bold; }
        '''
        gentle_off_style = '''
            QPushButton { padding: 6px; background-color: #E8F5E9; border: 2px solid #A5D6A7; border-radius: 3px; }
            QPushButton:hover { background-color: #C8E6C9; }
            QPushButton:checked { background-color: #2E7D32; color: white; border: 2px solid #1B5E20; font-weight: bold; }
        '''
        hill_off_style = '''
            QPushButton { padding: 6px; background-color: #FFF3E0; border: 2px solid #FFCC80; border-radius: 3px; }
            QPushButton:hover { background-color: #FFE0B2; }
            QPushButton:checked { background-color: #EF6C00; color: white; border: 2px solid #E65100; font-weight: bold; }
        '''
        steep_off_style = '''
            QPushButton { padding: 6px; background-color: #FFEBEE; border: 2px solid #FFAB91; border-radius: 3px; }
            QPushButton:hover { background-color: #FFCDD2; }
            QPushButton:checked { background-color: #C62828; color: white; border: 2px solid #B71C1C; font-weight: bold; }
        '''
        
        self.flat_btn = QPushButton('Flat Terrain (0°)')
        self.flat_btn.setCheckable(True)
        self.flat_btn.setStyleSheet(flat_off_style)
        self.flat_btn.clicked.connect(lambda: self.load_scenario('flat'))
        self.scenario_btn_group.addButton(self.flat_btn)
        scenario_layout.addWidget(self.flat_btn)
        
        self.gentle_btn = QPushButton('Gentle Slope (7°)')
        self.gentle_btn.setCheckable(True)
        self.gentle_btn.setStyleSheet(gentle_off_style)
        self.gentle_btn.clicked.connect(lambda: self.load_scenario('gentle'))
        self.scenario_btn_group.addButton(self.gentle_btn)
        scenario_layout.addWidget(self.gentle_btn)
        
        self.hill_btn = QPushButton('Moderate Hill (15°)')
        self.hill_btn.setCheckable(True)
        self.hill_btn.setStyleSheet(hill_off_style)
        self.hill_btn.clicked.connect(lambda: self.load_scenario('hill'))
        self.scenario_btn_group.addButton(self.hill_btn)
        scenario_layout.addWidget(self.hill_btn)
        
        self.steep_btn = QPushButton('Steep Climb (30°)')
        self.steep_btn.setCheckable(True)
        self.steep_btn.setStyleSheet(steep_off_style)
        self.steep_btn.clicked.connect(lambda: self.load_scenario('steep'))
        self.scenario_btn_group.addButton(self.steep_btn)
        scenario_layout.addWidget(self.steep_btn)
        
        self.scenario_group.setLayout(scenario_layout)
        layout.addWidget(self.scenario_group)
        
        # Control Buttons
        self.btn_layout_widget = QWidget()
        btn_layout = QVBoxLayout(self.btn_layout_widget)
        
        self.run_btn = QPushButton('▶ Run Simulation')
        self.run_btn.setStyleSheet('''
            QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; border: none; border-radius: 5px; }
            QPushButton:hover { background-color: #43A047; }
            QPushButton:pressed { background-color: #2E7D32; }
        ''')
        self.run_btn.clicked.connect(self.run_simulation)
        btn_layout.addWidget(self.run_btn)
        
        export_btn = QPushButton('💾 Export Results')
        export_btn.setStyleSheet('''
            QPushButton { background-color: #2196F3; color: white; font-weight: bold; padding: 8px; border: none; border-radius: 5px; }
            QPushButton:hover { background-color: #1E88E5; }
            QPushButton:pressed { background-color: #1565C0; }
        ''')
        export_btn.clicked.connect(self.export_results)
        btn_layout.addWidget(export_btn)
        
        check_suitability_btn = QPushButton('🔍 Check Motor Suitability')
        check_suitability_btn.setStyleSheet('''
            QPushButton { background-color: #9C27B0; color: white; font-weight: bold; padding: 8px; border: none; border-radius: 5px; }
            QPushButton:hover { background-color: #8E24AA; }
            QPushButton:pressed { background-color: #6A1B9A; }
        ''')
        check_suitability_btn.clicked.connect(self.check_motor_suitability)
        btn_layout.addWidget(check_suitability_btn)
        
        reset_btn = QPushButton('🔄 Reset')
        reset_btn.setStyleSheet('''
            QPushButton { background-color: #FF9800; color: white; font-weight: bold; padding: 8px; border: none; border-radius: 5px; }
            QPushButton:hover { background-color: #FB8C00; }
            QPushButton:pressed { background-color: #EF6C00; }
        ''')
        reset_btn.clicked.connect(self.reset_simulation)
        btn_layout.addWidget(reset_btn)
        
        layout.addWidget(self.btn_layout_widget)
        
        layout.addStretch()
        
        # Set content widget into scroll area
        scroll_area.setWidget(content_widget)
        panel_layout.addWidget(scroll_area)
        
        # Output value compute button - STICKY at bottom (outside scroll area)
        self.output_compute_btn = QPushButton('🧮 Compute Output Values')
        self.output_compute_btn.setStyleSheet('''
            QPushButton { background-color: #28a745; color: white; font-weight: bold; padding: 12px; border: none; border-radius: 5px; font-size: 14px; }
            QPushButton:hover { background-color: #218838; }
            QPushButton:pressed { background-color: #1e7e34; }
        ''')
        self.output_compute_btn.clicked.connect(self.compute_output_values)
        self.output_compute_btn.setVisible(False)  # Hidden by default, shown in Output mode
        self.output_compute_btn.setMinimumHeight(45)
        panel_layout.addWidget(self.output_compute_btn)
        
        # Set minimum width for left panel
        panel.setMinimumWidth(350)
        panel.setMaximumWidth(600)
        
        return panel
    
    def create_visualization_panel(self):
        """Create right visualization panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tab widget for different plots
        self.tab_widget = QTabWidget()
        
        # Speed plot
        self.speed_canvas = PlotCanvas(self, width=8, height=6)
        self.tab_widget.addTab(self.speed_canvas, '📈 Speed')
        
        # Power plot
        self.power_canvas = PlotCanvas(self, width=8, height=6)
        self.tab_widget.addTab(self.power_canvas, '⚡ Power')
        
        # Forces plot
        self.forces_canvas = PlotCanvas(self, width=8, height=6)
        self.tab_widget.addTab(self.forces_canvas, '🔧 Forces')
        
        # Motor plot
        self.motor_canvas = PlotCanvas(self, width=8, height=6)
        self.tab_widget.addTab(self.motor_canvas, '⚙️ Motor')
        
        # Data Table tab for graph simulation parameters
        self.graph_sim_tab = QWidget()
        graph_sim_layout = QVBoxLayout(self.graph_sim_tab)
        
        # Title and controls
        header_layout = QHBoxLayout()
        table_title = QLabel('Graph Simulation Parameters')
        table_title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        header_layout.addWidget(table_title)
        header_layout.addStretch()
        
        graph_sim_layout.addLayout(header_layout)
        
        # Table widget
        self.graph_data_table = QTableWidget()
        self.graph_data_table.setAlternatingRowColors(True)
        self.graph_data_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 6px;
                font-weight: bold;
                border: 1px solid #1976D2;
            }
        """)
        graph_sim_layout.addWidget(self.graph_data_table)
        
        self.tab_widget.addTab(self.graph_sim_tab, '📋 Data Table')
        
        layout.addWidget(self.tab_widget)
        
        return panel
    
    def load_scenario(self, scenario_type):
        """Load predefined scenario"""
        if scenario_type == 'flat':
            self.gradient_input.setValue(0)
        elif scenario_type == 'gentle':
            self.gradient_input.setValue(7)
        elif scenario_type == 'hill':
            self.gradient_input.setValue(15)
        elif scenario_type == 'steep':
            self.gradient_input.setValue(30)
        
        self.statusBar().showMessage(f'Loaded {scenario_type} terrain scenario')
    
    def run_simulation(self):
        """Run the simulation - directly generates table data"""
        self.run_btn.setEnabled(False)
        self.statusBar().showMessage('Running simulation...')
        
        # Directly generate table data (no background thread needed - it's fast)
        self.generate_graph_simulation_data()
        
        self.run_btn.setEnabled(True)
        # Status message updated by generate_graph_simulation_data
    
    def check_motor_suitability(self):
        """Check if the selected motor is suitable for vehicle requirements"""
        import math
        
        # Get motor parameters
        motor_key = self.motor_combo.currentText()
        mode = self.mode_combo.currentText()
        
        if motor_key == 'Customize':
            peak_torque = self.custom_peak_torque.value()
            peak_power = self.custom_peak_power.value()
            motor_name = f"Custom Motor ({peak_torque} Nm, {peak_power} W)"
        else:
            motor = GPM_MOTORS.get(motor_key, GPM_MOTORS['Default'])
            peak_torque = motor['peak_torque_nm']
            peak_power = motor['peak_power_w'] if mode == 'boost' else motor['continuous_power_w']
            motor_name = motor['name']
        
        # Get vehicle parameters
        gvw = EV_DEFAULTS['gvw']
        gear_ratio = EV_DEFAULTS['gear_ratio']
        gear_efficiency = EV_DEFAULTS['gear_efficiency'] / 100.0
        wheel_radius = EV_DEFAULTS['wheel_radius']
        cr = EV_DEFAULTS['cr']
        cd = EV_DEFAULTS['cd']
        air_density = EV_DEFAULTS['air_density']
        frontal_area = EV_DEFAULTS['frontal_area']
        num_motors = self.init_num_power_wheels.value()
        
        # Performance requirements from EV_DEFAULTS
        target_max_speed_kmph = EV_DEFAULTS['max_speed']
        target_slope_speed_kmph = EV_DEFAULTS['slope_speed']
        target_gradeability_deg = EV_DEFAULTS['gradeability']
        target_accel_time = EV_DEFAULTS['accel_period']
        target_accel_speed = EV_DEFAULTS['accel_end_speed']
        
        results = []
        overall_suitable = True
        
        # Test 1: Can achieve max speed on flat ground?
        # At max speed, power required = resistance forces × speed
        max_speed_ms = target_max_speed_kmph / 3.6
        F_roll = cr * gvw * 9.81
        F_drag = 0.5 * cd * air_density * frontal_area * (max_speed_ms ** 2)
        F_total_flat = F_roll + F_drag
        power_required_flat = F_total_flat * max_speed_ms
        power_available = peak_power * num_motors * gear_efficiency
        
        flat_speed_pass = power_available >= power_required_flat
        if not flat_speed_pass:
            overall_suitable = False
            max_achievable_speed = self._calculate_max_speed(peak_power, num_motors, gear_efficiency, gvw, cr, cd, air_density, frontal_area)
            results.append(f"❌ Max Speed on Flat: FAIL\n   Required: {power_required_flat:.0f} W, Available: {power_available:.0f} W\n   Max achievable: {max_achievable_speed:.1f} km/h (target: {target_max_speed_kmph} km/h)")
        else:
            results.append(f"✅ Max Speed on Flat: PASS\n   Can achieve {target_max_speed_kmph} km/h with {power_required_flat:.0f} W (available: {power_available:.0f} W)")
        
        # Test 2: Can climb target gradient at slope speed?
        gradient_rad = math.radians(target_gradeability_deg)
        slope_speed_ms = target_slope_speed_kmph / 3.6
        F_roll_slope = cr * gvw * 9.81 * math.cos(gradient_rad)
        F_drag_slope = 0.5 * cd * air_density * frontal_area * (slope_speed_ms ** 2)
        F_climb = gvw * 9.81 * math.sin(gradient_rad)
        F_total_slope = F_roll_slope + F_drag_slope + F_climb
        
        # Check torque requirement
        torque_required_per_wheel = (F_total_slope * wheel_radius) / (gear_ratio * gear_efficiency)
        torque_required_per_motor = torque_required_per_wheel / num_motors
        
        gradient_pass = peak_torque >= torque_required_per_motor
        if not gradient_pass:
            overall_suitable = False
            max_gradient = self._calculate_max_gradient(peak_torque, num_motors, gvw, gear_ratio, gear_efficiency, wheel_radius, cr, cd, air_density, frontal_area, slope_speed_ms)
            results.append(f"❌ Gradient Climbing ({target_gradeability_deg}° at {target_slope_speed_kmph} km/h): FAIL\n   Required: {torque_required_per_motor:.1f} Nm/motor, Available: {peak_torque} Nm/motor\n   Max climbable: {max_gradient:.1f}°")
        else:
            results.append(f"✅ Gradient Climbing ({target_gradeability_deg}° at {target_slope_speed_kmph} km/h): PASS\n   Required: {torque_required_per_motor:.1f} Nm/motor, Available: {peak_torque} Nm/motor")
        
        # Test 3: Acceleration capability
        # Simplified: check if torque is enough for reasonable acceleration
        max_tractive_force = (peak_torque * num_motors * gear_ratio * gear_efficiency) / wheel_radius
        max_acceleration = (max_tractive_force - F_roll) / gvw
        estimated_accel_time = (target_accel_speed / 3.6) / max_acceleration if max_acceleration > 0 else float('inf')
        
        accel_pass = estimated_accel_time <= target_accel_time * 1.5  # Allow 50% margin
        if not accel_pass:
            overall_suitable = False
            results.append(f"❌ Acceleration (0-{target_accel_speed} km/h in {target_accel_time}s): FAIL\n   Estimated time: {estimated_accel_time:.1f}s (target: {target_accel_time}s)\n   Max acceleration: {max_acceleration:.2f} m/s²")
        else:
            results.append(f"✅ Acceleration (0-{target_accel_speed} km/h in {target_accel_time}s): PASS\n   Estimated time: {estimated_accel_time:.1f}s\n   Max acceleration: {max_acceleration:.2f} m/s²")
        
        # Build result message
        if overall_suitable:
            title = "✅ Motor SUITABLE"
            header = f"<b style='color: green; font-size: 16px;'>Motor is SUITABLE for this vehicle!</b><br><br>"
        else:
            title = "❌ Motor NOT SUITABLE"
            header = f"<b style='color: red; font-size: 16px;'>Motor is NOT SUITABLE for this vehicle!</b><br><br>"
        
        details = f"<b>Motor:</b> {motor_name}<br>"
        details += f"<b>Mode:</b> {mode.upper()}<br>"
        details += f"<b>Number of Motors:</b> {num_motors}<br><br>"
        details += "<b>Test Results:</b><br><pre>" + "\n\n".join(results) + "</pre>"
        
        # Show result dialog
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(header + details)
        msg.setIcon(QMessageBox.Icon.Information if overall_suitable else QMessageBox.Icon.Warning)
        msg.exec()
        
        self.statusBar().showMessage(f"Motor suitability check: {'SUITABLE' if overall_suitable else 'NOT SUITABLE'}")
    
    def _calculate_max_speed(self, peak_power, num_motors, efficiency, gvw, cr, cd, air_density, frontal_area):
        """Calculate maximum achievable speed given motor power"""
        power_available = peak_power * num_motors * efficiency
        # Iterative approximation
        for speed_kmph in range(1, 200):
            speed_ms = speed_kmph / 3.6
            F_roll = cr * gvw * 9.81
            F_drag = 0.5 * cd * air_density * frontal_area * (speed_ms ** 2)
            power_required = (F_roll + F_drag) * speed_ms
            if power_required > power_available:
                return speed_kmph - 1
        return 200
    
    def _calculate_max_gradient(self, peak_torque, num_motors, gvw, gear_ratio, gear_efficiency, wheel_radius, cr, cd, air_density, frontal_area, speed_ms):
        """Calculate maximum climbable gradient given motor torque"""
        import math
        max_tractive_force = (peak_torque * num_motors * gear_ratio * gear_efficiency) / wheel_radius
        F_drag = 0.5 * cd * air_density * frontal_area * (speed_ms ** 2)
        
        for gradient_deg in range(0, 90):
            gradient_rad = math.radians(gradient_deg)
            F_roll = cr * gvw * 9.81 * math.cos(gradient_rad)
            F_climb = gvw * 9.81 * math.sin(gradient_rad)
            F_total = F_roll + F_drag + F_climb
            if F_total > max_tractive_force:
                return gradient_deg - 1
        return 90

    
    def export_results(self):
        """Export simulation table data"""
        # Check if we have data to export
        has_table_data = hasattr(self, 'graph_simulation_data') and bool(self.graph_simulation_data)
        
        if not has_table_data:
            QMessageBox.warning(self, 'No Data', 'Please run a simulation first!')
            return
        
        # Ask user for export file location (Excel format)
        filename, _ = QFileDialog.getSaveFileName(
            self, 'Export Results', 'simulation_results.xlsx', 'Excel Files (*.xlsx);;All Files (*)'
        )
        
        if filename:
            try:
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # Export simulation table data
                    df_table = pd.DataFrame(self.graph_simulation_data)
                    df_table.to_excel(writer, sheet_name='Simulation Data', index=False)
                
                # Success message
                message = f'Exported to:\n{filename}\n\nRows: {len(self.graph_simulation_data)}'
                QMessageBox.information(self, 'Export Successful', message)
                self.statusBar().showMessage(f'Exported {len(self.graph_simulation_data)} rows to {filename}')
            
            except Exception as e:
                QMessageBox.critical(self, 'Export Failed', f'Error exporting data:\n{str(e)}')
                self.statusBar().showMessage('Export failed')
    
    def update_ev_calculated_weights(self):
        """Auto-update calculated weight fields based on formulas"""
        # Formula: kerb_weight = battery_weight_input + vehicle_weight
        battery_weight = self.ev_battery_weight_input.value()
        vehicle_weight = self.ev_vehicle_weight_input.value()
        kerb_weight = battery_weight + vehicle_weight
        self.ev_kerb_weight_input.setValue(kerb_weight)
        
        # Formula: gvw = kerb_weight + passenger_weight
        passenger_weight = self.ev_passenger_weight_input.value()
        gvw = kerb_weight + passenger_weight
        self.ev_gvw_input.setValue(gvw)
    
    def update_ugv_calculated_weights(self):
        """Auto-update UGV calculated weight fields based on formulas"""
        # Formula: kerb_weight = battery_weight_input + vehicle_weight
        battery_weight = self.ugv_battery_weight_input.value()
        vehicle_weight = self.ugv_vehicle_weight_input.value()
        kerb_weight = battery_weight + vehicle_weight
        self.ugv_kerb_weight_input.setValue(kerb_weight)
        
        # Formula: gvw = kerb_weight + passenger_weight
        passenger_weight = self.ugv_passenger_weight_input.value()
        gvw = kerb_weight + passenger_weight
        self.ugv_gvw_input.setValue(gvw)
    
    def update_graph_sim_calculated_values(self):
        """Auto-update graph simulation calculated fields based on formulas"""
        # Formula 1: init_vehicle_speed_kmph = init_vehicle_speed_ms * 3.6
        speed_ms = self.init_vehicle_speed_ms.value()
        speed_kmph = speed_ms * 3.6
        self.init_vehicle_speed_kmph.setValue(speed_kmph)
        
        # Formula 2: init_motor_speed_rpm = (speed_kmph * gear_ratio) / (2 * π * wheel_radius * 0.001 * 60)
        # Uses EV_DEFAULTS for gear_ratio and wheel_radius
        gear_ratio = EV_DEFAULTS['gear_ratio']
        wheel_radius = EV_DEFAULTS['wheel_radius']
        motor_rpm = (speed_kmph * gear_ratio) / (2 * 3.14159 * wheel_radius * 0.001 * 60)
        self.init_motor_speed_rpm.setValue(motor_rpm)
        
        # Formula 3: init_total_motor_torque based on mode, motor selection, and motor RPM
        # Get motor parameters from selection
        motor_key = self.motor_combo.currentText()
        mode = self.mode_combo.currentText()
        
        # Get motor specs based on selection
        if motor_key == 'Customize':
            # Use custom input values
            peak_torque = self.custom_peak_torque.value()
            peak_power = self.custom_peak_power.value()
            continuous_torque = peak_torque / 2  # Default assumption
            continuous_power = peak_power / 2
            base_rpm = 500  # Default
        else:
            # Use predefined motor specs from GPM_MOTORS
            motor = GPM_MOTORS.get(motor_key, GPM_MOTORS['Default'])
            peak_torque = motor['peak_torque_nm']
            peak_power = motor['peak_power_w']
            continuous_torque = motor['continuous_torque_nm']
            continuous_power = motor['continuous_power_w']
            base_rpm = motor['base_rpm']
        
        # Select torque and power based on mode (boost = peak, eco = continuous)
        if mode == 'boost':
            torque_per_motor = peak_torque
            power_per_motor = peak_power
        else:  # eco mode
            torque_per_motor = continuous_torque
            power_per_motor = continuous_power
        
        # Calculate torque based on motor RPM (constant torque below base RPM, constant power above)
        if motor_rpm < base_rpm:
            torque = torque_per_motor  # Constant torque region
        else:
            # Constant power region: P = (2π × RPM × T) / 60 → T = (P × 60) / (2π × RPM)
            torque = (power_per_motor * 60) / (2 * 3.14159 * motor_rpm)
        
        # Total torque from all motors (currently using 2 motors)
        num_power_wheels = self.init_num_power_wheels.value()
        total_torque = torque * num_power_wheels
        self.init_total_motor_torque.setValue(total_torque)

        
        # Formula 4: init_per_motor_torque = total_torque / num_power_wheels
        num_power_wheels = self.init_num_power_wheels.value()
        per_motor_torque = total_torque / num_power_wheels
        self.init_per_motor_torque.setValue(per_motor_torque)
        
        # Formula 5: init_per_motor_power = (2π × RPM × per_motor_torque) / 60
        per_motor_power = (2 * 3.14159 * motor_rpm * per_motor_torque) / 60
        self.init_per_motor_power.setValue(per_motor_power)
        
        # Formula 6: init_tractive_force = (total_torque × gear_efficiency × gear_ratio) / wheel_radius
        # Uses EV_DEFAULTS for gear_efficiency, gear_ratio, and wheel_radius
        gear_efficiency = EV_DEFAULTS['gear_efficiency'] / 100.0  # Convert % to decimal
        gear_ratio = EV_DEFAULTS['gear_ratio']
        wheel_radius = EV_DEFAULTS['wheel_radius']
        tractive_force = (total_torque * gear_efficiency * gear_ratio) / wheel_radius
        self.init_tractive_force.setValue(tractive_force)
        
        # Formula 7: init_froll = cr × mass × g (rolling resistance)
        # Uses EV_DEFAULTS for cr and gvw
        cr = EV_DEFAULTS['cr']
        gvw = EV_DEFAULTS['gvw']
        froll = cr * gvw * 9.81
        self.init_froll.setValue(froll)
        
        # Formula 8: init_fdrag = cd × air_density × frontal_area × speed² × 0.03858025308642 (aerodynamic drag)
        # Uses EV_DEFAULTS for cd, air_density, frontal_area
        cd = EV_DEFAULTS['cd']
        air_density = EV_DEFAULTS['air_density']
        frontal_area = EV_DEFAULTS['frontal_area']
        fdrag = cd * air_density * frontal_area * speed_kmph * speed_kmph * 0.03858025308642
        self.init_fdrag.setValue(fdrag)
        
        # Formula 9: init_fclimb = mass × g × sin(gradient) (climbing force)
        # Uses EV_DEFAULTS for gvw
        import math
        gradient_deg = self.gradient_input.value()
        fclimb = gvw * 9.81 * math.sin(gradient_deg * 0.01745329)
        self.init_fclimb.setValue(fclimb)
        
        # Formula 10: init_fload = froll + fdrag + fclimb (total load resistance)
        fload = froll + fdrag + fclimb
        self.init_fload.setValue(fload)
        
        # Formula 11: init_fnet = tractive_force - fload (net force)
        fnet = tractive_force - fload
        self.init_fnet.setValue(fnet)
        
        # Formula 12: init_vehicle_accel = fnet / mass (acceleration)
        # Uses gvw (already retrieved) as total mass
        vehicle_accel = fnet / gvw
        self.init_vehicle_accel.setValue(vehicle_accel)
    
    def reset_ev_defaults(self):
        """Reset EV parameters to default values from EV_DEFAULTS constants"""
        # Physical Parameters
        self.ev_cd_input.setValue(EV_DEFAULTS['cd'])
        self.ev_cr_input.setValue(EV_DEFAULTS['cr'])
        self.ev_wheel_radius_input.setValue(EV_DEFAULTS['wheel_radius'])
        self.ev_air_density_input.setValue(EV_DEFAULTS['air_density'])
        self.ev_frontal_area_input.setValue(EV_DEFAULTS['frontal_area'])
        
        # Drivetrain Parameters
        self.ev_gear_ratio_input.setValue(EV_DEFAULTS['gear_ratio'])
        self.ev_gear_efficiency_input.setValue(EV_DEFAULTS['gear_efficiency'])
        self.ev_motor_efficiency_input.setValue(EV_DEFAULTS['motor_efficiency'])
        self.ev_motor_base_rpm_input.setValue(EV_DEFAULTS['motor_base_rpm'])
        
        # Weight Parameters
        self.ev_kerb_weight_input.setValue(EV_DEFAULTS['kerb_weight'])
        self.ev_passenger_weight_input.setValue(EV_DEFAULTS['passenger_weight'])
        self.ev_gvw_input.setValue(EV_DEFAULTS['gvw'])
        self.ev_motor_controller_weight_input.setValue(EV_DEFAULTS['motor_controller_weight'])
        self.ev_battery_weight_input.setValue(EV_DEFAULTS['battery_weight_input'])
        self.ev_vehicle_weight_input.setValue(EV_DEFAULTS['vehicle_weight'])
        self.ev_other_weights_input.setValue(EV_DEFAULTS['other_weights'])
        self.ev_generator_weight_input.setValue(EV_DEFAULTS['generator_weight'])
        
        # Battery Parameters
        self.ev_battery_req_input.setCurrentText(EV_DEFAULTS['battery_requirements'])
        self.ev_battery_chem_input.setCurrentText(EV_DEFAULTS['battery_chemistry'])
        self.ev_battery_voltage_input.setValue(EV_DEFAULTS['battery_voltage'])
        self.ev_weight_per_wh_input.setValue(EV_DEFAULTS['weight_per_wh'])
        self.ev_peukert_input.setValue(EV_DEFAULTS['peukert_coeff'])
        self.ev_discharge_hr_input.setValue(EV_DEFAULTS['discharge_hr'])
        self.ev_dod_input.setValue(EV_DEFAULTS['dod_pct'])
        self.ev_battery_current_input.setValue(EV_DEFAULTS['battery_current'])
        self.ev_true_capacity_wh_input.setValue(EV_DEFAULTS['true_capacity_wh'])
        self.ev_true_capacity_ah_input.setValue(EV_DEFAULTS['true_capacity_ah'])
        self.ev_tentative_ah_input.setValue(EV_DEFAULTS['tentative_ah'])
        self.ev_tentative_wh_input.setValue(EV_DEFAULTS['tentative_wh'])
        self.ev_battery_weight_total_input.setValue(EV_DEFAULTS['battery_weight_total'])
        
        # Performance Parameters
        self.ev_rotary_inertia_input.setValue(EV_DEFAULTS['rotary_inertia'])
        self.ev_max_speed_input.setValue(EV_DEFAULTS['max_speed'])
        self.ev_slope_speed_input.setValue(EV_DEFAULTS['slope_speed'])
        self.ev_gradeability_input.setValue(EV_DEFAULTS['gradeability'])
        self.ev_accel_end_speed_input.setValue(EV_DEFAULTS['accel_end_speed'])
        self.ev_accel_period_input.setValue(EV_DEFAULTS['accel_period'])
        self.ev_vehicle_range_input.setValue(EV_DEFAULTS['vehicle_range'])
        
        # Clear output area
        self.output_text.clear()
        
        self.statusBar().showMessage('EV parameters reset to defaults')
    
    def reset_ugv_defaults(self):
        """Reset UGV parameters to default values using UGV_DEFAULTS dictionary"""
        # Physical Parameters
        self.ugv_cd_input.setValue(UGV_DEFAULTS['cd'])
        self.ugv_cr_input.setValue(UGV_DEFAULTS['cr'])
        self.ugv_wheel_radius_input.setValue(UGV_DEFAULTS['wheel_radius'])
        self.ugv_air_density_input.setValue(UGV_DEFAULTS['air_density'])
        self.ugv_frontal_area_input.setValue(UGV_DEFAULTS['frontal_area'])
        
        # Drivetrain Parameters
        self.ugv_gear_ratio_input.setValue(UGV_DEFAULTS['gear_ratio'])
        self.ugv_gear_efficiency_input.setValue(UGV_DEFAULTS['gear_efficiency'])
        self.ugv_motor_efficiency_input.setValue(UGV_DEFAULTS['motor_efficiency'])
        self.ugv_motor_base_rpm_input.setValue(UGV_DEFAULTS['motor_base_rpm'])
        
        # Weight Parameters
        self.ugv_kerb_weight_input.setValue(UGV_DEFAULTS['kerb_weight'])
        self.ugv_passenger_weight_input.setValue(UGV_DEFAULTS['passenger_weight'])
        self.ugv_gvw_input.setValue(UGV_DEFAULTS['gvw'])
        self.ugv_motor_controller_weight_input.setValue(UGV_DEFAULTS['motor_controller_weight'])
        self.ugv_battery_weight_input.setValue(UGV_DEFAULTS['battery_weight_input'])
        self.ugv_vehicle_weight_input.setValue(UGV_DEFAULTS['vehicle_weight'])
        self.ugv_other_weights_input.setValue(UGV_DEFAULTS['other_weights'])
        self.ugv_generator_weight_input.setValue(UGV_DEFAULTS['generator_weight'])
        
        # Battery Parameters
        self.ugv_battery_req_input.setCurrentText(UGV_DEFAULTS['battery_requirements'])
        self.ugv_battery_chem_input.setCurrentText(UGV_DEFAULTS['battery_chemistry'])
        self.ugv_battery_voltage_input.setValue(UGV_DEFAULTS['battery_voltage'])
        self.ugv_weight_per_wh_input.setValue(UGV_DEFAULTS['weight_per_wh'])
        self.ugv_peukert_input.setValue(UGV_DEFAULTS['peukert_coeff'])
        self.ugv_discharge_hr_input.setValue(UGV_DEFAULTS['discharge_hr'])
        self.ugv_dod_input.setValue(UGV_DEFAULTS['dod_pct'])
        self.ugv_battery_current_input.setValue(UGV_DEFAULTS['battery_current'])
        self.ugv_true_capacity_wh_input.setValue(UGV_DEFAULTS['true_capacity_wh'])
        self.ugv_true_capacity_ah_input.setValue(UGV_DEFAULTS['true_capacity_ah'])
        self.ugv_tentative_ah_input.setValue(UGV_DEFAULTS['tentative_ah'])
        self.ugv_tentative_wh_input.setValue(UGV_DEFAULTS['tentative_wh'])
        self.ugv_battery_weight_total_input.setValue(UGV_DEFAULTS['battery_weight_total'])
        
        # Performance Parameters
        self.ugv_rotary_inertia_input.setValue(UGV_DEFAULTS['rotary_inertia'])
        self.ugv_max_speed_input.setValue(UGV_DEFAULTS['max_speed'])
        self.ugv_slope_speed_input.setValue(UGV_DEFAULTS['slope_speed'])
        self.ugv_gradeability_input.setValue(UGV_DEFAULTS['gradeability'])
        self.ugv_accel_end_speed_input.setValue(UGV_DEFAULTS['accel_end_speed'])
        self.ugv_accel_period_input.setValue(UGV_DEFAULTS['accel_period'])
        self.ugv_vehicle_range_input.setValue(UGV_DEFAULTS['vehicle_range'])
        
        # UGV-Specific Parameters
        self.ugv_step_height_input.setValue(UGV_DEFAULTS['step_height'])
        self.ugv_num_wheels_input.setValue(UGV_DEFAULTS['num_wheels'])
        self.ugv_num_powered_wheels_input.setValue(UGV_DEFAULTS['num_powered_wheels'])
        self.ugv_load_per_wheel_input.setValue(UGV_DEFAULTS['load_per_wheel'])
        self.ugv_torque_climb_input.setValue(UGV_DEFAULTS['torque_climb'])
        self.ugv_track_width_input.setValue(UGV_DEFAULTS['track_width'])
        self.ugv_skid_coefficient_input.setValue(UGV_DEFAULTS['skid_coefficient'])
        self.ugv_spin_angular_rad_input.setValue(UGV_DEFAULTS['spin_angular_rad'])
        self.ugv_spin_angular_deg_input.setValue(UGV_DEFAULTS['spin_angular_deg'])
        
        # Clear output area
        self.output_text.clear()
        
        self.statusBar().showMessage('UGV parameters reset to defaults')
    
    def reset_simulation(self):
        """Reset simulation and parameters to defaults"""
        # Clear table data
        if hasattr(self, 'graph_simulation_data'):
            self.graph_simulation_data = []
        
        # Clear table widget
        self.graph_data_table.setRowCount(0)
        
        # Reset simulation parameters to defaults
        self.gradient_input.setValue(GRAPH_SIM_DEFAULTS['gradient_deg'])
        self.mode_combo.setCurrentIndex(0)  # boost (matches GRAPH_SIM_DEFAULTS['mode'])
        
        # Clear plots
        for canvas in [self.speed_canvas, self.power_canvas, 
                      self.forces_canvas, self.motor_canvas]:
            canvas.fig.clear()
            canvas.draw()
        
        self.statusBar().showMessage('Simulation reset - parameters unchanged')


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Force light mode theme
    app.setStyle('Fusion')
    
    # Set light color palette
    from PyQt6.QtGui import QPalette, QColor
    palette = QPalette()
    
    # Window colors
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    
    # Base colors (input fields)
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
    
    # Text colors
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
    
    # Button colors
    palette.setColor(QPalette.ColorRole.Button, QColor(225, 225, 225))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    
    # Selection colors
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    # Disabled colors
    palette.setColor(QPalette.ColorRole.Light, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Midlight, QColor(227, 227, 227))
    palette.setColor(QPalette.ColorRole.Dark, QColor(160, 160, 160))
    palette.setColor(QPalette.ColorRole.Mid, QColor(180, 180, 180))
    palette.setColor(QPalette.ColorRole.Shadow, QColor(105, 105, 105))
    
    app.setPalette(palette)
    
    window = EVSimulationApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
