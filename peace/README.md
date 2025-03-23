This framework focuses on the analysis and optimization of code functions, encompassing a comprehensive process from function dependency analysis, search for associated code edits, to leveraging Large Language Models (LLMs) for predictions and enhancing the results with small fine - tuned models. Through the collaborative work of multiple modules, the aim is to improve code quality and performance.

## Project Structure

1. **`validAssociatedEdit` Folder**: It contains files related to processing code edits. For example, `agent.py` is used to interact with GPT - like models to find relevant code edits, and `RAGEditPool.py` manages and analyzes code edit fragments.
2. **`performanceOptimizer` Folder**: Stores data and models for LoRA fine - tuning of small models, which are used to enhance the prediction results of LLMs.
3. **Main Folder**: Houses core analysis and processing scripts. For instance, `FunctionDependencyAnalyzer.py` analyzes function dependencies, and `FunctionOptimizer.py` optimizes function performance.

## Configuration

**Environmental Dependencies**: Convenience, we set for our warehouse are configured with the corresponding operation and test environment, detail can see at https://mega.nz/folder/bGYHlKRQ#tZIyXJgEnt5o1662miifMQ. The project is developed based on Python. The required libraries can be installed through the `requirements.txt` file. Use the following commands to create a virtual environment and install dependencies:

bash

```bash
python -m venv myenv
source myenv/bin/activate  # On Windows, use myenv\Scripts\activate
pip install -r requirements.txt
```

**API Key Configuration**: In `agent.py` and `FunctionOptimizer.py`, the `GPT_API_KEY` environment variable needs to be set. On Linux/macOS:

bash

```bash
export GPT_API_KEY='your_api_key'
```

On Windows:

bash

```bash
set GPT_API_KEY=your_api_key
```

**Path Configuration**: In each script, modify configuration parameters such as repository paths and file paths according to the actual situation. For example, set `repo_dir` in `FunctionDependencyAnalyzer.py`, and set `INPUT_FILE` and `OUTPUT_FILE` in `model.py`.

## Usage

**Function Dependency Analysis and Modification Determination**: Run the `FunctionDependencyAnalyzer.py` or `get_modifications.py` script, specifying the repository path, target function, and class name (if applicable) to analyze function dependencies and determine the functions that need to be modified.

bash

```bash
python FunctionDependencyAnalyzer.py --repo_dir /path/to/repository --target_function magphase
```

**Function Optimization and Edit Search**: Run the `FunctionOptimizer.py` script to construct data, generate prompts, and obtain the optimized functions predicted by the LLM.

bash

```bash
python FunctionOptimizer.py --repo_path /path/to/repository --function_name target_function
```

**Full - process Execution**: In `model.py` and `process_function_modifications.py`, a complete processing flow is defined. You can run `model.py` to load the input JSON data, process the function modifications in the repositories, and save the results.

bash

```bash
python model.py
```

**Small Model Enhancement**: Input the LLM prediction results into the small models in the `performanceOptimizer` folder for enhancement. The specific operations are based on the usage instructions of the small models.