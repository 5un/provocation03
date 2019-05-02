import apa102
import time

pixels = apa102.APA102(num_led=3)
pixels.set_pixel(0, 255, 0, 0)
pixels.set_pixel(1, 0, 255, 0)
pixels.set_pixel(2, 0, 0, 255)
pixels.show()

time.sleep(1)

pixels.set_pixel(0, 0, 0, 0)
pixels.set_pixel(1, 0, 0, 0)
pixels.set_pixel(2, 0, 0, 0)
pixels.show()
