from mqtt_device import TankController, add_method
import time 


# If you want to use a specific client id, use
# mqttc = MyMQTTClass("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = TankController()
mqttc.set_local(True)
rc = mqttc.run()

@add_method(TankController)
def heater_control(temperature: float):
    # simple thermostat
    print("Heater control checking temperature:", temperature)
    return temperature < 20.0

while True:
    mqttc.update_data()
    mqttc.publish_data()
    time.sleep(10)

