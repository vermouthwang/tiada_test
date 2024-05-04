from model import Persona, Persona_Demands, Persona_Generated_Response
from pymongo.mongo_client import MongoClient
#from utils import generate_persona_with_client_demands 

from openai import OpenAI
import json
from typing import List

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
generate_collection = database.generated_collection
persona_collection = database.persona_collection

#set up the connection to the OpenAI API
OpenAIclient = OpenAI(api_key='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')

async def generate_persona_with_client_demands(product_info, persona_demands):   
    functions = [
        {
            "name": "createpersona",
            "description": "Create a persona based on the given feature.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the persona."
                    },
                    "age": {
                        "type": "integer",
                        "description": "Age of the persona."
                    },
                    "occupation": {
                        "type": "string",
                        "description": "Occupation of the persona."
                    },
                    "location": {
                        "type": "string",
                        "description": "Location of the persona."
                    },
                    "gender": {
                        "type": "string",
                        "description" : "Gender of the persona."
                    },
                    "characteristic": {
                        "type": "string",
                        "description": "A around 150 words description of the persona's characteristic."
                    },
                    "have_use_the_product": {
                        "type": "boolean",
                        "description": "Whether the persona has used the product before."
                    },
                    "exploration_rate": {
                        "type": "number",
                        "description": "A float number between 0 and 1 to indicate how much the persona is willing to explore new things or new elements in the product."
                    }
                }, "required": ["name", "age", "occupation", "location", "gender", "characteristic", "have_use_the_product", "exploration_rate"]
            }  
        }
    ]
    message = [
                {
                    "role": "system",
                    "content": "You are persona creator. Please generate a persona based on the given feature."
                },
                {
                    "role": "user",
                    "content": f"For the product:instagram, Create a persona based on the following requirements:."
                }
            ]
    #  { persona_demands["demands"] }
    result = []
    for i in range(persona_demands["number"]):
        response = OpenAIclient.chat.completions.create(
            model = "gpt-4-turbo-preview",
            messages = message,
            functions = functions,
            function_call = {
                "name": functions[0]["name"]
            }
        )
        new_persona = response.choices[0].message.function_call.arguments
        personas_arguments = json.loads(new_persona)
        result.append(await generate_persona_object(personas_arguments))
        message.append({"role": "assistant", "content": new_persona})
        message.append({"role": "user", "content": "Create another different persona."})
    
    return result

# single persona function
async def generate_persona_object(persona):
    the_persona = Persona(
                   name=persona["name"], 
                   age=persona["age"], 
                   occupation=persona["occupation"], 
                   location=persona["location"],
                   gender=persona["gender"],
                   characteristic=persona["characteristic"],
                   have_use_the_product=persona["have_use_the_product"],
                   exploration_rate=persona["exploration_rate"])
    result = persona_collection.insert_one(the_persona.dict())
    return the_persona
    
# persona collection function
async def create_persona_collection(persona_demands):
    persona_list = await generate_persona_with_client_demands("instagram",persona_demands)
    #chatgpt_response = await generate_persona_with_client_demands("instagram",persona_demands)
    # document = Persona_Generated_Response(collection_name=persona_demands["collection_name"], number=persona_demands["number"], response=chatgpt_response)
    # result = collection.insert_one(document.dict())
    document = Persona_Generated_Response(case_name=persona_demands["case_name"],collection_name=persona_demands["collection_name"], number=persona_demands["number"], response=persona_list)
    result = generate_collection.insert_one(document.dict())
    return document

async def fetch_one_collection_by_name(collection_name):
    document = generate_collection.find_one({"collection_name": collection_name})
    return document

async def fetch_all_collections():
    collections = []
    cursor = generate_collection.find({})
    for document in cursor:
        collections.append(Persona_Generated_Response(**document))
    return collections

async def remove_collection_by_name(collection_name):
    generate_collection.delete_one({"collection_name": collection_name})
    return True

async def update_collection_by_name(collection_name, new_collection_name):
    generate_collection.update_one({"collection_name": collection_name}, {"$set": {"collection_name": new_collection_name}})
    document = generate_collection.find_one({"collection_name": new_collection_name})
    return document
    

async def remove_all_collections():
    generate_collection.delete_many({})
    return True


