The program for Raspberry Pi, which sends data from sensors to the database, also provides an HTTP server with a simple website, device configuration, sending commands and reading the log.

The program is started with the script sender.py, which initializes all threads, you can also start the server itself by calling the server.py script.
The device configures the config.json file, where you should set the device name, a special device password, WiFi network login details and the time zone.
In order to increase security, you can generate an SSL certificate by saving it to the file cert.pem and placing the key in key.pem.
Example command using OpenSSL: openssl req -x509 -newkey rsa: 4096 -nodes -out cert.pem -keyout key.pem -days 365