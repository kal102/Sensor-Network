"""
sensor.py: libary used as an abstraction layer for sensors in this project.
Provides two public methods, init() and read(), using list of sensors as an argument.
Based on it imports necessary drivers, initializes sensors and reads data.
"""

import logger

GPS_UART = 2

DS18B20_PIN = 25
GPS_TX_PIN  = 26
GPS_RX_PIN  = 27

ds18b20 = None
gps = None

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
    global ds18b20, gps

    if 'ds18b20' in sensors:
        from drivers.ds18b20 import DS18B20
        ds18b20 = DS18B20(DS18B20_PIN)
    if 'gps' in sensors:
        from drivers.gps import GPS
        gps = GPS(uart_if=GPS_UART, tx=GPS_TX_PIN, rx=GPS_RX_PIN)

# Function for reading data from sensors
def read(sensors):
    """Function for reading data from sensors."""
    status = "ok"
    data = {}
    temperature = 0.0
    latitude = ''
    longitude = ''

    global ds18b20, gps

    if 'ds18b20' in sensors:
        try:
            temperature = ds18b20.read()
            status = __merge_status(status, ds18b20.status)
        except ImportError:
            logger.error('DS18B20 is not initialized')
    if 'gps' in sensors:
        try:
            latitude, longitude = gps.read()
            status = __merge_status(status, gps.status)
        except ImportError:
            logger.error('GPS is not initialized')
    if not sensors:
        status = __merge_status(status, "no sensors")

    data['temp'] = temperature
    data['lati'] = latitude
    data['long'] = longitude

    return (status, data)
