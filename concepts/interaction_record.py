from model import Persona, Action, Test_Result
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
# class Action(BaseModel):
#     action: Literal["button_click", "scroll_down", "scroll_up"]
#     action_description: str
#     feedback: str
    
# class Test_Result(BaseModel):
#     persona: Persona
#     step_length: int
#     actions: list[Action]
#     message: str = ""
#     goal_achieved: bool = False

# class Result_Collection(BaseModel):
#     collection_name: str
#     number: int
#     results: list[Test_Result]

    
database = client.Personas
interaction_collection = database.interaction_record_collection


async def create_a_interaction_record(persona: Persona):
    document = Test_Result(persona=persona,step_length=0, actions=[], message="", goal_achieved=False)
    result = interaction_collection.insert_one(document.dict())
    return document

async def fetch_one_interaction_record_by_id(_id: str):
    document = interaction_collection.find_one({"_id":ObjectId(_id)})
    # return document
    return document

async def fetch_all_interaction_records():
    all_records = []
    cursor = interaction_collection.find({})
    for document in cursor:
        all_records.append(Test_Result(**document))
    return all_records

async def update_interaction_action_by_id(id: str, action: Action):
    document = await fetch_one_interaction_record_by_id(id)
    the_action = action.model_dump()  # Convert Pydantic model to dictionary
    if document:
        document['actions'].append(the_action)
        print(document)
        interaction_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"actions": document['actions']}}
        )
        return document
    else:
        return None
    
async def update_interaction_message_by_id(id: str, message: str):
    document = await fetch_one_interaction_record_by_id(id)
    if document:
        document['message'] = message
        interaction_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"message": message}}
        )
        return document
    else:
        return None
    
async def update_interaction_goal_achieved_by_id(id: str, goal_achieved: bool):
    document = await fetch_one_interaction_record_by_id(id)
    if document:
        document['goal_achieved'] = goal_achieved
        interaction_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"goal_achieved": goal_achieved}}
        )
        return document
    else:
        return None
    
async def remove_interaction_record_by_id(id: str):
    interaction_collection.delete_one({"_id": ObjectId(id)})
    return True

async def add_interaction_step_length_by_id(id: str):
    document = await fetch_one_interaction_record_by_id(id)
    if document:
        document['step_length'] += 1
        interaction_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"step_length": document['step_length']}}
        )
        return document
    else:
        return None