#!/usr/bin/env python3

import time
import logging
import os
from collections import namedtuple
import csv
import random
import support
import chipshouter

import numpy as np

import chipwhisperer as cw
from chipwhisperer.capture.api.programmers import XMEGAProgrammer,AVRProgrammer
logging.basicConfig(level=logging.WARN)
scope= cw.scope()
target = cw.target(scope)

scope.glitch.clk_src = 'clkgen'

scope.gain.gain = 25
scope.adc.samples = 3000
scope.adc.offset = 0
scope.adc.basic_mode = "rising_edge"
scope.clock.clkgen_freq = 7370000
scope.clock.adc_src = "clkgen_x4"
scope.trigger.triggers = "tio4"
scope.io.tio1 = "serial_rx"
scope.io.tio2 = "serial_tx"
scope.io.hs2 = "clkgen"
scope.glitch.output = "glitch_only"
scope.io.glitch_lp = False
scope.io.glitch_hp = False
print(scope.io.glitch_lp)
print(scope.io.glitch_hp)
target.go_cmd = ""
target.key_cmd = ""

print("Erase target...")

# program the XMEGA with the built hex file
# programmer = AVRProgrammer()
programmer = XMEGAProgrammer()
programmer.scope = scope
programmer._logging = None
programmer.find()
# programmer.erase()

print("Programming...")

# programmer.program("~/software/chipwhisperer/hardware/victims/firmware/glitch-simple/glitchsimple-CW304.hex", memtype="flash")
programmer.program("glitchsimple.hex", memtype="flash",verify=True)
programmer.close()

scope.glitch.trigger_src = 'ext_single'

traces = []
outputs = []
widths = []
offsets = []

Range = namedtuple('Range', ['min', 'max', 'step'])

gc = support.GlitchCore()
# gc.setRepeatRange(55,105,3)
gc.setRepeat(1)
gc.setWidth(21.9)
gc.setOffsetRange(23.5,28.5,0.3)
gc.setExtOffset(15)

target.init()
gc.lock()

cs = chipshouter.ChipSHOUTER("/dev/ttyUSB0")
cs.voltage = 350
cs.pulse.width = 30
cs.pulse.repeat = 5
cs.pulse.deadtime = 15
cs.clr_armed = True
print("Give it a sec...")
time.sleep(3.0)
print("OK go...")

x = gc.generateFault()
while x is not None:
  (width,offset,ext,repeat) = x
  scope.glitch.width = width
  scope.glitch.offset = offset
  scope.glitch.ext_offset = ext
  scope.glitch.repeat = repeat

  output = ""
  # if target.in_waiting() != 0:
  #   target.flush()
  scope.io.pdic = "low"
  # print("Arm")
  scope.arm()
  scope.io.pdic = "high"
  target.ser.write("A")

  # ok, arm
  timeout = 100
  while target.isDone() is False and timeout != 0:
    timeout -= 1
    time.sleep(0.01)

  # print("Reading")

  output = target.ser.read(64, timeout=1000) #onl yneed first char
  print(repr(output))
  x = gc.generateFault()

print('Done')

cs.clr_armed = False

scope.dis()
target.dis()
