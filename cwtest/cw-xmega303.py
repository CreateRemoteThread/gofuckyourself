#!/usr/bin/env python3

import time
import logging
import os
from collections import namedtuple
import csv

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
# scope.io.hs2 = "glitch"
scope.io.hs2 = "clkgen"
scope.glitch.output = "glitch_only"
scope.io.glitch_lp = True
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


programmer.program("glitchsimple-CW303.hex", memtype="flash", verify=True)
programmer.close()

scope.glitch.trigger_src = 'ext_single'

traces = []
outputs = []
widths = []
offsets = []

Range = namedtuple('Range', ['min', 'max', 'step'])
repeat_range = Range(105,125,3)
# width_range = Range(15.85,16.3, 0.1)
width_range = Range(19.2,22.9,0.2)
offset_range = Range(-30,30, 0.7)
ext_offset_range = Range(25000,59190,100)
scope.glitch.ext_offset = ext_offset_range.min
scope.io.pdic = 'high'

scope.glitch.offset = 20.0

# pew pew pew
scope.glitch.width = width_range.min
target.init()
while scope.glitch.width < width_range.max:
  while scope.glitch.ext_offset < ext_offset_range.max:
    scope.glitch.repeat = repeat_range.min
    while scope.glitch.repeat < repeat_range.max:
      output = ""
      target.ser.flush()

      scope.io.pdic = 'low'
      scope.io.pdic = 'high'

      scope.arm()
      target.ser.write("1")
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
      output = target.ser.read(64, timeout=500)
      print("R=%d:W=%f:E=%d:%s" % (scope.glitch.repeat,scope.glitch.width,scope.glitch.ext_offset,repr(output)))
      # traces.append(trace)
      scope.glitch.repeat += repeat_range.step
    print("Adding e...")
    scope.glitch.ext_offset += ext_offset_range.step
  print("Adding w...")
  scope.glitch.width += width_range.step
print('Done')

# np.save("lol.npy",traces)

scope.dis()
target.dis()
