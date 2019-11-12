#!/usr/bin/env python3

from collections import namedtuple 

Range = namedtuple("Range",["min","max","step"])

class GlitchCore:
  def __init__(self):
    self.widthRange = Range(0,1,2)
    self.extOffsetRange = Range(0,1,2)
    self.repeatRange = Range(0,1,2)
    self.offsetRange = Range(0,1,2)

  def setWidthRange(self,width_min,width_max,width_step):
    self.widthRange = Range(width_min,width_max,width_step)      

  def setWidth(self,width):
    self.widthRange = Range(width,width+1.0,2.0)

  def setOffsetRange(self,offset_min,offset_max,offset_step):
    self.offsetRange = Range(offset_min,offset_max,offset_step)

  def setOffset(self,offset):
    self.offsetRange = Range(offset,offset+1,2)

  def setExtOffsetRange(self,ext_offset_min,ext_offset_max,ext_offset_step):
    self.extOffsetRange = Range(ext_offset_min,ext_offset_max,ext_offset_step)

  def setExtOffset(self,ext_offset):
    self.extOffsetRange = Range(ext_offset,ext_offset + 1, 2)

  def setRepeat(self,repeat):
    self.repeatRange = Range(repeat,repeat+1,2)
  
  def setRepeatRange(self,repeat_min,repeat_max,repeat_step):
    self.repeatRange = Range(repeat_min,repeat_max,repeat_step)

  def lock(self):
    self.currentWidth = self.widthRange.min
    self.currentOffset = self.offsetRange.min
    self.currentExtOffset = self.extOffsetRange.min
    self.currentRepeat = self.repeatRange.min

  def generateFault(self):
    # print(self.extOffsetRange)
    while self.currentWidth < self.widthRange.max:
      while self.currentOffset < self.offsetRange.max:
        while self.currentExtOffset < self.extOffsetRange.max:
          while self.currentRepeat < self.repeatRange.max:
            self.currentRepeat += self.repeatRange.step
            print("W:%f,O:%f,R:%d,E:%d" % (self.currentWidth,self.currentOffset,self.currentRepeat,self.currentExtOffset))
            return (self.currentWidth,self.currentOffset,self.currentExtOffset,self.currentRepeat)
          self.currentExtOffset += self.extOffsetRange.step
          self.currentRepeat = self.repeatRange.min
          # print("Adding Ext")
        self.currentOffset += self.offsetRange.step
        self.currentExtOffset = self.extOffsetRange.min
        # print("Adding Offset")
      self.currentWidth += self.widthRange.step
      self.currentOffset = self.offsetRange.min
      # print("Adding Width")
    return None

if __name__ == "__main__":
  print("test")
  gc = GlitchCore() 
  gc.setWidth(15.5)
  gc.setOffsetRange(20.3,20.9,0.2)
  gc.setExtOffsetRange(20,50,3)
  gc.setRepeat(50)
  gc.lock()
  # generate a fault.
  gcx = gc.generateFault()
  while gcx:
    gcx = gc.generateFault()