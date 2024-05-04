from pydantic import BaseModel, Field
from enum import Enum
from typing import Literal
from bson.objectid import ObjectId

class Test_Case(BaseModel):
    case_name: str
    pass_word: str
    
class Todo(BaseModel):
    title: str
    description: str
    
class Persona_Demands(BaseModel):
#This is the model for client input of what they want in the personas.
    case_name: str
    collection_name: str
    number: int
    demands: str
    test_problems: str = "general problems"
    
class Persona(BaseModel):
    name: str
    age: int
    occupation: str
    location: str
    gender: str
    characteristic: str
    have_use_the_product: bool
    exploration_rate: float
    
class Persona_Generated_Response(BaseModel):
#This is the model for the response of the generated personas from ChatGPT
    case_name: str
    collection_name: str
    number: int
    #response is a list of Persona
    response: list[Persona]
    

    
# class ActionType(str, Enum):
#     BUTTON_CLICK = "button_click"
#     SCROLL_DOWN = "scroll_down"
#     SCROLL_UP = "scroll_up"

class Action(BaseModel):
    action: Literal["button_click", "scroll_down", "scroll_up"]
    action_description: str
    feedback: str
    
class Test_Result(BaseModel):
    persona: Persona
    step_length: int
    actions: list[Action]
    message: str = ""
    goal_achieved: bool = False

class Result_Collection(BaseModel):
    collection_name: str
    number: int
    results: list[Test_Result]
    
class Audio_Record(BaseModel):
    index: int
    audio_note: list[str]
    
class Audience_doc(BaseModel):
    index: int
    audiencename: str
    audience_description: str
    
class Design_Project(BaseModel):
    author_name: str
    project_name: str
    description: str
    image_path: list[str] #"./detect_image/butter.jpg"
class Single_Project_Prediction(BaseModel):
    project_name: str
    audience_name: str
    prediction_result: str
class Predicted_Audience_Response(BaseModel):
    audience_name: str
    # original_prediction: list[str]
    processed_response: str
    
class Audience_feedback(BaseModel):
    audience_name: str
    feedback: str