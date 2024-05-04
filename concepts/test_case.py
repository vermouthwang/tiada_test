from model import Persona, Action, Test_Result, Test_Case
from pymongo.mongo_client import MongoClient
#from utils import generate_persona_with_client_demands 
from openai import OpenAI
import json
from typing import List
import bson
import random
from bson.objectid import ObjectId

#set up the connection to the database
uri = "mongodb+srv://houhouwa:19981118Ac@tiada0.6myxdhp.mongodb.net/?retryWrites=true&w=majority&appName=tiada0"
# Create a new client and connect to the server
client = MongoClient(uri)
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
#Model
# class Test_Case(BaseModel):
#     case_name: str
#     pass_word: str

database = client.Personas
test_case_collection = database.test_case_collection

async def get_a_test_case_by_name(Case_name: str):
    document = test_case_collection.find_one({"Case_name": Case_name})
    return document

async def create_a_test_case(test_case: Test_Case):
    any_doc = get_a_test_case_by_name(test_case.case_name)
    if any_doc:
        return None
    else:
        document = test_case
        result = test_case_collection.insert_one(document.dict())
        return document

async def check_authorization_namepass(case_name: str, Pass_word: str):
    document = await get_a_test_case_by_name(case_name)
    if document:
        if document["pass_word"] == Pass_word:
            return document
        else:
            return False
    else:
        return False