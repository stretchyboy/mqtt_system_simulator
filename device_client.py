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



class MQTTDevice(mqtt.Client):
    local = False

    def on_connect(self, mqttc, obj, flags, reason_code, properties):
        print("rc: "+str(reason_code))

    def on_connect_fail(self, mqttc, obj):
        print("Connect failed")

    def on_message(self, mqttc, obj, msg):
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        print(msg)

    def on_publish(self, mqttc, obj, mid, reason_codes, properties):
        print("mid: "+str(mid))

    def on_subscribe(self, mqttc, obj, mid, reason_code_list, properties):
        print("Subscribed: "+str(mid)+" "+str(reason_code_list))

    def on_log(self, mqttc, obj, level, string):
        print(string)
    
    def set_local(self, local: bool=True):
            self.local = local

    def run(self):
        #client.username_pw_set("meggleton_client_1", '",9*yX~Rg2j9_*H')
        

        if self.local:
            self.connect("127.0.0.1")  # use port 1883 for unencrypted connection
        else:
            self.connect("4f8d5d75e7ee4747a9c3043262312926.s1.eu.hivemq.cloud", 8883,client_id="", userdata=None, protocol=mqtt.MQTTv5)
        
        self.subscribe("OLP/device/#", qos=1)

        #client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        # connect to HiveMQ Cloud on port 8883 (default for MQTT)
        
        self.loop_forever(1)
        '''rc = 0
        while rc == 0:
            rc = self.loop()
        return rc
        '''


# If you want to use a specific client id, use
# mqttc = MyMQTTClass("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = MQTTDevice(mqtt.CallbackAPIVersion.VERSION2)
mqttc.set_local(True)

rc = mqttc.run()

print("rc: "+str(rc))