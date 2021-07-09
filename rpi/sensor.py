#!/usr/bin/env python3

"""
sensor.py: libary used as abstraction layer for sensors in this project.
Provides two public methods, init() and read(), using list of sensors as an argument.
Based on it imports necessary drivers, initializes sensors and reads data.
"""

import logging

# Function for merging sensor status into one string
def __merge_status(status1, status2):
    """Function for merging sensor status into one string."""

    if status1 == "ok":
        if status2 == "ok":
            return "ok"
        else:
            return status2
    else:
        if status2 == "ok":
            return status1
        else:
            return ", ".join([status1, status2])

# Function for initializing sensors
def init(sensors):
    """Function for initializing sensors."""
    pass
    
# Function for reading data from sensors
def read(sensors):
    """Function for reading data from sensors."""
    status = "ok"
    data = {}
    temperature = 0.0
    humidity = 0.0
    pressure = 0.0

    if 'ds18b20' in sensors:
        from drivers import ds18b20
        temperature = ds18b20.get()
        status = __merge_status(status, ds18b20.status)
    if 'bme280' in sensors:
        from drivers import user_bme280
        temperature, humidity, pressure = user_bme280.get()
        status = __merge_status(status, user_bme280.status)
    if not sensors:
        status = __merge_status(status, "no sensors")

    data['temp'] = temperature
    data['humi'] = humidity
    data['pres'] = pressure

    return (status, data)
