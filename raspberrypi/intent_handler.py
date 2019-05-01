import RPi.GPIO as GPIO
import time

class IntentHandler:

  def __init__(self):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(12, GPIO.OUT)
    self.servo = p = GPIO.PWM(12, 50)
    self.servo.start(7.5)

  def handle_misogynistic(self):
    # Control Neopixel
    # Control The Servo
    self.servo.ChangeDutyCycle(12.5)
    pass

  def handle_assertive(self):
    # Control Neopixel
    
    pass

  def handle_test(self):
    # Control Neopixel
    pass

  def handle_intent(self, query_result):
    if query_result.intent is not None:
      name = query_result.intent.display_name
      if name == 'Misogynistic':
        self.handle_misogynistic()

      if name == 'Assertive'
        self.handle_assertive()

      if name == 'Test'
        self.handle_test()

  def clean_up():
    self.servo.stop()
    GPIO.cleanup()
    