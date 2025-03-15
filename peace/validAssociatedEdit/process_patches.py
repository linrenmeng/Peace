import json
import logging
from RAGEditPool import RAGEditPool
from agent import process_response_loop

# ========== Configuration Constants ==========
INPUT_FILE = "output_results.json"   # 输入 JSON 文件
OUTPUT_FILE = "processed_results.json"  # 输出 JSON 文件
MAX_LINES = 10   # 每个编辑片段的最大行数
TOP_K = 2  # 选取的前 K 个最相关编辑片段

# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ========== Utility Functions ==========
def load_json(file_path):
    """
    Load JSON data from a file.

    Parameters
    ----------
    file_path : str
        Path to the input JSON file.

    Returns
    -------
    list
        Parsed JSON data as a list of dictionaries.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logging.info(f"Successfully loaded data from {file_path}")
        return data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.error(f"Failed to load JSON file {file_path}: {e}")
        return []

def save_json(data, file_path):
    """
    Save JSON data to a file.

    Parameters
    ----------
    data : list
        The JSON data to save.
    file_path : str
        Path to the output JSON file.

    Returns
    -------
    None
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logging.info(f"Results successfully saved to {file_path}")
    except Exception as e:
        logging.error(f"Failed to save JSON file {file_path}: {e}")

def process_single_item(item, max_lines, top_k):
    """
    Process a single JSON record by extracting patches and finding relevant edits.

    Parameters
    ----------
    item : dict
        A single JSON data item containing patchList and funcBody.
    max_lines : int
        Maximum number of lines per edit fragment.
    top_k : int
        Number of top-ranked edit fragments to retrieve.

    Returns
    -------
    str
        The extracted edit snippets.
    """
    rag_pool = RAGEditPool(max_lines=max_lines)

    # Extract patches and add to RAGEditPool
    patch_list = item.get("patchList", [])
    if not patch_list:
        logging.warning("No patchList found for an item.")
    
    for patch in patch_list:
        rag_pool.add_edit_from_patch(patch)

    # Extract function body
    func_body = item.get("funcBody", "")
    if not func_body:
        logging.warning("No funcBody found for an item.")

    # Retrieve relevant edit fragments
    final_output = rag_pool.get_top_k_fragments(func_body, top_k)
    
    # Format output
    final_output_str = "\n".join([fragment for fragment, _ in final_output])
    return final_output_str

def process_patch_data(input_file, output_file, max_lines=10, top_k=2):
    """
    Processes the patch data from a JSON file, retrieves relevant edits, and saves the results.

    Parameters
    ----------
    input_file : str
        Path to the input JSON file.
    output_file : str
        Path to save the processed JSON file.
    max_lines : int, optional
        Maximum number of lines per edit fragment (default is 10).
    top_k : int, optional
        Number of top-ranked edit fragments to retrieve (default is 2).

    Returns
    -------
    None
    """
    data = load_json(input_file)
    
    if not data:
        logging.error("No data to process. Exiting...")
        return

    # Process each item in the dataset
    processed_count = 0
    for item in data:
        item["results"] = process_single_item(item, max_lines, top_k)
        processed_count += 1

    # Save results
    save_json(data, output_file)
    logging.info(f"Processing complete. {processed_count} items processed.")

# ========== Main Execution ==========
if __name__ == "__main__":
    process_patch_data(INPUT_FILE, OUTPUT_FILE, MAX_LINES, TOP_K)
