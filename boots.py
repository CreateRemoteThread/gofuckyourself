#!/usr/bin/python

from __future__ import division

import sys
import getopt
import binascii
import hashlib
import time
import logging
import os
from collections import namedtuple
import csv
import numpy as np
import chipwhisperer as cw
import string
import uuid

logging.basicConfig(level=logging.WARN)

if __name__ != "__main__":
  print "This is a front-end, no importing please."
  sys.exit(0)

def rockyRoad(s):
  numRows = (len(s) / 16) + 1
  normalOut = ""
  shortOut = ""
  for i in range(1,len(s) + 1):
    thisChar = s[i - 1]
    normalOut += "%02x " % ord(thisChar) 
    if i % 8 == 0 and i % 16 != 0 and i != 0: 
      normalOut += "- "
    if thisChar.isalnum():
      shortOut += thisChar
    else:
      shortOut += "."
    if i % 16 == 0 and i != 0:
      print normalOut + ": " + shortOut
      normalOut = ""
      shortOut = ""
  if normalOut != "": # if we're not aligned to 16:
    l = 16 - len(shortOut)
    for i in range(len(shortOut), 16):
      if i % 8 == 0:
        normalOut += "- "
      normalOut += ".. "
      shortOut += "." 
    print normalOut + ": " +  shortOut

def parseFloatTuple(s):
  if "," in s:
    (min,max,step) = s.split(",")
    return Range(float(min),float(max),float(step))
  else:
    return Range(float(s),float(s) + 1.0,2.0)

def parseIntTuple(s):
  if "," in s:
    (min,max,step) = s.split(",")
    return Range(int(min),int(max),int(step))
  else:
    return Range(float(s),float(s) + 1,2)

Range = namedtuple('Range', ['min', 'max', 'step'])

ext_offset_range = Range(0,1,2)
offset_range = Range(-11,11,2)
width_range = Range(-11,11,2)
repeat_range = Range(55,56,2)
baudrate = 9600

save_prefix = uuid.uuid4()

opts,args = getopt.getopt(sys.argv[1:],"e:o:w:r:",["ext_offset=","offset=","width=","repeat="])
for opt,arg in opts:
  if opt in ("-e","--ext_offset"):
    ext_offset_range = parseIntTuple(arg)
  elif opt in ("-o","--offset"):
    offset_range = parseFloatTuple(arg)
  elif opt in ("-w","--width"):
    width_range = parseFloatTuple(arg)
  elif opt in ("-r","--repeat"):
    repeat_range = parseIntTuple(arg)

def countAttempts(x):
  r =  ((x.max - x.min) / x.step) + 1
  # print x
  # print int(r)
  return int(r)

print "-- CONFIGURATION --"

print "Delay: %s" % repr(ext_offset_range)
print "Glitch Offset: %s" % repr(offset_range)
print "Glitch Width: %s (%% of clk)" % repr(width_range)
print "Glitch Repeat: %s" % repr(repeat_range)

totalAttempts = countAttempts(ext_offset_range) * countAttempts(offset_range) * countAttempts(width_range) * countAttempts(repeat_range)

print "(Est) Total attempts: %d" % totalAttempts

# sys.exit(0)

print "-- CONNECT TO HW --"

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

cpufreq = 16000000

print "Initializating target manager..."
target.init()
print "Configuring test baud rate..."
target.baud = baudrate

open('glitch_out.csv', 'w').close()
f = open('glitch_out.csv', 'ab')
writer = csv.writer(f)
writer.writerow(["Output","Width","Offset","Success"])
scope.glitch.offset = -4.25
scope.glitch.ext_offset = 0
# scope.glitch.offset = 100 * cpufreq

totalCount = 1

scope.glitch.ext_offset = ext_offset_range.min
while scope.glitch.ext_offset <= ext_offset_range.max:
  scope.glitch.width = width_range.min
  while scope.glitch.width <= width_range.max:
    scope.glitch.offset = offset_range.min
    while scope.glitch.offset <= offset_range.max:
      scope.glitch.repeat = repeat_range.min
      while scope.glitch.repeat <= repeat_range.max:
        print "-" * 68
        print " Test %d of %d" % (totalCount,totalAttempts)
        print " E: %d O: %f W: %f R: %d" % (scope.glitch.ext_offset, scope.glitch.offset, scope.glitch.width,scope.glitch.repeat)

        print " > Resetting target via PDIC... "
        scope.io.pdic = 'low'
        scope.io.pdic = 'high'

        print " > Flush buffers until ':' "

        dat = "lol"
        tries = 10
        while tries > 0 and ":" not in dat:
          dat = target.ser.read(32,timeout=10)
          tries -= 1

        if tries == 0:
          print " ! Bad state detected. Rebooting device"
          continue

        totalCount += 1

        print " > Arming FPGA!"
        scope.arm()

        target.ser.write("c")

        timeout = 50
        while target.isDone() is False and timeout:
          timeout -= 1
          time.sleep(0.01)

        scope.capture()
        t = scope.getLastTrace() 
        traces.append(t)
     
        output = target.ser.read(25, timeout=50)

        print ""
        rockyRoad(output)
        print ""

        outputs.append(output)
        widths.append(scope.glitch.width)
        offsets.append(scope.glitch.width)

        hash = binascii.hexlify(hashlib.md5(output).digest())
        print " > len: %d, md5: %s" % (len(output),hash)

        success = False
        if "b98e6c2e1eddeb52f59ff62722bfd325" not in hash:
          print " !! SUCCESS !!"
          success = True
        data = [repr(output), hash, scope.glitch.ext_offset, scope.glitch.offset, scope.glitch.width, scope.glitch.repeat, success]
        writer.writerow(data)
        print "-" * 68
        scope.glitch.repeat += repeat_range.step
      scope.glitch.offset += offset_range.step
    scope.glitch.width += width_range.step
  scope.glitch.ext_offset += ext_offset_range.step
f.close()
traces = np.asarray(traces)
print "Saving power traces..."
np.savez("glitch_traces.npz",traces)
print "Done!"

scope.dis()
target.dis()
