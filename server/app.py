from pydoc_data.topics import topics
import time
import json
import wiotp.sdk.application
from flask import Flask, render_template

app = Flask(__name__)

dec_arr = []

def DoorCallback(evt):
    global dec_arr
    payload = json.dumps(evt.data).strip("{\" }").replace('"','').split(":")
    command = payload[1].lstrip(' ')
    decision = f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} || Decision: {command}"
    print(decision)
    dec_arr.append(decision)

print('1')
options = wiotp.sdk.application.parseConfigFile("application.yaml")
print('2')
client = wiotp.sdk.application.ApplicationClient(config=options)
print('3')
client.connect()
print('4')
client.subscribeToDeviceEvents(eventId="Door")
print('5')
client.deviceEventCallback = DoorCallback
print('6')

@app.route("/")
def getUser():
    return "Hello, World!"

@app.route("/<name>", methods=['GET'])
def queryDataMessageByName(name):
    pass

if __name__ == '__main__':
    app.run()