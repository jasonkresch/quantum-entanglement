#!/bin/bash

# Windows
# python3 ../log_geiger.py --port COM5 --out --out run-3c.csv

# Linux
# python3 ../log_geiger.py --port /dev/ttyACM0 --out --out run-3c.csv

# macOS
python3 ../log_geiger.py --port /dev/cu.usbmodem206EF13166CC2 --out run-3c.csv