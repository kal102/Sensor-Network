#!/usr/bin/env python3

"""
server.py: script running Flask HTTP server.
Used to edit configuration, serve commands and send log file.
Reads configuration from config.json file, remember to set it before use!
It can be run as standalone module or used by sender.py script.
"""

from flask import Flask, Response
from flask import render_template, send_file, send_from_directory
from flask import redirect, url_for, request, abort
from flask import json, jsonify
from werkzeug.utils import secure_filename

import config as cfg
import logging
import threading
import sys
import os
import ssl

# Supported commands and number of mandatory arguments
cmd_supported = {'stop_data':0, 'start_data':0, 'clear_data':0, 'save_cfg':0, 'load_cfg':0, 'clear_log':0, 'restart':0}

# Passed commands to other modules
cmd_passed = []
cmd_notify = threading.Condition()

# Global variables
base_dir = ''
log_path = 'log.log'

# Function for clearing log file
def _clear_log(log_path):
	"""Function for clearing log file."""

	with logging._lock:
		with open(log_path, 'w'):
			pass

# Function passing command to other modules
def _pass_cmd(cmd, cmd_args):
    """Function passing command to other modules."""
    global cmd_passed

    with cmd_notify:
        cmd_passed.append((cmd, tuple(cmd_args)))
        cmd_notify.notify_all()

# Main Flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = ''

@app.route('/')
def index():
    return render_template('index.html', name = cfg.cfg["NAME"])

@app.route('/configuration')
def configuration():
     return render_template('login.html', name = cfg.cfg["NAME"], route = 'config.json')

@app.route('/config.json', methods=['POST', 'GET'])
def configfile():

    # Authenticate server
    try:
        name = request.args.get('id')
        password = request.args.get('pass')
        if cfg.cfg["NAME"] != name or cfg.cfg["PASSWORD"] != password:
            abort(401)
    except KeyError:
        abort(401)

    # Handle POST request
    if request.method == 'POST':
        post_resp = ''

        # Load new configuration
        cfg_new = request.get_json()
        for key, value in cfg_new.items():
            if key in cfg.cfg.keys():
                cfg.cfg[key] = value
                post_resp += 'Updated %s field in configuration with value %s\n' % (key, value)

        # Print and send response
        logging.info(post_resp)
        return Response(post_resp, mimetype='text/plain')
    
    # Handle GET request
    else:
        # Send config file
        return jsonify(cfg.cfg)

@app.route('/commands')
def commands():
    return render_template('login.html', name = cfg.cfg["NAME"], route = '/cmds')

@app.route('/cmds', methods=['POST', 'GET'])
def cmds():

    # Authenticate server
    try:
        name = request.args.get('id')
        password = request.args.get('pass')
        if cfg.cfg["NAME"] != name or cfg.cfg["PASSWORD"] != password:
            abort(401)
    except KeyError:
        abort(401) 

    # Handle POST request
    if request.method == 'POST':
        post_resp = ''

        # Get command
        try:
            cmd_str = request.form.get('cmd')
        except KeyError:
            post_resp += 'Bad request\n'
            return (post_resp, 400)

        # Parse command
        cmd_str.strip()
        cmd_args = cmd_str.split(' ')
        cmd = cmd_args.pop(0)
        cmd = cmd.strip()
        if cmd not in cmd_supported.keys():
            post_resp += 'Unrecognized command ' + cmd + '\n'
            logging.warning(post_resp)
            return post_resp
        elif len(cmd_args) < cmd_supported[cmd]:
            post_resp += 'Expected at least %d arguments for command %s, %d given\n' % (cmd_supported[cmd], cmd, len(cmd_args))
            logging.warning(post_resp)
            return post_resp
        else:
            post_resp += 'Received %s command with %d arguments\n' % (cmd, len(cmd_args)) 

        # Run command or pass to other modules
        if cmd == 'save_cfg':
            cfg.save()
            post_resp += "Saved configuration to file\n"
        elif cmd == 'load_cfg':
            cfg.load()
            post_resp += "Loaded configuration from file\n"
        elif cmd == 'clear_log':
            _clear_log(log_path)
            post_resp += "Cleared log file\n"
        elif __name__ != "__main__":
            _pass_cmd(cmd, cmd_args)
            post_resp += "Passing command to other modules\n"
        elif cmd == 'restart':
            logging.warning('Restarting script...')
            os.execv(sys.executable, ['python3'] + sys.argv)
        else:
            post_resp += "Server could not handle this command!\n"

        # Print and send response
        logging.info(post_resp)
        return Response(post_resp, mimetype='text/plain')

    # Handle GET request
    else:
        return render_template('cmds.html', name = cfg.cfg["NAME"], password = cfg.cfg["PASSWORD"])

@app.route('/log')
def log():
    return render_template('login.html', name = cfg.cfg["NAME"], route = 'log.log')

@app.route('/log.log')
def logfile():
    global log_path

    # Authenticate server
    try:
        name = request.args.get('id')
        password = request.args.get('pass')
        if cfg.cfg["NAME"] != name or cfg.cfg["PASSWORD"] != password:
            abort(401)
    except KeyError:
        abort(401)   

    # Read log file
    with logging._lock:
        with open(log_path, 'r') as log_file:
            log_text = log_file.read()

    # Send log text
    return Response(log_text, mimetype='text/plain')

@app.route('/files')
def files():
    return render_template('login.html', name = cfg.cfg["NAME"], route = '/rpi')

@app.route('/rpi', methods=['POST', 'GET'])
def main_dir():
    global base_dir

    # Authenticate server
    try:
        name = request.args.get('id')
        password = request.args.get('pass')
        if cfg.cfg["NAME"] != name or cfg.cfg["PASSWORD"] != password:
            abort(401)
    except KeyError:
        abort(401)

    # Handle POST request
    if request.method == 'POST':
        post_resp = ''

        # Check if any files were uploaded
        if request.files:

            # Save files
            for f in request.files.getlist("file[]"):
                app.config["UPLOAD_FOLDER"] = base_dir
                filename = secure_filename(f.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                f.save(path)
                post_resp += 'Uploaded file ' + filename + '\n'
        else:
            post_resp += 'Missing files to upload' + '\n'

        logging.info(post_resp)
        return Response(post_resp, mimetype='text/plain')

    # Handle GET request
    else:

        # Show directory contents
        base_dir = os.path.dirname(os.path.realpath(__file__))
        files = os.listdir(base_dir)
        return render_template('files.html', name = cfg.cfg["NAME"], password = cfg.cfg["PASSWORD"], files = files)

@app.route('/rpi/<path:req_path>', methods=['POST', 'GET'])
def other_dir(req_path):
    global base_dir

    # Authenticate server
    try:
        name = request.args.get('id')
        password = request.args.get('pass')
        if cfg.cfg["NAME"] != name or cfg.cfg["PASSWORD"] != password:
            abort(401)
    except KeyError:
        abort(401)

    # Joining the base and the requested path
    abs_path = os.path.join(base_dir, req_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Handle POST request
    if request.method == 'POST':
        post_resp = ''

        # Check if any files were uploaded
        if request.files:

            # Check if path is a file
            if os.path.isfile(abs_path):
                post_resp += 'Path must lead to a directory when uploading files\n'
                logging.info(post_resp)
                return Response(post_resp, mimetype='text/plain')

            # Save files
            for f in request.files.getlist("file[]"):
                app.config["UPLOAD_FOLDER"] = abs_path
                filename = secure_filename(f.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                f.save(path)
                post_resp += 'Uploaded file ' + filename + '\n'
        else:
            post_resp += 'Missing files to upload' + '\n'

        logging.info(post_resp)
        return Response(post_resp, mimetype='text/plain')

    # Handle GET request
    else:

        # Check if path is a file and serve
        if os.path.isfile(abs_path):
            return send_file(abs_path)

        # Show directory contents
        files = os.listdir(abs_path)
        return render_template('files.html', name = cfg.cfg["NAME"], password = cfg.cfg["PASSWORD"], files = files)

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

# Function for running HTTP server
def run():
    """Function for running HTTP server."""
    global base_dir
    
    cert_path = os.path.join(base_dir, 'cert.pem')
    key_path = os.path.join(base_dir, 'key.pem')
    if os.path.isfile(cert_path) and os.path.isfile(key_path):
        logging.info('Found SSL certificate files cert.pem and key.pem')
        logging.info('Server will run in HTTPS mode')
        try:
            app.run(host=cfg.cfg['ADDRESS'], port=cfg.cfg['PORT'], ssl_context=(cert_path, key_path))
        except ssl.SSLError:
            logging.error('Detected problem with certificate files!')
            logging.error('Server will not start!')
    else:
        logging.warning('SSL certificate files cert.pem and key.pem not found!')
        logging.warning('Server will run in HTTP mode!')
        app.run(host=cfg.cfg['ADDRESS'], port=cfg.cfg['PORT'])

# Main function
if __name__ == "__main__":
    """Starts standalone HTTP server, which can serve commands."""

    # Configure environment
    config()

    # Start server
    logging.info("Starting HTTP server...")
    run()
