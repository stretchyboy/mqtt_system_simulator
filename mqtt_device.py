
#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Roger Light <roger@atchoo.org>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Distribution License v1.0
# which accompanies this distribution.
#
# The Eclipse Distribution License is available at
#   http://www.eclipse.org/org/documents/edl-v10.php.
#
# Contributors:
#    Roger Light - initial implementation

# This example shows how you can use the MQTT client in a class.

#import context  # Ensures paho is in PYTHONPATH

import paho.mqtt.client as mqtt
#from dataclasses import dataclass
from timeit import default_timer as timer
import time
import json
from functools import wraps # This convenience func preserves name and docstring


def add_method(cls):
    def decorator(func):
        @wraps(func) 
        def wrapper(self, *args, **kwargs): 
            return func(*args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
        return func # returning func means func can still be used normally
    return decorator


#@dataclass
class MQTTClient(mqtt.Client):
    time_multiplier: float = 1.0
    local = False
    dirty = False
    debug = False
    individual_publish = False

    #OLP/device/tank/id/control/heater
    #OLP/device/tank/id/control/light
    #OLP/device/tank/id/control/pump

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("callback_api_version", mqtt.CallbackAPIVersion.VERSION2)
        super(MQTTClient, self).__init__(*args, **kwargs)
        setattr(self, 'last_time', timer())
        
    def on_connect(self, mqttc, obj, flags, reason_code, properties):
        if self.debug:
            print("Connected rc: "+str(reason_code))

    def on_connect_fail(self, mqttc, obj):
        if self.debug:
            print("Connect failed")

    def on_message(self, mqttc, obj, msg):
        if self.debug:
            print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    
    def __repr__(self):
        return self.__class__.__name__ + f'(temperature={self.temperature}, brightness={self.brightness}, humidity={self.humidity}, heater={self.heater}, light={self.light}, pump={self.pump})'

    def update_data(self):
        now_time = timer()
        self.diff = now_time - getattr(self, 'last_time', now_time)
        setattr(self, 'last_time', now_time)
        self.dirty = False

    def publish_data(self):
        pass
    
    def update_hardware(self):
        pass
        
    def on_publish(self, mqttc, obj, mid, reason_codes, properties):
        if self.debug:
            print("mid: "+str(mid))

    def on_subscribe(self, mqttc, obj, mid, reason_code_list, properties):
        if self.debug:
            print("Subscribed: "+str(mid)+" "+str(reason_code_list))

    def on_log(self, mqttc, obj, level, string):
        if self.debug:
            print(string)
    
    def set_local(self, local: bool=True):
        self.local = local
        
    def run(self):
        if self.local:
            self.connect("127.0.0.1")  # use port 1883 for unencrypted connection
        else:
            self.connect("4f8d5d75e7ee4747a9c3043262312926.s1.eu.hivemq.cloud", 8883,client_id="", userdata=None, protocol=mqtt.MQTTv5)
        
        # TODO : what are we subscribing to in sub classes
        self.subscribe("OLP/device/#", qos=1)
        #self.subscribe("$SYS/#", 0)

        self.loop_start()

class TankDevice(MQTTClient):
    temperature: float = 15.0
    ambient_temperature: float = 10.0
    brightness: float = 1.85
    humidity: float = 1.85
    
    heater: bool = False
    light: bool = False
    pump: bool = False
    
    '''
    def update_data(self):
        super(TankDevice, self).update_data()

    def update_hardware(self):
        super(TankDevice, self).update_hardware()
    '''

    def on_message(self, mqttc, obj, msg):
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        topic_parts = msg.topic.split('/')
        if topic_parts[4] == 'control':
            if self.individual_publish:
                if topic_parts[5] == 'heater':
                    self.heater = msg.payload.lower() == b'true'
                elif topic_parts[5] == 'light':
                    self.light = msg.payload.lower() == b'true'
                elif topic_parts[5] == 'pump':
                    self.pump = msg.payload.lower() == b'true'
            if topic_parts[5] == 'all':
                payload = json.loads(msg.payload)
                if 'heater' in payload:
                    self.heater = payload['heater']
                if 'light' in payload:
                    self.light = payload['light']
                if 'pump' in payload:
                    self.pump = payload['pump']
        if topic_parts[4] == 'sensors':
            if self.individual_publish:
                if topic_parts[5] == 'temperature':
                    self.temperature = float(msg.payload)
                elif topic_parts[5] == 'ambient_temperature':
                    self.ambient_temperature = float(msg.payload)
                elif topic_parts[5] == 'brightness':
                    self.brightness = float(msg.payload)
                elif topic_parts[5] == 'humidity':
                    self.humidity = float(msg.payload)

                print("Updated from ",topic_parts[5],":", self.temperature, self.ambient_temperature, self.brightness, self.humidity)
  
            if topic_parts[5] == 'all':
                payload = json.loads(msg.payload)
                print("Payload:", payload)
                if 'temperature' in payload:
                    self.temperature = float(payload['temperature'])
                if 'ambient_temperature' in payload:
                    self.ambient_temperature = float(payload['ambient_temperature'])
                if 'brightness' in payload:
                    self.brightness = float(payload['brightness'])          
                if 'humidity' in payload:
                    self.humidity = float(payload['humidity'])
                print("Updated from all:", self.temperature, self.ambient_temperature, self.brightness, self.humidity)



    def publish_data(self):
        if self.dirty == False:
            return
        
        self.dirty = False
        if self.individual_publish:
            self.publish("OLP/device/tank/id/sensors/temperature", payload=str(round(self.temperature, 2)), qos=1, retain=True)
            self.publish("OLP/device/tank/id/sensors/brightness", payload=str(round(self.brightness, 2)), qos=1, retain=True)
            self.publish("OLP/device/tank/id/sensors/humidity", payload=str(round(self.humidity, 2)), qos=1, retain=True)
            self.publish("OLP/device/tank/id/sensors/ambient_temperature", payload=str(round(self.ambient_temperature, 2)), qos=1, retain=True)
        self.publish("OLP/device/tank/id/sensors/all", payload=json.dumps({
            'temperature': round(self.temperature, 2),
            'brightness': round(self.brightness, 2),
            'humidity': round(self.humidity, 2),
            'ambient_temperature': round(self.ambient_temperature, 2)
        }), qos=1, retain=True)


class TankSimulator(TankDevice):
    # TODO : add min/max values
    # FIXME : is not starting cleanly it is receiving the retained state and then losing it

    def update_data(self):
        super(TankSimulator, self).update_data()

        if self.heater:
            self.temperature += 0.1 * self.diff * self.time_multiplier
        else:
            self.temperature += (self.ambient_temperature - self.temperature) * 0.01 * self.diff * self.time_multiplier
        #self.temperature += 0.1 if self.heater
        #self.brightness = 10.0 if self.light else -0.1
        self.humidity += (0.1 * self.diff * self.time_multiplier) if self.pump else (-0.1 * self.diff * self.time_multiplier) 

        self.dirty = True


class TankController(TankDevice):

    def __init__(self, *args, **kwargs):
        super(TankController, self).__init__(*args, **kwargs)
        if "heater_control" in kwargs:
            # stash this function for use on heater update
            self.heater_control = kwargs["heater_control"]
        
        if "pump_control" in kwargs:
            self.pump_control = kwargs["pump_control"]
        
        if "light_control" in kwargs:
            self.light_control = kwargs["light_control"]

    def heater_control(self, temperature: float) -> bool:
        return False

    def pump_control(self, humidity: float) -> bool:
        return False    
    
    def light_control(self, brightness: float) -> bool:
        return False    
    
    '''
    @temperature.setter
    def temperature(self, value):
        temp = float(value)
        if temp != self.temperature:
            self.temperature = value
            self.dirty = True
    
    @ambient_temperature.setter
    def ambient_temperature(self, value):
        temp = float(value)
        if temp != self.ambient_temperature:
            self.ambient_temperature = value
            self.dirty = True

    @brightness.setter
    def brightness(self, value):        
        bright = float(value)
        if bright != self.brightness:
            self.brightness = value
            self.dirty = True

    @humidity.setter
    def humidity(self, value):        
        hum = float(value)
        if hum != self.humidity:
            self.humidity = value
            self.dirty = True
    '''
    '''
    def on_message(self, mqttc, obj, msg):
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        topic_parts = msg.topic.split('/')
    '''

    def update_data(self):
        super(TankController, self).update_data()
        # call the heater control function to determine if we need to turn the heater on or off
        heater = self.heater_control(self.temperature)
        print("Heater control returned:", heater, "current state:", self.heater)
        
        if heater != self.heater:
            self.heater = heater
            self.dirty = True
    
        pump = self.pump_control(self.humidity)
        if pump != self.pump:
            self.pump = pump
            self.dirty = True           
    
        light = self.light_control(self.brightness)
        if light != self.light:
            self.light = light
            self.dirty = True
            

    def publish_data(self):
        if self.dirty == False:
            print("Not dirty, not publishing")
            return
        self.dirty = False
        if self.individual_publish:
            self.publish("OLP/device/tank/id/control/heater", payload=str(self.heater), qos=1, retain=True)
            self.publish("OLP/device/tank/id/control/light", payload=str(self.light), qos=1, retain=True)
            self.publish("OLP/device/tank/id/control/pump", payload=str(self.pump), qos=1, retain=True)
        self.publish("OLP/device/tank/id/control/all", payload=json.dumps({
            'heater': self.heater,
            'light': self.light,
            'pump': self.pump
        }), qos=1, retain=True)



