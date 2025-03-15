import json
import logging
from RAGEditPool import RAGEditPool
from agent import process_response_loop  # Ensure the correct function is imported

# ========== Configuration ==========
INPUT_FILE = "output_results.json"
OUTPUT_FILE = "processed_results.json"
MAX_LINES = 10  # Maximum number of lines per edit fragment

# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ========== Utility Functions ==========
def load_json(file_path):
    """
    Loads JSON data from a file.

    Parameters
    ----------
    file_path : str
        The path to the JSON file.

    Returns
    -------
    list
        Parsed JSON data. Returns an empty list if loading fails.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logging.info(f"Successfully loaded JSON file: {file_path}")
        return data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.error(f"Failed to read JSON file: {e}")
        return []

def save_json(data, file_path):
    """
    Saves data to a JSON file.

    Parameters
    ----------
    data : list
        The JSON data to save.
    file_path : str
        The output file path.

    Returns
    -------
    None
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logging.info(f"Results successfully saved to {file_path}")
    except Exception as e:
        logging.error(f"Failed to save JSON file: {e}")

# ========== Core Processing Functions ==========
def process_single_item(item, max_lines):
    """
    Processes a single JSON record by extracting patches and finding relevant edits.

    Parameters
    ----------
    item : dict
        JSON data item containing `patchList` and `funcBody`.
    max_lines : int
        Maximum number of lines per edit fragment.

    Returns
    -------
    str
        Extracted edit snippets, or an empty string if no relevant edits are found.
    """
    rag_pool = RAGEditPool(max_lines=max_lines)

    # Extract patches and add them to RAGEditPool
    patch_list = item.get("patchList", [])
    if not patch_list:
        logging.warning("patchList is empty, skipping this entry.")

    for patch in patch_list:
        rag_pool.add_edit_from_patch(patch)

    # Extract function body
    func_body = item.get("funcBody", "")
    if not func_body:
        logging.warning("funcBody is missing, may affect edit retrieval.")

    # Retrieve relevant edit fragments
    final_output = process_response_loop(rag_pool, func_body)

    return final_output

def process_edits(input_file, output_file, max_lines=10):
    """
    Processes a JSON dataset, retrieves code-related edits, and saves results.

    Parameters
    ----------
    input_file : str
        Path to the input JSON file.
    output_file : str
        Path to save the processed JSON file.
    max_lines : int, optional
        Maximum number of lines per edit fragment (default is 10).

    Returns
    -------
    None
    """
    data = load_json(input_file)

    if not data:
        logging.error("No data available for processing. Exiting.")
        return

    processed_count = 0

    for item in data:
        item["results"] = process_single_item(item, max_lines)
        processed_count += 1

    # Save results
    save_json(data, output_file)
    logging.info(f"Processing complete. {processed_count} items processed.")

# ========== Entry Point ==========
if __name__ == "__main__":
    process_edits(INPUT_FILE, OUTPUT_FILE, MAX_LINES)