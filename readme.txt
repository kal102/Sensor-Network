The repository contains a set of programs for sensor network devices that are used to record data. This data is then sent to the master server which inserts it into the database. Devices can be remotely configured, it is also possible to send commands to them and read logs thanks to the HTTP server (not applicable to ESP8266). The project consists of several main directories, each with its own readme file.

* esp32 - Micropython program for ESP32
* esp8266 - Micropython program for ESP8266
* rpi - Python program for Raspberry Pi
* server - main server page and scripts 