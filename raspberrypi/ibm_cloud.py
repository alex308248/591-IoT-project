# Installation
# $pip3 install libsvm-official
# If you ran into error such as (ERROR: Could not build wheels for scipy which use PEP 517 and cannot be installed directly)
# Try update pip
# $pip3 install --upgrade pip
# https://stackoverflow.com/questions/61365790/error-could-not-build-wheels-for-scipy-which-use-pep-517-and-cannot-be-installe
from libsvm.svmutil import *
import wiotp.sdk.application
import time
import json

client_id = "1"
MQTT_TOPICS = ["Door"]
resetFlag = False

"""
# Read data in LIBSVM format. Replace 'combine_open_close.txt' with your training dataset.
y, x = svm_read_problem('combine_open_close.txt')
# Generate model
m = svm_train(y, x)
# Save trained model
svm_save_model('trained.model', m)
"""

# Load model
#trained_model = svm_load_model('trained.model')
#trained_model = svm_load_model('threelabel.model')

# label
y_2 = [-1]
"""
# vector
x_2 = [{1: 3.5267175572519083, 2: 0.20610687022900764, 3: -0.3893129770992366, 4: 1.05419921875, 5: -0.01123046875, 6: 0.13134765625}]
"""

"""
def publish(topic, payload):
    print(f"Send to topic `{topic}`:    {payload}")
"""

def eventPublishCallback(topic, payload):
    print(f"Send to topic `{topic}`:    {payload}")

def myEventCallback(event):
    global resetFlag
    #str = "%s event '%s' received from device [%s]: %s"
    print(event.eventId)
    #print(str % (event.format, event.eventId, event.device, json.dumps(event.data)))
    #print(event.data)
    #print(event.data[event.eventId])
    #reset condition
    
    if "reset" in event.eventId:
        print("reset")
        resetFlag = True
        
    elif "41_217_238_60" == event.data[event.eventId]:
        print("reset")
        resetFlag = True
    


def subscribe(client, topic):
    client.deviceEventCallback = myEventCallback
    client.subscribeToDeviceEvents(eventId=topic, qos = 2)
    print(f"Subscribe to topic {topic}")

def publish(client, topic, payload):
    eventData = {topic : payload}
    client.publishEvent(typeId="RaspberryPi", deviceId=client_id, eventId=topic, msgFormat="json", data=eventData, qos = 2, onPublish=eventPublishCallback(topic = topic, payload = payload))

def connect_ibm():
    options = wiotp.sdk.application.parseConfigFile("application.yaml")
    client = wiotp.sdk.application.ApplicationClient(config=options)
    client.connect()
    return(client)

def getResetFlag():
    return(resetFlag)

def reset():
    global resetFlag
    resetFlag = False

# label [+1] or [-1]
# vector [{1: 3.5267175572519083, 2: 0.20610687022900764, 3: -0.3893129770992366, 4: 1.05419921875, 5: -0.01123046875, 6: 0.13134765625}]
def run_prediction(label, vector, model, client, lastDecision):
    client_id = "1"
    MQTT_TOPICS = ["Door"]
    n = 0
    p_labs, p_acc, p_vals = svm_predict(label, vector, model)
    # print(f"p_labs: {p_labs}")
    #decision = 'Open' if p_labs == [1.0] else 'Close'
    if p_labs[0] == 1.0:
        decision = "Open"
    elif p_labs[0] == -1.0:
        decision = "Close"
    elif p_labs[0] == 0.0:
        decision = "Stable"
    """
    options = wiotp.sdk.application.parseConfigFile("application.yaml")
    client = wiotp.sdk.application.ApplicationClient(config=options)
    client.connect()
    """
    payload = decision
    eventData = {'Door' : payload}
    """
    if lastDecision != decision:
        client.publishEvent(typeId="RaspberryPi", deviceId=client_id, eventId=MQTT_TOPICS[n], msgFormat="json", data=eventData, qos = 2, onPublish=publish(topic = MQTT_TOPICS[n], payload = payload))
        print(f"Decision: {decision}")
    """
    if lastDecision == "Stable" and decision != "Stable":
        client.publishEvent(typeId="RaspberryPi", deviceId=client_id, eventId=MQTT_TOPICS[n], msgFormat="json", data=eventData, qos = 2, onPublish=eventPublishCallback(topic = MQTT_TOPICS[n], payload = payload))
    print(f"Decision: {decision}")
    #lastDecision = decision
    time.sleep(1)
    return(decision)
"""
if __name__ == "__main__":
    run_prediction(y_2, x_2, trained_model)
"""