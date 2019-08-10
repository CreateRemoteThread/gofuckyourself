#!/usr/bin/env python

# hostrun

import sys;
import binascii;
import array;
import time;
import warnings

from testusb import GoodFETMAXUSBHost;

client=GoodFETMAXUSBHost();
client.serInit()

client.MAXUSBsetup();

client.hostinit();
client.usbverbose=True;

client.hostrun();
