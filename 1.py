import time
import board
import digitalio
import Adafruit_DHT
import adafruit_character_lcd.character_lcd as characterlcd
import RPi.GPIO as GPIO
from influxdb import InfluxDBClient
from subprocess import Popen, PIPE
from time import sleep
from datetime import datetime

# Red and Green LED
LED_PIN = [5,6]

# InfluxDB Config
host = ''
port = 
user = ''
password = ''
dbname = ''
measurement = ''
location = ''

# InfluxDB Client Object
client = InfluxDBClient(host, port, user, password, dbname)

# Wait time between sensor readout
interval = 5.0

# Temperature and Humidity Sensor DHT11
sensor = Adafruit_DHT.DHT22
pin = 26

# Modify this if you have a different sized character LCD
lcd_columns = 16
lcd_rows = 2

# compatible with all versions of RPI as of Jan. 2019
# v1 - v3B+
lcd_rs = digitalio.DigitalInOut(board.D22)
lcd_en = digitalio.DigitalInOut(board.D17)
lcd_d4 = digitalio.DigitalInOut(board.D25)
lcd_d5 = digitalio.DigitalInOut(board.D24)
lcd_d6 = digitalio.DigitalInOut(board.D23)
lcd_d7 = digitalio.DigitalInOut(board.D18)

# Initialise the lcd class
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                      lcd_d7, lcd_columns, lcd_rows)

# Buffer Size
buff_size = 7

h_array = [0 for i in range(buff_size)]
t_array = [0 for i in range(buff_size)]
h_array_sort = [0 for i in range(buff_size)]
t_array_sort = [0 for i in range(buff_size)]

# Init GPIO for LEDs
def setgpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)

# Write Sensor Data to InfluxDB
def influxdb_data(iso, h, t):
    data = [{
          "measurement": measurement,
          "tags": {
            "location": location,
          },
          "time": iso,
          "fields": {
            "temperature": t,
            "humidity": h
            #"heat_index": hic
          }
    }]

    client.write_points(data)

def bubble_sort(sort_array, n):
    i = 0
    j = 0
    temp = 0
    for i in range(n-1):
        for j in range(n-1):
            if (sort_array[j] > sort_array[j+1]):
                temp = sort_array[j]
                sort_array[j] = sort_array[j+1]
                sort_array[j+1] = temp
            

def init():
    lcd.clear() # wipe LCD screen before we start and init gpio
    setgpio()
    lcd_line_1 = "Initializing\n"
    lcd_line_2 = ""
    
    for i in range(buff_size):
        sleep(interval)
        print("INIT")

        lcd_line_2 += "."
        # combine both lines into one update to the display
        lcd.message = lcd_line_1 + lcd_line_2
        try:
            humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
            if humidity is not None and temperature is not None:
                h_array[i] = humidity
                t_array[i] = temperature
        except RuntimeError as err:
            print("Reading from DHT failure: ", err.args)

def main():
    a=0
    b=0
    median_index=0
    init()

    sleep(interval)

    while True:
        
        # read sensor, write to influxdb
        try:
           humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
           print('humidity' + str(humidity))
           print('temperature' + str(temperature))
           if humidity is not None and temperature is not None:
             for i in range(buff_size - 1):
               h_array[i] = h_array[i+1]
               t_array[i] = t_array[i+1]
                
             h_array[buff_size-1] = humidity
             t_array[buff_size-1] = temperature

             for i in range(buff_size):
               h_array_sort[i] = h_array[i]
               t_array_sort[i] = t_array[i]
             bubble_sort(h_array_sort, buff_size)
             bubble_sort(t_array_sort, buff_size)

             median_index = int(buff_size/2)
             humidity = h_array_sort[median_index]
             temperature = t_array_sort[median_index]
             influxdb_data(time.ctime(), temperature, humidity)
             # date and time
             lcd_line_1 = datetime.now().strftime('%b %d  %H:%M:%S\n')
             lcd_line_2 = u'\N{DEGREE SIGN}'+'C:' + "{:.1f}".format((temperature)) + '  %H:' + "{:.1f}".format((humidity))
             # combine both lines into one update to the display
             lcd.message = lcd_line_1 + lcd_line_2
        except RuntimeError as err:
           print("Reading from DHT failure: ", err.args)

        # switch led lights
        if b == 0:
           GPIO.output(LED_PIN, (GPIO.HIGH, GPIO.LOW))
           b=1
        else:
           GPIO.output(LED_PIN, (GPIO.LOW, GPIO.HIGH))
           b=0

        sleep(interval)
    GPIO.cleanup()

if __name__ == '__main__':
    main()
