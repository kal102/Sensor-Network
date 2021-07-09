#!/usr/bin/python3

"""
Script for loading files into Micropython filesystem.
You can specifiy files to load by editting files.txt.
Glob wildcards can be used to load all files from directory.
Requires board_driver.py script with driver for the specific board.
"""

from board_driver import *
import time
import subprocess
import glob

file_names = []

with open("files.txt","r") as file:
    files = file.read()
    paths = files.split('\n')
    for path in paths:
        file_names += glob.glob(path, recursive=True) # search through wildcards (glob style)

try:
    connect()
    terminate_script()
    clean_workspace()
    for file_name in file_names:
        file_name = file_name.strip()
        if file_name:
            try:
                with open(file_name,"rb") as file:
                    print("Loading file: " + file_name)
                    write_data_as_file(file_name,file.read())
            except FileNotFoundError:
                print("Missing file: " + file_name)
                print("Script Exit.")
                quit()
            except IsADirectoryError:
                pass
    print("Resetting...")
    time.sleep(1)
    reset_machine()
finally:
    close()
    
print("Finished")
print("type t+ENTER to connect to device terminal")
print("or just press ENTER to exit script.")

if input().startswith("t"): # connect to device
    time.sleep(0.5)
    subprocess.run(["picocom","/dev/ttyUSB0","-b115200"])
else:
    print("Script Exit.")
