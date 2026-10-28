from CoDrone.codrone import *
from CoDrone.protocol import *
from CoDrone.system import *



# Send the code a request to the drone   
drone = Drone()
drone.connect()

# Getting the data from the drone
while True:

    # Getting the 3 gyroscope angles
    x_angle = drone.get_gyro_x()
    y_angle = drone.get_gyro_y()
    z_angle = drone.get_gyro_z() 
    # Getting Front Range
    front_range = drone.get_front_range()
    back_range = drone.get_back_range()


    #now print the values for the sensor data
    # Barometer/ Gyroscope
    print(x_angle)
    print(y_angle)
    print(z_angle)
    # Front Range and Bottom Range
    print(front_range)
    print(back_range)

drone.disconnect()