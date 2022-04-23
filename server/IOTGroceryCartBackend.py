from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
from mlxtend.preprocessing import TransactionEncoder
import time
import random

#install uvicorn,pandas,fastapi,pydantic,BaseModel,Optional,mlxtend
#to run  use "uvicorn main:app --reload"

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

# Create an instance of the application
app = FastAPI()
#Global Variables
app.model = GroceryDataModel()
app.cost_dict = {}
app.product_suggestion_dict = {}
app.bill = 0
app.member_id = 0
app.session_data = []

@app.get('/hello')
def hello_world():
    return("Welcome to IOT Shopping Cart Backend by Group 17")

@app.post('/Initialize')
async def init(dataset: str):
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

@app.post('/validate_user')
def validate_user(mobile_id:str):
    member_ids = app.model.database['Member_number'].unique()
    member_id = int(random.choice(member_ids))
    return member_id
    

@app.get('/getproduct/cost/{p_name}')
def get_product_cost(p_name: str):
    if p_name in app.cost_dict:
        product_inst = Product()
        product_inst.itemDescription = p_name
        product_inst.itemCost = app.cost_dict[p_name]
        product_inst_json = jsonable_encoder(product_inst)
        return JSONResponse(content = product_inst_json)
    else:
        raise HTTPException(status_code=404, detail="Product not found")
    

@app.get('/getproduct/cost_and_suggestion/{p_name}')
def get_product_cost_suggestion(p_name: str):
    if p_name in app.product_suggestion_dict:
        product_inst = Product()
        product_inst.itemDescription = p_name
        product_inst.itemCost = app.cost_dict[p_name]
        product_inst.productSuggestion = app.product_suggestion_dict[p_name]
        product_inst_json = jsonable_encoder(product_inst)
        return JSONResponse(content = product_inst_json)
    else:
        raise HTTPException(status_code=404, detail="Product not found")

@app.put('/putproduct/{member_product_name}')
def put_product(member_id: int, p_name: str):
    if p_name in app.cost_dict:
        app.session_data.append([member_id,p_name,app.cost_dict[p_name]])        
        app.bill = app.bill + app.cost_dict[p_name]        
        data_json = jsonable_encoder([member_id,p_name,app.cost_dict[p_name]])
        return JSONResponse(content=data_json)
    else:
        raise HTTPException(status_code=404, detail="Product not found")

@app.get('/bill/{member}')
def get_bill(member:int):
    return app.bill

@app.post('/update_database')
def update_database():
    timestr = time.strftime("%Y%m%d_%H%M%S")
    filename = "Grocery_data_" + timestr + ".csv"
    app.model.database = app.model.database.append(pd.DataFrame(app.session_data,columns = ['Member_number','itemDescription','itemCost']))
    app.model.database.to_csv(filename)
    msg = "Updated dataset " + filename + " at time " + timestr
    print(app.model.database.tail())
    return msg