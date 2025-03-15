import os
import ast
import logging

# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def extract_imports(script):
    """
    Extracts all import statements from the given script.

    Parameters
    ----------
    script : str
        Python script as a string.

    Returns
    -------
    list
        List of extracted import statements.
    """
    return [
        line.strip() for line in script.split("\n")
        if line.strip().startswith(("import ", "from "))
    ]

def extract_function_calls(script, function_name):
    """
    Extracts all unique function calls from the given function body.

    Parameters
    ----------
    script : str
        Python script as a string.
    function_name : str
        The function name to analyze.

    Returns
    -------
    list
        List of extracted function calls.
    """
    try:
        tree = ast.parse(script)
    except SyntaxError:
        logging.warning("Syntax error encountered in script. Skipping function analysis.")
        return []

    calls = set()

    # Locate the target function
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            # Find function calls within the function body
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):  # Direct function call
                        calls.add(child.func.id)
                    elif isinstance(child.func, ast.Attribute):  # Attribute-based calls
                        value = child.func.value
                        if isinstance(value, ast.Name):  
                            calls.add(f"{value.id}.{child.func.attr}")
                        elif isinstance(value, ast.Attribute):  
                            calls.add(f"{value.attr}.{child.func.attr}")

    return list(calls)

def find_target_file(repo_path, target_function, target_class=None):
    """
    Searches for the Python file containing the target function or class.

    Parameters
    ----------
    repo_path : str
        Path to the repository.
    target_function : str
        Function name to search for.
    target_class : str or None, optional
        Class name (if applicable).

    Returns
    -------
    str or None
        Path of the target file if found, otherwise None.
    """
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        script = f.read()
                    tree = ast.parse(script)

                    for node in ast.walk(tree):
                        if target_class and isinstance(node, ast.ClassDef) and node.name == target_class:
                            return file_path
                        elif not target_class and isinstance(node, ast.FunctionDef) and node.name == target_function:
                            return file_path
                except (SyntaxError, FileNotFoundError) as e:
                    logging.warning(f"Skipping file {file_path} due to error: {e}")
    return None

def FindApi(repo_path, target_function, target_class=None):
    """
    Analyzes a function to extract imports and API calls.

    Parameters
    ----------
    repo_path : str
        Path to the repository.
    target_function : str
        Name of the function to analyze.
    target_class : str or None, optional
        Name of the class if the function belongs to a class.

    Returns
    -------
    dict
        Dictionary containing "imports" and "api_calls".
    """
    try:
        target_file = find_target_file(repo_path, target_function, target_class)

        if not target_file:
            logging.error(f"Target function '{target_function}' or class '{target_class}' not found.")
            return {"imports": [], "api_calls": []}

        with open(target_file, "r", encoding="utf-8") as f:
            script = f.read()

        imports = extract_imports(script)
        api_calls = extract_function_calls(script, target_function)

        logging.info(f"Analysis completed for function: {target_function}")
        return {"imports": imports, "api_calls": api_calls}

    except Exception as e:
        logging.error(f"An error occurred during API analysis: {e}")
        return {"imports": [], "api_calls": []}

# ========== Example Usage ==========
if __name__ == '__main__':
    REPO_PATH = "/path/to/repository"
    TARGET_FUNCTION = "_get_ticker_tz"
    TARGET_CLASS = "TickerBase"

    results = FindApi(REPO_PATH, TARGET_FUNCTION, TARGET_CLASS)

    print("Imports:", results["imports"])
    print("API Calls:", results["api_calls"])
