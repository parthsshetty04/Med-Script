from time import sleep
import openai
import pandas as pd
import os
from tqdm import tqdm
import json
from datetime import datetime

# Verify environment variables
openai_organization = os.getenv('OPENAI_ORGANIZATION')
openai_api_key = os.getenv('OPENAI_API_KEY')

if not openai_organization:
    raise Exception("Missing value for OPENAI_ORGANIZATION environment variable.")

if not openai_api_key:
    raise Exception("Missing value for OPENAI_API_KEY environment variable.")

# Set OpenAI credentials
openai.organization = openai_organization
openai.api_key = openai_api_key

class CFG:
    ingredients_file = './ingredient_list.csv'
    input_file = './synthetic_rx.txt'
    prompt_columns = ['prompts']
    retries = 10
    min_sleep = 40  # minimum sleep time in seconds
    max_sleep = 60  # maximum sleep time in seconds
    model_name = 'gpt-3.5-turbo'
    function_test = True
    temperature = 0
    timeout = 20
    output_file = './outputs/dose_predictions.xlsx'

rx_ingredients = pd.read_csv(CFG.ingredients_file)['Ingredient'].unique().tolist()

CFG.functions = [
    {
        "name": "dosing_information",
        "description": "information about dosing in the prescription label",
        "parameters": {
            "type": "object",
            "properties": {
                "medication_unit_size": {
                    "type": "number",
                    "description": "Unit size of medication in mg"
                },
                "dose_unit_size": {
                    "type": "number",
                    "description": "Units of medication given per dose"
                },
                "patient_weight": {
                    "type": "number",
                    "description": "Weight of patient in kg"
                },
                "dosing_freq": {
                    "type": "number",
                    "description" : "number of times per day the medication is given"
                },
                "units_dispensed": {
                    "type" : "number",
                    "description" : "number of medication units dispensed"
                },
                "ingredient": {
                    "type": "string", 
                    "enum": rx_ingredients,
                    "description": "Referencing the trade name, identify each active ingredient that forms the medication. For combination drugs, ensure to list all components."
                },
            },
            "required": ["medication_unit_size", "dose_unit_size", "patient_weight", "dosing_freq", "units_dispensed", "ingredient"]
        }
    }
]

def create_chat_completion(prompt):
    retries = CFG.retries
    sleep_duration = CFG.min_sleep  # initial sleep duration

    for attempt in range(retries):
        try:
            chat_completion_resp = openai.ChatCompletion.create(
                model=CFG.model_name, 
                messages=[{"role": "user", "content": prompt}],
                timeout=CFG.timeout,
                temperature=CFG.temperature
            )
            response = chat_completion_resp['choices'][0]['message']['content']
            
            if response:
                return response
            else:
                print(f"Empty response on attempt {attempt + 1}. Retrying.")

        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {str(e)}")
            if attempt < retries - 1:  # if not on final attempt
                sleep_duration = min(2 * sleep_duration, CFG.max_sleep)  # exponential backoff
                print(f"Sleeping for {sleep_duration} seconds before next attempt.")
                sleep(sleep_duration)
            else:
                return None  # return None after too many failed attempts

def get_dose(medication_unit_size, dose_unit_size, patient_weight, dosing_freq, units_dispensed, ingredient):
    """Get the dose and length of administration of the medication given"""
    dose_info = {
        "dose": (medication_unit_size * dose_unit_size) / patient_weight,
        "length_admin": units_dispensed / (dose_unit_size * dosing_freq),
        "dose_freq": dosing_freq,
        "units_dispensed": units_dispensed,
        "medication_unit_size": medication_unit_size,
        "dose_unit_size": dose_unit_size,
        "patient_weight": patient_weight,
        "ingredient": ingredient
    }
    return json.dumps(dose_info)

def create_fun_chat_completion(prompt, functions=CFG.functions):
    retries = CFG.retries
    sleep_duration = CFG.min_sleep  # initial sleep duration
    PREFIX = 'What is the dosing information for the medication given **\\ Instance to Label: '

    for attempt in range(retries):
        try:
            print(f'Prompt: {PREFIX + prompt}')
            response = openai.ChatCompletion.create(
                model=CFG.model_name, 
                messages=[{"role": "user", "content": PREFIX + prompt}],
                functions=functions,
                function_call="auto",
                timeout=CFG.timeout
            )

            if response:
                response_message = response["choices"][0]["message"]
                if response_message.get("function_call"):
                    available_functions = {
                        "dosing_information": get_dose,
                    }

                    function_name = response_message["function_call"]["name"]
                    function_to_call = available_functions[function_name]
                    
                    function_args = json.loads(response_message["function_call"]["arguments"])
                    function_response = function_to_call(
                        medication_unit_size=function_args.get("medication_unit_size"),
                        dose_unit_size=function_args.get("dose_unit_size"),
                        patient_weight=function_args.get("patient_weight"),
                        dosing_freq=function_args.get("dosing_freq"),
                        units_dispensed=function_args.get("units_dispensed"),
                        ingredient=function_args.get("ingredient"),
                    )
                return function_response
            else:
                print(f"Empty response on attempt {attempt + 1}. Retrying.")

        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {str(e)}")
            if attempt < retries - 1:  # if not on final attempt
                sleep_duration = min(2 * sleep_duration, CFG.max_sleep)  # exponential backoff
                print(f"Sleeping for {sleep_duration} seconds before next attempt.")
                sleep(sleep_duration)
            else:
                return None

def process_prompts(df):
    responses = {}
    for j, col in enumerate(CFG.prompt_columns, start=1):
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Processing column {j}/{len(CFG.prompt_columns)}: {col}")

        progress_bar = tqdm(total=len(df), ncols=70)  # setting up progress bar
        col_responses = []
        
        for i in range(len(df)):
            prompt = df.iloc[i][col]
            if CFG.function_test:
                response = create_fun_chat_completion(prompt)
            else:
                response = create_chat_completion(prompt)
            
            if isinstance(response, Exception):
                print(f"Task failed due to {str(response)}")
                col_responses.append(None)
            else:
                col_responses.append(response)

            progress_bar.update(1)

        progress_bar.close()
        responses[col] = col_responses

    return responses

try:
    # Load DataFrame
    lines_list = []
    with open(CFG.input_file, "r") as file:
        for line in file:
            lines_list.append(line.strip())
    df = pd.DataFrame(lines_list, columns=CFG.prompt_columns)

    print(df.columns)
    print(df.head())

    # Run process_prompts
    print(f"loading files - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    responses = process_prompts(df)
    
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Completed run")
    
    # Add responses to DataFrame
    for col, resp in responses.items():
        df[f"{col}_response"] = resp

    # Save the final DataFrame
    df.to_excel(CFG.output_file, index=False)  # Save without index

except Exception as e:
    print(f"An error occurred during processing: {str(e)}")

print("Done!")
