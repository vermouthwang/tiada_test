from model import Audience_feedback
from pymongo.mongo_client import MongoClient
#from utils import generate_persona_with_client_demands 
import random
from openai import OpenAI
import json
from typing import List
import base64

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

database = client.Personas
feedback_collection = database.feedback_collection

async def create_a_feedback_record(audience_name: str, feedback: str):
    document = Audience_feedback(audience_name=audience_name, feedback=feedback)
    result = feedback_collection.insert_one(document.dict())
    return document
