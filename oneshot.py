#!/usr/bin/env python3

# this is a command line tool to help you
# eyeball glitch parameters and convert
# from time to percent of clock cycle.

import chipwhisperer as cw
import sys
import os

target = None
scope = None

# default config options

scope = cw.scope()
target = cw.target(scope)
scope.adc.samples = 3000
scope.adc.offset = 0
scope.adc.basic_mode = "rising_edge"
scope.clock.clkgen_freq = 8000000
scope.clock.adc_src = "clkgen_x1"
scope.trigger.triggers = "tio4"
scope.glitch.clk_src = "clkgen"
scope.glitch.output = "enable_only"
scope.io.glitch_lp = False
scope.io.glitch_hp = True
target.go_cmd = ""
target.key_cmd = ""
# scope.glitch.trigger_src = 'ext_single'
scope.glitch.trigger_src = 'manual'
target.init()

print("ok")

while True:
  cmd = input(" > ").lower().rstrip()
  if cmd in ("q","quit"):
    print("Bye")
    break
  elif cmd in ("f","fire"):
    scope.glitch.manual_trigger()
  else:
    r = eval(cmd)
    print(r)

sys.exit(0)
