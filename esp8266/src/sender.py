"""
sender.py: script reading data from sensors and sending it to main server.
Uses configuration from config.json file, remember to set it before use!
"""

import ujson as json
import network
import urequests as requests
import utime as time
import ntptime
import machine

import logger
import config as cfg
import sensor

# Parameters
MAX_DATA_LEN = 10

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
    logger.config(timezone = cfg.cfg["TIMEZONE"], filename='')

    # Connect to WLAN network
    connect()

    # Synchronize time
    try:
        ntptime.settime()
        logger.info("Time synchronized")
    except OSError:
        logger.error("Time couldn't be synchronized")

# Main function
def run():
    """Sends data with POST requests to the given URL.
    You can set parameters by editing config.json file."""
    data = []
    data_path = 'data.json'
    fails = 0

    # Configure environment and connect to WLAN
    config()

    # Read data from the previous run
    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        with open(data_path, 'r') as f:
            data = json.load(f)

    # Initialize sensors
    sensor.init(cfg.cfg['SENSORS'])

    while True:
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

        # Insert data into DB
        while data:
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
                break
            except IndexError:
                logger.error('Host not found')
                data.append(record)
                fails +=1
                break

        # Check if sleep flag was set
        if cfg.cfg["SLEEP"]:

            # Save data to file for the next run
            with open(data_path, 'w') as f:
                json.dump(data, f)

            # Put device into deep-sleep mode
            logger.info("Putting device into sleep mode...")
            sleep_time = cfg.cfg["PERIOD"] - 10
            if sleep_time > 0:
                machine.deepsleep(sleep_time * 1000)
            else:
                machine.deepsleep(1)
        else:
            # Wait some time before sending another data
            time.sleep(cfg.cfg["PERIOD"])
