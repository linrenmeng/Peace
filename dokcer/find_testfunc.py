import os
import re
import logging

# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def search_test_functions_in_repo(function_name, repo_path='.', search_patterns=None):
    """
    Searches for test functions in a repository based on the given function name.

    Parameters
    ----------
    function_name : str
        The name of the function to search for.
    repo_path : str, optional
        The path to the repository, by default current directory.
    search_patterns : list, optional
        The patterns to search for in the test files, by default None.

    Returns
    -------
    list
        A list of file paths containing the test functions.
    """
    if search_patterns is None:
        search_patterns = [
            f"test_{function_name}",
            f"tests_{function_name}",
            f"{function_name}"
        ]
    
    test_functions_found = []
    
    logging.info(f"Searching for test functions related to '{function_name}' in repository: {repo_path}")
    
    # Regex patterns for flexibility
    patterns = [re.compile(pattern) for pattern in search_patterns]

    # Walk through the repository
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):  # Assuming test files are Python files
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Check if any of the search patterns exist in the file content
                    for pattern in patterns:
                        if pattern.search(content):
                            test_functions_found.append(file_path)
                            break  # Stop after the first match for efficiency

                except Exception as e:
                    logging.error(f"Error reading file {file_path}: {e}")

    return test_functions_found

def display_test_functions(test_files):
    """
    Displays the test files containing the test functions for the specified function.

    Parameters
    ----------
    test_files : list
        List of file paths containing the test functions.
    """
    if test_files:
        logging.info("Found the following test functions:")
        for test_file in test_files:
            logging.info(f"  {test_file}")
    else:
        logging.info("No test functions found.")

# ========== Example Usage ==========
if __name__ == "__main__":
    # Example repository path and function name
    repo_path = '/data/junwan/repoexec/docker/repoexec/repo_python/mkdocs'  # Replace with actual repository path
    function_name = 'get_relative_url'  # Replace with the function name you are searching for

    # Search for the test functions
    test_files = search_test_functions_in_repo(function_name, repo_path)

    # Display results
    display_test_functions(test_files)
