#!/usr/bin/env python3

import time
import logging
import os
from collections import namedtuple
import csv

import numpy as np

import chipwhisperer as cw
logging.basicConfig(level=logging.WARN)
scope= cw.scope()
target = cw.target(scope)

scope.adc.samples = 3000
scope.adc.offset = 0
scope.adc.basic_mode = "rising_edge"
scope.clock.clkgen_freq = 120000000 # 7370000
scope.clock.adc_src = "clkgen_x1"
scope.trigger.triggers = "tio4"
scope.glitch.clk_src = "clkgen"
scope.glitch.output = "enable_only"
scope.io.glitch_lp = False
scope.io.glitch_hp = True
target.go_cmd = ""
target.key_cmd = ""

print(scope.clock.clkgen_freq)

scope.glitch.trigger_src = 'ext_single'
print("OK, go")

scope.glitch.offset = 45
scope.glitch.width = 45
scope.glitch.repeat = 165
scope.glitch.ext_offset =5

target.init()

while True:
  print("Arming scope...")
  scope.arm()
  timeout = 100000
  while target.isDone() is False and timeout:
    timeout -= 1
    time.sleep(0.01)
  try:
    ret = scope.capture()
    if ret:
      print("Error: timeout during acquisition")
  except IOError as e:
    print(e)

scope.dis()
target.dis()
