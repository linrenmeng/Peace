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
        function_body (str): The original Python function code.

    Returns:
        str: The optimized function code, or None if the request fails.
    """
    prompt = (
        f"Given the Python function below, improve its performance. "
        f"Please only respond with the function code:\n"
        f"### Code:\n{function_body}\n### Optimized Version:"
    )

    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "n": 1
    }

    try:
        response = requests.post(CHAT_API_URL, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()  # Raise an error if the request fails
        
        optimized_code = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        
        # Clean up any unwanted formatting from API response
        if optimized_code.startswith("```python"):
            optimized_code = optimized_code[9:].strip()
        if optimized_code.startswith("```"):
            optimized_code = optimized_code[3:].strip()
        if optimized_code.endswith("```"):
            optimized_code = optimized_code[:-3].strip()

        return optimized_code if optimized_code else None

    except requests.RequestException as e:
        print(f" API request failed: {e}")
        return None

# ================== Process JSON File with Extracted Functions ==================
def process_extracted_functions(input_json_path, output_json_path):
    """
    Reads JSON containing extracted Python functions, sends them for optimization,
    and saves the optimized functions to a new JSON file.

    Args:
        input_json_path (str): Path to the input JSON file containing original code.
        output_json_path (str): Path to save the optimized code.
    """
    if not os.path.exists(input_json_path):
        print(f"Input file not found: {input_json_path}")
        return

    with open(input_json_path, "r", encoding="utf-8") as file:
        extracted_data = json.load(file)

    optimized_results = {}

    for sha, data in extracted_data.items():
        function_body = data.get("repoinput", {}).get("original_code", "")
        if not function_body:
            print(f"Skipping SHA '{sha}' as function body is empty.")
            continue

        print(f"Sending SHA '{sha}' function to ChatAPI for optimization...")
        optimized_code = send_to_chatapi(function_body)

        if optimized_code:
            optimized_results[sha] = optimized_code
            print(f" SHA '{sha}' optimization completed!")
        else:
            print(f" Optimization failed for SHA '{sha}', skipping.")

    with open(output_json_path, "w", encoding="utf-8") as file:
        json.dump(optimized_results, file, indent=4, ensure_ascii=False)

    print(f"All optimized functions saved to '{output_json_path}'")

# ================== Main Execution ==================
if __name__ == "__main__":
    # Define JSON file paths (use placeholder names to avoid sensitive data exposure)
    input_json = "data/input_data.json"  # Input JSON containing extracted functions
    output_json = "data/optimized_code.json"  # Output JSON with optimized code

    process_extracted_functions(input_json, output_json)