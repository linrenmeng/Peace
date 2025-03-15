import os
import requests
import json
import re
from RAGEditPool import RAGEditPool

# ========== JSON Extraction Functions ==========
def extract_json_from_text(text):
    """
    Extracts JSON-formatted content from a given text.

    Parameters
    ----------
    text : str
        The input text.

    Returns
    -------
    str
        Extracted JSON string or an empty string if no valid JSON is found.
    """
    json_pattern = r'\{.*?\}'
    match = re.search(json_pattern, text, re.DOTALL)

    if match:
        json_str = match.group(0).replace('"""', '').replace("\n", "")
        return json_str
    return ""

def extract_values(text):
    """
    Extracts specific values from a JSON string.

    Parameters
    ----------
    text : str
        The extracted JSON string.

    Returns
    -------
    tuple
        (isfinal_response, usingtool, response) extracted from JSON.
    """
    json_str = extract_json_from_text(text)
    
    if json_str:
        try:
            response_dict = json.loads(json_str)
            return (
                response_dict.get("isfinal_response", "1"),
                response_dict.get("usingtool", ""),
                response_dict.get("response", "")
            )
        except Exception as e:
            return "1", "", ""  # Default values in case of error
    return "1", "", ""

# ========== Tool Execution Functions ==========
def call_tool(rag_pool, initial_code, usingtool_str):
    """
    Calls the appropriate RAGEditPool method based on the tool command.

    Parameters
    ----------
    rag_pool : RAGEditPool
        The instance of RAGEditPool.
    initial_code : str
        The reference code used for dependency analysis.
    usingtool_str : str
        The function tool call string.

    Returns
    -------
    str
        The tool response formatted as a string.
    """
    result = []

    # Match get_top_k_fragments(k)
    pattern_k = r'get_top_k_fragments\((\d+)\)'
    matches_k = re.findall(pattern_k, usingtool_str)

    for match in matches_k:
        k = int(match.strip())
        tool_response = rag_pool.get_top_k_fragments(initial_code, k)
        result.append(f"get_top_k_fragments({k}): {tool_response}")

    # Match get_fragments_in_range(l, r)
    pattern_range = r'get_fragments_in_range\((\d+),\s*(\d+)\)'
    matches_range = re.findall(pattern_range, usingtool_str)

    for match in matches_range:
        l, r = int(match[0].strip()), int(match[1].strip())
        tool_response = rag_pool.get_fragments_in_range(initial_code, l, r)
        result.append(f"get_fragments_in_range({l}, {r}): {tool_response}")

    return '\n'.join(result)

# ========== GPT Interaction Functions ==========
def send_to_gpt(prompt):
    """
    Sends a request to the GPT API.

    Parameters
    ----------
    prompt : str
        The input prompt.

    Returns
    -------
    str
        The GPT response.
    """
    max_length = 8000  # Truncate long prompts
    prompt = prompt[:max_length]

    url = "https://api.example.com/v1/chat/completions"  # Placeholder URL
    api_key = os.environ.get("GPT_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx")  # Secure API Key
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
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException:
        return ""

# ========== Prompt Generation ==========
def get_prompt(init_code):
    """
    Generates a structured prompt for GPT.

    Parameters
    ----------
    init_code : str
        The initial reference code.

    Returns
    -------
    str
        The generated prompt.
    """
    return f"""user:
    You are an expert Python programmer.
    You are given the following code:\n{init_code}
    Your task is to find previous associated edits relevant to this code.
    If no valid associated edits are found, return an empty string.

    Available tool calls:
    - get_top_k_fragments(k): Retrieve the top k edit fragments with the highest dependency score.
    - get_fragments_in_range(l, r): Retrieve edit fragments ranked between l and r by dependency score.

    Please respond in JSON format:
    {{
        "isfinal_response": "",
        "usingtool": "",
        "response": ""
    }}

    - "isfinal_response": "1" if the response is final, "0" if more tool calls are needed.
    - "usingtool": The tool call string (e.g., get_top_k_fragments(2)).
    - "response": The final response containing relevant edit snippets.
    """

# ========== GPT Response Processing Loop ==========
def process_response_loop(rag_pool, initial_code, max_requests=5):
    """
    Processes the GPT response loop.

    Parameters
    ----------
    rag_pool : RAGEditPool
        The RAGEditPool instance.
    initial_code : str
        The reference code.
    max_requests : int, optional
        Maximum number of iterations, default is 5.

    Returns
    -------
    str
        The final response.
    """
    prompt = get_prompt(initial_code)
    num_requests = 0

    while num_requests < max_requests:
        response = send_to_gpt(prompt)

        isfinal_response, usingtool_str, answer = extract_values(response)

        if int(isfinal_response) == 1:
            return answer  # Return final response

        # Call the tool based on the extracted command
        tool_response = call_tool(rag_pool, initial_code, usingtool_str)

        # Update prompt with the tool response
        prompt += f"\nUser:\n{tool_response}\nresponse:\n"
        num_requests += 1

    return "No valid response found."

# ========== Main Execution ==========
if __name__ == '__main__':
    rag_pool = RAGEditPool(max_lines=20)

    # Adding some edit fragments
    edits = [
        ("def add(a, b): return a + b", "def add(a, b, c): return a + b + c"),
        ("def multiply(a, b): return a * b", "def multiply(a, b, c): return a * b * c"),
    ]
    
    for before, after in edits:
        rag_pool.add_edit(before, after)

    # Reference code for testing
    reference_code = "def calculate(x, y): return x + y"

    # Running the process
    final_output = process_response_loop(rag_pool, reference_code)

    print("Final Edit Snippets:\n", final_output)
