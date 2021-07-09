import time
import machine
import onewire, ds18x20
import logger

class DS18B20:
    status = "ok"
    ds = None
    roms = []

    def __init__(self, pin = 12):
        """Initializes OneWire and scans devices on the bus. Default args:
            pin = 12"""

        # create the onewire object
        dat = machine.Pin(pin)
        self.ds = ds18x20.DS18X20(onewire.OneWire(dat))

        # scan for devices on the bus
        self.roms = self.ds.scan()
        logger.info('Found DS18B20 sensors: %d' % len(self.roms))
        
    def read(self, rom_idx = 0):
        """Reads temperature from sensor of the given index. Default args:
            rom_idx = 0"""

        self.status = "ok"
        temperature = 0.0

        # get sensor handle
        try:
            rom = self.roms[rom_idx]
        except IndexError:
            logger.error("DS18B20 not available")
            self.status  = "ds18b20 error"
            return temperature

        # check null pointers
        if rom == None:
            logger.error('No DS18B20 available')
            self.status  = "ds18b20 error"
            return temperature
        if self.ds == None:
            logger.error('DS18B20 not initialized')
            self.status  = "ds18b20 error"
            return temperature
        
        # read temperature
        try:
            self.ds.convert_temp()
            time.sleep_ms(750)
            temperature = self.ds.read_temp(rom)
            return temperature
        except OneWireError:
            logger.error('OneWire error')
            self.status  = "ds18b20 error"
            return temperature
