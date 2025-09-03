from mqtt_device import TankSimulator
import time 

mqttc = TankSimulator()
mqttc.set_local(True)
rc = mqttc.run()

while True:
    mqttc.update_data()
    mqttc.publish_data()
    time.sleep(10)

