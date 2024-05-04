from fastapi import FastAPI, HTTPException
import pydantic.json
from fastapi.middleware.cors import CORSMiddleware
from model import Todo, Persona_Demands, Persona_Generated_Response, Persona, Action, Test_Result, Test_Case, Audio_Record, Audience_doc, Design_Project, Predicted_Audience_Response, Single_Project_Prediction, Audience_feedback
app = FastAPI()


from database import (
    fetch_one_todo,
    fetch_all_todos,
    create_todo,
    update_todo,
    remove_todo
)
from concepts.generate_personas_ondemand import (
    create_persona_collection,
    fetch_one_collection_by_name,
    fetch_all_collections,
    remove_collection_by_name,
    update_collection_by_name,
    remove_all_collections
    )
from concepts.interaction_record import (
    create_a_interaction_record,
    fetch_one_interaction_record_by_id,
    fetch_all_interaction_records,
    update_interaction_action_by_id,
    update_interaction_message_by_id,
    update_interaction_goal_achieved_by_id,
    remove_interaction_record_by_id,
    add_interaction_step_length_by_id
    )

from concepts.test_case import (
    get_a_test_case_by_name,
    create_a_test_case,
    check_authorization_namepass
)

from concepts.audio_process import (
    create_a_audio_record,
    fetch_one_audio_record_by_index,
    fetch_one_audio_record_by_id,
    fetch_all_audio_records,
    add_audio_note_by_id,
    add_audio_note_by_index,
    remove_audio_record_by_id,
    remove_audio_record_by_index,
    get_most_recent_audio_record,
    update_most_recent_audio_record,
    parse_audio_to_audience_notes,
    create_Audience_doc,
    get_audience_doc_by_index
)

from concepts.design_project import (
    create_a_design_project,
    get_a_design_project_by_name,
    get_all_design_project
)

from concepts.predict_response_op import (
    predict_audience_response_on_projects,
    all_prediction_and_response,
    get_all_predicted_audience_response,
    get_predicted_audience_collection_length,
    get_predicted_audience_response_by_name,
    get_single_project_prediction
)
from concepts.audience_feedback import (
    create_a_feedback_record
)
origins = ['http://localhost:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
async def read_root():
    response = await fetch_all_todos()
    return {'Hello': 'World'}

@app.get("/api/todo")
async def get_todo():
    response = await fetch_all_todos()
    return response

@app.get("/api/todo/{title}", response_model=Todo)
async def get_todo_by_id(title):
    response = await fetch_one_todo(title)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no todo item with title {title}')

@app.post("/api/todo", response_model=Todo)
async def post_todo(todo: Todo):
    response = await create_todo(todo.dict())
    if response:
        return response
    else:
        raise HTTPException(400, 'Something went wrong')

@app.put("/api/todo/{title}", response_model=Todo)
async def update_todo_by_id(title: str, description: str):
    response = await update_todo(title, description)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no todo item with title {title}')

@app.delete("/api/todo/{title}")
async def delete_todo_by_id(title):
    response = await remove_todo(title)
    if response:
        return {'message': f'Successfully deleted todo item with title {title}'}
    else:
        raise HTTPException(404, f'There is no todo item with title {title}')

# Generate Personas Based on Client Demand
@app.post("/api/generate_personas", response_model=Persona_Generated_Response) #
async def generate_original_personas(persona_demands: Persona_Demands):
    response = await create_persona_collection(persona_demands.model_dump())
    if response:
        return response
    else:
        raise HTTPException(400, 'Something went wrong')

@app.get("/api/generate_personas/{collection_name}", response_model=Persona_Generated_Response)
async def get_generated_personas_collection(collection_name: str):
    response = await fetch_one_collection_by_name(collection_name)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no collection with name {collection_name}')

@app.get("/api/generate_personas")
async def get_all_generated_personas_collection():
    response = await fetch_all_collections()
    if response:
        return response
    else:
        raise HTTPException(404, 'There is no collection')
    

@app.put("/api/generate_personas/{collection_name}", response_model=Persona_Generated_Response)
async def update_collection_by_collection_name(collection_name: str, new_collection_name: str):
    response = await update_collection_by_name(collection_name, new_collection_name)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no collection with name {collection_name}')

@app.delete("/api/generate_personas/{collection_name}", response_model=Persona_Generated_Response)
async def delete_generated_personas_by_collection_name(collection_name: str):
    response = await remove_collection_by_name(collection_name)
    if response:
        return {'message': f'Successfully deleted collection with name {collection_name}'}
    else:
        raise HTTPException(404, f'There is no collection with name {collection_name}')
    
# Record Interaction
@app.post("/api/interaction_record")
async def create_interaction_record(persona: Persona):
    response = await create_a_interaction_record(persona)
    if response:
        return response
    else:
        raise HTTPException(400, 'Unable to create interaction record')

@app.get("/api/interaction_record/all")
async def get_all_interaction_records():
    response = await fetch_all_interaction_records()
    if response:
        return response
    else:
        raise HTTPException(404, 'There is no interaction record')

@app.get("/api/interaction_record/{id}",response_model=Test_Result)
async def get_interaction_record_by_id(_id: str):
    response = await fetch_one_interaction_record_by_id(_id)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no interaction record with id {_id}')

@app.put("/api/interaction_record/action/{id}", response_model=Test_Result)
async def update_interaction_action(id: str, action: Action):
    response = await update_interaction_action_by_id(id, action)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no interaction record with id {id}')

@app.put("/api/interaction_record/message/{id}", response_model=Test_Result)
async def update_interaction_message(id: str, message: str):
    response = await update_interaction_message_by_id(id, message)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no interaction record with id {id}')

@app.put("/api/interaction_record/achieve_goal/{id}", response_model=Test_Result)
async def update_interaction_goal_achieved(id: str, goal_achieved: bool):
    response = await update_interaction_goal_achieved_by_id(id, goal_achieved)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no interaction record with id {id}')

@app.delete("/api/interaction_record/{id}")
async def delete_interaction_record_by_id(id: str):
    response = await remove_interaction_record_by_id(id)
    if response:
        return {'message': f'Successfully deleted interaction record with id {id}'}
    else:
        raise HTTPException(404, f'There is no interaction record with id {id}')
    
@app.put("/api/interaction_record/step/{id}", response_model=Test_Result)
async def add_interaction_step_length(id: str):
    response = await add_interaction_step_length_by_id(id)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no interaction record with id {id}')
    
@app.get("/api/test_case/{name}", response_model=Test_Case)
async def get_test_case_by_name(name: str):
    response = await get_a_test_case_by_name(name)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no test case with name {name}')
    
@app.post("/api/test_case/create", response_model=Test_Case)
async def create_test_case(test_case: Test_Case):
    response = await create_a_test_case(test_case)
    if response:
        return response
    else:
        raise HTTPException(400, 'test case already exists')

@app.get("/api/test_case/auth/{case_name}", response_model=Test_Case)
async def authorize_existed_test_case(case_name: str, pass_word: str):
    response = await check_authorization_namepass(case_name, pass_word)
    if response:
        return response
    else:
        raise HTTPException(404, 'wrong password, or no such test case')

@app.get("/api/audio/{index}", response_model=Audio_Record)
async def get_audio_record_by_index(index: int):
    response = await fetch_one_audio_record_by_index(index)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no audio record with index {index}')
    
@app.get("/api/audio/id/{_id}", response_model=Audio_Record)
async def get_audio_record_by_id(_id: str):
    response = await fetch_one_audio_record_by_id(_id)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no audio record with id {_id}')
    
@app.get("/api/audio/all")
async def get_all_audio_records():
    response = await fetch_all_audio_records()
    if response:
        return response
    else:
        raise HTTPException(404, 'There is no audio record')
    
@app.post("/api/audio", response_model=Audio_Record)
async def create_audio_record(audio_note: Audio_Record):
    response = await create_a_audio_record(audio_note.index,audio_note.audio_note[0])
    if response:
        return response
    else:
        raise HTTPException(400, 'Unable to create audio record')
    
@app.put("/api/audio/note/{_id}", response_model=Audio_Record)
async def add_audio_note_by_id(_id: str, audio_note: str):
    response = await add_audio_note_by_id(_id, audio_note)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no audio record with id {_id}')
    
@app.put("/api/audio/note/index/{index}", response_model=Audio_Record)
async def add_audio_note_with_index(index: int, audio_note: str):
    response = await add_audio_note_by_index(index, audio_note)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no audio record with index {index}')

@app.delete("/api/audio/{_id}")
async def delete_audio_record_by_id(_id: str):
    response = await remove_audio_record_by_id(_id)
    if response:
        return {'message': f'Successfully deleted audio record with id {_id}'}
    else:
        raise HTTPException(404, f'There is no audio record with id {_id}')
    
@app.delete("/api/audio/index/{index}")
async def delete_audio_record_by_index(index: int):
    response = await remove_audio_record_by_index(index)
    if response:
        return {'message': f'Successfully deleted audio record with index {index}'}
    else:
        raise HTTPException(404, f'There is no audio record with index {index}')
    
@app.get("/api/audio/latest", response_model=Audio_Record)
async def get_most_recent_audio():
    response = await get_most_recent_audio_record()
    if response:
        return response
    else:
        raise HTTPException(404, 'There is no audio record')
    
@app.put("/api/audio/latest", response_model=Audio_Record)
async def update_latest_audio(note: str):
    response = await update_most_recent_audio_record(note)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no audio record with id {note}')
    
@app.put("/api/design_project", response_model=Design_Project)
async def create_design_project(author_name: str, project_name: str, description: str, image_path: list[str]):
    response = await create_a_design_project(author_name, project_name, description, image_path)
    if response:
        return response
    else:
        raise HTTPException(400, 'Unable to create design project')
    
@app.get("/api/design_project/{projectname}", response_model=Design_Project)
async def get_design_project_by_name(projectname: str):
    response = await get_a_design_project_by_name(projectname)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no design project with name {projectname}')
    
@app.get("/api/parseaudio/{parseindex}", response_model= Audience_doc)
async def parse_audio(parseindex: int):
    #get the audio record by index
    print("backend received")
    print(parseindex)
    #todo: the index is not available, check if the audio not is created or not
    audio_note = await fetch_one_audio_record_by_index(parseindex)
    audience_precreated_doc = await parse_audio_to_audience_notes(audio_note["audio_note"])
    doc = await create_Audience_doc(parseindex, audience_precreated_doc["audience_name"], audience_precreated_doc["audio_note"])
    if doc:
        return doc
    else:
        raise HTTPException(400, 'Unable to parse audio to audience notes')
    
@app.get("/api/designproject/all", response_model= list[Design_Project])
async def get_all_design_projects():
    response = await get_all_design_project()
    if response:
        return response
    else:
        raise HTTPException(404, 'There is no design project')
@app.post("/api/audienceprediction", response_model= str)
async def predict_audience_response(audience: Audience_doc):

    all_projects = await get_all_design_project()
    responses_list = "" #list of string
    for project in all_projects:
        response = await predict_audience_response_on_projects(project, audience)
        #TODO: cereate Single_Project_Prediction model instance and store it in the database
        responses_list += project["project_name"]+ ": " + response + "\n"
    processed_response = await all_prediction_and_response(audience, responses_list)
    return processed_response
    # response = await predict_audience_response_on_projects(project, audience)
    # if response:
    #     return response
    # else:
    #     raise HTTPException(400, 'Unable to predict audience response')

@app.get("/api/predictedresponse/audio/all", response_model= list[Predicted_Audience_Response])
async def get_all_predicted_response():
    response = await get_all_predicted_audience_response()
    if response:
        return response
    else:
        return []
    
@app.get("/api/predictedresponse/count", response_model= bool)
async def get_number_of_predicted_response():
    length = await get_predicted_audience_collection_length()
    return length

@app.get("/api/predictioncontent/{audience_name}", response_model= str)
async def get_prediction_content_by_audience(audience_name: str):
    response = await get_predicted_audience_response_by_name(audience_name)
    if response:
        return response["processed_response"]
    else:
        raise HTTPException(404, f'There is no predicted response with name {audience_name}')
    
@app.get("/api/singleprojectprediction/{audiencename}", response_model= list[Single_Project_Prediction])
async def get_single_project_prediction_by_audience_project(audiencename: str):
    print("receive single project prediction request")
    response = await get_single_project_prediction(audiencename)
    if response:
        return response
    else:
        raise HTTPException(404, f'There is no predicted response with name {audiencename} for projects')
    
@app.post("/api/audiencefeedback", response_model= Audience_feedback)
async def create_feedback(audience_feedback: Audience_feedback):
    print("get")
    response = await create_a_feedback_record(audience_feedback.audience_name, audience_feedback.feedback)
    if response:
        return response
    else:
        raise HTTPException(400, 'Unable to create feedback')