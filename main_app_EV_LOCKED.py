"""
EV Power Train Simulation Tool - Main Application
Desktop GUI application for simulating EV performance
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QGroupBox, QGridLayout, QTabWidget,
                             QTextEdit, QFileDialog, QMessageBox, QProgressBar,
                             QDoubleSpinBox, QSpinBox, QMenuBar, QMenu, QSplitter,
                             QStackedWidget, QScrollArea)
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

from simulation_engine import EVSimulationEngine, VehicleParameters


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
    'battery_weight_total': 10.5,  # kg
    
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

# Energy density by battery chemistry (Wh/kg)
BATTERY_ENERGY_DENSITY = {
    'NCM': 250,  # Nickel Cobalt Manganese
    'NCA': 260,  # Nickel Cobalt Aluminum
    'LFP': 160,  # Lithium Iron Phosphate
    'LTO': 80    # Lithium Titanate Oxide
}

# Physical constants
GRAVITY = 9.81  # m/s²
DEG_TO_RAD = 0.01745329  # degrees to radians conversion
KMH_TO_MS = 0.2777778    # km/h to m/s conversion


class SimulationThread(QThread):
    """Thread for running simulation without blocking UI"""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(int)
    
    def __init__(self, engine, duration, target_speed, gradient, mode):
        super().__init__()
        self.engine = engine
        self.duration = duration
        self.target_speed = target_speed
        self.gradient = gradient
        self.mode = mode
    
    def run(self):
        """Run simulation in background"""
        self.engine.run_simulation(
            duration=self.duration,
            target_speed_kmh=self.target_speed,
            gradient_deg=self.gradient,
            mode=self.mode
        )
        stats = self.engine.get_summary_stats()
        self.finished.emit(stats)


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
            ax.plot(history['time'], history['speed_kmh'], 'b-', linewidth=2)
            ax.set_xlabel('Time (s)', fontsize=10)
            ax.set_ylabel('Speed (km/h)', fontsize=10)
            ax.set_title('Vehicle Speed vs Time', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
        
        elif plot_type == 'power':
            ax = self.fig.add_subplot(111)
            ax.plot(history['time'], history['motor_power'], 'r-', linewidth=2)
            ax.set_xlabel('Time (s)', fontsize=10)
            ax.set_ylabel('Power (kW)', fontsize=10)
            ax.set_title('Motor Power vs Time', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
        
        elif plot_type == 'forces':
            ax = self.fig.add_subplot(111)
            ax.plot(history['time'], history['tractive_force'], 'g-', 
                   linewidth=2, label='Tractive Force')
            ax.plot(history['time'], history['total_resistance'], 'r-', 
                   linewidth=2, label='Total Resistance')
            ax.plot(history['time'], history['drag_force'], 'b--', 
                   linewidth=1.5, label='Drag Force')
            ax.plot(history['time'], history['rolling_resistance'], 'y--', 
                   linewidth=1.5, label='Rolling Resistance')
            if max(history['climbing_force']) > 0:
                ax.plot(history['time'], history['climbing_force'], 'm--', 
                       linewidth=1.5, label='Climbing Force')
            ax.set_xlabel('Time (s)', fontsize=10)
            ax.set_ylabel('Force (N)', fontsize=10)
            ax.set_title('Forces Analysis', fontsize=12, fontweight='bold')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
        
        elif plot_type == 'motor':
            ax1 = self.fig.add_subplot(211)
            ax1.plot(history['time'], history['motor_rpm'], 'b-', linewidth=2)
            ax1.set_ylabel('Motor RPM', fontsize=10)
            ax1.set_title('Motor Performance', fontsize=12, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            
            ax2 = self.fig.add_subplot(212)
            ax2.plot(history['time'], history['motor_torque'], 'r-', linewidth=2)
            ax2.set_xlabel('Time (s)', fontsize=10)
            ax2.set_ylabel('Motor Torque (Nm)', fontsize=10)
            ax2.grid(True, alpha=0.3)
        
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
        self.params = VehicleParameters()
        self.engine = EVSimulationEngine(self.params)
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

        self.statusBar().showMessage('Ready')
    
    def on_nav_changed(self, index: int):
        """Handle navbar tab changes to switch right view and buttons"""
        if index == 0:  # Output Value Simulation (default first tab)
            # Show output panel with comprehensive EV/UGV parameters
            self.right_stack.setCurrentIndex(0)  # Output panel
            self.left_panel.setVisible(True)
            # Hide graph simulation controls
            self.sim_group.setVisible(False)
            self.scenario_group.setVisible(False)
            self.btn_layout_widget.setVisible(False)
            self.results_group.setVisible(False)
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
        else:  # Graph Simulation
            # Show graphs with basic simulation controls on the left
            self.right_stack.setCurrentIndex(1)  # Graphs panel
            self.left_panel.setVisible(True)
            # Show only basic simulation controls for running simulations
            self.sim_group.setVisible(True)
            self.scenario_group.setVisible(True)
            self.btn_layout_widget.setVisible(True)
            self.results_group.setVisible(True)
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
            vehicle_mass = self.ugv_vehicle_weight_input.value()
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
        
        # --- BATTERY CALCULATIONS USING FORMULAS ---
        # Get battery voltage and vehicle range
        battery_voltage = self.ev_battery_voltage_input.value() if vehicle_type == 'EV' else 24.0
        vehicle_range_km = self.ev_vehicle_range_input.value() if vehicle_type == 'EV' else 70.0
        
        # Battery parameters from inputs
        battery_chemistry = self.ev_battery_chem_input.currentText() if vehicle_type == 'EV' else 'NCM'
        battery_requirements = self.ev_battery_req_input.currentText() if vehicle_type == 'EV' else 'Lithium'
        weight_per_wh = self.ev_weight_per_wh_input.value() if vehicle_type == 'EV' else 0.0065
        peukert_coeff = self.ev_peukert_input.value() if vehicle_type == 'EV' else 1.05
        discharge_hr = self.ev_discharge_hr_input.value() if vehicle_type == 'EV' else 2.0
        dod_pct = self.ev_dod_input.value() if vehicle_type == 'EV' else 100.0

        
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
            final_ah = (true_usable_ah * ((battery_current * discharge_hr) ** (peukert_coeff - 1))) ** (1/peukert_coeff)# Add 5% margin
            
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
            num_motors = self.ugv_num_powered_wheels_input.value()
            num_wheels = self.ugv_num_wheels_input.value()
            track_width = self.ugv_track_width_input.value()
            skid_coefficient = self.ugv_skid_coefficient_input.value()
            spin_angular_rad = self.ugv_spin_angular_rad_input.value()
            spin_angular_deg = self.ugv_spin_angular_deg_input.value()
            
            # --- PER MOTOR OUTPUT POWER ---
            per_motor_output_max = motor_output_max / num_motors if num_motors > 0 else 0
            per_motor_output_slope = motor_output_slope / num_motors if num_motors > 0 else 0
            per_motor_output_accel = motor_output_accel / num_motors if num_motors > 0 else 0
            
            # --- PER MOTOR TORQUE AND RPM ---
            per_motor_torque_max = torque_motor_max / num_motors if num_motors > 0 else 0
            per_motor_torque_accel = torque_motor_accel / num_motors if num_motors > 0 else 0
            per_motor_torque_slope = torque_motor_slope / num_motors if num_motors > 0 else 0
            
            # --- POWER OUTPUT PER WHEELS (Powered wheels only) ---
            per_wheel_power_max = wheel_power_max / num_motors if num_motors > 0 else 0
            per_wheel_power_accel = wheel_power_accel / num_motors if num_motors > 0 else 0
            per_wheel_power_slope = wheel_power_slope / num_motors if num_motors > 0 else 0
            
            # --- TORQUE AND RPM PER WHEEL (Powered wheels only) ---
            per_wheel_torque_max = torque_wheel_max / num_motors if num_motors > 0 else 0
            per_wheel_torque_accel = torque_wheel_accel / num_motors if num_motors > 0 else 0
            per_wheel_torque_slope = torque_wheel_slope / num_motors if num_motors > 0 else 0
            
            # --- SKID PARAMETERS AND POWER ESTIMATION ---
            # Total Skid Friction Force
            total_skid_friction = vehicle_mass * 9.81 * skid_coefficient
            
            # Per wheel Skid Friction Force
            per_wheel_skid_friction = total_skid_friction / num_motors if num_motors > 0 else 0
            
            # Wheel linear speed during turning
            wheel_linear_speed_turn = spin_angular_rad * (track_width / 2)
            
            # Power for each motor during turn
            power_per_motor_turn = per_wheel_skid_friction * wheel_linear_speed_turn
            
            # Total power for all motors
            total_power_turn = power_per_motor_turn * num_motors
            
            # Wheel RPM during turn
            wheel_rpm_turn = (wheel_linear_speed_turn * 60) / (2 * math.pi * wheel_radius) if wheel_radius > 0 else 0
            
            # Vehicle rotational degree per second
            vehicle_rot_deg_per_sec = spin_angular_deg
            
            # Total Wheel Torque
            total_wheel_torque = per_wheel_skid_friction * wheel_radius * num_motors
            
            # Total Motor Wheel Torque (accounting for gear efficiency)
            total_motor_wheel_torque = total_wheel_torque / gear_ratio if gear_ratio > 0 else 0
            
            # Per Motor Wheel Torque
            per_motor_wheel_torque = total_motor_wheel_torque / num_motors if num_motors > 0 else 0
            
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
        
        # Simulation Parameters
        self.sim_group = QGroupBox('Simulation Parameters')
        sim_layout = QGridLayout()
        
        # Duration
        sim_layout.addWidget(QLabel('Duration (s):'), 0, 0)
        self.duration_input = QSpinBox()
        self.duration_input.setRange(10, 600)
        self.duration_input.setValue(90)
        sim_layout.addWidget(self.duration_input, 0, 1)
        
        # Target Speed
        sim_layout.addWidget(QLabel('Target Speed (km/h):'), 1, 0)
        self.speed_input = QDoubleSpinBox()
        self.speed_input.setRange(0, 200)
        self.speed_input.setValue(150)  # High default - continuous acceleration like table
        sim_layout.addWidget(self.speed_input, 1, 1)
        
        # Gradient
        sim_layout.addWidget(QLabel('Gradient (°):'), 2, 0)
        self.gradient_input = QDoubleSpinBox()
        self.gradient_input.setRange(-30, 60)
        self.gradient_input.setValue(0)
        sim_layout.addWidget(self.gradient_input, 2, 1)
        
        # Mode
        sim_layout.addWidget(QLabel('Mode:'), 3, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['boost', 'eco'])
        sim_layout.addWidget(self.mode_combo, 3, 1)
        
        # Constant Power
        sim_layout.addWidget(QLabel('Constant Power (W):'), 4, 0)
        self.constant_power_input = QDoubleSpinBox()
        self.constant_power_input.setRange(100, 50000)
        self.constant_power_input.setValue(2000)
        self.constant_power_input.setDecimals(0)
        self.constant_power_input.setSingleStep(100)
        self.constant_power_input.valueChanged.connect(self.update_constant_torque)
        sim_layout.addWidget(self.constant_power_input, 4, 1)
        
        # Base RPM
        sim_layout.addWidget(QLabel('Base RPM:'), 5, 0)
        self.base_rpm_input = QDoubleSpinBox()
        self.base_rpm_input.setRange(50, 5000)
        self.base_rpm_input.setValue(500)
        self.base_rpm_input.setDecimals(0)
        self.base_rpm_input.setSingleStep(10)
        self.base_rpm_input.valueChanged.connect(self.update_constant_torque)
        sim_layout.addWidget(self.base_rpm_input, 5, 1)
        
        # Constant Torque (calculated, read-only)
        sim_layout.addWidget(QLabel('Constant Torque (Nm):'), 6, 0)
        self.constant_torque_display = QLineEdit()
        self.constant_torque_display.setReadOnly(True)
        self.constant_torque_display.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")
        sim_layout.addWidget(self.constant_torque_display, 6, 1)
        
        # Calculate initial constant torque
        self.update_constant_torque()
        
        self.sim_group.setLayout(sim_layout)
        layout.addWidget(self.sim_group)
        
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
        ev_reset_btn.setStyleSheet('background-color: #FF5722; color: white; font-weight: bold; padding: 10px; border: none; border-radius: 5px;')
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
        ugv_reset_btn.setStyleSheet('background-color: #FF5722; color: white; font-weight: bold; padding: 10px; border: none; border-radius: 5px;')
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
        
        flat_btn = QPushButton('Flat Terrain (0°)')
        flat_btn.setStyleSheet('padding: 6px; background-color: #E3F2FD; border: 1px solid #90CAF9; border-radius: 3px;')
        flat_btn.clicked.connect(lambda: self.load_scenario('flat'))
        scenario_layout.addWidget(flat_btn)
        
        gentle_btn = QPushButton('Gentle Slope (7°)')
        gentle_btn.setStyleSheet('padding: 6px; background-color: #E8F5E9; border: 1px solid #A5D6A7; border-radius: 3px;')
        gentle_btn.clicked.connect(lambda: self.load_scenario('gentle'))
        scenario_layout.addWidget(gentle_btn)
        
        hill_btn = QPushButton('Moderate Hill (15°)')
        hill_btn.setStyleSheet('padding: 6px; background-color: #FFF3E0; border: 1px solid #FFCC80; border-radius: 3px;')
        hill_btn.clicked.connect(lambda: self.load_scenario('hill'))
        scenario_layout.addWidget(hill_btn)
        
        steep_btn = QPushButton('Steep Climb (30°)')
        steep_btn.setStyleSheet('padding: 6px; background-color: #FFEBEE; border: 1px solid #FFAB91; border-radius: 3px;')
        steep_btn.clicked.connect(lambda: self.load_scenario('steep'))
        scenario_layout.addWidget(steep_btn)
        
        self.scenario_group.setLayout(scenario_layout)
        layout.addWidget(self.scenario_group)
        
        # Control Buttons
        self.btn_layout_widget = QWidget()
        btn_layout = QVBoxLayout(self.btn_layout_widget)
        
        self.run_btn = QPushButton('▶ Run Simulation')
        self.run_btn.setStyleSheet('background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; border: none; border-radius: 5px;')
        self.run_btn.clicked.connect(self.run_simulation)
        btn_layout.addWidget(self.run_btn)
        
        export_btn = QPushButton('💾 Export Results')
        export_btn.setStyleSheet('background-color: #2196F3; color: white; font-weight: bold; padding: 8px; border: none; border-radius: 5px;')
        export_btn.clicked.connect(self.export_results)
        btn_layout.addWidget(export_btn)
        
        reset_btn = QPushButton('🔄 Reset')
        reset_btn.setStyleSheet('background-color: #FF9800; color: white; font-weight: bold; padding: 8px; border: none; border-radius: 5px;')
        reset_btn.clicked.connect(self.reset_simulation)
        btn_layout.addWidget(reset_btn)
        
        layout.addWidget(self.btn_layout_widget)
        
        # Results Summary
        self.results_group = QGroupBox('Results Summary')
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(150)
        self.results_text.setMaximumHeight(250)
        results_layout.addWidget(self.results_text)
        
        self.results_group.setLayout(results_layout)
        layout.addWidget(self.results_group)
        
        layout.addStretch()
        
        # Set content widget into scroll area
        scroll_area.setWidget(content_widget)
        panel_layout.addWidget(scroll_area)
        
        # Output value compute button - STICKY at bottom (outside scroll area)
        self.output_compute_btn = QPushButton('🧮 Compute Output Values')
        self.output_compute_btn.setStyleSheet('background-color: #28a745; color: white; font-weight: bold; padding: 12px; border: none; border-radius: 5px; font-size: 14px;')
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
        
        # Energy plot
        self.energy_canvas = PlotCanvas(self, width=8, height=6)
        self.tab_widget.addTab(self.energy_canvas, '🔋 Energy')
        
        layout.addWidget(self.tab_widget)
        
        return panel
    
    def load_scenario(self, scenario_type):
        """Load predefined scenario"""
        if scenario_type == 'flat':
            self.gradient_input.setValue(0)
            self.speed_input.setValue(85)
            self.duration_input.setValue(90)
        elif scenario_type == 'gentle':
            self.gradient_input.setValue(7)
            self.speed_input.setValue(70)
            self.duration_input.setValue(100)
        elif scenario_type == 'hill':
            self.gradient_input.setValue(15)
            self.speed_input.setValue(60)
            self.duration_input.setValue(120)
        elif scenario_type == 'steep':
            self.gradient_input.setValue(30)
            self.speed_input.setValue(50)
            self.duration_input.setValue(150)
        
        self.statusBar().showMessage(f'Loaded {scenario_type} terrain scenario')
    
    def update_parameters(self):
        """Update engine parameters from UI"""
        vehicle_type = self.vehicle_type_combo.currentText()
        
        if vehicle_type == 'EV':
            self.params.drag_coefficient = self.ev_cd_input.value()
            self.params.rolling_resistance = self.ev_cr_input.value()
            self.params.vehicle_mass = self.ev_vehicle_weight_input.value()
            self.params.frontal_area = self.ev_frontal_area_input.value()
            self.params.wheel_radius = self.ev_wheel_radius_input.value()
            self.params.gear_ratio = self.ev_gear_ratio_input.value()
            self.params.gear_efficiency = self.ev_gear_efficiency_input.value() / 100.0
            self.params.motor_efficiency = self.ev_motor_efficiency_input.value() / 100.0
        else:  # UGV
            self.params.drag_coefficient = self.ugv_cd_input.value()
            self.params.rolling_resistance = self.ugv_cr_input.value()
            self.params.vehicle_mass = self.ugv_vehicle_weight_input.value()
            self.params.frontal_area = self.ugv_frontal_area_input.value()
            self.params.wheel_radius = self.ugv_wheel_radius_input.value()
            self.params.gear_ratio = self.ugv_gear_ratio_input.value()
            self.params.gear_efficiency = self.ugv_gear_efficiency_input.value() / 100.0
            self.params.motor_efficiency = self.ugv_motor_efficiency_input.value() / 100.0
        
        # Update motor torque curve parameters from Simulation Parameters
        self.params.base_rpm = self.base_rpm_input.value()
        constant_power = self.constant_power_input.value()
        
        # Set power based on current mode selection
        mode = self.mode_combo.currentText()
        if mode == 'eco':
            self.params.max_power_eco = constant_power
        else:  # boost
            self.params.max_power_boost = constant_power
        
        self.engine = EVSimulationEngine(self.params)
    
    def update_constant_torque(self):
        """Calculate and update constant torque display based on power and base RPM"""
        import math
        
        constant_power = self.constant_power_input.value()
        base_rpm = self.base_rpm_input.value()
        
        if base_rpm > 0:
            # Formula: Torque = (Power * 60) / (2 * π * RPM)
            constant_torque = (constant_power * 60) / (2 * math.pi * base_rpm)
            self.constant_torque_display.setText(f"{constant_torque:.5f}")
        else:
            self.constant_torque_display.setText("N/A")
    
    def run_simulation(self):
        """Run the simulation"""
        self.update_parameters()
        
        duration = self.duration_input.value()
        target_speed = self.speed_input.value()
        gradient = self.gradient_input.value()
        mode = self.mode_combo.currentText()
        
        self.run_btn.setEnabled(False)
        self.statusBar().showMessage('Running simulation...')
        
        # Run simulation in thread
        self.sim_thread = SimulationThread(
            self.engine, duration, target_speed, gradient, mode
        )
        self.sim_thread.finished.connect(self.on_simulation_finished)
        self.sim_thread.start()
    
    def on_simulation_finished(self, stats):
        """Handle simulation completion"""
        # Update plots
        history = self.engine.history
        
        self.speed_canvas.plot_results(history, 'speed')
        self.power_canvas.plot_results(history, 'power')
        self.forces_canvas.plot_results(history, 'forces')
        self.motor_canvas.plot_results(history, 'motor')
        self.energy_canvas.plot_results(history, 'energy')
        
        # Update results text with HTML formatting
        results = f"""
        <html>
        <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 5px; }}
            .header-box {{ 
                border: 2px solid #333; 
                background: linear-gradient(to right, #f0f0f0, #e0e0e0);
                padding: 8px; 
                margin-bottom: 15px;
                text-align: center;
                border-radius: 5px;
            }}
            .header-title {{ 
                font-size: 14px; 
                font-weight: bold; 
                color: #333;
                letter-spacing: 1px;
            }}
            .section {{ 
                margin-bottom: 15px; 
                background: #ffffff;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
            }}
            .section-title {{ 
                font-size: 12px; 
                font-weight: bold; 
                color: #2196F3;
                margin-bottom: 8px;
                padding-bottom: 5px;
                border-bottom: 2px solid #2196F3;
            }}
            .metric-row {{ 
                display: flex; 
                justify-content: space-between;
                padding: 3px 0;
                font-size: 11px;
            }}
            .metric-label {{ 
                color: #555;
                font-weight: 500;
            }}
            .metric-value {{ 
                color: #000;
                font-weight: bold;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            td {{
                padding: 4px 8px;
                font-size: 11px;
            }}
            .label-col {{
                text-align: left;
                color: #555;
                width: 60%;
            }}
            .value-col {{
                text-align: right;
                color: #000;
                font-weight: bold;
                width: 40%;
            }}
        </style>
        </head>
        <body>
            <div class="header-box">
                <div class="header-title">SIMULATION RESULTS SUMMARY</div>
            </div>
            
            <div class="section">
                <div class="section-title">📊 PERFORMANCE METRICS</div>
                <table>
                    <tr>
                        <td class="label-col">Max Speed:</td>
                        <td class="value-col">{stats['max_speed_kmh']:.2f} km/h</td>
                    </tr>
                    <tr>
                        <td class="label-col">Avg Speed:</td>
                        <td class="value-col">{stats['avg_speed_kmh']:.2f} km/h</td>
                    </tr>
                    <tr>
                        <td class="label-col">Max Acceleration:</td>
                        <td class="value-col">{stats['max_acceleration']:.2f} m/s²</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <div class="section-title">⚙️ MOTOR PERFORMANCE</div>
                <table>
                    <tr>
                        <td class="label-col">Max Motor RPM:</td>
                        <td class="value-col">{stats['max_motor_rpm']:.0f} RPM</td>
                    </tr>
                    <tr>
                        <td class="label-col">Max Motor Torque:</td>
                        <td class="value-col">{stats['max_motor_torque']:.2f} Nm</td>
                    </tr>
                    <tr>
                        <td class="label-col">Max Motor Power:</td>
                        <td class="value-col">{stats['max_motor_power_kw']:.2f} kW</td>
                    </tr>
                    <tr>
                        <td class="label-col">Avg Motor Power:</td>
                        <td class="value-col">{stats['avg_power_kw']:.2f} kW</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <div class="section-title">🔋 ENERGY & EFFICIENCY</div>
                <table>
                    <tr>
                        <td class="label-col">Total Distance:</td>
                        <td class="value-col">{stats['total_distance_km']:.3f} km</td>
                    </tr>
                    <tr>
                        <td class="label-col">Total Energy:</td>
                        <td class="value-col">{stats['total_energy_kwh']:.4f} kWh</td>
                    </tr>
                    <tr>
                        <td class="label-col">Energy per km:</td>
                        <td class="value-col">{stats['energy_per_km_wh']:.2f} Wh/km</td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """
        self.results_text.setHtml(results)
        
        self.run_btn.setEnabled(True)
        self.statusBar().showMessage('Simulation completed successfully!')
    
    def export_results(self):
        """Export simulation results to CSV"""
        if not self.engine.history['time']:
            QMessageBox.warning(self, 'No Data', 'Please run a simulation first!')
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, 'Export Results', '', 'CSV Files (*.csv);;All Files (*)'
        )
        
        if filename:
            df = pd.DataFrame(self.engine.history)
            df.to_csv(filename, index=False)
            QMessageBox.information(self, 'Success', f'Results exported to {filename}')
            self.statusBar().showMessage(f'Exported to {filename}')
    
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
        
        self.statusBar().showMessage('EV parameters reset to defaults')
    
    def reset_ugv_defaults(self):
        """Reset UGV parameters to default values"""
        # Physical Parameters
        self.ugv_cd_input.setValue(0.8)
        self.ugv_cr_input.setValue(0.02)
        self.ugv_wheel_radius_input.setValue(0.2795)
        self.ugv_air_density_input.setValue(1.164)
        self.ugv_frontal_area_input.setValue(0.5)
        
        # Drivetrain Parameters
        self.ugv_gear_ratio_input.setValue(5.221)
        self.ugv_gear_efficiency_input.setValue(95.0)
        self.ugv_motor_efficiency_input.setValue(85.0)
        self.ugv_motor_base_rpm_input.setValue(500)
        
        # Weight Parameters
        self.ugv_kerb_weight_input.setValue(150.0)
        self.ugv_passenger_weight_input.setValue(0.0)
        self.ugv_gvw_input.setValue(150.0)
        self.ugv_motor_controller_weight_input.setValue(0.0)
        self.ugv_battery_weight_input.setValue(0.0)
        self.ugv_vehicle_weight_input.setValue(150.0)
        self.ugv_other_weights_input.setValue(0.0)
        self.ugv_generator_weight_input.setValue(0.0)
        
        # Battery Parameters
        self.ugv_battery_req_input.setCurrentText('Lithium')
        self.ugv_battery_chem_input.setCurrentText('NCM')
        self.ugv_battery_voltage_input.setValue(24.0)
        self.ugv_weight_per_wh_input.setValue(0.0)
        self.ugv_peukert_input.setValue(1.05)
        self.ugv_discharge_hr_input.setValue(2.0)
        self.ugv_dod_input.setValue(100.0)
        self.ugv_battery_current_input.setValue(53.0)
        self.ugv_true_capacity_wh_input.setValue(1789.0)
        self.ugv_true_capacity_ah_input.setValue(75.0)
        self.ugv_tentative_ah_input.setValue(76.0)
        self.ugv_tentative_wh_input.setValue(1820.0)
        self.ugv_battery_weight_total_input.setValue(12.0)
        
        # Performance Parameters
        self.ugv_rotary_inertia_input.setValue(1.06)
        self.ugv_max_speed_input.setValue(50.0)
        self.ugv_slope_speed_input.setValue(5.0)
        self.ugv_gradeability_input.setValue(30.0)
        self.ugv_accel_end_speed_input.setValue(50.0)
        self.ugv_accel_period_input.setValue(5.0)
        self.ugv_vehicle_range_input.setValue(70.0)
        
        # UGV-Specific Parameters
        self.ugv_step_height_input.setValue(0.1)
        self.ugv_num_wheels_input.setValue(4)
        self.ugv_num_powered_wheels_input.setValue(2)
        self.ugv_load_per_wheel_input.setValue(37.5)
        self.ugv_torque_climb_input.setValue(36.75)
        self.ugv_track_width_input.setValue(0.6)
        self.ugv_skid_coefficient_input.setValue(0.7)
        self.ugv_spin_angular_rad_input.setValue(0.5)
        self.ugv_spin_angular_deg_input.setValue(28.6479)
        
        self.statusBar().showMessage('UGV parameters reset to defaults')
    
    def reset_simulation(self):
        """Reset simulation and parameters to defaults"""
        self.engine.reset()
        self.results_text.clear()
        
        # Reset simulation parameters to defaults
        self.duration_input.setValue(90)
        self.speed_input.setValue(150)  # High default for continuous acceleration
        self.gradient_input.setValue(0)
        self.mode_combo.setCurrentIndex(0)  # boost
        
        # Clear plots
        for canvas in [self.speed_canvas, self.power_canvas, 
                      self.forces_canvas, self.motor_canvas, self.energy_canvas]:
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
