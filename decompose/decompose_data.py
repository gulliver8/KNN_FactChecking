# Author: Lucia Makaiova phi4:14b-fp16
# Date: 13-03-2025
# Description: This script is used to run the fact-checking pipeline on the translated data using the FactCheck API.
# used models "qwen2.5:32b-instruct-q4_K_M" "phi4:14b-fp16" "phi4:14b-q8_0"
import json
from factcheck import FactCheck
from time import sleep

fc_model = "phi4:14b-q8_0"
fcgpt_path = "results_FCGPT_" + fc_model + "_czprompt_CoT.json"
comments_path = "results_comments_" + fc_model + "_czprompt_CoT.json"
fc_prompt = "cz_prompt_CoT.yaml"

api_cfg = {
    'LOCAL_API_URL': 'http://localhost:11434',
}

factcheck_instance = FactCheck(api_config=api_cfg, default_model=fc_model,prompt=fc_prompt)

#load translated data
with open('../data/translated_factual.json', 'r') as file:
    translated_data = json.load(file)
    #print(len(translated_data))
file.close()

data = translated_data
#run the fact-check pipeline for all data
results = []
with open(fcgpt_path, 'a') as file:
    for d in data:
        res = factcheck_instance.check_text(d['response'])
        print(res)
        new = {
            'source': d["response"],
            'claims': res
        }
     
        file.write(",")
        json.dump(new, file, indent=4)
        #api limit of 5 responses/minute
        #sleep(30)
file.close()

#load translated data
with open('../data/comments_grouped.json', 'r') as file:
    translated_data = json.load(file)
    #print(len(translated_data))
file.close()

data = translated_data
#run the fact-check pipeline for all data
results = []
with open(comments_path, 'a') as file:
    for d in data:
        res = factcheck_instance.check_text(d['comment'])
        print(res)
        new = {
            'source': d["comment"],
            'claims': res
        }

        file.write(",")
        json.dump(new, file, indent=4)
        #api limit of 5 responses/minute
        #sleep(30)
file.close()

