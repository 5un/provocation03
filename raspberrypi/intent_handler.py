import RPi.GPIO as GPIO
import time
import board
import neopixel

class IntentHandler:

  def __init__(self):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(12, GPIO.OUT)
    self.servo = p = GPIO.PWM(12, 50)
    self.servo.start(7.5)

    self.pixels = pixels = neopixel.NeoPixel(board.D21, 1)

  def handle_misogynistic(self):
    # Control Neopixel
    self.pixels.fill((255, 0, 0))
    # Control The Servo
    self.servo.ChangeDutyCycle(12.5)
    pass

  def handle_supportive(self):
    # Control Neopixel
    self.pixels.fill((0, 255, 0))
    pass

  def handle_test(self):
    # Control Neopixel
    self.pixels.fill((255, 255, 255))
    pass

  def handle_intent(self, query_result):
    if query_result.intent is not None:
      name = query_result.intent.display_name
      if name == 'Misogynistic':
        self.handle_misogynistic()

      if name == 'Supportive':
        self.handle_supportive()

      if name == 'Test':
        self.handle_test()

  def clean_up():
    self.servo.stop()
    GPIO.cleanup()
    
