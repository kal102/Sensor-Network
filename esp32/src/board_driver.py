#!/usr/bin/python3

"""
Board driver for ESP32 Micropython.
Provides API to control device via REPL.
"""

import serial
import time
import os

com=None

# connection
def connect():
    global com
    #com = serial.Serial('COM3',115200,timeout=1) # Windows
    com = serial.Serial('/dev/ttyUSB0',115200,timeout=1) # Linux
    time.sleep(0.5)
    com.flushInput()

def close():
    com.close()

# internal
def _write_command_read_answer(cmd):
   global com
   com.write(cmd.encode('UTF-8')+b'\r\n')
   com.flushOutput()
   com.readline()
   r=com.readline()
   com.read(3)
   return r.decode('UTF-8').strip()

def _write_command(cmd):
   global com
   com.write(cmd.encode('UTF-8')+b'\r\n')
   com.flushOutput()
   com.readline()
   com.read(3) #len(cmd)+2+3+1)

# API
def set_port(state):
    _write_command('set('+str(state)+')')

def get_port():
    return int(_write_command_read_answer('get()'))

def led(state):
   _write_command('led('+str(state)+')')

def but():
   return int(_write_command_read_answer('but()')) #.strip('\''),16)

def det():
   return int(_write_command_read_answer('det()'))

def pot():
   return int(_write_command_read_answer('pot()'))

def clear():
    resp = ''
    while resp != '>>>':
        resp = _write_command_read_answer('\n') #Escape any indentation blocks

def terminate_script():
    _write_command('\x03')
    clear()

def clean_workspace():
    _write_command('[uos.remove(f) for f in uos.listdir() if f!="boot.py" and f!="main.py" and f!="lib"]')
    clear()

def reset_machine():
    _write_command('import machine')
    clear()
    _write_command('machine.reset()')

def import_module(modName):
    _write_command('import '+str(modName)+'')

def create_dir(dirName):
    _write_command('import os')
    _write_command('os.mkdir("' + str(dirName) + '")')

def create_path(pathName, isDir=False):
    _write_command('import os')
    dirNames = pathName.split('/')
    if isDir == False:
        dirNames.pop(-1)    #Remove file name
    for dirName in dirNames:
       _write_command('os.mkdir("' + str(dirName) + '")')
       _write_command('os.chdir("' + str(dirName) + '")') 
    _write_command("os.chdir('/')")

def remove_file(fileName):
    _write_command('import os')
    _write_command('os.remove("'+str(fileName)+'")')

def write_data_as_file(fileName,dataBytes):
    create_path(fileName)
    _write_command('__tempFileHandle = open("'+str(fileName)+'","wb")')
    i = 0
    while i < len(dataBytes):
        l = min(128,len(dataBytes)-i)
        buff = dataBytes[i:i+l]
        i += l
        _write_command('__tempFileHandle.write('+str(bytes(buff))+')')
        clear()
    _write_command('__tempFileHandle.close()')
    _write_command('del __tempFileHandle')
