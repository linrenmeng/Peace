import os
import json
import ast
import astor
import logging

# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def replace_function_body_with_file_content(target_file_path, function_name, source_file_path, class_name=None):
    """
    Replaces the body of a function in the target file with the body from the source file.
    
    Parameters
    ----------
    target_file_path : str
        Path to the target file where the function body needs to be replaced.
    function_name : str
        Name of the function whose body needs to be replaced.
    source_file_path : str
        Path to the file containing the new function body.
    class_name : str, optional
        Name of the class to search for the method within (if applicable).
        
    Returns
    -------
    bool
        Returns True if the replacement was successful, False otherwise.
    """
    try:
        # Read the new function body from the source file
        with open(source_file_path, 'r', encoding='utf-8') as file:
            new_body = file.read()

        # Read the target file's source code
        with open(target_file_path, 'r', encoding='utf-8') as file:
            target_source_code = file.read()

        # Parse the target file's source code
        parsed_code = ast.parse(target_source_code)

        # Helper function to replace the function body
        def replace_body(node):
            for subnode in ast.iter_child_nodes(node):
                if isinstance(subnode, ast.FunctionDef) and subnode.name == function_name:
                    subnode.body = ast.parse(new_body).body
                    logging.info(f"Replaced body of function '{function_name}' in {'class ' + class_name if class_name else 'global scope'}.")
                    return True
            return False

        # Execute the replacement within a class or globally
        if class_name:
            for node in ast.walk(parsed_code):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    if replace_body(node):
                        break
            else:
                logging.warning(f"Class '{class_name}' not found in {target_file_path}.")
                return False
        else:
            if not replace_body(parsed_code):
                logging.warning(f"Function '{function_name}' not found in {target_file_path}.")
                return False

        # Write the modified AST back to the target file
        with open(target_file_path, 'w', encoding='utf-8') as file:
            file.write(astor.to_source(parsed_code))
        
        return True

    except FileNotFoundError:
        logging.error(f"One of the files was not found: {source_file_path} or {target_file_path}.")
        return False
    except Exception as e:
        logging.error(f"An error occurred while replacing the function body: {e}")
        return False

def replace_with_llm_code(reponame, function_name, target_file_path, class_name=None):
    """
    Replaces the function body in the target file with LLM-optimized code from the LLM_predict folder.
    
    Parameters
    ----------
    reponame : str
        The name of the repository.
    function_name : str
        The function name to be replaced.
    target_file_path : str
        The target file path where the function body should be replaced.
    class_name : str, optional
        Class name if the function is a method inside a class.
    """
    source_file_path = os.path.join('data', 'LLM_predict', reponame, f"{function_name}.py")
    success = replace_function_body_with_file_content(target_file_path, function_name, source_file_path, class_name)
    if success:
        logging.info(f"Function '{function_name}' in repository '{reponame}' successfully replaced with LLM-optimized code.")
    else:
        logging.error(f"Failed to replace function '{function_name}' in repository '{reponame}'.")

def restore_original_code(reponame, function_name, target_file_path, class_name=None):
    """
    Restores the original function body from the extract_func folder in the target file.
    
    Parameters
    ----------
    reponame : str
        The name of the repository.
    function_name : str
        The function name to be restored.
    target_file_path : str
        The target file path where the function body should be restored.
    class_name : str, optional
        Class name if the function is a method inside a class.
    """
    source_file_path = os.path.join('data', 'extract_func', reponame, f"{function_name}.py")
    success = replace_function_body_with_file_content(target_file_path, function_name, source_file_path, class_name)
    if success:
        logging.info(f"Function '{function_name}' in repository '{reponame}' restored to the original version.")
    else:
        logging.error(f"Failed to restore function '{function_name}' in repository '{reponame}'.")

def process_repositories(json_path, base_repo_dir, mode="replace"):
    """
    Processes repositories to replace or restore function bodies based on the mode.
    
    Parameters
    ----------
    json_path : str
        The path to the JSON file containing repository information.
    base_repo_dir : str
        The base directory where repositories are located.
    mode : str, optional
        "replace" to replace with LLM code or "restore" to restore original code, by default "replace".
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as json_file:
            repo_data = json.load(json_file)
    except FileNotFoundError:
        logging.error(f"JSON file {json_path} not found.")
        return
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON file {json_path}.")
        return

    # Iterate over each repository's information
    for repo_name, repo_info_list in repo_data.items():
        for repo_info in repo_info_list:
            reponame = repo_info.get('reponame')
            target_file = repo_info.get('target_file')
            target_class = repo_info.get('target_class')
            target_func = repo_info.get('target_func')

            if not all([reponame, target_file, target_func]):
                logging.warning(f"Missing required fields in repository data for {repo_name}. Skipping.")
                continue

            repo_root_path = os.path.join(base_repo_dir, reponame)
            target_file_path = os.path.join(repo_root_path, target_file.split('::')[0])

            logging.info(f"Processing repository '{reponame}', file '{target_file_path}', function '{target_func}'")

            if mode == "replace":
                replace_with_llm_code(reponame, target_func, target_file_path, target_class)
            elif mode == "restore":
                restore_original_code(reponame, target_func, target_file_path, target_class)
            else:
                logging.error(f"Invalid mode '{mode}' provided. Please use 'replace' or 'restore'.")

# Example usage
json_path = 'data/repoexec_python.json'  # Path to the JSON file
base_repo_dir = 'repo_python'  # Base directory where the repositories are located

# Uncomment the following lines to execute the respective mode
# Replace with LLM optimized code
# process_repositories(json_path, base_repo_dir, mode="replace")

# Restore to the original extracted code
process_repositories(json_path, base_repo_dir, mode="restore")
