"""
EV Power Train Simulation Engine
Handles all physics calculations and simulation logic
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
import math


@dataclass
class VehicleParameters:
    """Vehicle configuration parameters"""
    # Aerodynamic parameters
    drag_coefficient: float = 0.8  # Cd
    rolling_resistance: float = 0.0214  # Cr (corrected from spreadsheet analysis)
    air_density: float = 1.164  # kg/m³
    frontal_area: float = 0.5  # m²
    
    # Mechanical parameters
    wheel_radius: float = 0.2795  # m
    gear_ratio: float = 5.268  # Updated to match DCE simulation (was 4.960)
    vehicle_mass: float = 160.4  # kg (corrected from spreadsheet analysis)
    
    # Motor parameters
    num_motors: int = 2
    max_torque_per_motor_eco: float = 37.0  # Nm
    max_torque_per_motor_boost: float = 52.0  # Nm
    base_rpm: float = 258.0  # RPM at which constant power region begins (calculated from P=T*ω)
    max_motor_rpm: float = 2500.0  # Updated to match DCE simulation (was 2746.0)
    max_power_eco: float = 4000.0  # W (2000W per motor × 2 motors)
    max_power_boost: float = 22000.0  # W
    
    # Gravity
    gravity: float = 9.81  # m/s²


@dataclass
class SimulationState:
    """Current state of the simulation"""
    time: float = 0.0
    speed: float = 0.0  # m/s
    acceleration: float = 0.0  # m/s²
    motor_rpm: float = 0.0
    motor_torque: float = 0.0  # Nm (total)
    motor_power: float = 0.0  # W
    distance: float = 0.0  # m
    energy_consumed: float = 0.0  # Wh


class EVSimulationEngine:
    """Main simulation engine for EV power train"""
    
    def __init__(self, params: VehicleParameters):
        self.params = params
        self.reset()
    
    def reset(self):
        """Reset simulation to initial state"""
        self.state = SimulationState()
        self.history = {
            'time': [],
            'speed_ms': [],
            'speed_kmh': [],
            'motor_rpm': [],
            'motor_torque': [],
            'motor_power': [],
            'tractive_force': [],
            'rolling_resistance': [],
            'drag_force': [],
            'climbing_force': [],
            'total_resistance': [],
            'net_force': [],
            'acceleration': [],
            'distance': [],
            'energy': []
        }
    
    def calculate_motor_rpm(self, speed_ms: float) -> float:
        """Calculate motor RPM from vehicle speed
        Excel Formula: RPM = (Speed*GearRatio)/(2*3.1415*WheelRadius*0.001*60)
        Note: In Excel, WheelRadius is in meters, and 0.001 is used in a different context
        Correct interpretation: RPM = (Speed_kmh * GearRatio) / (2 * 3.1415 * WheelRadius * 60)
        where WheelRadius is in meters and Speed is in km/h
        """
        if speed_ms <= 0:
            return 0.0
        # Convert m/s to km/h for Excel formula
        speed_kmh = speed_ms * 3.6
        # Corrected Excel formula interpretation:
        # RPM = (Speed_kmh * GearRatio) / (2 * π * WheelRadius_m * 60)
        # This gives wheel speed, then multiply by gear ratio for motor RPM
        # Actually: Motor_RPM = Wheel_RPM * GearRatio
        # Wheel_RPM = (Linear_Speed_m/s) / (2 * π * WheelRadius_m) * 60
        wheel_rpm = (speed_ms / (2 * 3.1415 * self.params.wheel_radius)) * 60
        motor_rpm = wheel_rpm * self.params.gear_ratio
        return min(motor_rpm, self.params.max_motor_rpm)
    
    def calculate_rolling_resistance(self, gradient_deg: float) -> float:
        """Calculate rolling resistance force
        Excel Formula: Froll(N) = Cr*(KerbWeight+LoadWeight)*9.8
        """
        # Excel formula uses simplified version without cos(angle)
        # Froll = Cr * (KerbWeight + LoadWeight) * 9.8
        F_roll = self.params.rolling_resistance * self.params.vehicle_mass * 9.8
        return F_roll
    
    def calculate_drag_force(self, speed_ms: float) -> float:
        """Calculate aerodynamic drag force
        Excel Formula: Fdrag(N) = Cd*Density*Area*Speed*Speed*0.03858025308642
        Where 0.03858025308642 = 0.5/(3.6^2) for km/h input
        """
        # Convert m/s to km/h for Excel formula
        speed_kmh = speed_ms * 3.6
        # Excel formula: Fdrag = Cd * Density * Area * Speed_kmh^2 * 0.03858025308642
        F_drag = (self.params.drag_coefficient * 
                  self.params.air_density * 
                  self.params.frontal_area * 
                  speed_kmh * speed_kmh * 0.03858025308642)
        return F_drag
    
    def calculate_climbing_force(self, gradient_deg: float) -> float:
        """Calculate climbing resistance force
        Excel Formula: FClimb(N) = (KerbWeight+LoadWeight)*9.8*SIN(Angle*0.01745329)
        Where 0.01745329 = π/180 (degrees to radians)
        """
        # Excel formula: FClimb = (KerbWeight + LoadWeight) * 9.8 * sin(Angle * 0.01745329)
        F_climb = (self.params.vehicle_mass * 
                   9.8 * 
                   math.sin(gradient_deg * 0.01745329))
        return F_climb
    
    def calculate_tractive_force(self, motor_torque: float) -> float:
        """Calculate tractive force from motor torque"""
        F_tractive = (motor_torque * 
                      self.params.gear_ratio / 
                      self.params.wheel_radius)
        return F_tractive
    
    def calculate_acceleration_terms_excel(self, acc_speed_kmh: float, acc_time: float, inertia: float = 1.1) -> tuple:
        """Calculate acceleration terms using exact Excel formulas
        
        Excel Formulas:
        Term1 = ((Inertia*GVW)/(2*AccTime))*((AccSpeed*0.277777777777777)^2)+((AccSpeed*0.277777777777777)^2))
        Term2 = (Density*Cd*Area*(AccSpeed*0.277777777777777)*(AccSpeed*0.277777777777777)*(AccSpeed*0.277777777777777))/5
        Term3 = (2*Cr*GVW*9.8*(AccSpeed*0.277777777777777))/3
        
        Args:
            acc_speed_kmh: Acceleration end speed in km/h
            acc_time: Acceleration time in seconds
            inertia: Inertia factor (default 1.1)
        
        Returns:
            Tuple of (Term1, Term2, Term3)
        """
        # Convert km/h to m/s: 0.277777777777777 = 1/3.6
        acc_speed_ms = acc_speed_kmh * 0.277777777777777
        gvw = self.params.vehicle_mass
        
        # Term1: Inertial component
        term1 = ((inertia * gvw) / (2 * acc_time)) * (
            (acc_speed_ms ** 2) + (acc_speed_ms ** 2)
        )
        
        # Term2: Aerodynamic component
        term2 = (self.params.air_density * self.params.drag_coefficient * 
                 self.params.frontal_area * acc_speed_ms * acc_speed_ms * acc_speed_ms) / 5
        
        # Term3: Rolling resistance component
        term3 = (2 * self.params.rolling_resistance * gvw * 9.8 * acc_speed_ms) / 3
        
        return term1, term2, term3
    
    def calculate_required_power_for_acceleration_excel(self, acc_speed_kmh: float, acc_time: float, 
                                                        gear_efficiency: float = 0.95, 
                                                        motor_efficiency: float = 0.90,
                                                        inertia: float = 1.1) -> float:
        """Calculate required power for acceleration using exact Excel formula
        
        Excel Formula:
        Required Power for Acceleration = (Term1+Term2+Term3)/(GearEfficency*MotorEfficiency)
        
        Args:
            acc_speed_kmh: Acceleration end speed in km/h
            acc_time: Acceleration time in seconds
            gear_efficiency: Gear efficiency (0.95 = 95%)
            motor_efficiency: Motor efficiency (0.90 = 90%)
            inertia: Inertia factor (default 1.1)
        
        Returns:
            Required power in Watts
        """
        term1, term2, term3 = self.calculate_acceleration_terms_excel(acc_speed_kmh, acc_time, inertia)
        required_power = (term1 + term2 + term3) / (gear_efficiency * motor_efficiency)
        return required_power
    
    def calculate_motor_torque_with_curve(self, rpm: float, mode: str = 'boost') -> float:
        """
        Calculate motor torque with constant torque/constant power regions
        Implements: Torque = IF((RPM<BaseRPM), (ConstantTorque), ((ConstantPower*60)/(2*PI()*RPM))) * 2
        
        Args:
            rpm: Motor RPM
            mode: 'eco' or 'boost'
        
        Returns:
            Total motor torque (Nm) for all motors
        """
        # Motor parameters based on mode
        if mode == 'boost':
            constant_torque_per_motor = self.params.max_torque_per_motor_boost  # 52 Nm
            constant_power = self.params.max_power_boost  # 22000 W
        else:  # eco mode
            constant_torque_per_motor = self.params.max_torque_per_motor_eco  # 37 Nm
            constant_power = self.params.max_power_eco  # 4000 W
        
        base_rpm = self.params.base_rpm
        num_motors = self.params.num_motors
        
        # Piecewise torque calculation
        if rpm <= base_rpm:
            # Constant torque region (below, at, or starting from 0 RPM)
            # At startup (rpm=0), motor provides full constant torque
            total_torque = constant_torque_per_motor * num_motors
        else:
            # Constant power region (above base RPM): T = (P * 60) / (2π * RPM)
            # Power is distributed among motors
            torque_per_motor = (constant_power / num_motors * 60) / (2 * math.pi * rpm)
            total_torque = torque_per_motor * num_motors
        
        return total_torque
    
    def calculate_required_torque(self, target_speed: float, gradient_deg: float, mode: str, current_rpm: float = 0) -> float:
        """
        Calculate required motor torque to maintain/reach target speed
        Uses piecewise torque curve (constant torque/constant power regions)
        
        Args:
            target_speed: Target speed in m/s
            gradient_deg: Road gradient in degrees
            mode: 'eco' or 'boost'
            current_rpm: Current motor RPM (for torque curve lookup)
        
        Returns:
            Motor torque limited by motor capability curve
        """
        # Get maximum available torque from motor curve at current RPM
        max_available_torque = self.calculate_motor_torque_with_curve(current_rpm, mode)
        
        # If accelerating, use full available motor torque for maximum acceleration
        if target_speed > self.state.speed:
            return max_available_torque
        
        # If at target speed, calculate torque needed to overcome resistance
        F_roll = self.calculate_rolling_resistance(gradient_deg)
        F_drag = self.calculate_drag_force(self.state.speed)
        F_climb = self.calculate_climbing_force(gradient_deg)
        F_total_resistance = F_roll + F_drag + F_climb
        
        # Calculate required torque from resistance forces
        required_torque = (F_total_resistance * 
                          self.params.wheel_radius / 
                          self.params.gear_ratio)
        
        # Return the minimum of required and available torque
        return min(required_torque, max_available_torque)
    
    def step(self, dt: float, target_speed_kmh: float, gradient_deg: float, mode: str = 'boost'):
        """
        Perform one simulation step
        
        Args:
            dt: Time step in seconds
            target_speed_kmh: Target speed in km/h
            gradient_deg: Road gradient in degrees
            mode: 'eco' or 'boost'
        """
        target_speed_ms = target_speed_kmh / 3.6
        
        # Calculate current motor RPM based on current speed
        current_motor_rpm = self.calculate_motor_rpm(self.state.speed)
        
        # Calculate motor torque needed (limited by motor curve at current RPM)
        motor_torque = self.calculate_required_torque(target_speed_ms, gradient_deg, mode, current_motor_rpm)
        
        # Calculate forces
        F_tractive = self.calculate_tractive_force(motor_torque)
        F_roll = self.calculate_rolling_resistance(gradient_deg)
        F_drag = self.calculate_drag_force(self.state.speed)
        F_climb = self.calculate_climbing_force(gradient_deg)
        F_total_resistance = F_roll + F_drag + F_climb
        
        # Calculate net force and acceleration
        F_net = F_tractive - F_total_resistance
        acceleration = F_net / self.params.vehicle_mass
        
        # Update speed (limit to target speed)
        new_speed = self.state.speed + acceleration * dt
        if acceleration > 0:
            new_speed = min(new_speed, target_speed_ms)
        else:
            new_speed = max(new_speed, 0)
        
        # Update motor RPM based on new speed
        motor_rpm = self.calculate_motor_rpm(new_speed)
        
        # Calculate motor power
        motor_angular_velocity = motor_rpm * 2 * math.pi / 60  # rad/s
        motor_power = motor_torque * motor_angular_velocity  # W
        
        # Limit power to motor capabilities
        max_power = (self.params.max_power_boost if mode == 'boost' 
                    else self.params.max_power_eco)
        motor_power = min(motor_power, max_power)
        
        # Update distance
        distance_increment = (self.state.speed + new_speed) / 2 * dt
        
        # Update energy (Wh)
        energy_increment = motor_power * dt / 3600  # Convert W*s to Wh
        
        # Update state
        self.state.time += dt
        self.state.speed = new_speed
        self.state.acceleration = acceleration
        self.state.motor_rpm = motor_rpm
        self.state.motor_torque = motor_torque
        self.state.motor_power = motor_power
        self.state.distance += distance_increment
        self.state.energy_consumed += energy_increment
        
        # Store history
        self.history['time'].append(self.state.time)
        self.history['speed_ms'].append(self.state.speed)
        self.history['speed_kmh'].append(self.state.speed * 3.6)
        self.history['motor_rpm'].append(motor_rpm)
        self.history['motor_torque'].append(motor_torque)
        self.history['motor_power'].append(motor_power / 1000)  # kW
        self.history['tractive_force'].append(F_tractive)
        self.history['rolling_resistance'].append(F_roll)
        self.history['drag_force'].append(F_drag)
        self.history['climbing_force'].append(F_climb)
        self.history['total_resistance'].append(F_total_resistance)
        self.history['net_force'].append(F_net)
        self.history['acceleration'].append(acceleration)
        self.history['distance'].append(self.state.distance / 1000)  # km
        self.history['energy'].append(self.state.energy_consumed / 1000)  # kWh
    
    def run_simulation(self, duration: float, target_speed_kmh: float, 
                      gradient_deg: float, mode: str = 'boost', dt: float = 0.5):
        """
        Run complete simulation
        
        Args:
            duration: Simulation duration in seconds
            target_speed_kmh: Target speed in km/h
            gradient_deg: Road gradient in degrees
            mode: 'eco' or 'boost'
            dt: Time step in seconds
        """
        self.reset()
        
        # Record initial state (t=0) to show power ramp-up from 0
        self.history['time'].append(0.0)
        self.history['speed_ms'].append(0.0)
        self.history['speed_kmh'].append(0.0)
        self.history['motor_rpm'].append(0.0)
        self.history['motor_torque'].append(0.0)
        self.history['motor_power'].append(0.0)  # kW (starts at 0)
        self.history['tractive_force'].append(0.0)
        self.history['rolling_resistance'].append(
            self.calculate_rolling_resistance(gradient_deg))
        self.history['drag_force'].append(0.0)
        self.history['climbing_force'].append(
            self.calculate_climbing_force(gradient_deg))
        self.history['total_resistance'].append(
            self.calculate_rolling_resistance(gradient_deg) + 
            self.calculate_climbing_force(gradient_deg))
        self.history['net_force'].append(0.0)
        self.history['acceleration'].append(0.0)
        self.history['distance'].append(0.0)
        self.history['energy'].append(0.0)
        
        num_steps = int(duration / dt)
        
        for _ in range(num_steps):
            self.step(dt, target_speed_kmh, gradient_deg, mode)
    
    def get_summary_stats(self) -> dict:
        """Get summary statistics from simulation"""
        if not self.history['time']:
            return {}
        
        return {
            'max_speed_kmh': max(self.history['speed_kmh']) if self.history['speed_kmh'] else 0,
            'avg_speed_kmh': np.mean(self.history['speed_kmh']) if self.history['speed_kmh'] else 0,
            'max_acceleration': max(self.history['acceleration']) if self.history['acceleration'] else 0,
            'max_motor_rpm': max(self.history['motor_rpm']) if self.history['motor_rpm'] else 0,
            'max_motor_torque': max(self.history['motor_torque']) if self.history['motor_torque'] else 0,
            'max_motor_power_kw': max(self.history['motor_power']) if self.history['motor_power'] else 0,
            'total_distance_km': self.state.distance / 1000,
            'total_energy_kwh': self.state.energy_consumed / 1000,
            'energy_per_km_wh': (self.state.energy_consumed / (self.state.distance / 1000)) 
                               if self.state.distance > 0 else 0,
            'avg_power_kw': np.mean(self.history['motor_power']) if self.history['motor_power'] else 0
        }
