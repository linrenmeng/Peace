import os
import json
import requests

# ================== ChatAPI Configuration ==================
CHAT_API_URL = "your-api-web"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-XXXXXXXXXXXXXXXXXXXXXXXXXX"  # Replace with your API Key
}

# ================== Send Request to ChatAPI ==================
def send_to_chatapi(function_body):
    """
    Sends a Python function to ChatAPI for performance optimization.

    Args:
        function_body (str): The original Python function body.

    Returns:
        str: The optimized function body, or None if the request fails.
    """
    prompt = (
        f"Given the Python function body below, improve its performance. "
        f"Please only respond with the function body:\n"
        f"### Code:\n{function_body}\n### Optimized Version:"
    )

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "n": 1
    }

    try:
        response = requests.post(CHAT_API_URL, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()  # Raise an error if the request fails

        optimized_code = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        # Clean up API response formatting
        if optimized_code.startswith("```python"):
            optimized_code = optimized_code[9:].strip()
        if optimized_code.startswith("```"):
            optimized_code = optimized_code[3:].strip()
        if optimized_code.endswith("```"):
            optimized_code = optimized_code[:-3].strip()

        return optimized_code if optimized_code else None

    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return None

# ================== Save Optimized Function ==================
def save_optimized_function(optimized_body, repo_name, function_name):
    """
    Saves the optimized function body to a structured directory.

    Args:
        optimized_body (str): The optimized function content.
        repo_name (str): The repository name.
        function_name (str): The function name.
    """
    # Define the save path
    save_dir = os.path.join("data", "LLM_predict", repo_name)
    os.makedirs(save_dir, exist_ok=True)

    # Save the optimized function
    file_path = os.path.join(save_dir, f"{function_name}.py")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(optimized_body)

    print(f"Optimized function '{function_name}' from '{repo_name}' saved to '{file_path}'.")

# ================== Process Extracted Functions ==================
def process_extracted_functions(extract_dir):
    """
    Processes extracted functions, sends them for optimization, and saves the results.

    Args:
        extract_dir (str): The directory containing extracted function files.
    """
    if not os.path.exists(extract_dir):
        print(f"Extracted function directory not found: {extract_dir}")
        return

    for repo_name in os.listdir(extract_dir):
        repo_path = os.path.join(extract_dir, repo_name)

        if os.path.isdir(repo_path):
            for function_file in os.listdir(repo_path):
                function_name, ext = os.path.splitext(function_file)
                if ext == ".py":
                    file_path = os.path.join(repo_path, function_file)
                    with open(file_path, "r", encoding="utf-8") as file:
                        function_body = file.read()

                    print(f"Sending function '{function_name}' from '{repo_name}' to ChatAPI for optimization...")
                    optimized_code = send_to_chatapi(function_body)

                    if optimized_code:
                        save_optimized_function(optimized_code, repo_name, function_name)
                    else:
                        print(f"Optimization failed for '{function_name}' in '{repo_name}', skipping.")

    print("Optimization process completed.")

# ================== Main Execution ==================
if __name__ == "__main__":
    extract_dir = "data/extract_func"  # Directory containing extracted functions
    process_extracted_functions(extract_dir)
