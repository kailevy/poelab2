"""This script interacts with the arduino poelab2.ino to generate a 3d plot"""

import serial
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import time

port = '/dev/ttyACM0'
frequency = 9600
y_threshold = 40
noise_thresh = 60

class Plotter(object):
    """Class to handle plotting and interactions with arduino"""
    def __init__(self):
        """Plotting set up"""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlim3d(-80,80)
        self.ax.set_ylim3d(0,80)
        self.ax.set_zlim3d(0,80)
        self.ax.set_xlabel('X Distance (cm)')
        self.ax.set_ylabel('Y Distance (cm)')
        self.ax.set_zlabel('Z Distance (cm)')
        plt.title('3D Scanner!')
        plt.ion()
        plt.show()

    def prepare_data(self,data):
        """Function to prepare the scanning data"""
        tilt_data = [point[0] for point in data]
        pan_data = [point[1] for point in data]
        scan_distances = []
        # Average three distance readings
        for point in data:
            scan_distances.append(self.average_readings(point[2:]))
        # Converts to cm
        scan_distances = self.convert_distance(scan_distances)
        # Remove readings over (noise)
        for index,distance in enumerate(scan_distances):
            if distance > noise_thresh:
                del tilt_data[index]
                del pan_data[index]
                del scan_distances[index]
        return [tilt_data,pan_data,scan_distances]

    def convert_distance(self,scan_distances):
        """Uses calibration function to convert from voltage reading to distance"""
        return [-30.5064 * np.log(0.00123381 * (-97 + scan)) for scan in scan_distances]

    def average_readings(self,multi_readings):
        """Averages multiple readings"""
        tmp_tot = 0
        for r in multi_readings:
            tmp_tot += r
        return tmp_tot/len(multi_readings)

    def convert_to_cartesian(self,scan):
        """Converts spherical coordinates to cartesian"""
        th = np.radians(np.subtract(180,scan[0]))
        ph = np.radians(scan[1])
        x = np.multiply(scan[2],np.multiply(np.sin(th),np.cos(ph)))
        y = np.multiply(scan[2],np.multiply(np.sin(th),np.sin(ph)))
        z = np.multiply(scan[2],np.cos(th))
        return [x,y,z]

    def colorcode(self,scans):
        """Color codes points, sets blue if y distance is greater than threshold"""
        colors = []
        for scan in scans:
            if scan > y_threshold:
                colors.append('b')
            else:
                colors.append('r')
        return colors

    def graph_3d(self,data):
        """Calls data preparation functions and the plots"""
        data = self.prepare_data(data)
        data = self.convert_to_cartesian(data)
        color = self.colorcode(data[1])
        self.ax.scatter(data[0],data[1],data[2],s=10,c=color)
        plt.pause(0.001)


    def graph_2d(self,data):
        """Deprecated function for visualizing readings in 2d"""
        plt.ylabel('Distance Reading (cm)')
        plt.xlabel('Pan degree')
        data = self.prepare_data(data)
        plt.plot(data[1],data[2],'ro')
        self.fig.canvas.draw()
        raw_input("Press enter to exit")


if __name__ == '__main__':
    data = []
    # Series of raw_inputs to make user interact with script
    raw_input("Ensure that the scanner is connected")
    # Initiates serial connection and pauses to ensure it connects
    ser = serial.Serial(port, frequency, timeout=2)
    print "Please wait while I connect..."
    time.sleep(2)
    raw_input("Press enter to start")
    start = True
    # Instantiates plotter
    p = Plotter()
    # To remove leftover serial data
    ser.readline()
    # Functional loop
    while True:
        # Writes on serial to tell arduino to go ahead
        if start:
            ser.write("START")
        # If there is any data, it stops putting out serial output and reads it
        if ser.inWaiting():
            start = False
            reading = ser.readline()
            # "b" from arduino signals end of scanning
            if "b" in reading:
                raw_input("Press enter to exit")
                break
            # "a" from arduino signals one complete sweep, so it plots the data, clears it, and sends a start signal again
            if "a" in reading:
                p.graph_3d(data)
                data = [];
                start = True
            # Otherwise, it reads the data and adds it to a list
            else:
                data += [[int(r) for r in reading.strip().split(',')]]
                # print data
