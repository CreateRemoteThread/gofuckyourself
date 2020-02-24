#!/usr/bin/env python3

import support
import phywhisperer.usb as pw
import base64
import pickle
import sys
import getopt
import csv

# reads classifier csv
# and feeds it into classifier core

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Use: ./reader.py <blah>")
    sys.exit(0)

phy = pw.Usb()

c = support.ReportingCore()

f = open(sys.argv[1],"r")
spamreader = csv.reader(f,delimiter=',')
for row in spamreader:
  (delay,width,output,rawdata) = row
  output = output[2:-1]
  rawdata = rawdata[2:-1]
  print("%s:%s:%s" % (delay,width,base64.b64decode(output)))
  delay = float(delay)
  width = int(width)
  if base64.b64decode(output) == b'HelloHelloHelloHelloHello':
    c.addResult(delay,width,status=support.Status.Expected)
  else:
    c.addResult(delay,width,status=support.Status.Mute)
  data = base64.b64decode(rawdata)
  data = pickle.loads(data)
  packets=phy.split_packets(data)
  printPackets=pw.USBSimplePrintSink(highspeed=1)
  for packet in packets:
    printPackets.handle_usb_packet(ts=packet['timestamp'],buf=bytearray(packet['contents']),flags=0)

c.startPlot()
