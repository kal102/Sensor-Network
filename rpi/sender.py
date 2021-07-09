#!/usr/bin/env python3

"""
sender.py: script reading data from sensors and sending it to main server.
Uses configuration from config.json file, remember to set it before use!
Runs HTTP server used to edit configuration, receive commands and read log file.
"""

import config as cfg
import sensor

import logging
import sys
import json
import threading
import time
import requests
import os

from datetime import datetime

# Parameters
MAX_DATA_LEN = 1000

# Flags
sensors_active = 1

# Global variables
base_dir = ''
log_path = 'log.log'

# Thread for running HTTP server
def thread_server():
	"""Thread for running HTTP server."""
	global base_dir, log_path

	logging.info("Starting HTTP server...")
	server.base_dir = base_dir
	server.log_path = log_path
	server.run()

# Thread for running commands
def thread_commands(data):
	"""Thread for running commands from HTTP server."""

	while(1):
		# Wait for new command
		with server.cmd_notify:
			while not len(server.cmd_passed):
				server.cmd_notify.wait()
			cmd_new = server.cmd_passed.pop()
			cmd = cmd_new[0]
			#cmd_args = cmd_new[1]

		# Run command
		logging.info("Running new command %s..." % cmd)
		if cmd == 'stop_data':
			sensors_active = 0
			logging.info("Deactivating fetching data from sensors")
		elif cmd == 'start_data':
			sensors_active = 1
			logging.info("Activating fetching data from sensors")
		elif cmd == 'clear_data':
			data.clear()
			logging.info("Cleared sensors data queue")
		elif cmd == 'restart':
			logging.warning('Restarting script...')
			time.sleep(1)
			os.execv(sys.executable, ['python3'] + sys.argv)
		else:
			logging.warning("Received unrecognized command from HTTP server!")

# Thread for fetching data from sensors
def thread_sensors(data):
	"""Thread for fetching data from sensors."""
	status = 0

	# Initialize sensors
	sensor.init(cfg.cfg['SENSORS'])
	
	while(1):
		# Check if fetching data is activated
		if sensors_active:

			# Read data from sensors
			status, sensor_data = sensor.read(cfg.cfg['SENSORS'])

			# Prepare new data record
			timestamp = datetime.now()
			date_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
			record = {'date':date_time, 'id':str(cfg.cfg['NAME']), 'stat':status}
			for key, value in sensor_data.items():
				record[key] = str(value)

			# Push new data record
			if len(data) > MAX_DATA_LEN:
				data.pop(0)
			data.append(record)
			logging.info('Got new data record:')
			logging.info(record)

		# Wait some time before fetching another data
		time.sleep(cfg.cfg['SENSOR_T'])

# Thread for sending data to DB
def thread_sending(data):
	"""Thread for sending data to DB."""
	fails = 0

	while(1):
		# Insert data into DB
		if data:
			record = data.pop(0)
			logging.info('Sending data record...')
			try:
				post_url = cfg.cfg['URL'] + "?id=%s&pass=%s" % (cfg.cfg['NAME'], cfg.cfg['PASSWORD'])
				post_url = post_url.replace(' ', '%20')
				post_data = record
				post_data['fail'] = fails
				r = requests.post(url=post_url, data=post_data)
				logging.info(r.text)
				r.close()
			except requests.exceptions.ConnectionError:
				logging.error("Connection lost")
				data.append(record)
				fails += 1

		# Wait some time before sending another data
		time.sleep(cfg.cfg['SEND_T'])

# Exception logging hook
def _excepthook(exctype, exc, tb):
	"""Exception logging hook."""
	logging.error("An unhandled exception occurred!", exc_info=(exctype, exc, tb))

# Function configuring environment for HTTP server
def config():
	"""Function configuring environment for HTTP server."""
	global base_dir, log_path

	# Set paths
	base_dir = os.path.dirname(os.path.realpath(__file__))
	cfg.path = base_dir + '/config.json'
	log_path = base_dir + '/log.log'

	# Start logging
	logging.basicConfig(filename=log_path, format='%(asctime)-16s | %(levelname)-5s | %(message)s', level=logging.DEBUG)
	sys.excepthook = _excepthook

	# Load configuration
	cfg.load()
	logging.info('Loaded configuration')

	# Print configuration and check if is complete
	cfg.print()
	if not cfg.check:
		logging.info('Exiting...')
		sys.exit(1)

# Main function
if __name__ == "__main__":
	"""Sends data with HTTP requests to the given URL.
	You can set parameters by editing config.json file."""
	data = []

	# Configure environment
	config()

	# Create threads
	th_server = threading.Thread(target=thread_server, args=())
	th_commands = threading.Thread(target=thread_commands, args=(data, ))
	th_sensors = threading.Thread(target=thread_sensors, args=(data, ))
	th_sending = threading.Thread(target=thread_sending, args=(data, ))
	logging.info('Threads created')

	# Run sender threads
	th_sensors.start()
	th_sending.start()

	# Run server threads
	if cfg.cfg["SERVER"]:
		import server
		th_server.start()
		th_commands.start()
		
	logging.info('Threads started')
