import json
import os
import re
import logging
from FunctionOptimizer import add_data, get_prompt, send_to_gpt
from RAGEditPool import RAGEditPool
from get_modifications import FunctionModificationAnalyzer

# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def filter_response(code):
    """
    Cleans the response code by removing unnecessary markdown formatting.

    Parameters
    ----------
    code : str
        The raw response code.

    Returns
    -------
    str
        Cleaned code string.
    """
    code = re.sub(r'^```python\n', '', code)  # Remove leading ```python
    code = re.sub(r'```$', '', code)  # Remove trailing ```
    return code.strip()

def process_function_modifications(modifications):
    """
    Processes function modifications by retrieving function details, 
    generating optimized versions, and tracking edits.

    Parameters
    ----------
    modifications : list
        List of function modification dictionaries.

    Returns
    -------
    list
        List of processed function modifications.
    """
    results = []
    rag_pool = RAGEditPool(max_lines=10)

    for data in modifications:
        try:
            result = {}
            
            # Construct data input
            input_data = add_data(data, rag_pool)

            result["repo_path"] = data.get("repo_path", "")
            result["file_path"] = data.get("file_path", "")
            result["function_name"] = data.get("function_name", "")
            result["class_name"] = data.get("class_name", "")
            result["message"] = data.get("message", "")

            result["before"] = input_data.get("function_body", "")
            
            # Generate optimized function
            optimized_code = send_to_gpt(get_prompt(input_data))
            result["after"] = filter_response(optimized_code)

            # Store edit in RAG pool
            rag_pool.add_edit(result["before"], result["after"])

            results.append(result)

        except Exception as e:
            logging.error(f"Error processing function {data.get('function_name', '')}: {e}")

    return results

def pipeline_function_modifications(data):
    """
    Runs the pipeline to analyze function dependencies and apply modifications.

    Parameters
    ----------
    data : dict
        Dictionary containing repository path, function name, class name, and message.

    Returns
    -------
    list
        List of processed function modifications.
    """
    try:
        repo_path = data.get("repo_path", "")
        target_function = data.get("function_name", "")
        target_class = data.get("class_name", "")
        message = data.get("message", "")

        if not repo_path or not target_function:
            logging.error("Missing required parameters: repo_path or function_name")
            return []

        # Analyze function dependencies
        analyzer = FunctionModificationAnalyzer(repo_path, target_function, target_class)
        modifications = analyzer.get_modifications()

        # Update each modification entry with additional metadata
        for mod in modifications:
            mod["repo_path"] = repo_path
            mod["message"] = message

        return process_function_modifications(modifications)

    except Exception as e:
        logging.error(f"Pipeline execution error: {e}")
        return []

# ========== Example Usage ==========
if __name__ == "__main__":
    DATA = {
        "repo_path": "/path/to/repository",
        "function_name": "lines_with_leading_tabs_expanded",
        "class_name": None,  # None if function is not inside a class
        "message": "Optimize for performance."
    }

    # Run the function modification pipeline
    results = pipeline_function_modifications(DATA)

    # Save results to JSON
    output_file = "modified_functions.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    logging.info(f"Results have been saved to {output_file}")
