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
interval = 2.5

# Temperature and Humidity Sensor DHT11
sensor = Adafruit_DHT.DHT11
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

# run unix shell command, return as ASCII
def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output.decode('ascii')

# Init GPIO for LEDs
def setgpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)

# Write Sensor Data to InfluxDB
def influxdb_data(iso, h, t):
    data = [
        {
            "measurement": measurement,
                "tags": {
                    "location": location,
            },
            "time": iso,
            "fields": {
                "temperature": t,
                "humidity": h
               # "heat_index": hic
            }
        }
    ]
    client.write_points(data)


def main():
    # wipe LCD screen before we start and init gpio
    lcd.clear()
    setgpio()
    sleep(2)

    while True:
        # read sensor, write to influxdb
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        influxdb_data(time.ctime(), temperature, humidity)

        # switch led lights
        GPIO.output(LED_PIN, (GPIO.HIGH, GPIO.LOW))
        sleep(interval)
        GPIO.output(LED_PIN, (GPIO.LOW, GPIO.HIGH))

        # date and time
        lcd_line_1 = datetime.now().strftime('%b %d  %H:%M:%S\n')

        # current ip address
        lcd_line_2 = str(temperature) + ' - ' + str(humidity)

        # combine both lines into one update to the display
        lcd.message = lcd_line_1 + lcd_line_2

        sleep(interval)
    GPIO.cleanup()

if __name__ == '__main__':
    main()