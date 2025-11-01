"""
EV Power Train Simulation Tool - Main Application
Desktop GUI application for simulating EV performance
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QGroupBox, QGridLayout, QTabWidget,
                             QTextEdit, QFileDialog, QMessageBox, QProgressBar,
                             QDoubleSpinBox, QSpinBox)
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
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle('EV Power Train Simulation Tool')
        self.setGeometry(100, 100, 1400, 900)

        # Set application icon
        icon_path = 'ePropelled Logo.jpg'
        app_icon = QIcon(icon_path)
        self.setWindowIcon(app_icon)
    
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Visualization
        right_panel = self.create_visualization_panel()
        main_layout.addWidget(right_panel, 2)
        
        self.statusBar().showMessage('Ready')
    
    def create_control_panel(self):
        """Create left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel('EV Power Train Simulator')
        title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Simulation Parameters
        sim_group = QGroupBox('Simulation Parameters')
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
        self.speed_input.setRange(0, 120)
        self.speed_input.setValue(85)
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
        
        sim_group.setLayout(sim_layout)
        layout.addWidget(sim_group)
        
        # Vehicle Parameters
        vehicle_group = QGroupBox('Vehicle Parameters')
        vehicle_layout = QGridLayout()
        
        # Drag Coefficient
        vehicle_layout.addWidget(QLabel('Drag Coeff (Cd):'), 0, 0)
        self.cd_input = QDoubleSpinBox()
        self.cd_input.setRange(0.1, 2.0)
        self.cd_input.setSingleStep(0.01)
        self.cd_input.setValue(self.params.drag_coefficient)
        vehicle_layout.addWidget(self.cd_input, 0, 1)
        
        # Rolling Resistance
        vehicle_layout.addWidget(QLabel('Rolling Resist (Cr):'), 1, 0)
        self.cr_input = QDoubleSpinBox()
        self.cr_input.setRange(0.001, 0.1)
        self.cr_input.setSingleStep(0.001)
        self.cr_input.setValue(self.params.rolling_resistance)
        self.cr_input.setDecimals(3)
        vehicle_layout.addWidget(self.cr_input, 1, 1)
        
        # Vehicle Mass
        vehicle_layout.addWidget(QLabel('Mass (kg):'), 2, 0)
        self.mass_input = QDoubleSpinBox()
        self.mass_input.setRange(50, 500)
        self.mass_input.setValue(self.params.vehicle_mass)
        vehicle_layout.addWidget(self.mass_input, 2, 1)
        
        # Frontal Area
        vehicle_layout.addWidget(QLabel('Frontal Area (m²):'), 3, 0)
        self.area_input = QDoubleSpinBox()
        self.area_input.setRange(0.1, 5.0)
        self.area_input.setSingleStep(0.1)
        self.area_input.setValue(self.params.frontal_area)
        vehicle_layout.addWidget(self.area_input, 3, 1)
        
        vehicle_group.setLayout(vehicle_layout)
        layout.addWidget(vehicle_group)
        
        # Quick Scenarios
        scenario_group = QGroupBox('Quick Scenarios')
        scenario_layout = QVBoxLayout()
        
        flat_btn = QPushButton('Flat Terrain (0°)')
        flat_btn.setStyleSheet('padding: 6px; background-color: #E3F2FD; border: 1px solid #90CAF9; border-radius: 3px;')
        flat_btn.clicked.connect(lambda: self.load_scenario('flat'))
        scenario_layout.addWidget(flat_btn)
        
        hill_btn = QPushButton('Moderate Hill (15°)')
        hill_btn.setStyleSheet('padding: 6px; background-color: #FFF3E0; border: 1px solid #FFCC80; border-radius: 3px;')
        hill_btn.clicked.connect(lambda: self.load_scenario('hill'))
        scenario_layout.addWidget(hill_btn)
        
        steep_btn = QPushButton('Steep Climb (60°)')
        steep_btn.setStyleSheet('padding: 6px; background-color: #FFEBEE; border: 1px solid #FFAB91; border-radius: 3px;')
        steep_btn.clicked.connect(lambda: self.load_scenario('steep'))
        scenario_layout.addWidget(steep_btn)
        
        scenario_group.setLayout(scenario_layout)
        layout.addWidget(scenario_group)
        
        # Control Buttons
        btn_layout = QVBoxLayout()
        
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
        
        layout.addLayout(btn_layout)
        
        # Results Summary
        results_group = QGroupBox('Results Summary')
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(200)
        results_layout.addWidget(self.results_text)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        layout.addStretch()
        
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
        elif scenario_type == 'hill':
            self.gradient_input.setValue(15)
            self.speed_input.setValue(60)
            self.duration_input.setValue(120)
        elif scenario_type == 'steep':
            self.gradient_input.setValue(60)
            self.speed_input.setValue(55)
            self.duration_input.setValue(180)
        
        self.statusBar().showMessage(f'Loaded {scenario_type} terrain scenario')
    
    def update_parameters(self):
        """Update engine parameters from UI"""
        self.params.drag_coefficient = self.cd_input.value()
        self.params.rolling_resistance = self.cr_input.value()
        self.params.vehicle_mass = self.mass_input.value()
        self.params.frontal_area = self.area_input.value()
        self.engine = EVSimulationEngine(self.params)
    
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
    
    def reset_simulation(self):
        """Reset simulation and parameters to defaults"""
        self.engine.reset()
        self.results_text.clear()
        
        # Reset simulation parameters to defaults
        self.duration_input.setValue(90)
        self.speed_input.setValue(85)
        self.gradient_input.setValue(0)
        self.mode_combo.setCurrentIndex(0)  # boost
        
        # Reset vehicle parameters to defaults
        default_params = VehicleParameters()
        self.cd_input.setValue(default_params.drag_coefficient)
        self.cr_input.setValue(default_params.rolling_resistance)
        self.mass_input.setValue(default_params.vehicle_mass)
        self.area_input.setValue(default_params.frontal_area)
        
        # Clear plots
        for canvas in [self.speed_canvas, self.power_canvas, 
                      self.forces_canvas, self.motor_canvas, self.energy_canvas]:
            canvas.fig.clear()
            canvas.draw()
        
        self.statusBar().showMessage('Simulation and parameters reset to defaults')


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
