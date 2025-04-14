# Author: Lucia Makaiova
# Date: 13-03-2025
# Description: This script is 
import json
from factcheck import FactCheck
from time import sleep

api_cfg = {
    'LOCAL_API_URL': 'http://localhost:11434',
}

factcheck_instance = FactCheck(api_config=api_cfg, default_model="phi3")

#load translated data
with open('../translate/translated.json', 'r') as file:
    translated_data = json.load(file)
    #print(len(translated_data))
file.close()

data = translated_data[0:10]
#run the fact-check pipeline for all data
results = []
with open('atomic_claims_FCGPT.json', 'a') as file:
    for d in data:
        res = factcheck_instance.check_text(d['response'])
        new = {
            'source': d["response"],
            'claims': res
        }
        print(new)
        file.write(",")
        json.dump(new, file, indent=4)
        #api limit of 5 responses/minute
        #sleep(30)
file.close()


