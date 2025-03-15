import ast
import os
import logging
import concurrent.futures
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class FunctionAnalyzer:
    def __init__(self, repo_path, target_function, target_class=None, parallel=False):
        """
        Initialize the function analyzer.

        :param repo_path: Path to the repository.
        :param target_function: Name of the function to locate.
        :param target_class: Class containing the function (None if function is standalone).
        :param parallel: Whether to use multi-threading for file parsing.
        """
        self.repo_path = repo_path
        self.target_function = target_function
        self.target_class = target_class
        self.target_file = None
        self.target_function_node = None
        self.class_function_map = defaultdict(set)  # Store class-method mappings
        self.file_cache = {}  # Cache parsed AST trees to avoid redundant parsing
        self.parallel = parallel

    def is_valid_file(self, file_path):
        """Check if the file is a valid Python script and not in excluded directories."""
        return file_path.endswith('.py') and 'site-packages' not in file_path and '__pycache__' not in file_path

    def extract_class_function_map(self, tree):
        """Extract mappings of class names to their corresponding functions."""
        class_function_map = defaultdict(set)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                methods = {item.name for item in node.body if isinstance(item, ast.FunctionDef)}
                class_function_map[class_name].update(methods)
        return class_function_map

    def parse_file(self, file_path):
        """Parse a Python file and extract its AST tree."""
        if file_path in self.file_cache:
            return self.file_cache[file_path]

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=file_path)
                self.file_cache[file_path] = tree  # Cache the parsed tree
                return tree
        except (SyntaxError, UnicodeDecodeError) as e:
            logging.warning(f"Skipping file {file_path} due to error: {e}")
            return None

    def analyze_function(self, file_path):
        """
        Analyze a Python file to check if it contains the target function.
        If found, update `self.target_file` and `self.target_function_node`.
        """
        tree = self.parse_file(file_path)
        if not tree:
            return False

        self.class_function_map.update(self.extract_class_function_map(tree))

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == self.target_function:
                if self.target_class:
                    # Ensure function belongs to the correct class
                    if self.target_class in self.class_function_map and self.target_function in self.class_function_map[self.target_class]:
                        self.target_file = file_path
                        self.target_function_node = node
                        logging.info(f"Found function {self.target_class}::{self.target_function} in {file_path}")
                        return True
                else:
                    # Ensure it's not part of any class if no class is specified
                    if self.target_function not in self.class_function_map:
                        self.target_file = file_path
                        self.target_function_node = node
                        logging.info(f"Found function {self.target_function} in {file_path}")
                        return True
        return False

    def find_target_function(self):
        """Search for the target function across all Python files in the repository."""
        file_paths = []
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                if self.is_valid_file(file_path):
                    file_paths.append(file_path)

        if self.parallel:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = executor.map(self.analyze_function, file_paths)
                if any(results):  # If any file contains the function, stop searching
                    return
        else:
            for file_path in file_paths:
                if self.analyze_function(file_path):
                    return  # Stop once function is found

    def get_function_details(self):
        """Retrieve function signature and body."""
        if not self.target_function_node or not self.target_file:
            return None, None

        # Extract function signature
        args = [arg.arg for arg in self.target_function_node.args.args]
        signature = f"def {self.target_function}({', '.join(args)}):"

        # Read full file content
        with open(self.target_file, encoding='utf-8') as f:
            source_code = f.read()

        # Extract function body
        body_lines = [
            ast.get_source_segment(source_code, node)
            for node in self.target_function_node.body
        ]

        return signature, '\n'.join(filter(None, body_lines))

    def find(self):
        """Run the function search process and return results."""
        self.find_target_function()
        if not self.target_file:
            logging.warning("Target function not found.")
            return None, None

        return self.get_function_details()


# Example usage
if __name__ == '__main__':
    repo_path = "/path/to/repository"  # Replace with actual repository path
    target_function = "_get_ticker_tz"  # Function to locate
    target_class = None  # Set class name if function is within a class, otherwise None

    analyzer = FunctionAnalyzer(repo_path, target_function, target_class, parallel=True)
    signature, body = analyzer.find()

    if signature and body:
        print("\nFunction Signature:\n", signature)
        print("\nFunction Body:\n", body)
    else:
        print("Function not found.")
