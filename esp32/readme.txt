Program for ESP32, which sends data from sensors to the database, also provides an HTTP server with a simple website, device configuration, sending commands and reading the log.

There are three bash scripts in the directory:
- flash.sh - clears ESP32 memory and loads Micropython
- load.sh - loads the program, sending files defined in files.txt to the device's memory
- connect.sh - connects to the device's REPL via the serial port

The device configures the config.json file, where you should set the device name, a special device password, WiFi network login details and the time zone.
After the first loading of the program, run the setup.py script to install additional packages (you must first set the WiFi network parameters in the configuration).
The script is run by importing the sender module and running its run() method, you can also start the server itself similarly after importing it by calling the run() method.