import json
import os
import logging
from calbleu import compute_bleu  # 确保 calbleu.py 中有 compute_bleu 函数

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_json(json_file_path):
    """
    Load JSON data from the given file path.
    
    Args:
        json_file_path (str): Path to the JSON file.
    
    Returns:
        list: Loaded JSON data (expected as a list of entries).
    """
    if not os.path.exists(json_file_path):
        logging.error(f"File not found: {json_file_path}")
        return []

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("Invalid JSON format: expected a list of entries.")
        
        logging.info(f"Successfully loaded {len(data)} entries from {json_file_path}")
        return data

    except (json.JSONDecodeError, ValueError) as e:
        logging.error(f"Error loading JSON file: {e}")
        return []


def clean_text(text):
    """
    Clean the input text by stripping whitespace and ensuring it is a valid string.

    Args:
        text (str): The input text.

    Returns:
        str: Cleaned text.
    """
    return text.strip() if isinstance(text, str) else ""


def calculate_bleu_scores(json_data, verbose=False):
    """
    Compute BLEU scores for all entries in the dataset.

    Args:
        json_data (list): List of entries containing `results2` and `groundtruth`.
        verbose (bool): If True, print detailed BLEU scores for each entry.

    Returns:
        float: The average BLEU score.
    """
    total_bleu_score = 0.0
    valid_entries = 0

    for idx, entry in enumerate(json_data):
        result = clean_text(entry.get("results2", ""))
        groundtruth = clean_text(entry.get("groundtruth", ""))

        if result and groundtruth:
            bleu_score = compute_bleu(groundtruth, result)
            total_bleu_score += bleu_score
            valid_entries += 1

            if verbose:
                logging.info(f"[{idx + 1}] BLEU: {bleu_score:.4f} | Result: {result[:50]}... | Groundtruth: {groundtruth[:50]}...")

    if valid_entries == 0:
        logging.warning("No valid entries found for BLEU computation.")
        return 0.0

    avg_bleu_score = total_bleu_score / valid_entries
    logging.info(f"Computed BLEU scores for {valid_entries} valid entries.")
    
    return avg_bleu_score


def main():
    """
    Main function to load JSON, compute BLEU scores, and print the average BLEU score.
    """
    json_file_path = "output_results_with_results2.json"  # Modify as needed
    json_data = load_json(json_file_path)

    if not json_data:
        logging.error("No valid data loaded. Exiting.")
        return

    avg_bleu_score = calculate_bleu_scores(json_data, verbose=True)
    print(f"\nFinal Average BLEU Score: {avg_bleu_score:.4f}")


if __name__ == "__main__":
    main()
