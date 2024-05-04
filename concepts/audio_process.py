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
audio_collection = database.audio_collection
audience_document = database.audience_document


async def create_a_audio_record(audio_idx:int,audio_note: str):
    #check if the audio_idx is already in the database
    document = audio_collection.find_one({"index":audio_idx})
    if document:
        print("The audio index is already in the database")
        return await add_audio_note_by_index(audio_idx, audio_note)
    else:
        audio_note_list = [audio_note]
        document = Audio_Record(index=audio_idx, audio_note=audio_note_list)
        result = audio_collection.insert_one(document.dict())
        return document

async def fetch_one_audio_record_by_id(_id: str):
    document = audio_collection.find_one({"_id":ObjectId(_id)})
    return document

async def fetch_one_audio_record_by_index(index: int):
    document = audio_collection.find_one({"index":index})
    return document

async def fetch_all_audio_records():
    all_records = []
    cursor = audio_collection.find({})
    for document in cursor:
        all_records.append(Audio_Record(**document))
    return all_records

async def add_audio_note_by_id(_id: str, audio_note: str):
    document = fetch_one_audio_record_by_id(_id)
    if document:
        document["audio_note"].append(audio_note)
        audio_collection.update_one({"_id":ObjectId(_id)}, {"$set": {"audio_note": document["audio_note"]}})
        return document
    else:
        return None
    
async def add_audio_note_by_index(index: int, audio_note: str):
    document = await fetch_one_audio_record_by_index(index)
    if document:
        document["audio_note"].append(audio_note)
        audio_collection.update_one({"index":index}, {"$set": {"audio_note": document["audio_note"]}})
        return document
    else:
        return None
    
async def remove_latest_audio_note_by_id(_id: str):
    document = fetch_one_audio_record_by_id(_id)
    if document:
        document["audio_note"].pop()
        audio_collection.update_one({"_id":ObjectId(_id)}, {"$set": {"audio_note": document["audio_note"]}})
        return document
    else:
        return None
    
async def remove_audio_record_by_id(_id: str):
    document = fetch_one_audio_record_by_id(_id)
    if document:
        audio_collection.delete_one({"_id":ObjectId(_id)})
        return True
    else:
        return False
    
async def remove_audio_record_by_index(index: int):
    document = fetch_one_audio_record_by_index(index)
    if document:
        audio_collection.delete_one({"index":index})
        return True
    else:
        return False

async def get_most_recent_audio_record():
    docs = await fetch_all_audio_records()
    return docs[-1]
    
async def update_most_recent_audio_record(audio_note: str):
    doc = await get_most_recent_audio_record()
    return await add_audio_note_by_index(doc.index, audio_note)



OpenAIclient = OpenAI(api_key='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')
     
assitence_questions = [
    'Can you introduce yourself? What is your name? What is your age?',
    'Are you a student or a faculty at GSD community? What is your major or profession?',
    'Why you come to this exhibition?'
    'How would you describe yourself? Your characteristics, your interests, your hobbies, etc.',
    'How do you define the boundary between digital and physical realities? Do you believe these boundaries are rigid or fluid?',
    "What are your thoughts on AI's role in shaping our daily experiences and the future of human work?",
    'How do you think of the  technologies like AR, VR, and the Metaverse blurring the lines between realities, how do you personally relate to these technologies?'
]
async def merge_audio_notes_with_questions(audio_note: list[str]):
    merge_result = ''
    for i in range(len(assitence_questions)):
        merge_result += "question: " + assitence_questions[i] + "audience anwser: " + audio_note[i]
    return merge_result
async def parse_audio_to_audience_notes(audio_note: list[str]):
    function = [
        {
            "name": "parse_audio_to_audience_doc_object",
            "description": "summary and reform the audio notes and create a audience doc object",
            "parameters": {
                "type": "object",
                "properties": {
                    "audience_name": {
                        "type": "string",
                        "description": "the name of the audience"
                    },
                    "audio_note": {
                        "type": "string",
                        "description": "the description that describes the audience based on the audio notes"
                    }
                }
            }
        }
    ]
    audio_message = await merge_audio_notes_with_questions(audio_note)
    message = [
            {
                "role": "system",
                "content": "You are a persona creator. You will be provided with a set of questions and anwsers \
                    which are conversation with an audience. Based on these set of Q&A, form a description of a 'persona'\
                    which should detaily describe and simulate the audience feautures including but not limited to the points that\
                    are mentioned in the questions."
            },
            {
                "role": "user",
                "content": audio_message
            }
        ]
    print("done")
    # for i in range(len(audio_note)-1):
    response = OpenAIclient.chat.completions.create(
        model = "gpt-4-turbo-preview",
        messages = message,
        functions = function,
        function_call = {
            "name": function[0]["name"]
        }
    )
    result_args = response.choices[0].message.function_call.arguments
    return json.loads(result_args)
    
    
# async def get_audience_name(audio_note: str):
#     message = [
#         {
#             "role": "system",
#             "content": "Based on the string, which is the response from a person to the question 'What is your name? What is your age?', get the name of the audience. Because the string is generated by the audio, it might be a little bit different from the original response. Try to take a guess on the most possible name."
#         }, 
#         {
#             "role": "user",
#             "content": audio_note
#         }
#     ]
#     response = OpenAIclient.chat.completions.create(
#         model = "gpt-4.0",
#         messages = message,
#     )
#     return response.choices[0].message
    
# process the audio_not (a list of string) to a dictionary
async def create_Audience_doc(index:int, audience_name: str, audience_description: str):
    document = Audience_doc(index=index, audiencename = audience_name, audience_description=audience_description)
    result = audience_document.insert_one(document.dict())
    return document

async def get_audience_doc_by_index(index: int):
    document = audience_document.find_one({"index":index})
    return document

