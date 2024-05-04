from model import Persona, Persona_Demands, Persona_Generated_Response, Audience_doc, Audio_Record, Design_Project, Predicted_Audience_Response,Single_Project_Prediction
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
Audience_Response_collection = database.Audience_Response_collection
Processed_Prediction = database.Predicted_Audience_Response
Single_Project_Prediction_Collection = database.Single_Project_Prediction_collection
OpenAIclient = OpenAI(api_key='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')

async def predict_audience_response_on_projects(project: Design_Project, audience: Audience_doc):
    #args: project: a Design_Project object, audience: a Audience_doc object
    #return: a string of response from the audience to the project
    
    #get image through the image_path
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    image_path = project["image_path"][0] #"./detect_image/butter.jpg"
    base64_image1 = encode_image(image_path)
    projectname = project["project_name"]
    projectauthor = project["author_name"]
    projectdescription = project["description"]
    print("predicted on", project["project_name"])
    message = [
        {
            "role": "system",
            "content": "You are a persona simulator expert. Based on the given person description, \
                        You should now pretent that you are that person and complete the following tasks."
        },
        {
            "role": "user",
            "content": [
                {"type": "text", 
                 "text":
                    f"Here is the person description: {audience.audiencename}.\
                        try to deeply comprehend the characteristics and imagine that you are the person.\
                        Now, I have a design project for you. The project is called {projectname}, created by {projectauthor}\
                        The project description is: {projectdescription}.\
                        The project image is shown belowed.\
                        Now, you are that person, try to describe what will be your reaction to the project.\
                        Your response may include but not limited to the following points:\
                            1.whether you like the project or not\
                            2.what do you think of the project\
                            3.what do you think of the underlying idea (philosophy) of the project\
                            4.how you might (physically or digirally) interact with the project\
                            5.what feedback you might give to the project author\
                            6.any other thoughts you might have on the project."
                },
                {"type": "image_url", 
                 "image_url": {
                    "url":f"data:image/jpeg;base64,{base64_image1}"
                    }
                }
            ]
        } 
    ]
    response = OpenAIclient.chat.completions.create(
        model = "gpt-4-turbo",
        messages = message,
        max_tokens = 100
    )
    await create_single_project_prediction(project["project_name"], audience.audiencename, response.choices[0].message.content)
    return response.choices[0].message.content

    #processed_response = await process_response(audience.audiencename, predicted_result)

async def create_single_project_prediction(project_name: str, audience_name: str, prediction_result: str):
   #exist_document = Single_Project_Prediction.find_one({"project_name":project_name, "audience_name":audience_name})
    # if exist_document:
        #first delete the existing document
    # await delete_single_project_prediction(project_name, audience_name)
    document = Single_Project_Prediction(project_name=project_name, audience_name=audience_name, prediction_result=prediction_result)
    result = Single_Project_Prediction_Collection.insert_one(document.dict())
    return document
    
async def delete_single_project_prediction(project_name: str, audience_name: str):
    exist_document = Single_Project_Prediction_Collection.find_one({"project_name":project_name, "audience_name":audience_name})
    if exist_document:
        Single_Project_Prediction_Collection.delete_one({"project_name":project_name, "audience_name":audience_name})
        return True
    else:
        return False
    
async def get_single_project_prediction(audience_name: str):
    result = []
    cursor = Single_Project_Prediction_Collection.find({"audience_name":audience_name})
    for document in cursor:
        result.append(document)
    print(result)
    return result

project_name_list = ["AnotherWorld"]

async def all_prediction_and_response(audience: Audience_doc, project_responses: str):
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    floorplan_path = "./project_images/floorplan.png"
    base64_image1 = encode_image(floorplan_path)
    print("process all")
    message = [
        {
            "role": "system",
            "content": f"We are holding a creative-tech exhibition. We have an audience, named {audience.audiencename} coming to the exhibition.\
                So far we have another AI agent that predict and simulate how {audience.audiencename} might respond to each projects in the exhibition.\
                Your task is processing all the responses and rewrite a paragraph to summarize the responds and provide the\
                overall prediction of {audience.audiencename} response to the whole exhibition.\
                Your summary should include but not limited to the following points:\
                    1. which project they might like most\
                    2. what should they consider when they are viewing the exhibition\
                    3. is there any recommendation for they to view the exhibition\
                    4. any other thoughts they might have on the exhibition. \
                in the final output, your tone of voice should be a simulator of {audience.audiencename}\
                as your text will be an audio that played when the audience enter the exhibition, the final response example maybe like:\
                    'Hi, I am {audience.audiencename}, or let's say, another you. I am so excited to be here.\
                    Technologically speaking, I am a little bit conservative towards AI technology, but I am open to new things.\
                    One of the projects that might be interesting is called..., but I'm also wondering ... '\
                In addition, the floor plan of the exhibition is shown belowed.\
                You can add contents related to the overallfloor plan in your response."
        }, 
        {
            "role": "user",
            "content": [
                {"type": "text",
                 "text": f"The audience original response corresponding to each projects are: {project_responses}.\
                     The whole exhibition is like a house, each project takes a room, the floor plan image is shown belowed."}, 
                {
                    "type": "image_url",
                    "image_url": {"url":f"data:image/jpeg;base64,{base64_image1}"}
                }]
        }
    ]
    response = OpenAIclient.chat.completions.create(
        model = "gpt-4-turbo",
        messages = message,
    )
    all_processed_result = response.choices[0].message.content
    new_predicted_audience_response = Predicted_Audience_Response(audience_name=audience.audiencename, processed_response=all_processed_result)
    Processed_Prediction.insert_one(new_predicted_audience_response.dict())
    return all_processed_result

async def get_all_predicted_audience_response():
    result = []
    cursor = Processed_Prediction.find({})
    for document in cursor:
        result.append(document)
    return result

length = 0
async def get_predicted_audience_collection_length():
    global length
    new_length = Processed_Prediction.count_documents({})
    if new_length > length:
        length = new_length
        print("new length", length)
        return True
    else:
        print("no new length")
        return False
    
async def get_predicted_audience_response_by_name(audience_name: str):
    document = Processed_Prediction.find_one({"audience_name":audience_name})
    return document

# async def process_response(audience_name: str, original_doc: Predicted_Audience_Response):
#     #args: original_response: a string of response from the audience to the project
#     #return: a list of string which is the processed response
#     #process the original response to a structure project: reponse
#     original_predicts = ""
#     for i in range(len(original_doc.original_prediction)):
#         original_predicts += project_name_list[i]+": "+original_doc.original_prediction[i] + " \n"
        
#     def encode_image(image_path):
#         with open(image_path, "rb") as image_file:
#             return base64.b64encode(image_file.read()).decode('utf-8')
    
#     floorplan_path = "./project_images/floorplan.jpg"
#     base64_image1 = encode_image(floorplan_path)
#     message = [
#         {
#             "role": "system",
#             "content": f"You will be given a paragraph of text which will be the original prediction\
#                 about {original_doc.audience_name} responds to several projects in an exhibition. As the prediction is seperated by different projects,\
#                 you should process the response and rewrite a paragraph to summarize the responds and provide the\
#                 overall prediction of {original_doc.audience_name} response to the whole exhibition.\
#                 Your summary should include but not limited to the following points:\
#                     1. which project {original_doc.audience_name} might like most\
#                     2. what should {original_doc.audience_name} consider when they are viewing the exhibition\
#                     3. is there any recommendation for {original_doc.audience_name} to view the exhibition\
#                     4. any other thoughts {original_doc.audience_name} might have on the exhibition. \
#                 in the final output, your tone of voice should be a simulator of the audience (another him/her)\
#                 as your text will be an audio that played when the audience enter the exhibition, the final response example maybe like:\
#                     'Hi, I am {original_doc.audience_name}, or let's say, another {original_doc.audience_name}. I am so excited to be here.\
#                     Technologically speaking, I am a little bit conservative towards AI technology, but I am open to new things.\
#                     One of the projects that might be interesting is called..., but I'm also wondering ... '\
#                 In addition, the floor plan of the exhibition is shown belowed.\
#                 You can add contents related to the overallfloor plan in your response."
#         }, 
#         {
#             "role": "user",
#             "content": [
#                 {"type": "text",
#                  "text": f"The original response is: {original_predicts}, the image is shown belowed."}, 
#                 {
#                     "type": "image_url",
#                     "image_url": f"data:image/jpeg;base64,{base64_image1}"
#                 }]
#         }
#     ]
#     response = OpenAIclient.chat.completions.create(
#         model = "gpt-4.0",
#         messages = message,
#     )
#     return response.choices[0].message
    