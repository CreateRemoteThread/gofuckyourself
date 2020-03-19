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
scope.glitch.output = "glitch_only"
scope.io.glitch_lp = False
scope.io.glitch_hp = True
target.go_cmd = ""
target.key_cmd = ""
scope.glitch.trigger_src = 'ext_single'

scope.glitch.ext_offset = 22
scope.glitch.width = 5
scope.glitch.repeat = 4

trycounter = 0
CONFIG_TRY = 5000

print("Configuring JLink")
jlink = pylink.JLink()
jlink.open()

gc = support.GlitchCore()
gc.setRepeatRange(1,2,1)
gc.setWidthRange(20,45,1)
# gc.setWidth(45i)
gc.setOffset(1)
gc.setExtOffsetRange(1200,1800,1)
gc.lock()

target.init()
trycounter = 0
while trycounter < CONFIG_TRY:
  scope.io.target_pwr = False
  x = gc.generateRandomFault()
  (width,offset,ext,repeat) = x
  trycounter += 1
  scope.glitch.width=width
  scope.glitch.repeat = 1
  scope.glitch.ext_offset = ext
  print("Trying (try:%d,wait:%d,width:%f)..." % (trycounter,scope.glitch.ext_offset,scope.glitch.width))
  scope.arm()
  time.sleep(0.25)
  scope.io.target_pwr = True
  timeout = 100000
  while target.isDone() is False and timeout > 0:
    timeout -= 1
    time.sleep(0.01)
  if timeout == 0:
    print("scope timed out!")
  time.sleep(0.25)
  jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
  try:
    r = jlink.connect("CORTEX-M3",verbose=True)
  except Exception as e:
    print(e,flush=True)
    r = False
  if r is False:
    scope.io.target_pwr = False
    time.sleep(0.25)
  else:
    print("Connected!")
    while True:
      x = eval(raw_input("py > "))

target.dis()
scope.dis()

print("Bye!")

