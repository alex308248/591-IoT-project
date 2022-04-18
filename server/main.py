from pydoc_data.topics import topics
import time
import json
import pandas as pd
from typing import Optional
import wiotp.sdk.application
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
from mlxtend.preprocessing import TransactionEncoder

class Product(BaseModel):
    itemDescription: Optional[str] = None
    itemCost: Optional[str] = None
    productSuggestion: Optional[str] = None

class GroceryDataModel(BaseModel):
    basket: Optional[pd.DataFrame] = None
    transactions: Optional[pd.DataFrame] = None
    frequent_itemsets: Optional[pd.DataFrame] = None
    rules: Optional[pd.DataFrame] = None
    database: Optional[pd.DataFrame] = None

    class Config:
        arbitrary_types_allowed = True

client_id = "project"
type_id = "RaspberryPi"
MQTT_TOPICS = ["Main","Suggestion"]
app = FastAPI()
app.model = GroceryDataModel()
app.cost_dict = {}
app.product_suggestion_dict = {}
app.bill = 0
app.member_id = 0
app.session_data = []
#df = pd.read_csv('Results_New.csv')


def init(dataset: str):
    #Create association rule mining model
    app.model.database = pd.read_csv(dataset)
    app.model.basket = pd.read_csv(dataset)#("Groceries_dataset_new.csv")
    app.model.basket.itemDescription = app.model.basket.itemDescription.transform(lambda x: [x])
    app.model.basket = app.model.basket.groupby(['Member_number','itemCost']).sum()['itemDescription'].reset_index(drop=True)
    encoder = TransactionEncoder()
    app.model.transactions = pd.DataFrame(encoder.fit(app.model.basket).transform(app.model.basket), columns=encoder.columns_)
    app.model.frequent_itemsets = apriori(app.model.transactions, min_support= 1/len(app.model.basket), use_colnames=True, max_len = 2)
    app.model.rules = association_rules(app.model.frequent_itemsets, metric="lift",  min_threshold = 1.5).sort_values("lift", ascending = False)
    app.product_suggestion_dict = dict(zip(app.model.rules["antecedents"].apply(lambda x: list(x)[0]).astype("unicode"),app.model.rules["consequents"].apply(lambda x: list(x)[0]).astype("unicode")))
    #print(app.model.rules)
    print(app.product_suggestion_dict)

    #Setup cost dictionary to lookup item cost
    temp_basket = pd.read_csv("Groceries_dataset_new.csv")
    temp_basket = temp_basket.drop_duplicates(subset = ['itemDescription'])
    app.cost_dict = dict(zip(temp_basket.itemDescription,temp_basket.itemCost))
    #print(app.cost_dict)

    cost_dict_json = jsonable_encoder(app.cost_dict)
    return JSONResponse(content=cost_dict_json)

def userChannel(evt):
    payload = json.dumps(evt.data).strip("{\" }").replace('"','').split(":")
    p_name = payload[1].lstrip(' ')
    row = df[df['antecedents']==p_name]
    for index,value in row['consequents'].items():
        print(f"Index : {index}, Value : {value}")
        MQTT_publish(MQTT_TOPICS[1], evt.eventId, value)
        return value
    
def globalChannel(evt):
    payload = json.dumps(evt.data).strip("{\" }").replace('"','').split(":")
    user_id = payload[1].lstrip(' ')
    print("Subscribe to", user_id)
    client.subscribeToDeviceEvents(eventId=user_id)

def CallBack(evt):
    print(evt.eventId)
    if evt.eventId == MQTT_TOPICS[0]:
        globalChannel(evt)
    else: 
        userChannel(evt)
    
def printing(topic, key, payload):
    print(f"Send to topic `{topic}` => {key}: {payload}")

def MQTT_publish(event_id, key, value):
    eventData = {key : value}
    client.publishEvent(typeId=type_id, deviceId=client_id, eventId=event_id, msgFormat="json", data=eventData, qos = 2, onPublish=printing(topic = MQTT_TOPICS[1], key = key, payload = value))




print('1')
options = wiotp.sdk.application.parseConfigFile("application.yaml")
print('2')
client = wiotp.sdk.application.ApplicationClient(config=options)
print('3')
client.connect()
print('4')
client.subscribeToDeviceEvents(eventId=MQTT_TOPICS[0])
print('5')
client.deviceEventCallback = CallBack
print('6')


if __name__ == '__main__':
    try:
        while True:
            time.sleep(5)
    except Exception as e:
        print("Exception: ", e)