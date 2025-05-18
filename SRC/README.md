# KNN_FactChecking - Scripts Documentation

This folder contains scripts and notebooks for fact-checking, claim decomposition, translation, and evaluation. Below is a description of each script and how to run it.

## Setting Up

### Virtual Environment (Recommended)
It's recommended to use a virtual environment to avoid dependency conflicts:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows
.venv\Scripts\activate
# On Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Data Files

### Dataset 1
- **Dataset:** `data/dataset_FCGPT.json` (90+ entries)  
- **Baseline Translated Results:** `data/atomic_claims_FCGPT_claude_translates.json`

### Dataset 2
- **Raw Data:** `data/comments.csv` (60 comments)  
- **Dataset:** `data/dataset_comments.json`  
- **Baseline Translated Results:** `data/atomic_claims_comments_claude_translates.json`  

## Scripts and Notebooks

### 1. `filter.py`
**Description:**  
Processes multiple JSON files containing claims, optionally translating them using the MarianMT translation model. It can filter claims based on "checkworthiness" and saves results to the `./filtered_results` directory.

**Input Data:**
- JSON files containing claim data with the following structure:
  ```json
  [
    {
      "source": "Original text...",
      "claims": [
        {
          "id": 0,
          "claim": "Text of the claim",
          "checkworthy": true,
          "checkworthy_reason": "Yes (Explanation why the claim is checkworthy)",
          "origin_text": "Original text segment",
          "start": 0,
          "end": 42
        },
        ...
      ]
    },
    ...
  ]
  ```

**Output Data:**
- Processed JSON files in the same format, with:
  - Non-checkworthy claims filtered out
  - Claims and explanations translated (if translation is enabled)
  - Files are saved to the `filtered_results` directory with the same base filenames

**Important Parameters:**
- **configurations**: List of [filename, translate] pairs defining which files to process and whether to translate them
- **model_name**: Translation model to use (default is "Helsinki-NLP/opus-mt-en-cs" for English to Czech)
- GPU usage is automatically detected and utilized if available

**How to run:**  
```bash
python filter.py
```
To modify which files are processed or change translation settings, edit the `configurations` list in the script.

### 2. `filter.ipynb`
**Description:**  
Jupyter notebook version of the filtering and translation pipeline. Similar to filter.py but in interactive notebook format.

**Input/Output Data:**
- Same as filter.py

**Important Parameters:**
- **filename**: Path to the input JSON file
- **translate**: Boolean indicating whether to translate the claims

**How to run:**  
```bash
jupyter notebook filter.ipynb
```
Edit the configuration variables at the beginning of the notebook to specify input files and whether to translate.

### 3. `translate.ipynb`
**Description:**  
Dedicated notebook for translating text between languages using the MarianMT model, with a focus on English to Czech translation.

**Input Data:**
- Text data in source language

**Output Data:**
- Translated text in target language

**Important Parameters:**
- **model_name**: Translation model to use

**How to run:**  
```bash
jupyter notebook translate.ipynb
```

### 4. `compare_rouge.ipynb`
**Description:**  
Evaluates the quality of generated claims by comparing them using ROUGE metrics, which measure overlap between texts.

**Input Data:**
- Generated claims to evaluate
- Reference claims to compare against

**Output Data:**
- ROUGE scores (precision, recall, F1) for each comparison

**How to run:**  
```bash
jupyter notebook compare_rouge.ipynb
```

### 5. `compare_edit_distance.ipynb`
**Description:**  
Compares claim decompositions using edit distance (Levenshtein distance) to measure similarity between texts.

**Input Data:**
- Generated claims to evaluate
- Reference claims to compare against

**Output Data:**
- Edit distance scores for each comparison

**How to run:**  
```bash
jupyter notebook compare_edit_distance.ipynb
```

### 6. `dataset_evaluate.ipynb`
**Description:**  
Evaluates the FCGPT dataset for fact-checking or claim decomposition performance.

**Input Data:**
- FCGPT dataset with decomposed claims
- Ground truth or baseline for comparison

**Output Data:**
- Evaluation metrics for claim decomposition quality

**How to run:**  
```bash
jupyter notebook dataset_evaluate.ipynb
```
Specify the evaluation file at the beginning of the notebook.

### 7. `dataset_evaluate_comments.ipynb`
**Description:**  
Similar to dataset_evaluate.ipynb but specifically tailored for the comments dataset.

**Input Data:**
- Comments dataset with decomposed claims
- Ground truth or baseline for comparison

**Output Data:**
- Evaluation metrics for claim decomposition quality

**How to run:**  
```bash
jupyter notebook dataset_evaluate_comments.ipynb
```
Specify the evaluation file at the beginning of the notebook.

## Decompose Tool

### Installation
Navigate to the `decompose` directory and install the requirements:
```bash
cd decompose
pip install -r requirements.txt
```

### Usage
To run the decomposition script:
```bash
python decompose_data.py
```

You can specify the model and prompt by editing the source code in decompose_data.py.

**Input Data:**
- Source text to decompose into atomic claims

**Output Data:**
- Decomposed text with extracted atomic claims and associated metadata

**Important Parameters:**
- **model**: The language model to use for decomposition (e.g., "gpt-4")
- **prompt**: The prompt template to guide the decomposition process

## Other Files

### `KNN_results.ods`
Spreadsheet containing analysis results.

## Hardware Requirements

- For GPU acceleration with AMD GPUs (like Radeon RX 6900 XT):
  - Install PyTorch with ROCm support:
  ```bash
  pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm5.6
  ```

- With NVIDIA GPUs:
  - Install PyTorch with CUDA support:
  ```bash
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
  ```

## Python Version
This project has been tested with Python 3.10 and 3.11. Some dependencies may have issues with Python 3.13.

## Notes
- For best performance, run the translation scripts on a machine with a GPU.
- The filter.py script handles different JSON structures and will automatically detect available GPU support.
- Evaluation notebooks output their results within the notebook for immediate analysis.
- All paths in notebooks should be specified relative to the src folder.