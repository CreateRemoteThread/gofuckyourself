#!/usr/bin/env python3

# use the glitch adapter.

import phywhisperer.usb as pw
import csv
import base64
import random
import pickle
import signal

f_csv = open("classifier.csv","w")
spamwriter = csv.writer(f_csv,delimiter=',',quotechar='\"')

import sys

refptn = [195, 63, 35, 35, 0, 2, 0, 0, 0, 27, 10, 25, 72, 101, 108, 108, 111, 72, 101, 108, 108, 111, 72, 101, 108, 108, 111, 72, 101, 108, 108, 111, 72, 101, 108, 108, 111, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 206, 206]

print("Configuring PhyWhispererUSB")
phy = pw.Usb()
# phy.set_usb_mode("LS")
phy.con(program_fpga = True)
phy.reset_fpga()
phy.addpattern = True
phy.set_power_source("off")
pattern = [ord(x) for x in "xyabc123"]
pattern_true = [ord(x) for x in "HelloHelloHelloHelloHello"]
print(pattern)
import time

from keepkeylib.client import KeepKeyClient, KeepKeyClientVerbose, KeepKeyDebuglinkClient, KeepKeyDebuglinkClientVerbose
import keepkeylib.types_pb2 as types
from keepkeylib.transport_hid import HidTransport

quietMode = False
oneshot = False

# dx = 0.6558979765582688 # usb corruption.
# dx = 0.6519845071548444
d =0.165299
# dx = None

def sighandler(signum,frame):
  print("Exception handler hit!")
  raise Exception("bye")

signal.signal(signal.SIGALRM,sighandler)

# randomize in the phywhisperer. 
for i in range(1,1000):
  if dx is None:
    delay = random.uniform(0.1,0.9)
  else:
    delay = random.uniform(dx - 0.05,dx + 0.05)
  width = random.randint(55,75)
  phy.set_trigger(num_triggers=1,delays=[phy.ms_trigger(delay)],widths=[width])
  phy.set_pattern(pattern_true,mask=[0xff for c in pattern_true])
  print("Preparing for attempt %d, glitch at %f, %d width" % (i,delay,width))
  phy.set_power_source("off")
  # phy.set_usb_mode(mode="LS")
  time.sleep(0.5)
  phy.set_power_source("host")
  time.sleep(3.0)
  enumerateStatus = False
  enumerateCount = 0
  while enumerateStatus is False:
    try:
      signal.alarm(10)
      print("Attempting enumeration...")
      path = HidTransport.enumerate()[0][0]
      print("Path OK!")
      enumerateStatus = True
      signal.alarm(0)
    except:
      print("Enumerate failed, continuing next pass")
      time.sleep(0.5)
      if enumerateCount == 3:
        break
      enumerateCount += 1
      continue
  if enumerateStatus is False:
    print("Enumerate hard failed, power cycling")
    continue
  print("Fetching path...")
  for d in HidTransport.enumerate():
    if path in d:
      transport = HidTransport(d)
      break
  print("Transport locked, continuing...")
  phy.set_capture_size(1025)
  client = KeepKeyClient(transport)
  print("KeepKeyClient OK, arming glitcher...")
  phy.arm()
  print("Arm OK")
  if oneshot:
    input("Hit enter to fire glitch event...")
  try:
    signal.alarm(10)
    data = client.ping("HelloHelloHelloHelloHello")
    print(data)
    if data != "HelloHelloHelloHelloHello":
      sys.exit(0)
    data = base64.b64encode(data.encode("utf-8"))
  except:
    data = ""
  print("Waiting for disarm...")
  phy.wait_disarmed()
  if quietMode:
    continue
  raw = phy.read_capture_data()
  packets = phy.split_packets(raw)
  spamwriter.writerow([delay,width,data,base64.b64encode(pickle.dumps(raw))])
  printPackets = pw.USBSimplePrintSink(highspeed=phy.get_usb_mode() == 'HS')
  for packet in packets:
    printPackets.handle_usb_packet(ts=packet['timestamp'],buf=bytearray(packet['contents']),flags=0)
    if packet["size"] > 30:
      if packet["contents"] != refptn:
        print("Glitch here!")
  if oneshot:
    print("Oneshot test mode, bye!")
    sys.exit(0)

f_csv.close()
print("Done!")
sys.exit(0)

