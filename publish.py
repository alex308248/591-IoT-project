import time
import wiotp.sdk.application

client_id = "project"
type_id = "RaspberryPi" 
MQTT_TOPICS = ["CustomerId", "User01"]

def publish(topic, payload):
    print(f"Send to topic `{topic}`:    {payload}")
    
def run():
    options = wiotp.sdk.application.parseConfigFile("application.yaml")
    client = wiotp.sdk.application.ApplicationClient(config=options)
    client.connect()
    client.publishEvent(typeId=type_id, deviceId=client_id, eventId=MQTT_TOPICS[0], msgFormat="json", data={'CustomerId': 'User01'}, qos = 2, onPublish=publish(topic = MQTT_TOPICS[0], payload = "User01"))    
    time.sleep(5)
    for i in range(3):
        n = 1
        if i % 2 == 0:
            payload =  "candy"
        else:
            payload = "honey"    
        eventData = {MQTT_TOPICS[n] : payload}
        client.publishEvent(typeId=type_id, deviceId=client_id, eventId=MQTT_TOPICS[n], msgFormat="json", data=eventData, qos = 2, onPublish=publish(topic = MQTT_TOPICS[n], payload = payload))
        time.sleep(5)
    client.publishEvent(typeId=type_id, deviceId=client_id, eventId="User01", msgFormat="json", data={'CustomerId': 'Reset'}, qos = 2, onPublish=publish(topic = MQTT_TOPICS[0], payload = "Reset"))
    
if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        print("Exception: ", e)