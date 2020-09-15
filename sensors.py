import RPi.GPIO as GPIO
import adafruit_dht
from Adafruit_CCS811 import Adafruit_CCS811

class Sensor():
    def __init__(self, name, measurement_name, unit):
        self.name = name
        self.measurement_name = measurement_name
        self.unit = unit
        self.last_value = -1
    def get_value(self):
        pass

class HumiditySensor(Sensor):
    def __init__(self, name):
        Sensor.__init__(self, name, "Humidity", "%")
    def get_value(self):
        pass
    
class DHT22_Humidity_Sensor(HumiditySensor):
    def __init__(self, name, DHT22):
        HumiditySensor.__init__(self, name)
        #self.dhtDevice = adafruit_dht.DHT22(pin, use_pulseio=False)
        self.dhtDevice = DHT22
    def get_value(self):
        NUM_TRIES = 10
        for try_num in range(NUM_TRIES):
            try:
                self.last_value = self.dhtDevice.humidity
                #print("Humidity: {}% ".format(self.last_value))
                return self.last_value
            except RuntimeError as error:
                #print(error.args[0])
                #time.sleep(2.0)
                continue
            except Exception as error:
                self.dhtDevice.exit()
                raise error
        print('Failed to read the humidity sensor ' + str(NUM_TRIES) + ' times.')
        return self.last_value
    
class Thermometer(Sensor):
    def __init__(self, name):
        Sensor.__init__(self, name, "Temperature", "°C")
    def get_value(self):
        pass

class DHT22_Thermometer(Thermometer):
    def __init__(self, name, DHT22):
        Thermometer.__init__(self, name)
        #self.dhtDevice = adafruit_dht.DHT22(pin, use_pulseio=False)
        self.dhtDevice = DHT22
    def get_value(self):
        NUM_TRIES = 10
        for try_num in range(NUM_TRIES):
            try:
                self.last_value = self.dhtDevice.temperature
                #print("Temperature: {}degC ".format(self.last_value))
                return self.last_value
            except RuntimeError as error:
                #print(error.args[0])
                #time.sleep(2.0)
                continue
            except Exception as error:
                self.dhtDevice.exit()
                raise error
        print('Failed to read the thermometer ' + str(NUM_TRIES) + ' times.')
        return self.last_value
    
class CO2Sensor(Sensor):
    def __init__(self, name):
        Sensor.__init__(self, name, "CO2", "ppm")
    def get_value(self):
        pass
    
import time

class CCS811(CO2Sensor):
    def __init__(self, name):
        CO2Sensor.__init__(self, name)
        self.ccs = Adafruit_CCS811()
    def get_value(self):
        NUM_TRIES = 10
        for try_num in range(NUM_TRIES):
            try:
                self.ccs.readData()
                #time.sleep(1)
                self.last_value = self.ccs.geteCO2()
                #print("CO2: {}degC ".format(self.last_value))
                return self.last_value
            except RuntimeError as error:
                #print(error.args[0])
                #time.sleep(2.0)
                continue
            except Exception as error:
                raise error
        print('Failed to read the C02 sensor ' + str(NUM_TRIES) + ' times.')
        return self.last_value