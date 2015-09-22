import serial
import re

#\d+(\.\d{1,5})?

port = '/dev/ttyACM0'
frequency = 9600

ser = serial.Serial(port, frequency)
while True:
    if ser.inWaiting():
        print ser.readline(ser.inWaiting())
