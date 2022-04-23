import time
import json
import pandas as pd
from typing import Optional
import wiotp.sdk.application
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from csv import writer
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

USER = ""
client_id = "project"
type_id = "RaspberryPi"
MQTT_TOPICS = ["CustomerId"]
dataset = "Groceries_dataset_new.csv"
app = FastAPI()
app.model = GroceryDataModel()
app.cost_dict = {}
app.product_suggestion_dict = {}
app.bill = 0
app.session_data = []
list_data = []


# Init the model
def init(dataset: str):
    #Create association rule mining model
    global list_data
    list_data = []
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

# Return the suggestion product and it's cost
def get_product_cost_suggestion(p_name: str):
    if p_name in app.product_suggestion_dict:
        product_inst = Product()
        product_inst.itemDescription = p_name
        product_inst.itemCost = app.cost_dict[p_name]
        product_inst.productSuggestion = app.product_suggestion_dict[p_name]
        #product_inst_json = jsonable_encoder(product_inst)
        return product_inst.productSuggestion, product_inst.itemCost
    else:
        raise HTTPException(status_code=404, detail="Product not found")

# Return the cost of the product
def get_product_cost(p_name: str):
    if p_name in app.cost_dict:
        product_inst = Product()
        product_inst.itemDescription = p_name
        product_inst.itemCost = app.cost_dict[p_name]
        #product_inst_json = jsonable_encoder(product_inst)
        return product_inst.itemCost
    else:
        raise HTTPException(status_code=404, detail="Product not found")

# The main callback function of subscribing
def CallBack(evt):
    if evt.eventId == MQTT_TOPICS[0]:
        globalChannel(evt)
    else: 
        userChannel(evt)

# When the message is from  a user channel, put the payload in model and get a suggestion back
def userChannel(evt):
    global list_data
    if evt.eventId == USER+":reset":
        update_database()
    else:
        payload = json.dumps(evt.data).strip("{\" }").replace('"','').split(":")
        p_name = payload[2].lstrip(' ')
        suggestion, suggestion_cost = get_product_cost_suggestion(p_name)
        product_cost = get_product_cost(p_name)
        print(f"Product : {p_name}, Suggestion : {suggestion}")
        list_data.append([evt.eventId, p_name, product_cost])
        MQTT_publish(USER+":suggestion", USER+":suggestion", suggestion)
        return suggestion
    
# When the message is from the global channel, subscribe to the user(which will be the payload of message) 
def globalChannel(evt):
    global USER
    payload = json.dumps(evt.data).strip("{\" }").replace('"','').split(":")
    user_id = payload[1].lstrip(' ')
    client.subscribeToDeviceEvents(eventId=user_id+":scanned_item")
    client.subscribeToDeviceEvents(eventId=user_id+":reset")
    USER = user_id
    print("Subscribe to", user_id)
    init(dataset)

# The onPublish function in MQTT_publish
def printing(topic, key, payload):
    print(f"Send to topic `{topic}` => {key}: {payload}")

# Publish the message by MQTT
# event_id: topic of the message
# key : the first part
# value : the second part
def MQTT_publish(event_id, key, value):
    eventData = {key : value}
    client.publishEvent(typeId=type_id, deviceId=client_id, eventId=event_id, msgFormat="json", data=eventData, qos = 2, onPublish=printing(topic = event_id, key = key, payload = value))

# Update the database after the user checkout
def update_database():
    timestr = time.strftime("%Y%m%d_%H%M%S")
    filename = "Grocery_data_" + timestr + ".csv"
    app.model.database = app.model.database.append(pd.DataFrame(app.session_data,columns = ['Member_number','itemDescription','itemCost']))
    msg = "Updated dataset " + filename + " at time " + timestr
    print(msg)

    with open(dataset, 'a', newline='') as f_object:  
        writer_object = writer(f_object)
        for data in list_data:
            writer_object.writerow(data)  
        f_object.close()
    return msg
    
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
            time.sleep(1)
    except Exception as e:
        print("Exception: ", e)