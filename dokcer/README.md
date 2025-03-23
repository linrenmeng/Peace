This file aims to manage and optimize the development and testing environments for Python repositories. It utilizes virtual environments, automation scripts, and large - language model (LLM) optimization to provide a comprehensive solution for tasks such as dependency installation, test function searching, code replacement, and performance optimization.

## Structure

```
docker/
├── repo_python/          # Each folder contains a GitHub Python repository named reponame. 
│                          # Due to large repo sizes, details can be found at https://mega.nz/folder/bGYHlKRQ#tZIyXJgEnt5o1662miifMQ
├── venv_python/          # Each folder holds a virtual environment for each Python repository, named owner_reponame
├── test/                 # Stores the relevant commands and code scripts for running evaluations. 
│                          # For example, test/testdemo.py uses pytest to run tests on each repository and fetches CPU instructions, space, etc., and stores results in /results
├── results/              # Stores some results
├── data/                 # Stores the entire dataset and Docker - related information
├── opt_venv_python.py    # Installs packages or performs unified operations for all virtual environments
├── find_testfunc.py      # Searches for test functions in the repositories
├── llmchange.py          # Replaces the LLM - optimized code or restores the original extracted code
├── findsave.py, output.py, outputsave.py
│                          # 'find' is for testing, and 'output' is for completion. 
│                          # Extracts the body of the target function and saves it
├── copy_conftest.py      # Copies data/conftest.py to the root of each repository
├── llmpredict_instruction.py # Sends the extracted functions to the ChatAPI for performance optimization
├── chatapi_predict.py    # Processes the extracted Python functions in the JSON file and performs optimization
├── Dockerfile            # Docker configuration file
└── README.md             # Project documentation
```

## Docker Environment Configuration

### Prerequisites

- Docker should be installed on your machine. You can download and install Docker from the official website:

  ```shell
  docker build -t your - image - name .
  ```

  After the image is successfully built, you can run a container based on this image. Use the following command, replacing the placeholder values:

  ```shell
  docker run --privileged -v /your/local/path:/container/path -it --name your_container_name your_image_name:tag
  ```



## Usage

##### Installing Packages in the Virtual Environment

```
python opt_venv_python.py
```

This command reads the `data/repoexec_test_python.json` file and installs the `cirron` and `psutil` packages for each virtual environment. Then searching for Test Functions

```
python find_testfunc.py
```

This command searches for test functions related to the `get_relative_url` function in the specified repository. You can modify the `repo_path` and `function_name` variables in the script to specify different repositories and function names.

##### Replacing or Restoring Code

```
# Replace with LLM - optimized code
python llmchange.py --mode replace

# Restore to the original extracted code
python llmchange.py --mode restore
```

This command reads the `data/repoexec_python.json` file and replaces or restores the co

de of the specified function in the repository according to the specified mode (`replace` or `restore`).

##### Copying the Configuration File

```
python copy_conftest.py
```

This command copies the `data/conftest.py` file to the root directory of each repository in the `repo_python` directory.

##### Optimizing the Extracted Functions

```
python llmpredict_instruction.py
```

This command sends the functions extracted from the `data/extract_func` directory to the ChatAPI for performance optimization and saves the optimized functions in the `data/LLM_predict` directory.



#### repo_python and venv_python

Each folder contains a github python repository named reponame and a virtual environment for each python repository.

```
since too much large repo and venv, detail can be find in https://mega.nz/folder/bGYHlKRQ#tZIyXJgEnt5o1662miifMQ
```









