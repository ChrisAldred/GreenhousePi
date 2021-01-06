from time import sleep
import RPi.GPIO as GPIO

channel = 3
GPIO.setmode(GPIO.BOARD)
GPIO.setup(channel, GPIO.IN)

while True:
	sleep(1)
	if GPIO.input(channel):
		print("no water detected")
	else:
		print("water detected")
