#!/usr/bin/python

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sys

# screen fix
mpl.rcParams['agg.path.chunksize'] = 10000

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print "usage: ./lol [traces.npz]"
    sys.exit(0)
  array = np.load(sys.argv[1])
  print array.files
  # 44, 3000. plot a sample of 3000.
  print array["arr_0"].shape
  plt.plot(array["arr_0"][int(sys.argv[2]),:])
  plt.show()
