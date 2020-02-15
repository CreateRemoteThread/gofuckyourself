#!/usr/bin/env python3

import base64
import csv
import sys
import glob
import re

crashes = 0
entries = 0
wins = 0

PC_crashes = {}

for fn in glob.glob("logs/*.csv"):
  with open(fn) as csvfile:
    csvreader = csv.reader(csvfile,delimiter=',')
    for row in csvreader:
      entries += 1
      (loc,len,result) = row
      result = result[2:-1]
      if result == "Li90cnltZQ0KNjI1MDAwMA0KZ3JpOjEwMDAvMTAwMC8xMDAwcGlAcmFzcGJlcnJ5cGk6fiQg":
        continue
      else:
        try:
          result = base64.b64decode(result).decode("utf-8")
        except:
          continue
        print(result)
        crashes += 1
        if "winner" in result:
          wins += 1
        if "PC is at" in result:
          f = re.search("PC is at (.*?)\r",result)
          pc_result = f.groups(0)[0]
          if pc_result in PC_crashes.keys():
            PC_crashes[pc_result] += 1
          else:
            PC_crashes[pc_result] = 1

print("Statistics...")
print("%d Wins" % wins)
print("%d Crashes" % crashes)
print("%d Total Entries" % entries)

d_view = [(d,v) for (v,d) in list(PC_crashes.items())]
d_view.sort(reverse=True)

for d,v in d_view:
  print("%s:%d" % (v,d))

# for x in PC_crashes.keys():
#   print("%s:%d" % (x,PC_crashes[x]))
