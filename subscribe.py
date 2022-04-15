from pydoc_data.topics import topics
import time
import json
import wiotp.sdk.application

client_id = "2"
subtopics = ["Door"]

def DoorCallback(evt):
    payload = json.dumps(evt.data).strip("{\" }").replace('"','').split(":")
    command = payload[1].lstrip(' ')
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + command)

def run():
    options = wiotp.sdk.application.parseConfigFile("application.yaml")
    client = wiotp.sdk.application.ApplicationClient(config=options)
    client.connect()
    for subs in subtopics:
        client.subscribeToDeviceEvents(eventId=subs)
    client.deviceEventCallback = DoorCallback
    
    while True:
        time.sleep(5)

if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        print("Exception: ", e)