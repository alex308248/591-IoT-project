from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import pandas as pd

#install uvicorn,pandas,fastapi,pydantic,BaseModel,Optional
#to run  use "uvicorn main:app --reload"

app = FastAPI()


class ProductSuggestion(BaseModel):
    id: int
    antecedents: str
    consequents: str
    support: float
    confidence: float
    lift: float


df = pd.read_csv('Results_New.csv')
#print(df['antecedents'])

@app.get('/hello')
def hello_world():
    return("Welcome to PRodcut Suggestion")
    

@app.get('/getproduct/{p_name}')
def get_product(p_name: str):
    row = df[df['antecedents']==p_name]
    for index,value in row['consequents'].items():
        print(f"Index : {index}, Value : {value}")
        return value
