~/.local/bin/esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
~/.local/bin/esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 bin/esp32-idf4-20210202-v1.14.bin
