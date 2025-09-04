from mqtt_device import TankController, add_method
import time 


# If you want to use a specific client id, use
# mqttc = MyMQTTClass("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
tank_controller = TankController()

tank_controller.set_local(True) # TODO : make this a parameter on init or a file based setting


@add_method(TankController)
def heater_control(temperature: float):
    # simple thermostat
    print("Heater control checking temperature:", temperature)
    return temperature < 20.0

rc = tank_controller.run() # if local is a parameter we could do this in init 
# as run works here we can put the loop in the library
# and have a controller that just sets up the callbacks
# and calls run

while True:
    tank_controller.update_data()
    tank_controller.publish_data()
    time.sleep(10) #This is blocking anyway 
    # is there a none blocking timer we could use for all this

