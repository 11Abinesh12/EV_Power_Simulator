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
    rolling_resistance: float = 0.02  # Cr
    air_density: float = 1.164  # kg/m³
    frontal_area: float = 0.5  # m²
    
    # Mechanical parameters
    wheel_radius: float = 0.2795  # m
    gear_ratio: float = 5.221
    vehicle_mass: float = 150.0  # kg (estimated)
    
    # Motor parameters
    num_motors: int = 2
    max_torque_per_motor_eco: float = 37.0  # Nm
    max_torque_per_motor_boost: float = 52.0  # Nm
    max_motor_rpm: float = 2746.0
    max_power_eco: float = 4000.0  # W
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
        """Calculate motor RPM from vehicle speed"""
        if speed_ms <= 0:
            return 0.0
        # RPM = (speed / wheel_radius) * (60 / 2π) * gear_ratio
        wheel_angular_velocity = speed_ms / self.params.wheel_radius  # rad/s
        motor_angular_velocity = wheel_angular_velocity * self.params.gear_ratio
        rpm = motor_angular_velocity * 60 / (2 * math.pi)
        return min(rpm, self.params.max_motor_rpm)
    
    def calculate_rolling_resistance(self, gradient_deg: float) -> float:
        """Calculate rolling resistance force"""
        gradient_rad = math.radians(gradient_deg)
        F_roll = (self.params.rolling_resistance * 
                  self.params.vehicle_mass * 
                  self.params.gravity * 
                  math.cos(gradient_rad))
        return F_roll
    
    def calculate_drag_force(self, speed_ms: float) -> float:
        """Calculate aerodynamic drag force"""
        F_drag = (0.5 * 
                  self.params.drag_coefficient * 
                  self.params.air_density * 
                  self.params.frontal_area * 
                  speed_ms ** 2)
        return F_drag
    
    def calculate_climbing_force(self, gradient_deg: float) -> float:
        """Calculate climbing resistance force"""
        gradient_rad = math.radians(gradient_deg)
        F_climb = (self.params.vehicle_mass * 
                   self.params.gravity * 
                   math.sin(gradient_rad))
        return F_climb
    
    def calculate_tractive_force(self, motor_torque: float) -> float:
        """Calculate tractive force from motor torque"""
        F_tractive = (motor_torque * 
                      self.params.gear_ratio / 
                      self.params.wheel_radius)
        return F_tractive
    
    def calculate_required_torque(self, target_speed: float, gradient_deg: float, mode: str) -> float:
        """Calculate required motor torque to maintain/reach target speed"""
        # Calculate resistance forces
        F_roll = self.calculate_rolling_resistance(gradient_deg)
        F_drag = self.calculate_drag_force(target_speed)
        F_climb = self.calculate_climbing_force(gradient_deg)
        F_total_resistance = F_roll + F_drag + F_climb
        
        # Add acceleration force if accelerating
        if target_speed > self.state.speed:
            # Assume 2 m/s² acceleration
            F_acceleration = self.params.vehicle_mass * 2.0
            F_total_resistance += F_acceleration
        
        # Calculate required torque
        required_torque = (F_total_resistance * 
                          self.params.wheel_radius / 
                          self.params.gear_ratio)
        
        # Limit to motor capabilities
        max_torque = (self.params.max_torque_per_motor_boost if mode == 'boost' 
                     else self.params.max_torque_per_motor_eco) * self.params.num_motors
        
        return min(required_torque, max_torque)
    
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
        
        # Calculate motor torque needed
        motor_torque = self.calculate_required_torque(target_speed_ms, gradient_deg, mode)
        
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
        
        # Update motor RPM
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
