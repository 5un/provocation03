import RPi.GPIO as GPIO
import time

print("starting")

GPIO.setmode(GPIO.BCM)

GPIO.setup(12, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.output(12, GPIO.LOW)
GPIO.output(13, GPIO.LOW)

try:
    while True: # Run forever
        GPIO.output(12, GPIO.HIGH) # Turn on
        GPIO.output(13, GPIO.HIGH) # Turn on
        time.sleep(1)                  # Sleep for 1 second
        GPIO.output(12, GPIO.LOW)  # Turn off
        GPIO.output(13, GPIO.LOW)  # Turn off
        time.sleep(1)                  # Sleep for 1 second
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
   print("Keyboard interrupt")

except:
   print("some error") 

finally:
   print("clean up") 
   GPIO.cleanup() # cleanup all GPIO 