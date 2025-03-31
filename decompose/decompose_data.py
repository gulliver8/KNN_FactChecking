import json
from factcheck import FactCheck
from time import sleep

api_cfg = {
    'ANTHROPIC_API_KEY': 'null'
}


factcheck_instance = FactCheck(api_config=api_cfg, default_model="claude-3-7-sonnet-latest")

#load translated data
with open('../translate/translated.json', 'r') as file:
    translated_data = json.load(file)
    #print(len(translated_data))
file.close()

data = translated_data
#run the fact-check pipeline for all data
results = []
with open('atomic_claims_FCGPT.json', 'a') as file:
    for d in data:
        res = factcheck_instance.check_text(d['response'])
        new = {
            'source': d["response"],
            'claims': res
        }
        file.write(",")
        json.dump(new, file, indent=4)
        #api limit of 5 responses/minute
        sleep(30)
file.close()


