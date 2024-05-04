from openai import OpenAI
import json
from typing import List
from model import Persona
client = OpenAI(api_key='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')



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
                    "content": f"For the product:instagram, Create a persona based on the following requirements: {persona_demands["demands"]}."
                }
            ]
    result = []
    for i in range(persona_demands["number"]):
        response = client.chat.completions.create(
            model = "gpt-3.5-turbo-0613",
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
    
    return

    
async def generate_persona_object(persona):
    return Persona(name=persona["name"], 
                   age=persona["age"], 
                   occupation=persona["occupation"], 
                   location=persona["location"],
                   gender=persona["gender"],
                   characteristic=persona["characteristic"],
                   have_use_the_product=persona["have_use_the_product"],
                   exploration_rate=persona["exploration_rate"])
    

    # # Define the parameters of your expected function call
    # functions = [
    #     {
    #         "name": "createPersonas",
    #         "result": {  # Note the change from "parameters" to "result"
    #         "type": "array",  # Assuming you want an array of personas
    #         "items": {  # Describe the objects within the array
    #             "type": "object",  # Each item is an object
    #             "properties": {
    #                 "name": {"type": "string"},
    #                 "age": {"type": "integer"},
    #                 "occupation": {"type": "string"},
    #                 "location": {"type": "string"},
    #                 "gender": {"type": "string"},
    #                 "characteristic": {"type": "string"},
    #                 "have_use_the_product": {"type": "boolean"},
    #                 "exploration_rate": {"type": "number", "minimum": 0, "maximum": 1}
    #             },
    #             "required": ["name", "age", "occupation", "location", "gender", "characteristic", "have_use_the_product", "exploration_rate"]
    #         }
    #     }
    #     }
    # ]

    # # Prepare the message that prompts the creation of persona objects
    # messages = [
    #     {
    #         "role": "system",
    #         "content": "Your are a very talented persona creator. Please generate a list of personas with detailed description based on the user requirements."
    #     },
    #     {
    #         "role": "user",
    #         "content": f"For the product:{product_info}, Create 1 persona based on the following requirements: {persona_demands["demands"]}. "
    #     }
    # ]
    # # Make the API call
    
    # gptResponse = client.chat.completions.create(
    #     model="gpt-4",
    #     messages = messages,
    #     functions= functions,
    #     function_call= {
    #         "name": "createPersonas"
    #     }
    # )
    # print (gptResponse)

    # # # Extract the function call response
    # # function_call_response = gptResponse.choices[0].message.function_call
    # # print(function_call_response)
    # # personas_arguments = json.loads(function_call_response.arguments)

    # # # Construct a list of Persona objects
    # # personas = [Persona(**persona_arg) for persona_arg in personas_arguments]

    # return 1

async def parse_chatgpt_response(response)-> List[Persona]:
    #parse the response from ChatGPT to a dictionary
    # the reponse should be a string that looks like a JSON object
    # but sometimes it will have some extra characters that need to be removed, 
    # and the given string may not exactly like the given format
    
    # name = ...
    # age = ...
    # occupation = ...
    # location = ...
    # gender: ...
    # characteristic: ...
    # have_use_the_product: ...
    # exploration_rate: ...
    # return Persona(name, age, occupation, gender, characteristic, have_use_the_product, exploration_rate)
    cleaned_response = response.strip('` ')
    try:
    # If the response is not a list, wrap it into a list
        if not response.strip().startswith('['):
            response = '[' + response.strip() + ']'

        # Attempt to parse the response as JSON
        personas_json = json.loads(response)
        # Construct Persona objects from the parsed JSON
        personas = [Persona(**persona_dict) for persona_dict in personas_json]

        return personas
    
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        print(f"Response: {response}")
        # Handle the error as appropriate (e.g., log it, return an empty list, raise an exception, etc.)
        return []

    except TypeError as e:
        print(f"Error while creating Persona objects: {e}")
        # Handle the error as appropriate
        return []
    
    
        # input = f"""
        #     Generate a list of {persona_demands["number"]} made-up personas with differen backgrounds and interests. \
        #     for testing on a the product, the product information is: {product_info}. \
        #     To generate each personas, you should consider the following constraints: \
        #     {persona_demands["demands"]}. \
        #     Also, we are using your generated personas to address the following issues: \
        #     {persona_demands["test_problems"]}. \ so, please make sure the personas are diverse and \
        #     have different interests and backgrounds, traits. And you should consider the traits \
        #     that are relevant to the product or potentially may influence their decision when interact
        #     with the product. When generating the personas traits, you should be as specific and detailed as possible. \
        #     You should also give a rate on "exploration" which indicate how much the personas are \
        #     exploring new things or interaction when given the product interface. A higher exploration \
        #     rate means the personas are more likely to explore new things. Lower exploration rate means \
        #     the personas are more likely to stick with what they know. \
            
        #     For the output, provide them in JSON format, each persona item should have the following keys, beside, do not include other output
        #         name: str
        #         age: int
        #         occupation: str
        #         location: str
        #         gender: str
        #         characteristic: str (around 150 words, describe the persona's personality, interests as detailed as possible)
        #         have_use_the_product: bool (True or False indicate whether the persona has used the test product before)
        #         exploration_rate: float (in range of [0,1], indicate how much the persona is willing to explore new things or new elements in the product)
        #     Attention!!! The output should be in JSON format, 
        #     and each persona should have the same keys as above, 
        #     do not include any other tokens or characters in the output.
        #     """