from codrone_edu.drone import *
from collections import deque
import time

sensorData = deque() # Hold the sensor data
sensorDataHeaders = ('temperature', 'pressure', 'elevation',
                     'roll', 'pitch', 'yaw', 'accel_x', 'accel_y', 'accel_z',
                     'angle_x', 'angle_y', 'angle_z', 'angular_speed_x',
                     'angular_speed_y', 'angular_speed_y'
                     'bottom_range', 'height',
                     'front_range', 'wall',
                     'pos_x', 'pos_y', 'pox_z', 'flow_velocity_x', 'flow_velocity_y',
                     'color',
                     'battery', 'flight_state', 'movement-state')

def getSensorData(d):
    # Temperature & Pressure Sensor (a.k.a Barometer)
    d_temp = d.get_drone_temperature()
    d_pressure = d.get_pressure()
    d_elevation = d.get_elevation()

    # Gyroscope & Accelerometer Sensors
    d_roll = d.get_angle_x()
    d_pitch = d.get_angle_y()
    d_yaw = d.get_angle_z()
    d_accel_x = d.get_accel_x()
    d_accel_y = d.get_accel_y()
    d_accel_z = d.get_accel_z()
    d_angle_x = d.get_angle_x()
    d_angle_y = d.get_angle_y()
    d_angle_z = d.get_angle_z()
    d_angular_speed_x = d.get_angular_speed_x()
    d_angular_speed_y = d.get_angular_speed_y()
    d_angular_speed_z = d.get_angular_speed_z()

    # Bottom Range Sensor
    d_bottom = d.get_bottom_range()
    d_height = d.get_height()

    # Front Range Sensor
    d_front = d.get_front_range()
    d_wall = d.detect_wall()
    
    # Optical Flow Sensor
    d_pos_x = d.get_pos_x()
    d_pos_y = d.get_pos_y()
    d_pos_z = d.get_pos_z()
    d_flow_velocity_x = d.get_flow_velocity_x()
    d_flow_velocity_y = d.get_flow_velocity_y()

    # Color Sensor
    d_color = d.get_color_data()

    # State Data Sensor
    d_battery = d.get_battery()
    d_flight_state = d.get_flight_state()
    d_movement_state = d.get_movement_state()

    sensorData.append((d_temp, d_pressure, d_elevation,
                       d_roll, d_pitch, d_yaw, d_accel_x, d_accel_y, d_accel_z, d_angle_x, 
                       d_angle_y, d_angle_z, d_angular_speed_x, d_angular_speed_y, d_angular_speed_z,
                       d_bottom, d_height, 
                       d_front, d_wall,
                       d_pos_x, d_pos_y, d_pos_z, d_flow_velocity_x, d_flow_velocity_y,
                       d_color,
                       d_battery, d_flight_state, d_movement_state))

def printSensorData():
    print(sensorData[-1])

drone = Drone()
drone.connect()

end_time = time.time() + 60 # How long the drone collects data for in seconds, adjust as needed

print(sensorDataHeaders)

while time.time() < end_time:
    getSensorData(drone)
    printSensorData()

drone.disconnect()