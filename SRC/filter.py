import requests
import json
import sentencepiece as SentencePiece
from transformers import MarianMTModel, MarianTokenizer
import re
import os
import torch

# Check for GPU availability
print("Checking for GPU support...")
if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"Using CUDA/ROCm device: {torch.cuda.get_device_name(0)}")
    # Move model to GPU
    model_on_gpu = True
else:
    device = torch.device("cpu")
    print("No GPU detected, using CPU instead")
    model_on_gpu = False

# Define all configurations to process
configurations = [
    # file name                                                          translate
    ['data/atomic_claims_comments_claude.json',                          True],
    ['data/atomic_claims_FCGPT_claude.json',                             True],
    ['data/atomic_claims_comments_claude_translated.json',               False],
    ['data/atomic_claims_FCGPT_claude_translated.json',                  False]
]

# Load the model and tokenizer for English to Czech - do this only once
print("Loading translation model...")
model_name = "Helsinki-NLP/opus-mt-en-cs"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

# Move model to GPU if available
if model_on_gpu:
    model = model.to(device)

def translate_text(input):
    inputs = tokenizer(input, return_tensors="pt", padding=True, truncation=True)
    # Move inputs to GPU if available
    if model_on_gpu:
        inputs = {k: v.to(device) for k, v in inputs.items()}
    translated = model.generate(**inputs)
    translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
    return translated_text

# Create filtered_results directory if it doesn't exist
os.makedirs('./filtered_results', exist_ok=True)

# Process each configuration
for config_num, configuration in enumerate(configurations, 1):
    error = 0
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
            except Exception as e:
                # keep the items that caused errors with empty claim list
                item['claims'] = []
                error += 1
        
        # Create output filename - preserve the base filename but change the directory
        base_filename = os.path.basename(filename)
        output_filename = os.path.join('./filtered_results', base_filename)
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
        print(f"Saved processed data to {output_filename}")
        print(f"Number of errors: {error}")
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")

print("\nAll configurations processed!")