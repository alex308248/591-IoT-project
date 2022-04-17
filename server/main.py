from pydoc_data.topics import topics
import time
import json
from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel
from typing import Optional
import wiotp.sdk.application
import ProductSuggestion
from flask import Flask, render_template

client_id = "project"
type_id = "RaspberryPi"
MQTT_TOPICS = ["Main","Suggestion"]
app = FastAPI()

def DoorCallback(evt):
    payload = json.dumps(evt.data).strip("{\" }").replace('"','').split(":")
    user_id = payload[1].lstrip(' ')
    decision = f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} || Decision: {command}"
    print(decision)
    client.subscribeToDeviceEvents(eventId=user_id)
    
def printing(topic, payload):
    print(f"Send to topic `{topic}`:    {payload}")

def publish(value):
    eventData = {'Suggestion' : value}
    client.publishEvent(typeId=type_id, deviceId=client_id, eventId=MQTT_TOPICS[1], msgFormat="json", data=eventData, qos = 2, onPublish=printing(topic = MQTT_TOPICS[1], payload = value))


print('1')
options = wiotp.sdk.application.parseConfigFile("application.yaml")
print('2')
client = wiotp.sdk.application.ApplicationClient(config=options)
print('3')
client.connect()
print('4')
client.subscribeToDeviceEvents(eventId=MQTT_TOPICS[0])
print('5')
client.deviceEventCallback = DoorCallback
print('6')

@app.get('/')
def hello_world():
    return("Main Page")
    
@app.get('/hello')
def hello_world():
    return("Welcome to PRodcut Suggestion")
    
@app.get('/getproduct/{p_name}')
def get_product(p_name: str):
    row = df[df['antecedents']==p_name]
    for index,value in row['consequents'].items():
        print(f"Index : {index}, Value : {value}")
        publish(value)
        return value

