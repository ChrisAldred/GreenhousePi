import sqlite3
from time import sleep
import datetime
import RPi.GPIO as GPIO
import os
import glob
import spidev

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
db = os.getenv('DB_PATH')

base_dir = '/sys/bus/w1/devices/'
temp1_folder = glob.glob(base_dir + '28-3c01b556e588')[0]
temp1_file = temp1_folder + '/w1_slave'
temp2_folder = glob.glob(base_dir + '28-031501c754ff')[0]
temp2_file = temp2_folder + '/w1_slave'

# Set-Up GPIO pin for water
GPIO.setmode(GPIO.BCM)
GPIO.setup(3, GPIO.IN)
GPIO.setup(14, GPIO.IN)
GPIO.setup(15, GPIO.IN)
GPIO.setup(18, GPIO.IN)
GPIO.setup(23, GPIO.IN)

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

# Function to read temperature
def read_temp(temp_file):
    f = open(temp_file, 'r')
    lines = f.readlines()
    f.close()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

while True:
	#define variabls for SQL insert
	date = datetime.datetime.now().strftime("%d-%b-%Y ")
	time = datetime.datetime.now().strftime("%X")
	plant1 = GPIO.input(3)
	plant2 = GPIO.input(14)
	plant3 = GPIO.input(15)
	plant4 = GPIO.input(18)
	plant5 = GPIO.input(23)
	tempIn = read_temp(temp1_file)
	tempOut = read_temp(temp2_file)
	lux = readAnalogue(0)

	sql = ''' INSERT INTO dhtreadings(date, time, plant1, plant2, plant3, plant4, plant5, tempIn, tempOut, lux)
			  VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''
	params = (date, time, plant1, plant2, plant3, plant4, plant5, tempIn, tempOut, lux)

	#connect to database file
	dbconnect = sqlite3.connect(db)
	#If we want to access columns by name we need to set
	#row_factory to sqlite3.Row class
	dbconnect.row_factory = sqlite3.Row
	#now we create a cursor to work with db
	cursor = dbconnect.cursor()
	#execute insert statement
	cursor.execute(sql, params)
	dbconnect.commit()
	cursor.close()
	#close the connection
	dbconnect.close()

	#wait 30mins
	sleep(1800)