#!/usr/bin/env python3

# this causes flash corruption [?] in the cw303 xmega target
# power cycling does nothing, reprogram your target to keep playing.

import time
import logging
import os
from collections import namedtuple
import csv
import random

import numpy as np

import chipwhisperer as cw
from chipwhisperer.capture.api.programmers import XMEGAProgrammer
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
scope.io.glitch_hp = True
print(scope.io.glitch_lp)
print(scope.io.glitch_hp)
target.go_cmd = ""
target.key_cmd = ""

print("Erase target...")

# program the XMEGA with the built hex file
programmer = XMEGAProgrammer()
programmer.scope = scope
programmer._logging = None
programmer.find()
programmer.erase()

print("Programming...")


programmer.program("glitchsimple.hex", memtype="flash", verify=True)
programmer.close()

scope.glitch.trigger_src = 'ext_single'

traces = []
outputs = []
widths = []
offsets = []

Range = namedtuple('Range', ['min', 'max', 'step'])
repeat_range = Range(1,5,2)
width_range = Range(19.3,20.4,0.3)
offset_range = Range(29.9,30.7,0.3)
scope.glitch.ext_offset = 5

# scope.glitch.offset = 27.7

scope.glitch.offset = offset_range.min

# pew pew pew
scope.glitch.width = width_range.min
target.init()
while scope.glitch.width < width_range.max:
  while scope.glitch.offset < offset_range.max:
    scope.glitch.repeat = repeat_range.min
    while scope.glitch.repeat < repeat_range.max:
      output = ""
      target.ser.flush()

      scope.io.pdic = 'low'
      scope.io.pdic = 'high'

      scope.arm()
      timeout = 100
      while target.isDone() is False and timeout:
        timeout -= 1
        time.sleep(0.01)

      try:
        ret = scope.capture()
        if ret:
          logging.warning('Timeout happened during acquisition')
      except IOError as e:
        logging.error('IOError: %s' % str(e))

      trace = scope.get_last_trace()
      output = target.ser.read(64, timeout=500) #onl yneed first char
      scope.glitch.width_fine = random.randint(0,100)
      print("R=%d:W=%f:O=%f:%s" % (scope.glitch.repeat,scope.glitch.width,scope.glitch.offset,repr(output)))
      if "1234" in output:
        print("done")
        scope.dis()
        target.dis()
        import sys
        sys.exit(0)
      # traces.append(trace)
      scope.glitch.repeat += repeat_range.step
    print("Adding e...")
    scope.glitch.offset += offset_range.step
  print("Adding w...")
  scope.glitch.width += width_range.step
  scope.glitch.offset = offset_range.min
print('Done')

scope.dis()
target.dis()
