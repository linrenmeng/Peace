import json
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from FindFunc import FindFunc

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Paths (Modify as needed)
JSON_FILE_PATH = "data.json"  # Input JSON file containing function search targets
OUTPUT_FILE_PATH = "output_results.json"  # Output JSON file with function bodies
REPO_BASE_PATH = "/path/to/repositories/"  # Modify this to the actual repository directory

def process_entry(entry):
    """
    Process a single entry from the dataset.
    Extract function details from the corresponding repository.
    """
    repo_path = os.path.join(REPO_BASE_PATH, entry["repo_name"])  # Construct full repository path
    target_function = entry["objectFunc"]  # Function name to search for
    target_class = None  # Default to no class-based filtering

    if not os.path.exists(repo_path):
        logging.warning(f"Repository not found: {repo_path}")
        entry["funcBody"] = "Repository not found"
        return entry

    # Use FindFunc to locate function definition
    signature, body = FindFunc(repo_path, target_function, target_class).find()

    if signature and body:
        func_body = f"{signature}\n{body}"
        logging.info(f"Function found: {target_function} in {repo_path}")
    else:
        func_body = "Function not found"
        logging.warning(f"Function {target_function} not found in {repo_path}")

    entry["funcBody"] = func_body
    return entry

def main():
    """Main execution function."""
    # Load JSON file
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading JSON file: {e}")
        return

    # Use multi-threading to speed up function extraction
    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:  # Adjust thread count as needed
        future_to_entry = {executor.submit(process_entry, entry): entry for entry in data}
        
        for future in as_completed(future_to_entry):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logging.error(f"Error processing entry: {e}")

    # Save results to JSON file
    try:
        with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as out_f:
            json.dump(results, out_f, indent=4, ensure_ascii=False)
        logging.info(f"Results saved to {OUTPUT_FILE_PATH}")
    except Exception as e:
        logging.error(f"Error saving results: {e}")

if __name__ == '__main__':
    main()
