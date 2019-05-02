import board
import neopixel
pixels = neopixel.NeoPixel(board.D12, 1)

# pixels[0] = (255, 0, 0)
pixels.fill((255, 255, 0))
