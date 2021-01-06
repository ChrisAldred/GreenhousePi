import RPi.GPIO as GPIO
import time
import spidev
# Static variable to define if Light is currently on
isLightOn = False

# Set-Up GPIO Pinfor water
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.OUT)
GPIO.output(2, False)

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def readAnalogue(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

while True:
        if (readAnalogue(0) < 150 and isLightOn == False):
                GPIO.output(2, True)
                isLightOn = True
        elif (readAnalogue(0) > 200 and isLightOn == True):
                GPIO.output(2, False)
                isLightOn = False
        time.sleep(15)
