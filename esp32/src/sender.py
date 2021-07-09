"""
sender.py: script reading data from sensors and sending it to main server.
Uses configuration from config.json file, remember to set it before use!
Runs HTTP server used to edit configuration, receive commands and read log file.
"""

import _thread
import ujson as json
import network
import urequests as requests
import utime as time
import ntptime
import webrepl

import logger
import config as cfg
import sensor
server = None

# Parameters
MAX_DATA_LEN = 10

# Flags
sensors_active = 1

# Thread for running HTTP server
def thread_server():
    """Thread for running HTTP server."""
    
    logger.info("Starting HTTP server...")
    server.main_app = False
    server.run()

# Thread for decoding commands
def thread_commands(data):
    """Thread for decoding commands from HTTP server."""

    while True:
        # Wait for new command
        if len(server.cmd_passed):
        
            # Get new command
            with server.cmd_lock:
                cmd_new = server.cmd_passed.pop()
                cmd = cmd_new[0]
                #cmd_args = cmd_new[1]

            # Run command
            logger.info("Running new command %s..." % cmd)
            if cmd == 'stop_data':
                sensors_active = 0
                logger.info("Deactivating fetching data from sensors")
            elif cmd == 'start_data':
                sensors_active = 1
                logger.info("Activating fetching data from sensors")
            elif cmd == 'clear_data':
                data.clear()
                logger.info("Cleared sensors data queue")
            else:
                logger.warning("Received unrecognized command from HTTP server!")

        time.sleep(1)

# Thread for fetching data from sensors
def thread_sensors(data):
    """Thread for fetching data from sensors."""

    # Initialize sensors
    sensor.init(cfg.cfg['SENSORS'])

    while True:
        # Check if fetching data is activated
        if sensors_active:

            # Read data from sensors
            status, sensor_data = sensor.read(cfg.cfg['SENSORS'])

            # Prepare new data record
            tm = time.localtime()
            tm_local = time.mktime((tm[0], tm[1], tm[2], tm[3] + cfg.cfg["TIMEZONE"], tm[4], tm[5], tm[6], tm[7]))
            timestamp = time.localtime(tm_local)
            date_time = "%4d-%02d-%02dT%02d:%02d:%02d" % timestamp[:6]
            record = {'date':date_time, 'id':cfg.cfg["NAME"], 'stat':status}
            for key, value in sensor_data.items():
                record[key] = str(value)

            # Push new data record
            if len(data) >= MAX_DATA_LEN:
                data.pop(0)
            data.append(record)
            logger.info('Got new data record:')
            logger.info(record)

        # Wait some time before fetching another data
        time.sleep(cfg.cfg["SENSOR_T"])

# Thread for sending data to DB
def thread_sending(data):
    """Thread for sending data to DB."""
    fails = 0

    while True:
        # Insert data into DB
        if data:
            record = data.pop(0)
            logger.info('Sending data record...')
            try:
                post_url = cfg.cfg['URL'] + "?id=%s&pass=%s" % (cfg.cfg['NAME'], cfg.cfg['PASSWORD'])
                post_url = post_url.replace(' ', '%20')
                post_data = "&".join(["%s=%s" % (key, value) for key, value in record.items()])
                post_data += "&fail=%s" % fails
                post_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                r = requests.post(post_url, data=post_data, headers=post_headers)
                logger.info(r.text)
                r.close()
            except OSError:
                logger.error('Host unreachable')
                data.append(record)
                fails +=1
            except IndexError:
                logger.error('Host not found')
                data.append(record)
                fails +=1

        # Wait some time before sending another data
        time.sleep(cfg.cfg["SEND_T"])

# Function connecting to WLAN network
def connect():
    """Function connecting to WLAN network."""

    # Connect to network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    while True:
        wlan.connect(cfg.cfg["WLAN_SSID"], cfg.cfg["WLAN_PASS"])
        time.sleep(5)
        if wlan.isconnected():
            logger.info('Connected to network: ' + cfg.cfg["WLAN_SSID"])
            break
        else:
            logger.error('Falied to connect to network: ' + cfg.cfg["WLAN_SSID"])

# Function configuring environment for HTTP server
def config():
    """Function configuring environment for HTTP server."""

    # Load configuration
    cfg.load()
    logger.info('Loaded configuration')

    # Print configuration and check if is complete
    cfg.print()
    if not cfg.check:
        logger.info('Exiting...')
        return 1

    # Start logger
    logger.config(timezone = cfg.cfg["TIMEZONE"], filename='log.log')

    # Connect to WLAN network
    connect()

    # Synchronize time
    ntptime.settime()
    logger.info('Time synchronized')

# Main function
def run():
    """Sends data with HTTP requests to the given URL."""
    data = []

    # Configure environment and connect to WLAN
    config()

    # Run sender threads
    _thread.stack_size(1024)
    _thread.start_new_thread(thread_sensors, (data, ))
    _thread.start_new_thread(thread_sending, (data, ))

    # Run server threads
    if cfg.cfg["SERVER"]:
        global server
        import server
        server.main_app = False
        _thread.start_new_thread(thread_commands, (data, ))
        _thread.stack_size(8192)
        _thread.start_new_thread(server.thread_server, ())
    
    logger.info('Threads started')

    # Start WebREPL
    logger.info('Starting WebREPL...')
    webrepl.start()
