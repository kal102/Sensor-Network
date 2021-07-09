"""
server.py: script running Picoweb HTTP server.
Used to edit configuration, serve commands and send log file.
Reads configuration from config.json file, remember to set it before use!
It can be run as standalone module or used by sender.py script.
"""

import picoweb
import ulogging as logging
import ujson as json
import utime as time
import network
import ntptime
import _thread
import webrepl

import logger
import config as cfg

# Parameters
MAX_LEN_CMD_PASSED = 10

# Supported commands and number of mandatory arguments
cmd_supported = {'stop_data':0, 'start_data':0, 'clear_data':0, 'save_cfg':0, 'load_cfg':0, 'clear_log':0}

# Passed commands to other modules
cmd_passed = []
cmd_lock = _thread.allocate_lock()

# Global variables
main_app = True
log_path = 'log.log'
ip_addr = '127.0.0.1'

# Function passing command to other modules
def _pass_cmd(cmd, cmd_args):
    """Function passing command to other modules."""
    global cmd_passed

    with cmd_lock:
        if len(cmd_passed) > MAX_LEN_CMD_PASSED:
            cmd_passed.pop(0)
        cmd_passed.append((cmd, tuple(cmd_args))) 

# Main application
app = picoweb.WebApp(None)

@app.route('/')
def index(req, resp):
    global ip_addr
    name = cfg.cfg["NAME"]
    yield from picoweb.start_response(resp)
    yield from app.render_template(resp, 'index.tpl', (name, ip_addr))

@app.route('/configuration')
def configuration(req, resp):
    global ip_addr
    name = cfg.cfg["NAME"]
    route = 'config.json'
    yield from picoweb.start_response(resp)
    yield from app.render_template(resp, 'login.tpl', (name, ip_addr, route))

@app.route('/config.json', methods=['POST', 'GET'])
def configfile(req, resp):

    # Authenticate server
    try:
        req.parse_qs()
        name = req.form['id']
        password = req.form['pass']
        if cfg.cfg["NAME"] != name or cfg.cfg["PASSWORD"] != password:
            yield from picoweb.http_error(resp, status="401")
            return
    except (TypeError, KeyError):
        yield from picoweb.http_error(resp, status="401")
        return

    # Handle POST request
    if req.method == 'POST':
        post_resp = ''

        # Load new configuration
        yield from req.read_form_data()
        cfg_str = str(list(req.form.keys())[0])
        cfg_new = json.loads(cfg_str)
        for key, value in cfg_new.items():
            if key in cfg.cfg.keys():
                cfg.cfg[key] = value
                post_resp += 'Updated %s field in configuration with value %s\n' % (key, value)

        # Print and send response
        logger.info(post_resp)
        yield from picoweb.start_response(resp, content_type = "text/plain")
        yield from resp.awrite(post_resp)
    
    # Handle GET request
    else:
        # Send config file
        yield from picoweb.jsonify(resp, cfg.cfg)

@app.route('/commands')
def commands(req, resp):
    global ip_addr
    name = cfg.cfg["NAME"]
    route = 'cmds'
    yield from picoweb.start_response(resp)
    yield from app.render_template(resp, 'login.tpl', (name, ip_addr, route))

@app.route('/cmds')
def cmds(req, resp):
    global main_app, ip_addr

    # Authenticate server
    try:
        req.parse_qs()
        name = req.form['id']
        password = req.form['pass']
        if cfg.cfg["NAME"] != name or cfg.cfg["PASSWORD"] != password:
            yield from picoweb.http_error(resp, status="401")
            return
    except (TypeError, KeyError):
        yield from picoweb.http_error(resp, status="401")
        return

    # Handle POST request
    if req.method == 'POST':
        post_resp = ''

        # Get command
        try:
            yield from req.read_form_data()
            cmd_str = req.form['cmd']
        except KeyError:
            yield from picoweb.http_error(resp, status="400")
            return

        # Parse command
        cmd_str.strip()
        cmd_args = cmd_str.split(' ')
        cmd = cmd_args.pop(0)
        cmd = cmd.strip()
        if cmd not in cmd_supported.keys():
            post_resp += 'Unrecognized command ' + cmd + '\n'
            logger.warning(post_resp)
            yield from picoweb.start_response(resp)
            yield from resp.awrite(post_resp)
            return
        elif len(cmd_args) < cmd_supported[cmd]:
            post_resp += 'Expected at least %d arguments for command %s, %d given\n' % (cmd_supported[cmd], cmd, len(cmd_args))
            logger.warning(post_resp)
            yield from picoweb.start_response(resp)
            yield from resp.awrite(post_resp)
            return
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
            logger.clear()
            post_resp += "Cleared log file\n"
        elif main_app == False:
            _pass_cmd(cmd, cmd_args)
            post_resp += "Passing command to other modules\n"
        else:
            post_resp += "Server could not handle this command!\n"

        # Print and send response
        logger.info(post_resp)
        yield from picoweb.start_response(resp, content_type = "text/plain")
        yield from resp.awrite(post_resp)

    # Handle GET request
    else:
        # Return page        
        name = cfg.cfg["NAME"]
        password = cfg.cfg["PASSWORD"]
        yield from picoweb.start_response(resp)
        yield from app.render_template(resp, 'cmds.tpl', (name, ip_addr, password))

@app.route('/log')
def log(req, resp):
    global ip_addr
    name = cfg.cfg["NAME"]
    route = 'log.log'
    yield from picoweb.start_response(resp)
    yield from app.render_template(resp, 'login.tpl', (name, ip_addr, route))

@app.route('/log.log')
def logfile(req, resp):

    # Authenticate server
    try:
        req.parse_qs()
        name = req.form['id']
        password = req.form['pass']
        if cfg.cfg["NAME"] != name or cfg.cfg["PASSWORD"] != password:
            yield from picoweb.http_error(resp, status="401")
            return
    except (TypeError, KeyError):
        yield from picoweb.http_error(resp, status="401")
        return 

    # Read and send log line by line
    with logger.log_lock:
        yield from picoweb.start_response(resp, content_type = "text/plain")
        with open(log_path, 'r') as log_file:
            while True:
                log_line = log_file.readline()
                if log_line:
                    yield from resp.awrite(log_line)
                else:
                    break

# Thread for running HTTP server
def thread_server():
    """Thread for running HTTP server."""

    wlan = network.WLAN(network.STA_IF)
    ip_addr = wlan.ifconfig()[0]
    globals().update(cfg=cfg, log_path=log_path, ip_addr=ip_addr)
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting HTTP server...")
    app.run(host=cfg.cfg['ADDRESS'], port=cfg.cfg['PORT'])

# Function connecting to WLAN network
def connect():
    """Function connecting to WLAN network."""

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
    logger.config(timezone = cfg.cfg["TIMEZONE"], filename=log_path)

    # Connect to WLAN network
    connect()

    # Synchronize time
    ntptime.settime()
    logger.info('Time synchronized')

# Main function
def run():
    """Starts HTTP server and WebREPL."""

    # Configure environment and connect to WLAN
    config()

    # Run server thread
    _thread.stack_size(8192)
    _thread.start_new_thread(thread_server, ())

    # Start WebREPL
    webrepl.start()
