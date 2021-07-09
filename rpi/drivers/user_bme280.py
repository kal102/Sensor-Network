import smbus2
import bme280

def get():

    global status
    port = 1
    address = 0x76
    bus = smbus2.SMBus(port)

    try:
        status = "ok"
        calibration_params = bme280.load_calibration_params(bus, address)
    except OSError:
        status = "bme280 error"
        return (0.0, 0.0, 0.0)

    # the sample method will take a single reading and return a
    # compensated_reading object
    data = bme280.sample(bus, address, calibration_params)

    # the compensated_reading class has the following attributes
    # print(data.id)
    # print(data.timestamp)
    # print(data.temperature)
    # print(data.pressure)
    # print(data.humidity)

    # there is a handy string representation too
    # print(data)

    return (data.temperature, data.humidity, data.pressure)
