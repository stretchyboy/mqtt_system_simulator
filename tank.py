from mqtt_device import TankSimulator
import paho.mqtt.client as mqtt
import time 

mqttc = TankSimulator(mqtt.CallbackAPIVersion.VERSION2)
mqttc.set_local(True)
rc = mqttc.run()

while True:
    mqttc.update_data()
    mqttc.publish_data()
    time.sleep(10)

