# raspberry-pi-sensor-display-influxdb


## Sources
[Getting Started with Python and InfluxDB](https://www.influxdata.com/blog/getting-started-python-influxdb/)

[Raspberry Pi: Measure Humidity and Temperature with DHT11/DHT22](https://tutorials-raspberrypi.com/raspberry-pi-measure-humidity-temperature-dht11-dht22/)

[Monitoring temperature and humidity with a Raspberry Pi 3, DHT22 sensor, InfluxDB and Grafana](https://www.definit.co.uk/2018/07/monitoring-temperature-and-humidity-with-a-raspberry-pi-3-dht22-sensor-influxdb-and-grafana/)

[Heat Index](https://en.wikipedia.org/wiki/Heat_index)

[Drive a 16x2 LCD with the Raspberry Pi](https://learn.adafruit.com/drive-a-16x2-lcd-directly-with-a-raspberry-pi/necessary-packages)

## Install Dependencies

```bash
sudo apt install python3-pip
pip3 install -r requirements.txt
```

## Add InfluxDB Credentials

In app.py add credentials under InfluxDB Config.

## Create a Service

```bash
sudo vim /lib/systemd/system/service-name.service
```

```bash
[Unit]
Description=Descriptive Description
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python3 /path/to/python/script.py
User=ubuntu

[Install]
WantedBy=multi-user.target
```

```bash
sudo chmod 644 /lib/systemd/system/service-name.service
sudo systemctl daemon-reload
sudo systemctl enable service-name.service
sudo systemctl start service-name.service
```
