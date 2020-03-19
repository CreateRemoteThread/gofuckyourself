#!/usr/bin/env python3

import sys
import logging
import chipwhisperer as cw
import time
import pylink
import support

print("Configuring CW")
logging.basicConfig(level = logging.WARN)
scope = cw.scope()
target = cw.target(scope)

scope.adc.samples = 3000
scope.adc.offset = 0
scope.adc.basic_mode = "rising_edge"
scope.clock.clkgen_freq = 8000000 # 120000000 # 7370000
scope.clock.adc_src = "clkgen_x1"
scope.trigger.triggers = "tio4"
scope.glitch.clk_src = "clkgen"
scope.glitch.output = "enable_only"
scope.io.glitch_lp = False
scope.io.glitch_hp = True
target.go_cmd = ""
target.key_cmd = ""
scope.glitch.trigger_src = 'ext_single'

scope.glitch.ext_offset = 22
scope.glitch.width = 45
scope.glitch.repeat = 4

trycounter = 0
CONFIG_TRY = 2500

print("Configuring JLink")
jlink = pylink.JLink()
jlink.open()

gc = support.GlitchCore()
gc.setRepeatRange(2,20,1)
gc.setWidth(45)
gc.setOffset(1)
gc.setExtOffsetRange(800,1600,1)
gc.lock()

target.init()
trycounter = 0
while trycounter < CONFIG_TRY:
  scope.io.target_pwr = False
  x = gc.generateRandomFault()
  (width,offset,ext,repeat) = x
  trycounter += 1
  scope.glitch.repeat = repeat
  scope.glitch.ext_offset = ext
  print("Trying (try:%d,wait:%d,repeat:%d)..." % (trycounter,scope.glitch.ext_offset,scope.glitch.repeat))
  scope.arm()
  time.sleep(1.0)
  scope.io.target_pwr = True
  timeout = 100000
  while target.isDone() is False and timeout > 0:
    timeout -= 1
    time.sleep(0.01)
  if timeout == 0:
    print("scope timed out!")
  time.sleep(1.0)
  jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
  try:
    r = jlink.connect("CORTEX-M0",verbose=True)
  except:
    r = False
  if r is False:
    scope.io.target_pwr = False
    time.sleep(1)
  else:
    print("Connected!")
    while True:
      x = eval(raw_input("py > "))

target.dis()
scope.dis()

print("Bye!")

