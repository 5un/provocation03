import RPi.GPIO as GPIO
import time
import board
import neopixel

class IntentHandler:

  def __init__(self, leds):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(12, GPIO.OUT)
    self.servo = p = GPIO.PWM(12, 50)
    self.servo.start(7.5)

    self.leds = leds
    self.pixels = neopixel.NeoPixel(board.D13, 1)

  def handle_misogynistic(self):
    # Control The Servo
    self.servo.ChangeDutyCycle(12.5)
    time.sleep(1)
    self.servo.ChangeDutyCycle(7.5)

    self.leds.blink(color=(255,0,0), num_repeat=3, duration=0.25)
    # Control Neopixel
    # self.pixels.fill((255, 0, 0))
    pass

  def handle_supportive(self):
    # Control Neopixel
    self.leds.blink(color=(255,0,255), num_repeat=3, duration=0.25)
    # self.pixels.fill((0, 255, 0))
    pass

  def handle_test(self):
    # Control Neopixel
    self.leds.blink(color=(128,128,128), num_repeat=3, duration=0.25)
    # self.pixels.fill((255, 255, 255))
    pass

  def handle_intent(self, query_result):
    print('Handling Intent...')
    if (query_result.intent is not None) and (query_result.intent.display_name is not None):
      name = query_result.intent.display_name
      if name == 'Misogynistic':
        self.handle_misogynistic()

      if name == 'Supportive':
        self.handle_supportive()

      if name == 'Test':
        self.handle_test()

  def clean_up(self):
    self.servo.stop()
    GPIO.cleanup()
    
