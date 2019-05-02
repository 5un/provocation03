import apa102
import time

class LEDHelper:
  def __init__(self):
    self.pixels = apa102.APA102(num_led=3)

  def clear(self, color=(0,0,0)):
    for i in range(3):
      self.pixels.set_pixel(i, color[0], color[1], color[2])
      self.pixels.show()

  def set_pixel(self, index, color)
    self.pixels.set_pixel(index, color[0], color[1], color[2])
    self.pixels.show()

  def pulse(self, color=(255,255,255), num_repeat=1):
    self.clear()
    for r in range(num_repeat):
      b = 0
      while b < 1.0:
        self.clear(color=(int(color[0] * b), int(color[1] * b), int(color[2] * b)))
        time.sleep(0.05)
        b += 0.05
      
      while b > 0.0:
        self.clear(color=(int(color[0] * b), int(color[1] * b), int(color[2] * b)))
        time.sleep(0.05)
        b -= 0.05

  def blink(self, color=(255,255,255), num_repeat=1, duration=1.0):
    self.clear()
    for r in range(num_repeat):
      self.clear()
      time.sleep(duration)
      self.clear(color=color)
      time.sleep(duration)

  def knight_rider(self, color=(255,255,255), num_repeat=1, duration=0.5):
    black = (0,0,0)
    for r in range(num_repeat):
      self.set_pixel(0, color)
      self.set_pixel(1, black)
      self.set_pixel(2, black)
      time.sleep(duration)
      self.set_pixel(0, black)
      self.set_pixel(1, color)
      self.set_pixel(2, black)
      time.sleep(duration)
      self.set_pixel(0, black)
      self.set_pixel(1, black)
      self.set_pixel(2, color)
      time.sleep(duration)
      self.set_pixel(0, black)
      self.set_pixel(1, black)
      self.set_pixel(2, black)
      time.sleep(duration)
