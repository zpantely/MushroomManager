import board
import RPi.GPIO as GPIO
from adafruit_blinka.microcontroller.bcm283x.pin import Pin

from enum import Enum
class GrowStage(Enum):
    colonization = 0
    incubation = 1
    fruiting = 2

from instruments import *
from sensors import *
from camera import Camera

HUMIDITY_LOW_LEVEL = 60
HUMIDITY_HIGH_LEVEL = 80

# 800 to 1,500 ppm optimal during fruiting
CO2_LOW_LEVEL = 800
CO2_HIGH_LEVEL = 1500

DHT22_INPUT = board.D23 #23 #GPIO23
FAN_OUTPUT = 18
WATER_LEVEL_PRESENT_INPUT = 6

class Manager():
    
    class __Manager:
        def __init__(self):
            self.create_instruments_and_sensors() #this is run only once when the first manager is created
            self.grow_stage = GrowStage.colonization
            
        def create_instruments_and_sensors(self):
            self.humidifier = Betazooer('Humidifier', WATER_LEVEL_PRESENT_INPUT, HUMIDITY_LOW_LEVEL, HUMIDITY_HIGH_LEVEL)
            self.light = Light('Light')
            self.fan = Fan('Fan', FAN_OUTPUT, CO2_LOW_LEVEL, CO2_HIGH_LEVEL)

            self.instrument_list = [
                self.humidifier,
                self.light,
                self.fan
            ]
            
            DHT22 = adafruit_dht.DHT22(DHT22_INPUT, use_pulseio=False)
            self.humidity_sensor = DHT22_Humidity_Sensor('Humidity Sensor', DHT22)
            self.thermometer = DHT22_Thermometer('Thermometer', DHT22)
            self.co2_sensor = CCS811('CO2 Sensor')

            self.sensor_list = [
                self.humidity_sensor,
                self.thermometer,
                self.co2_sensor
            ]
            
            self.camera = Camera()
        
        def set_grow_stage(self, grow_stage):
            self.grow_stage = grow_stage
        
        def shutdown(self):
             for inst in Manager.instance.instrument_list:
                 inst.shutdown()

    instance = None
    def __init__(self):
        if not Manager.instance:
            Manager.instance = Manager.__Manager()      
            



