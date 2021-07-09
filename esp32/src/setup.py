"""
setup.py: script connecting to WLAN network and installing all dependencies.
Uses configuration from config.json file, remember to set it before use!
"""

import ujson as json
import network
import utime as time
import ntptime
import upip

cfg_path = 'config.json'

# read configuration
with open(cfg_path) as data_file:
    cfg = json.load(data_file)

# print configuration
print()
for key, value in cfg.items():
    print('%-10s %s' % (key + ':', value))
print()

# connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.disconnect()
while True:
    wlan.connect(cfg["WLAN_SSID"], cfg["WLAN_PASS"])
    time.sleep(5)
    if wlan.isconnected():
        print('Connected to network: ' + cfg["WLAN_SSID"])
        break
    else:
        print('Falied to connect to network: ' + cfg["WLAN_SSID"])

# synchronize time
ntptime.settime()
print('Time synchronized')

# install modules
upip.install('picoweb')

# setup WebREPL
import webrepl_setup
