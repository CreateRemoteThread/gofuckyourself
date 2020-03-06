#!/usr/bin/env python3

# reader for KeepKey

import support
import phywhisperer.usb as pw
import base64
import pickle
import sys
import getopt
import csv
import string

# reads classifier csv
# and feeds it into classifier core

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Use: ./reader.py <blah>")
    sys.exit(0)

def tryhex(char_array):
  return "".join(["%02x" % x for x in char_array])

def tryfix(char_array):
  out = ""
  for c in char_array:
    if chr(c) in string.printable:
      out += chr(c)
    else:
      out += "."
  return out

phy = pw.Usb()

c = support.ReportingCore()
sanity = [75, 16, 3, 75, 0, 101, 0, 101, 0, 112, 0, 75, 0, 101, 0, 121, 0, 238, 104]
f = open(sys.argv[1],"r")
spamreader = csv.reader(f,delimiter=',')
for row in spamreader:
  (delay,width,output,rawdata) = row
  rawdata = rawdata[2:-1]
  print("%s:%s:%s" % (delay,width,output))
  delay = float(delay)
  width = int(width)
  muteFlag = False
  data = base64.b64decode(rawdata)
  data = pickle.loads(data)
  packets=phy.split_packets(data)
  printPackets=pw.USBSimplePrintSink(highspeed=1)
  for packet in packets:
    print(packet)
    printPackets.handle_usb_packet(ts=packet["timestamp"],buf=bytearray(packet["contents"]),flags=0)
    if packet["size"] == 3 and packet["contents"][0] == 45:
      print("SETUP, probably muted")
      c.addResult(delay,width,status=support.Status.Mute)
      muteFlag = True
    if packet["size"] > 3 and packet["contents"] != sanity:
      print(packet)
    if packet["size"] > 20:
      print(tryhex(packet["contents"]))
      print(tryfix(packet["contents"]))
      print("Pew!")
      c.addResult(delay,width,status=support.Status.Glitch)
      muteFlag = True
    if packet["contents"] == [45,0,16] and muteFlag is False:
      c.addResult(delay,width,status=support.Status.Mute)
      muteFlag = True
    if (len(packet["contents"]) == 3 and packet["contents"][0] == 165):
      continue
  if output == "KeepKey" and muteFlag is False:
    c.addResult(delay,width,status=support.Status.Expected)
    muteFlag = True
  if muteFlag is False:
    print("%f:MUTE:%s" % (delay,tryhex(packet["contents"])))
    c.addResult(delay,width,status=support.Status.Mute)

c.startPlot()
