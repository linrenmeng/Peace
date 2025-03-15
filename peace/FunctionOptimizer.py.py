import os
import requests
import logging
from agent import process_code_edit
from RAGEditPool import RAGEditPool
from FindFunc import FindFunc
from FindApi import FindApi

# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def add_data(data, rag_pool):
    """
    Constructs a single data entry by retrieving function details and relevant edits.

    Parameters
    ----------
    data : dict
        Data containing repository path, function name, class name, and message.
    rag_pool : RAGEditPool
        Instance of RAGEditPool for tracking function changes.

    Returns
    -------
    dict
        Updated data with function details, associated edits, and API info.
    """
    repo_path = data.get("repo_path")
    object_function = data.get("function_name")
    class_name = data.get("class_name")
    message = data.get("message", "")

    if not repo_path or not object_function:
        logging.error("Repository path and function name must be provided.")
        return data

    # Retrieve function signature and body
    try:
        signature, body = FindFunc(repo_path, object_function, class_name).find()
        data["function_body"] = f"{signature}\n{body}" if signature and body else ""
    except Exception as e:
        logging.warning(f"Failed to retrieve function details: {e}")
        data["function_body"] = ""

    # Get associated edits
    try:
        data["associated_edit"] = process_code_edit(rag_pool, data["function_body"])
    except Exception as e:
        logging.warning(f"Failed to process function edits: {e}")
        data["associated_edit"] = ""

    data["message"] = message
    data["api"] = ""

    return data

def get_prompt(data):
    """
    Constructs an optimization prompt for the LLM.

    Parameters
    ----------
    data : dict
        Dictionary containing function details, edits, and optimization message.

    Returns
    -------
    str
        Prompt to be sent to the LLM.
    """
    function_body = data.get("function_body", "")
    message = data.get("message", "")
    associated_edit = data.get("associated_edit", "")
    
    prompt = f"""Given the Python function below, improve its performance. Please only respond with the function code.

    Function to optimize:
    ```python
    {function_body}
    ```

    Associated edits (previous changes related to this function):
    ```python
    {associated_edit}
    ```

    If the message contains any information regarding the optimization goal, consider that as well. Otherwise, focus solely on improving execution speed, memory usage, and efficiency while keeping the functionality intact.

    Message (may or may not be relevant to optimization goal):
    ```text
    {message}
    ```

    Optimized Version:
    """
    return prompt[:8000]  # Ensure prompt length doesn't exceed GPT limits

def send_to_gpt(prompt):
    """
    Sends a request to the GPT API for function optimization.

    Parameters
    ----------
    prompt : str
        The prompt to be sent.

    Returns
    -------
    str
        The optimized function response.
    """
    url = "https://api.example.com/v1/chat/completions"  # Placeholder URL
    api_key = os.environ.get("GPT_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx")  # Use environment variable for security
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "n": 1
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in GPT API request: {e}")
        return ""

# ========== Example Usage ==========
if __name__ == "__main__":
    DATA = {
        "repo_path": "/path/to/repository",
        "function_name": "target_function",
        "class_name": None,
        "message": "Optimize this function for performance."
    }

    rag_pool = RAGEditPool(max_lines=10)
    updated_data = add_data(DATA, rag_pool)
    prompt = get_prompt(updated_data)
    optimized_code = send_to_gpt(prompt)

    logging.info("Optimized Function:")
    print(optimized_code)
