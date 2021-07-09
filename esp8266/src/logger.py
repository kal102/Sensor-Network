# -*- coding: utf-8 -*-

"""
logger.py: module developed as an alternative for ulogging library.
Includes timestamp in messages and can write also them to a file.
Manages size of log file, erasing it when there is no free memory.
"""

import gc
import utime as time

MIN_MEM_FREE = 1000

timezone = 0
filename = ""
filemode = "a"

def _get_time():
    global timezone

    tm = time.localtime()
    tm_local = time.mktime((tm[0], tm[1], tm[2], tm[3] + timezone, tm[4], tm[5], tm[6], tm[7]))
    timestamp = time.localtime(tm_local)
    date_time = "%4d-%02d-%02d %02d:%02d:%02d" % timestamp[:6]
    return date_time

def _format_msg(level, string):
    date_time = _get_time()
    string = date_time + ' | ' + level + ' | ' + str(string)
    return string

def _check_log_size():
    global filename

    mem_free = gc.mem_free()
    if mem_free < MIN_MEM_FREE:
        clear()
        warning('Log file was erased because of lack of free memory!')

def config(timezone = 0, filename = "", filemode = "a"):
    globals().update(timezone=timezone, filename=filename, filemode=filemode)

def log(level, msg):
    global filename, filemode

    msg = _format_msg(level, msg)
    print(msg)
    msg += '\n'
    if filename:
        _check_log_size()
        with open(filename, filemode) as log_file:
            log_file.write(msg)
            log_file.close()

def clear():
    global filename

    if filename:
        with open(filename, 'w'):
            pass

def info(msg):
    log('INFO', msg)

def warning(msg):
    log('WARNING', msg)

def error(msg):
    log('ERROR', msg)

def debug(msg):
    log('DEBUG', msg)
