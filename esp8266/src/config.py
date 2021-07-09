"""
config.py: module storing current device configuration.
Provides also useful methods f.e. saving to JSON file.
"""

import logger
import json
import sys

# Configuration
cfg = []

# Mandatory configuration fields
fields = ['NAME', 'PERIOD', 'SLEEP', 'URL', 'PASSWORD', 'WLAN_SSID', 'WLAN_PASS', 'TIMEZONE', 'SENSORS']

# Path to configuration file
path = 'config.json'

# Function for saving current configuration to JSON file
def save():
	"""Function for saving current configuration to JSON file."""
	global cfg, path

	with open(path, 'w') as f:
		json.dump(cfg, f)

# Function for loading current configuration from JSON file
def load():
	"""Function for loading current configuration from JSON file."""
	global cfg, path

	with open(path, 'r') as f:
		cfg = json.load(f)

# Function for printing configuration
def print():
	"""Function for printing configuration."""
	global cfg

	for key, value in cfg.items():
		logger.info('%-10s %s' % (key + ':', value))

# Check if configuration is complete
def check():
	"""Check if configuration is complete."""

	incomplete = 0
	for key in fields:
		if key not in cfg:
			logger.error('Configuration is incomplete, missing field: %s' % key)
			incomplete = 1
	return incomplete
