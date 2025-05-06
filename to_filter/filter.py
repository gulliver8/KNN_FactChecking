import requests
import json
import sentencepiece as SentencePiece
from transformers import MarianMTModel, MarianTokenizer
import re
import os

# Define all configurations to process
configurations = [
    # file name                                             translate
    ['results_comments_phi4_14b-fp16_czprompt.json',        False],
    ['results_comments_phi4_14b-fp16.json',                 True],
    ['results_comments_phi4_14b-q8_0_czprompt.json',        False],
    ['results_comments_qwen2.5_32b-instruct-q4_K_M.json',   True],
    ['results_FCGPT_phi4_14b-fp16_czprompt.json',           False],
    ['results_FCGPT_phi4_14b-q8_0_czprompt.json',           False],
    ['results_FCGPT_qwen2.5_32b-instruct-q4_K_M.json',      True],
    ['results_FCGPT_phi4_14b-fp16.json',                    True],
    ['results_comments_phi4:14b-q8_0_czprompt.json',        True],
    ['results_comments_phi4.json',                          True],
    ['results_comments_qwen2.5_32b_inst_q4.json',           True],
    ['results_FCGPT_phi4:14b-q8_0_czprompt.json',           False],
    ['results_FCGPT_phi4.json',                             False]
]

# Load the model and tokenizer for English to Czech - do this only once
print("Loading translation model...")
model_name = "Helsinki-NLP/opus-mt-en-cs"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

def translate_text(input):
    inputs = tokenizer(input, return_tensors="pt", padding=True, truncation=True)
    translated = model.generate(**inputs)
    translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
    return translated_text

# Create filtered directory if it doesn't exist
os.makedirs('./filtered', exist_ok=True)

# Process each configuration
for config_num, configuration in enumerate(configurations, 1):
    filename, translate = configuration
    # Check if file exists before processing
    if not os.path.exists(filename):
        print(f"File {filename} does not exist. Skipping...")
        continue
    print(f"\nProcessing configuration {config_num}/{len(configurations)}: {filename} (translate={translate})")
    
    try:
        data = []
        with open(filename) as f:
            data = json.load(f)
        print(f"Loaded {len(data)} items from {filename}")
        
        for item in data:
            try:
                for claim in item['claims']:
                    # Extract text between first '(' and last ')'
                    if '(' in claim['checkworthy_reason'] and ')' in claim['checkworthy_reason']:
                        start_idx = claim['checkworthy_reason'].find('(') + 1
                        end_idx = claim['checkworthy_reason'].rfind(')')
                        to_translate = claim['checkworthy_reason'][start_idx:end_idx]
                    else:
                        to_translate = claim['checkworthy_reason']
                    claim['checkworthy'] = claim['checkworthy_reason'].startswith('Yes')
                    # do not save if claim['checkworthy'] is False
                    if not claim['checkworthy']:
                        item['claims'] = [c for c in item['claims'] if c['id'] != claim['id']]
                        continue
                    claim['claim'] = translate_text(claim['claim']) if translate else claim['claim']
                    claim['checkworthy_reason'] = translate_text(to_translate) if translate else to_translate
            except:
                # Filter out items that caused errors
                data = [item for item in data if isinstance(item, dict) and 'claims' in item and isinstance(item['claims'], list)]
        
        output_filename = os.path.join('./filtered', filename)
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Saved processed data to {output_filename}")
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")

print("\nAll configurations processed!")