#!/usr/bin/python

# swiper.py: glitch success aggregator

from mpl_toolkits.mplot3d import Axes3D
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import numpy as np
import csv

class GlitchDataManager:
  def __init__(self):
    self.rdb = {}
    self.dataIndex = 0
    pass

  def loadData(self, prefix):
    f = open("%s-output.csv" % prefix)
    sr = csv.reader(f,delimiter=',',quotechar='\'')
    for r in sr:
      (output,hash,ext_offset,offset,width,repeat,success) = r
      if output == "Output":
        continue
      self.rdb[self.dataIndex] = (output,hash,int(ext_offset),float(offset),float(width),int(repeat),success == "True")
      self.dataIndex += 1
    f.close()

  def scatterWinCases(self,ignore="repeats"):
    p_ext_offset = []
    p_offset = []
    p_width = []
    p_repeat = []
    p_hashes = []
    for i in range(0,self.dataIndex):
      row = self.rdb[i]
      (output,hash,ext_offset,offset,width,repeat,success) = row
      if success == True:
        p_ext_offset.append(int(ext_offset))
        p_offset.append(float(offset))
        p_width.append(float(width))
        p_repeat.append(int(repeat))
        p_hashes.append(hash)
    p_hashmapc = []
    for i in range(0,len(p_hashes)):
      p_hashmapc.append(p_hashes.count(p_hashes[i]))
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')
    ax.scatter(p_ext_offset,p_offset,p_width,c=p_hashmapc,cmap='viridis')
    ax.set_xlabel("Ext. Offset")
    ax.set_ylabel("Offset")
    ax.set_zlabel("Width")
    plt.title("Glitch Successes")
    ax.legend()
    plt.show()    

mpl.rcParams['agg.path.chunksize'] = 10000

if __name__ == "__main__":
  if len(sys.argv) == 1:
    print "usage: ./swiper.py [set-prefix]"
    sys.exit(0)
  gdm = GlitchDataManager()
  for i in range(0,len(sys.argv[1:])):
    gdm.loadData(sys.argv[1 + i])
  gdm.scatterWinCases()
