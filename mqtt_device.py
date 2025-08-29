
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

#@dataclass
class MQTTClient(mqtt.Client):
    time_multiplier: float = 1.0
    local = False

    #OLP/device/tank/id/control/heater
    #OLP/device/tank/id/control/light
    #OLP/device/tank/id/control/pump

    def __init__(self, *args, **kwargs):
        super(MQTTClient, self).__init__(*args, **kwargs)
        setattr(self, 'last_time', timer())
        
    def on_connect(self, mqttc, obj, flags, reason_code, properties):
        print("rc: "+str(reason_code))

    def on_connect_fail(self, mqttc, obj):
        print("Connect failed")

    def on_message(self, mqttc, obj, msg):
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    
    def __repr__(self):
        return self.__class__.__name__ + f'(temperature={self.temperature}, brightness={self.brightness}, humidity={self.humidity}, heater={self.heater}, light={self.light}, pump={self.pump})'

    def update_data(self):
        now_time = timer()
        self.diff = now_time - getattr(self, 'last_time', now_time)
        setattr(self, 'last_time', now_time)

    def publish_data(self):
        pass
    
    def update_hardware(self):
        pass
        
    def on_publish(self, mqttc, obj, mid, reason_codes, properties):
        print("mid: "+str(mid))

    def on_subscribe(self, mqttc, obj, mid, reason_code_list, properties):
        print("Subscribed: "+str(mid)+" "+str(reason_code_list))

    def on_log(self, mqttc, obj, level, string):
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
    temperature: float = 20.0
    ambient_temperature: float = 10.0
    brightness: float = 1.85
    humidity: float = 1.85
    
    heater: bool = False
    light: bool = False
    pump: bool = False
    
    def update_data(self):
        super(TankDevice, self).update_data()

    def update_hardware(self):
        super(TankDevice, self).update_hardware()
    
    def on_message(self, mqttc, obj, msg):
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        topic_parts = msg.topic.split('/')
        if topic_parts[4] == 'control':
            if topic_parts[5] == 'heater':
                self.heater = msg.payload.lower() == b'true'
            elif topic_parts[5] == 'light':
                self.light = msg.payload.lower() == b'true'
            elif topic_parts[5] == 'pump':
                self.pump = msg.payload.lower() == b'true'


    def publish_data(self):
        super(TankDevice, self).publish_data()
        self.publish("OLP/device/tank/id/sensors/temperature", payload=str(round(self.temperature, 2)), qos=1, retain=True)
        self.publish("OLP/device/tank/id/sensors/brightness", payload=str(round(self.brightness, 2)), qos=1, retain=True)
        self.publish("OLP/device/tank/id/sensors/humidity", payload=str(round(self.humidity, 2)), qos=1, retain=True)

class TankSimulator(TankDevice):
    def update_data(self):
        super(TankSimulator, self).update_data()

        if self.heater:
            self.temperature += 0.1 * self.diff * self.time_multiplier
        else:
            self.temperature += (self.ambient_temperature - self.temperature) * 0.01 * self.diff * self.time_multiplier
        #self.temperature += 0.1 if self.heater
        #self.brightness = 10.0 if self.light else -0.1
        self.humidity += (0.1 * self.diff * self.time_multiplier) if self.pump else (-0.1 * self.diff * self.time_multiplier)        

class TankController(TankDevice):

    def __init__(self, *args, **kwargs):
        super(MQTTClient, self).__init__(*args, **kwargs)
        if "turn_heater_on" in kwargs:
            # stash this function for use on heater update
            #self.heater = kwargs["turn_heater_on"]
            pass


    def on_message(self, mqttc, obj, msg):
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        topic_parts = msg.topic.split('/')
        if topic_parts[4] == 'sensors':
            if topic_parts[5] == 'temperature':
                self.temperature = float(msg.payload)
            elif topic_parts[5] == 'ambient_temperature':
                self.ambient_temperature = float(msg.payload)
            elif topic_parts[5] == 'brightness':
                self.brightness = float(msg.payload)
            elif topic_parts[5] == 'humidity':
                self.humidity = float(msg.payload)  


# If you want to use a specific client id, use
# mqttc = MyMQTTClass("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = MQTTClient(mqtt.CallbackAPIVersion.VERSION2)
mqttc.set_local(True)
rc = mqttc.run()


while True:
    #temperature = read_from_imaginary_thermometer()
    #(rc, mid) = client.publish('encyclopedia/temperature', str(temperature), qos=1)
    mqttc.update_data()
    mqttc.publish_data()
    time.sleep(10)


print("rc: "+str(rc))