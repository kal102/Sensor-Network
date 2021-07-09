import subprocess
import glob 

def __scan():
	
	path = []

	path = glob.glob("/sys/bus/w1/devices/28-*")
	if (len(path)):
		return subprocess.getoutput("(cat " + path[0] +  "/w1_slave)")
	else:
		return ""

def get():
	global status
	tmp = __scan() #subprocess.getoutput("(cat  /sys/bus/w1/devices/28-0119523e96ff/w1_slave)")

	try :
		status = "ok"
		real_tmp  = tmp.split()[-1]
		real_tmp  = int(real_tmp[2:])
		real_tmp = real_tmp / 1000
	except (ValueError, IndexError):
		status = "ds18b20 error"
		real_tmp = 0.0

	return real_tmp
