import logger
import utime as time

from machine import UART
from drivers.micropyGPS import MicropyGPS

class GPS:
    status = "ok"
    uart = None
    gps = MicropyGPS()

    def __init__(self, uart_if = 1, tx = 26, rx = 27, uart_baud = 9600, uart_buff_len = 1000):
        """Initializes UART for GPS module."""

        # Initialize UART
        self.uart = UART(uart_if, uart_baud)
        self.uart.init(uart_baud, bits=8, parity=None, stop=1, tx=tx, rx=rx, rxbuf=uart_buff_len)
        logger.info('GPS UART initialized')

    def read(self):
        """Reads and parses characters from UART buffer.
            Returns latitude and longitude strings."""

        # Check if any data is available
        if self.uart.any:

            # Clear UART RX buffer
            self.uart.read()

            # Wait 1 second for new data
            time.sleep(1)

            # Read characters from UART RX buffer
            b = self.uart.read()

            # Parse NMEA sentences with GPS library
            if b:
                for x in b:
                    if 10 <= x <= 126:
                        self.gps.update(chr(x))
            else:
                self.status = "gps error"

        # Return the most important information
        return (self.gps.latitude_string(), self.gps.longitude_string())
