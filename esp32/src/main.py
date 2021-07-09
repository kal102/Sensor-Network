"""
main.py: script which can be used to run application on power-up.
Just add it to files.txt and it will be loaded to ESP memory.
"""

print("Waiting 30 seconds before application starts...")
import time
time.sleep(30)

import sender
sender.run()
