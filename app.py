import sys
import time
import math
import RPi.GPIO as GPIO
import Adafruit_DHT
from influxdb import InfluxDBClient

# InfluxDB Config
host = ''
port = 
user = ''
password = ''
dbname = ''
interval = 5

# InfluxDB Client Object
client = InfluxDBClient(host, port, user, password, dbname)

measurement = '' # i.e. sensor name
location = ''

# Sensor DHT11
sensor = Adafruit_DHT.DHT11
pin = 26

# Display LC1628-BMDWH6
LCD_RS = 25
LCD_E = 24
LCD_DATA4 = 23
LCD_DATA5 = 17
LCD_DATA6 = 18
LCD_DATA7 = 22
LCD_WIDTH = 16
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xc0
LCD_CHR = GPIO.HIGH
LCD_CMD = GPIO.LOW
E_PULSE = 0.0005
E_DELAY = 0.0005

def gpio_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LCD_E, GPIO.OUT)
    GPIO.setup(LCD_RS, GPIO.OUT)
    GPIO.setup(LCD_DATA4, GPIO.OUT)
    GPIO.setup(LCD_DATA5, GPIO.OUT)
    GPIO.setup(LCD_DATA6, GPIO.OUT)
    GPIO.setup(LCD_DATA7, GPIO.OUT)    

def display_init():
    lcd_write_byte(0x33, LCD_CMD)
    lcd_write_byte(0x32, LCD_CMD)
    lcd_write_byte(0x28, LCD_CMD)
    lcd_write_byte(0x0c, LCD_CMD)
    lcd_write_byte(0x06, LCD_CMD)
    lcd_write_byte(0x01, LCD_CMD)

def lcd_write_byte(bits, mode):
    GPIO.output(LCD_RS, mode)
    GPIO.output(LCD_DATA4, GPIO.LOW)
    GPIO.output(LCD_DATA5, GPIO.LOW)
    GPIO.output(LCD_DATA6, GPIO.LOW)
    GPIO.output(LCD_DATA7, GPIO.LOW)
    if bits & 0x10 == 0x10:
        GPIO.output(LCD_DATA4, GPIO.HIGH)
    if bits & 0x20 == 0x20:
        GPIO.output(LCD_DATA5, GPIO.HIGH)
    if bits & 0x40 == 0x40:
        GPIO.output(LCD_DATA6, GPIO.HIGH)
    if bits & 0x80 == 0x80:
        GPIO.output(LCD_DATA7, GPIO.HIGH)
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, GPIO.HIGH)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, GPIO.LOW)
    time.sleep(E_DELAY)
    GPIO.output(LCD_DATA4, GPIO.LOW)
    GPIO.output(LCD_DATA5, GPIO.LOW)
    GPIO.output(LCD_DATA6, GPIO.LOW)
    GPIO.output(LCD_DATA7, GPIO.LOW)
    if bits&0x01==0x01:
        GPIO.output(LCD_DATA4, GPIO.HIGH)
    if bits&0x02==0x02:
        GPIO.output(LCD_DATA5, GPIO.HIGH)
    if bits&0x04==0x04:
        GPIO.output(LCD_DATA6, GPIO.HIGH)
    if bits&0x08==0x08:
        GPIO.output(LCD_DATA7, GPIO.HIGH)
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, GPIO.HIGH)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, GPIO.LOW)
    time.sleep(E_DELAY)

def lcd_message(message):
    message = message.ljust(LCD_WIDTH," ")
    for i in range(LCD_WIDTH):
        lcd_write_byte(ord(message[i]), LCD_CHR)

def convert_c_to_f(c):
    return c * 1.8 + 32

def convert_f_to_c(f):
    return (f -32) * 0.55555

def heat_index(h, t):
    t = convert_c_to_f(t)

    hic = 0.5 * (t + 61.0 + ((t - 68.0) * 1.2) + (h * 0.094))

    if hic > 79:
        hic = -42.379 + 2.04901523 * t + 10.14333127 * h + \
        -0.22475541 * t * h + \
        -0.00683783 * pow(t, 2) + \
        -0.05481717 * pow(h, 2) + \
        0.00122874 * pow(t, 2) * h + \
        0.00085282 * t * pow(h, 2) + \
        -0.00000199 * pow(t, 2) * pow(h, 2)

    if ((h < 13) && (t >= 88.0) && (t <= 112.0)):
        hic -= ((13.0 - h) * 0.25) * sqrt((17.0 - abs(t -95.0)) * 0.05882)

    else if ((h > 85.0) && (t >= 80.0) && (t <= 87.0)):
        hic += ((h -85.0) * 0.1) * ((87.0 - t) * 0.2)

    return convert_f_to_c(hic)

def display_output(h, t):
    lcd_write_byte(LCD_LINE_1, LCD_CMD)
    lcd_message("TMP: " + str(t) + chr(223) + "C")
    lcd_write_byte(LCD_LINE_2, LCD_CMD)
    lcd_message("HMD: " + str(h) + "%")

def influxdb_data(iso, h, t, hic):
    data = [
        {
            "measurement": measurement,
                "tags": {
                    "location": location,
            },
            "time": iso,
            "fields": {
                "temperature": t,
                "humidity": h,
                "heat_index": hic
            }
        }
    ]
    client.write_points(data)

def main():
    gpio_init()
    display_init()

    while True:
        h, t = Adafruit_DHT.read_retry(sensor, pin)
        hic = heat_index(h, t)
        iso = time.ctime()
        
        display_output(h, t)
        influxdb_data(iso, h, t, hic)
        
        time.sleep(interval)

if __name__ == '__main__':
    main()
