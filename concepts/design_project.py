from model import Persona, Persona_Demands, Persona_Generated_Response, Audience_doc, Audio_Record, Design_Project
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
Design_Project_collection = database.Design_Project_collection

# class Design_Project(BaseModel):
#     author_name: str
#     project_name: str
#     description: str
#     image_path: list[str] #"./detect_image/butter.jpg"
design_projects_dict = [
    {"author_name": "Youtian Duan", 
     "project_name": "AnotherWorld", 
     "description": "Butter fly bulb",
     "image_path": ["./project_images/youtian_butterfly.png"]},
]
#TODO: currently only for one project, need to be extended to multiple projects
async def create_a_design_project(author_name: str, project_name: str, description: str, image_path: list[str]):
    exist_document = Design_Project_collection.find_one({"project_name":project_name})
    if exist_document:
        print("The design project is already in the database")
        return exist_document
    document = Design_Project(author_name=author_name, project_name=project_name, description=description, image_path=image_path)
    result = Design_Project_collection.insert_one(document.dict())
    return document

async def get_a_design_project_by_name(project_name: str):
    document = Design_Project_collection.find_one({"project_name":project_name})
    return document

async def get_all_design_project():
    project_name_list = ["AnotherWorld",
                         "Odyssey",
                         "Imaginary Physical Prototyping",
                         "Align: AI Rituals for Human Alignment",
                         "Pixel Persona",
                         "Harnessing the Power  of Video Games to Combat Climate Change"]
    all = []
    for projects in project_name_list:
        document = Design_Project_collection.find_one({"project_name":projects})
        all.append(document)
    return all