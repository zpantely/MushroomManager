import RPi.GPIO as GPIO

from manager import GrowStage

from enum import Enum
class Mode(Enum):
    on = 0
    off = 1
    auto = 2
class State(Enum):
    on = 0
    off = 1

class Instrument():
    def __init__(self, name):
        self.name = name
        self.mode = Mode.auto #whether it is forced on/off or allowed to decide for itself
        self.state = State.off #whether it is currently on/off
    def set_mode(self, mode):
        self.mode = mode
        if self.mode is Mode.on:
            self._set_state(State.on)
        elif self.mode is Mode.off:
            self._set_state(State.off)
    def get_state(self):
        return self.state
    def _set_state(self, state): #override
        self.state = state
    def shutdown(self):
        self._set_state(State.off);
    def update(self, grow_stage, measurement=None): #override
        print('Instrument update() function must be overridden')

class Humidifier(Instrument):
    def __init__(self, name, humidity_low_level, humidity_high_level):
        Instrument.__init__(self, name)
        self.humidity_low_level = humidity_low_level
        self.humidity_high_level = humidity_high_level
    def set_mode(self, mode):
        Instrument.set_mode(self, mode)
    def _set_state(self, state):
        Instrument._set_state(self, state)
        #output enable high = (self.state == State.on)
        pass
    def update(self, grow_stage, measurement=None):
        if self.mode is not Mode.auto:
            return
        if grow_stage is not GrowStage.fruiting:
            self._set_state(State.off)
            return
        if not measurement:
            self._set_state(State.off)
            return
        if measurement < self.humidity_low_level or (self.state == State.on and measurement < self.humidity_high_level):
            self._set_state(State.on)
        elif measurement > self.humidity_high_level or (self.state == State.off and measurement > self.humidity_low_level):
            self._set_state(State.off)

class Betazooer(Humidifier):
    def __init__(self, name, water_present_pin, humidity_low_level, humidity_high_level):
        Humidifier.__init__(self, name, humidity_low_level, humidity_high_level)
        self.water_present_pin = water_present_pin
        GPIO.setup(self.water_present_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    def get_water_present(self):
        return GPIO.input(self.water_present_pin)

class Light(Instrument):
    def __init__(self, name):
        Instrument.__init__(self, name)
    def set_mode(self, mode):
        Instrument.set_mode(self, mode)
        if self.mode is not Mode.auto:
            self.set_state(State.on) #the light just defaults to always on when set to auto
    def _set_state(self, state):
        Instrument._set_state(self, state)
        #output enable high = (self.state == State.on)
        pass
    def update(self, grow_stage, measurement=None):
        pass

class Fan(Instrument):
    def __init__(self, name, pin, co2_low_level, co2_high_level):
        Instrument.__init__(self, name)
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        self.co2_low_level = co2_low_level
        self.co2_high_level = co2_high_level
    def set_mode(self, mode):
        Instrument.set_mode(self, mode)
    def _set_state(self, state):
        Instrument._set_state(self, state)
        GPIO.output(self.pin, GPIO.HIGH if (self.state == State.on) else GPIO.LOW)
    def update(self, grow_stage, measurement=None):
        if self.mode is not Mode.auto:
            return
        if grow_stage is not GrowStage.fruiting:
            self._set_state(State.off)
            return
        if not measurement:
            self._set_state(State.off)
            return
        if measurement < self.co2_low_level or (self.state == State.off and measurement < self.co2_high_level):
            self._set_state(State.off)
        elif measurement > self.co2_high_level or (self.state == State.on and measurement > self.co2_low_level):
            self._set_state(State.on)