#!/usr/bin/env python3

# just for testing shouter api

import chipshouter 
import time

cs = chipshouter.ChipSHOUTER("/dev/ttyUSB0")
cs.voltage = 500
cs.pulse.width = 30
# cs.pat_wave = "110110"
cs.clr_armed = True
cs.clr_armed = False
