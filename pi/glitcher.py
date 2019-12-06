#!/usr/bin/env python3

import time
import logging
import os
from collections import namedtuple
import csv
import serial

import numpy as np
import sys

import chipwhisperer as cw
logging.basicConfig(level=logging.WARN)
scope= cw.scope()
target = cw.target(scope)

scope.adc.samples = 3000
scope.adc.offset = 0
scope.adc.basic_mode = "rising_edge"
scope.clock.clkgen_freq = 120000000 # 7370000
scope.clock.adc_src = "clkgen_x1"
scope.io.tio1 = "serial_rx"
scope.io.tio2 = "serial_tx"
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
scope.glitch.repeat = 175
scope.glitch.ext_offset =5

target.baud = 115200
target.init()

scope.io.pdic = "low"

ser = serial.Serial("/dev/ttyUSB0",baudrate=115200)

def resetDevice():
  scope.io.pdic = "high"
  time.sleep(0.3)
  scope.io.pdic = "low"

def doLogin():
  print("Waiting for login...")
  ser.read_until(b"raspberrypi login")
  ser.write(b"pi\n")
  print("Waiting for password...")
  ser.read_until(b"Password:")
  ser.write(b"raspberry\r\n")
  print("Waiting for shell...")
  ser.read_until(b"pi@raspberrypi")

ser.flush()
resetDevice()
doLogin()

while True:
  scope.arm()
  ser.write(b"./tryme")
  timeout = 10000
  while target.isDone() is False and timeout:
    timeout -= 1
    time.sleep(0.01)
  try:
    ret = scope.capture()
    if ret:
      print("Error: timeout during acquisition") 
  except IOError as e:
    print(e)
  ser.timeout = 10
  d = ser.read(1024)
  ser.timeout = None
  if b"dinner" in d:
    print("Op success.")
    scope.dis()
    target.dis()
    sys.exit(0)
  elif b"pi@raspberrypi" in d:
    print("Device seems ok")
    pass
  else:
    print("Resetting device")
    ser.flush()
    resetDevice()
    doLogin()

scope.dis()
target.dis()
sys.exit(0)

