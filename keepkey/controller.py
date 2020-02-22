#!/usr/bin/env python3

import phywhisperer.usb as pw
import csv
import base64
import random

f_csv = open("classifier.csv","w")
spamwriter = csv.writer(f_csv,delimiter=',',quotechar='\"')

print("Configuring PhyWhispererUSB")
phy = pw.Usb()
# phy.set_usb_mode("LS")
phy.con(program_fpga = True)
phy.addpattern = True
phy.set_power_source("off")
phy.reset_fpga()
pattern = [ord(x) for x in "Hello"]
phy.set_pattern(pattern)
phy.set_power_source("host")
import time

print("Configuring ChipWhisperer")
import chipwhisperer as cw
scope = cw.scope()
target = cw.target(scope)

scope.adc.samples = 3000
scope.adc.offset = 45
scope.adc.basic_mode = "rising_edge"
# scope.clock.clkgen_freq = 8000000 # 7370000
scope.clock.clkgen_freq = 8000000
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

target.init()

scope.glitch.output = "enable_only"
scope.glitch.width = 45

from keepkeylib.client import KeepKeyClient, KeepKeyClientVerbose, KeepKeyDebuglinkClient, KeepKeyDebuglinkClientVerbose
import keepkeylib.types_pb2 as types
from keepkeylib.transport_hid import HidTransport

scope.glitch.offset=45
quietMode = False

for i in range(0,1000):
  try_ext_offset = i
  try_repeat = random.randint(1,2)
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
  phy.set_trigger(enable=True)
  scope.arm()
  phy.arm()
  time.sleep(0.5)
  try:
    data = client.ping("HelloHelloHelloHelloHello")
    print(data)
    data = base64.b64encode(data.encode("utf-8"))
  except:
    data = ""
  time.sleep(0.5)
  if quietMode:
    continue
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
