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
  def __init__(self,prefix):
    self.csvname = "%s-output.csv" % prefix
    self.npzname = "%s-traces.npz" % prefix

  def scatterWinCases(self):
    sr = csv.reader(open(self.csvname),delimiter=',',quotechar='\'')
    p_ext_offset = []
    p_offset = []
    p_width = []
    p_repeat = []
    for row in sr:
      (output,hash,ext_offset,offset,width,repeat,success) = row
      if success == "True":
        p_ext_offset.append(int(ext_offset))
        p_offset.append(float(offset))
        p_width.append(float(width))
        p_repeat.append(int(repeat))
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')
    ax.scatter(p_ext_offset,p_offset,p_width)
    ax.set_xlabel("Ext. Offset")
    ax.set_ylabel("Offset")
    ax.set_zlabel("Width")
    plt.show()    

mpl.rcParams['agg.path.chunksize'] = 10000

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "usage: ./swiper.py [set-prefix]"
    sys.exit(0)
  if not (os.path.isfile("%s-output.csv" % sys.argv[1]) and os.path.isfile("%s-traces.npz" % sys.argv[1])):
    print "Cannot find %s-output.csv or %s-traces.npz" % (sys.argv[1],sys.argv[1])
    sys.exit(0)
  gdm = GlitchDataManager(sys.argv[1])
  gdm.scatterWinCases()
