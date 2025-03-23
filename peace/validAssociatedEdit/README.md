This project focuses on analyzing function dependencies, and finding associated edit for code snippets.  It includes multiple Python scripts to perform various tasks such as extracting function bodies from repositories, processing patches, and interacting with a GPT-like API to find relevant code edits.

## File Structure

- `process_patches.py`: Processes patch data from a JSON file, extracts relevant edits, and saves the results.
- `calBleu.py`: Computes the BLEU score between a reference and a candidate text.
- `printAvgBleu.py`: Loads JSON data, calculates BLEU scores for all entries, and prints the average BLEU score.
- `agent.py`: Interacts with a GPT-like API to find relevant code edits using tool calls.
- `RAGEditPool.py`: Manages and ranks code edit fragments using dependency analysis.
- `findFuncBody.py`: Extracts function bodies from repositories based on a JSON file containing function search targets.
- `process_edits.py`: Processes a JSON dataset, retrieves code-related edits, and saves the results.
- `FindFunc.py`: Searches for a target function in a repository and extracts its signature and body.

## Configuration

- You can modify the input and output file paths, maximum number of lines per edit fragment, and other parameters in the respective Python scripts.
- Set the `GPT_API_KEY` environment variable to your valid API key for the GPT-like service.

## Usage

### 1. Extract Function Bodies

Run the `findFuncBody.py` script to extract function bodies from repositories based on a JSON file containing function search targets:

bash

```bash
python findFuncBody.py
```

This script reads the input JSON file (`data.json` by default), extracts the function bodies, and saves the results to an output JSON file (`output_results.json` by default).

### 2. Process Patches

Run the `process_patches.py` script to process patch data from a JSON file, extract relevant edits, and save the results:

bash

```bash
python process_patches.py
```

This script reads the input JSON file (`output_results.json` by default), processes the patches, and saves the results to an output JSON file (`processed_results.json` by default).

### 3. Interact with GPT-like API

Run the `agent.py` script to interact with a GPT-like API to find relevant code edits using tool calls:

bash

```bash
python agent.py
```

This script initializes a `RAGEditPool`, adds some edit fragments, and uses the `process_response_loop` function to interact with the GPT-like API to find relevant code edits.