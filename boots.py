#!/usr/bin/python

# the magic talking monkey...

from __future__ import print_function, division

import binascii
import hashlib
import time
import logging
import os
from collections import namedtuple
import csv

import numpy as np

import chipwhisperer as cw
# from chipwhisperer.tests.tools_for_tests import FIRMWARE_DIR
from chipwhisperer.capture.api.programmers import XMEGAProgrammer
#from scripting_utils import GlitchResultsDisplay

logging.basicConfig(level=logging.WARN)
scope = cw.scope()
target = cw.target(scope)

scope.glitch.clk_src = 'clkgen'

scope.gain.gain = 45
scope.adc.samples = 15000
scope.adc.offset = 0
scope.adc.basic_mode = "rising_edge"
scope.clock.clkgen_freq = 16000000
scope.clock.adc_src = "clkgen_x4"
scope.io.tio2 = "serial_tx"
scope.io.tio1 = "serial_rx"
scope.io.hs2 = "glitch"
scope.glitch.offset = 4

target.go_cmd = ""
target.key_cmd = ""

scope.glitch.trigger_src = 'ext_single'
scope.glitch.repeat = 115 # was 105 for blind glitching
scope.trigger.triggers = "tio4"

traces = []
outputs = []
widths = []
offsets = []

Range = namedtuple('Range', ['min', 'max', 'step'])
width_range = Range(25,35, 0.5)
cpufreq = 16000000
# test here...
# offset_range = Range(1 * cpufreq,100 * cpufreq, cpufreq/2)
offset_range = Range(-11,11,2)
# offset_range = Range(-7,-2,1)
# offset_range = Range(65,175,3)
# offset_range = Range(10,500,3)

print("Initializating target buffer")
target.init()
print("Baudrate")
target.baud = 9600

open('glitch_out.csv', 'w').close()
f = open('glitch_out.csv', 'ab')
writer = csv.writer(f)
writer.writerow(["Output","Width","Offset","Success"])
scope.glitch.offset = -4.25
scope.glitch.ext_offset = 0
# scope.glitch.offset = 100 * cpufreq

scope.glitch.width = width_range.min
while scope.glitch.width < width_range.max:
  scope.glitch.offset = offset_range.min
  while scope.glitch.offset < offset_range.max:
    print("Glitching at offset %f, width %f" % (scope.glitch.offset,scope.glitch.width))
    # scope.io.pdid = 'low'
    # target.ser.flush()

    print("Resetting target")
    scope.io.pdic = 'low'
    # time.sleep(0.3)
    scope.io.pdic = 'high'
    # target.ser.flush()
    #time.sleep(0.25)

    dat = "lol"
    tries = 10
    while tries > 0 and ":" not in dat:
      dat = target.ser.read(32,timeout=10)
      # print(dat)
      tries -= 1

    if tries == 0:
      print("Actual flow corruption. Rebooting device")
      continue


    print("Fire!")
    scope.arm()
    # scope.io.pdid = 'high'
    # scope.io.pdid = 'low'
    target.ser.write("c")

    timeout = 50
    while target.isDone() is False and timeout:
      timeout -= 1
      time.sleep(0.01)

    scope.capture()
    t = scope.getLastTrace() 
    traces.append(t)
 
    output = target.ser.read(25, timeout=50)
    print(output)
    print(len(output))
    # traces.append(trace)
    outputs.append(output)
    widths.append(scope.glitch.width)
    offsets.append(scope.glitch.width)

    hash = binascii.hexlify(hashlib.md5(output).digest())
    print(hash)

    # for table display purposes
    # success = 'inn' in repr(output) # check for glitch success (depends on targets active firmware)
    success = False
    if "b98e6c2e1eddeb52f59ff62722bfd325" not in hash:
      # if "6f048b0393437cf46419d600a244b462" not in hash:
      # if "318171080c347061b82ca479b0f52843" not in hash:
      # if "fail" not in repr(output):
      print("*** WITH VICTORY OVER OURSELVES, WE ARE EXALTED ***")
      success = True
      # target.dis()
      # scope.dis()
      # sys.exit(0)
    # success = '2' in repr(output)
    # success = True
    data = [repr(output), hash,scope.glitch.width, scope.glitch.offset, success]
    #glitch_display.add_data(data)
    writer.writerow(data)

    # run aux stuff that should happen after trace here
    scope.glitch.offset += offset_range.step
  scope.glitch.width += width_range.step
f.close()
traces = np.asarray(traces)
print("Saving power traces...")
np.savez("glitch_traces.npz",traces)
# the rest of the data is available with the outputs, widths, and offsets lists
#glitch_display.display_table()
print('Done')

# clean up the connection to the scope and target
scope.dis()
target.dis()
