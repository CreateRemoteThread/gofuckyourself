#!/usr/bin/env python3

import phywhisperer.usb as pw
import csv
import base64
import random

f_csv = open("classifier.csv","w")
spamwriter = csv.writer(f_csv,delimiter=',',quotechar='\"')

import sys

print("Configuring PhyWhispererUSB")
phy = pw.Usb()
# phy.set_usb_mode("LS")
phy.con(program_fpga = True)
phy.reset_fpga()
phy.addpattern = True
phy.set_power_source("off")
pattern = [ord(x) for x in "xyabc123"]
pattern_true = [ord(x) for x in "Hello"]
print(pattern)
phy.set_trigger(num_triggers=1,delays=[0],widths=[100])
phy.set_pattern(pattern_true,mask=[0xff for c in pattern_true])
import time

print("Configuring ChipWhisperer")
import chipwhisperer as cw
scope = cw.scope()
target = cw.target(scope)

scope.adc.samples = 3000
scope.adc.offset = 45
scope.adc.basic_mode = "rising_edge"
scope.clock.clkgen_freq = 120000000
scope.clock.adc_src = "clkgen_x4"
scope.trigger.triggers = "tio4"
scope.glitch.clk_src = "clkgen"
scope.glitch.output = "enable_only"
scope.io.glitch_lp = False
scope.io.glitch_hp = True
target.go_cmd = ""
target.key_cmd = ""

target.init()

scope.glitch.output = "enable_only"
scope.glitch.width = 45
scope.glitch.trigger_src = 'ext_single'

from keepkeylib.client import KeepKeyClient, KeepKeyClientVerbose, KeepKeyDebuglinkClient, KeepKeyDebuglinkClientVerbose
import keepkeylib.types_pb2 as types
from keepkeylib.transport_hid import HidTransport

scope.glitch.offset=45
quietMode = False

for i in range(0,1000):
  try_ext_offset = 30
  try_repeat = 67
  scope.glitch.ext_offset = try_ext_offset
  scope.glitch.repeat = try_repeat
  print("Preparing for glitch at %d, %d width" % (try_ext_offset,try_repeat))
  phy.set_power_source("off")
  # phy.set_usb_mode(mode="LS")
  time.sleep(0.5)
  phy.set_power_source("host")
  time.sleep(3.0)
  try:
    path = HidTransport.enumerate()[0][0]
  except:
    print("Enumerate failed, continuing next pass")
    continue
  for d in HidTransport.enumerate():
    if path in d:
      transport = HidTransport(d)
      break
  phy.set_capture_size(1025)
  client = KeepKeyClient(transport)
  scope.arm()
  time.sleep(0.5)
  phy.arm()
  time.sleep(0.5)
  input("Logic!")
  time.sleep(0.5)
  data = client.ping("HelloHelloHelloHelloHello")
  print(data)
  data = base64.b64encode(data.encode("utf-8"))
  time.sleep(0.5)
  input("Did we fire?")
  if quietMode:
    continue
  phy.wait_disarmed()
  sys.exit(0)
  spamwriter.writerow([try_ext_offset,try_repeat,data])
  raw = phy.read_capture_data()
  packets = phy.split_packets(raw)
  printPackets = pw.USBSimplePrintSink(highspeed=phy.get_usb_mode() == 'HS')
  for packet in packets:
    printPackets.handle_usb_packet(ts=packet['timestamp'],buf=bytearray(packet['contents']),flags=0)


f_csv.close()
print("Done!")
sys.exit(0)


# f_csv.close()
