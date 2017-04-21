import os
import re
import datetime
from datetime import timedelta
import json
import subprocess
import sched
import time
import ConfigParser
from pymongo import MongoClient

import logging
logger = logging.getLogger(__name__)
hdlr = logging.FileHandler('./temperature.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

# function for reading DHT22 sensors
# https://github.com/jjpFin/DHT22-TemperatureLogger/blob/master/DHT22logger.py
def sensorReadings(gpio, sensor):

	configurations = getConfigurations()
	adafruit = configurations["adafruitpath"]

	sensorReadings = subprocess.check_output(['sudo',adafruit,sensor,gpio])

	try:
		# try to read neagtive numbers
		temperature = re.findall(r"Temp=(-\d+.\d+)", sensorReadings)[0]
	except:
		# if negative numbers caused exception, they are supposed to be positive
		try:
			temperature = re.findall(r"Temp=(\d+.\d+)", sensorReadings)[0]
		except:
			pass
	humidity = re.findall(r"Humidity=(\d+.\d+)", sensorReadings)[0]
	intTemp = float(temperature)
	intHumidity = float(humidity)

	return intTemp, intHumidity

# reading config of the sensors
def getConfigurations():

	path = os.getcwd()

	#get configs
	configurationFile = path + '/temperature_sensor_config.json'
	configurations = json.loads(open(configurationFile).read())

	return configurations

# get output of sensor as json
def read_sensors():
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    configurations = getConfigurations()

    # how many sensors there is 1 or 2
    sensorsToRead = configurations["sensoramount"]

    # Sensor names to add to database, e.g. carage, outside
    sensor1 = configurations["sensors"][0]["sensor1"]

    # Sensor gpios
    gpioForSensor1 = configurations["sensorgpios"][0]["gpiosensor1"]

    # type of the sensor used, e.g. DHT22 = 22
    sensorType = configurations["sensortype"]

    sensor1error = False
    sensor1exception = None
    sensor1temperature = None
    sensor1humidity = None
    # Sensor 1 readings
    try:
        sensor1temperature, sensor1humidity = sensorReadings(gpioForSensor1, sensorType)
    except Exception as e:
        sensor1error = True
        logger.error(e)
        sensor1exception = e
        pass

    output = {}
    output["date"] = currentTime
    output["temperature"] = sensor1temperature
    output["humidity"] = sensor1humidity
    output["error"] = sensor1error
    output["exception"] = sensor1exception

    return output

# get database
config = ConfigParser.ConfigParser()
config.read('secrets.ini')
mongo_client = MongoClient(config.get('MongoDB', 'ConnectionString'))
event_database = mongo_client.pluseoxdata

# scheduler for running every minute
s = sched.scheduler(time.time, time.sleep)

def temperature_sensor_loop(sc):
    # launch next read
    sc.enter(60, 1, temperature_sensor_loop, (sc,))
    # current read into ddbb
    output = read_sensors()
    try:
        event_database.temperatureevents.insert_one(output)
    except Exception as e:
        logger.error(e)
    logger.info(output)

s.enter(60, 1, temperature_sensor_loop, (s,))
s.run()
