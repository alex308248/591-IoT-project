import time
import wiotp.sdk.application

client_id = "project"
type_id = "RaspberryPi" 
MQTT_TOPICS = ["Door"]

def publish(topic, payload):
    print(f"Send to topic `{topic}`:    {payload}")
    
def run():
    options = wiotp.sdk.application.parseConfigFile("application.yaml")
    client = wiotp.sdk.application.ApplicationClient(config=options)
    client.connect()
    for i in range(10000):
        n = 0
        if i % 2 == 0:
            payload =  "Open"
        else:
            payload = "Close"    
        eventData = {'Door' : payload}
        client.publishEvent(typeId=type_id, deviceId=client_id, eventId=MQTT_TOPICS[n], msgFormat="json", data=eventData, qos = 2, onPublish=publish(topic = MQTT_TOPICS[n], payload = payload))
        time.sleep(5)

if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        print("Exception: ", e)