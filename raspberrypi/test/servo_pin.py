import RPi.GPIO as GPIO
import time
import sys

print("starting")

GPIO.setmode(GPIO.BCM)

pin = int(sys.argv[1])

GPIO.setup(pin, GPIO.OUT)

p = GPIO.PWM(pin, 50)

p.start(1)

try:
    while True:
        print('cycle')
        p.ChangeDutyCycle(5)  # turn towards 90 degree
        time.sleep(5) # sleep 1 second
        p.ChangeDutyCycle(1)  # turn towards 0 degree
        time.sleep(5) # sleep 1 second
        # p.ChangeDutyCycle(12.5) # turn towards 180 degree
        # time.sleep(1) # sleep 1 second
except KeyboardInterrupt:
    p.stop()
    GPIO.cleanup()
