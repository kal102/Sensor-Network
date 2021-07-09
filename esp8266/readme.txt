Program for ESP8266 that transfers data from sensors to the database.

There are two bash scripts in the directory:
- load.sh - loads the program, sending files defined in files.txt to the device's memory
- connect.sh - connects to the device's REPL via the serial port

The device configures the config.json file, where you should set the device name, a special device password, WiFi network login details and the time zone.
By setting the SLEEP flag to 1 in it, you can significantly reduce the power consumption between sending data.