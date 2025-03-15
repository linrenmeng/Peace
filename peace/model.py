import json
import logging
from process_function_modifications import pipeline_function_modifications as process_pipeline

# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def load_json(file_path):
    """
    Loads a JSON file.

    Parameters
    ----------
    file_path : str
        Path to the input JSON file.

    Returns
    -------
    dict or None
        Parsed JSON data or None if an error occurs.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logging.info(f"Successfully loaded JSON file: {file_path}")
        return data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.error(f"Failed to read JSON file {file_path}: {e}")
        return None

def save_json(data, file_path):
    """
    Saves data to a JSON file.

    Parameters
    ----------
    data : dict
        Data to save.
    file_path : str
        Path to the output JSON file.

    Returns
    -------
    None
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"Results successfully saved to {file_path}")
    except Exception as e:
        logging.error(f"Failed to save JSON file {file_path}: {e}")

def process_repositories(data):
    """
    Processes repositories by applying function modifications.

    Parameters
    ----------
    data : dict
        Dictionary containing repository data.

    Returns
    -------
    dict
        Processed results.
    """
    output_data = {}

    for repo_name, items in data.items():
        repo_results = {}

        for item in items:
            try:
                repo_path = item.get("reponame", "")
                function_name = item.get("target_func", "")
                class_name = item.get("target_class", "")
                message = item.get("prompt", "")

                if not repo_path or not function_name:
                    logging.warning(f"Skipping entry due to missing repo_path or function_name: {item}")
                    continue

                # Construct input data for pipeline
                data_for_pipeline = {
                    "repo_path": f"/path/to/repos/{repo_path}",  # Modify path accordingly
                    "function_name": function_name,
                    "class_name": class_name if class_name else None,
                    "message": message
                }

                # Process modifications
                results = process_pipeline(data_for_pipeline)
                repo_results[item.get("sha", "unknown_sha")] = results

            except Exception as e:
                logging.error(f"Error processing {item.get('sha', 'unknown_sha')}: {e}")

        output_data[repo_name] = repo_results

    return output_data

# ========== Main Execution ==========
if __name__ == "__main__":
    INPUT_FILE = "/path/to/input/repoexec_python.json"  # Modify path accordingly
    OUTPUT_FILE = "model_results.json"

    data = load_json(INPUT_FILE)
    if data:
        results = process_repositories(data)
        save_json(results, OUTPUT_FILE)
