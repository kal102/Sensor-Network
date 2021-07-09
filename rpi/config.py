#!/usr/bin/env python3

"""
config.py: module storing current device configuration.
Provides also useful methods f.e. saving to JSON file.
"""

import logging
import json
import sys

# Configuration
cfg = []

# Mandatory configuration fields
fields = ['NAME', 'SENSOR_T', 'SEND_T', 'URL', 'PASSWORD', 'ADDRESS', 'PORT', 'SENSORS']

# Path to configuration file
path = 'config.json'

# Function for saving current configuration to JSON file
def save():
	"""Function for saving current configuration to JSON file."""
	global cfg, path

	with open(path, 'w') as f:
		json.dump(cfg, f, indent=4)

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
		logging.info('%-10s %s' % (key + ':', value))

# Check if configuration is complete
def check():
	"""Check if configuration is complete."""

	incomplete = 0
	for key in fields:
		if key not in cfg:
			logging.error('Configuration is incomplete, missing field: %s' % key)
			incomplete = 1
	return incomplete
