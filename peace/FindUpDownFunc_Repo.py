import ast
import os
import logging

# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

class FindUpDownFunc:
    """
    Analyzes a Python repository to find upstream (callers) and downstream (callees) 
    of a given function, with support for class methods.
    """

    def __init__(self, repo_path, target_function, target_class=None):
        """
        Initializes the function analyzer.

        Parameters
        ----------
        repo_path : str
            Path to the repository.
        target_function : str
            Name of the target function.
        target_class : str or None, optional
            Name of the class containing the function (if applicable).
        """
        self.repo_path = repo_path
        self.target_function = target_function
        self.target_class = target_class
        self.target_file = None
        self.target_function_node = None
        self.class_function_map = {}

    def _is_valid_file(self, file_path):
        """Checks if a file is a valid Python file."""
        return file_path.endswith('.py') and 'site-packages' not in file_path and '__pycache__' not in file_path

    def _extract_class_function_map(self, tree):
        """Extracts a mapping of class names to their methods."""
        class_function_map = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                methods = [
                    item.name for item in node.body if isinstance(item, ast.FunctionDef)
                ]
                class_function_map[class_name] = methods
        return class_function_map

    def _find_target_function(self, file_path):
        """
        Checks if the target function exists in the given file.

        Parameters
        ----------
        file_path : str
            Path of the Python file.

        Returns
        -------
        bool
            True if the function is found, otherwise False.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=file_path)
                self.class_function_map = self._extract_class_function_map(tree)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == self.target_function:
                        if self.target_class:
                            if self.target_function in self.class_function_map.get(self.target_class, []):
                                self.target_file = file_path
                                self.target_function_node = node
                                logging.info(f"Found target function {self.target_class}::{self.target_function} in {file_path}")
                                return True
                        else:
                            if self.target_function not in self.class_function_map:
                                self.target_file = file_path
                                self.target_function_node = node
                                logging.info(f"Found target function {self.target_function} in {file_path}")
                                return True
        except (SyntaxError, FileNotFoundError) as e:
            logging.warning(f"Skipping file {file_path} due to error: {e}")
        return False

    def find_target_function(self):
        """Searches the repository for the target function's location."""
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_valid_file(file_path) and self._find_target_function(file_path):
                    return

    def _extract_function_calls(self, node):
        """Extracts function calls from an AST node."""
        calls = []
        for inner_node in ast.walk(node):
            if isinstance(inner_node, ast.Call):
                if isinstance(inner_node.func, ast.Name):  
                    calls.append(inner_node.func.id)
                elif isinstance(inner_node.func, ast.Attribute):  
                    calls.append(inner_node.func.attr)
        return calls

    def find_upstream_functions(self):
        """
        Identifies functions that call the target function.

        Returns
        -------
        list
            List of upstream function references.
        """
        if not self.target_file or not self.target_function_node:
            return []

        upstream = []
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                if not self._is_valid_file(file_path):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read(), filename=file_path)
                        class_function_map = self._extract_class_function_map(tree)

                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                function_calls = self._extract_function_calls(node)
                                if self.target_function in function_calls:
                                    upstream.append({
                                        "file_path": file_path,
                                        "class_name": next((cls for cls, methods in class_function_map.items() if node.name in methods), None),
                                        "function_name": node.name
                                    })
                except (SyntaxError, FileNotFoundError) as e:
                    logging.warning(f"Skipping file {file_path} due to error: {e}")
        return upstream

    def find_downstream_functions(self):
        """
        Identifies functions called by the target function.

        Returns
        -------
        list
            List of downstream function references.
        """
        if not self.target_function_node:
            return []

        downstream = self._extract_function_calls(self.target_function_node)

        result = []
        for func_name in set(downstream):
            for root, _, files in os.walk(self.repo_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if not self._is_valid_file(file_path):
                        continue

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            tree = ast.parse(f.read(), filename=file_path)
                            class_function_map = self._extract_class_function_map(tree)

                            for node in ast.walk(tree):
                                if isinstance(node, ast.FunctionDef) and node.name == func_name:
                                    result.append({
                                        "file_path": file_path,
                                        "class_name": next((cls for cls, methods in class_function_map.items() if func_name in methods), None),
                                        "function_name": func_name
                                    })
                    except (SyntaxError, FileNotFoundError) as e:
                        logging.warning(f"Skipping file {file_path} due to error: {e}")
        return result

    def find(self):
        """
        Runs the full analysis process.

        Returns
        -------
        tuple
            (upstream functions, downstream functions)
        """
        self.find_target_function()
        if not self.target_file:
            logging.error("Target function not found.")
            return [], []

        upstream = self.find_upstream_functions()
        downstream = self.find_downstream_functions()
        return upstream, downstream


# ========== Example Usage ==========
if __name__ == "__main__":
    REPO_PATH = "/path/to/repository"
    TARGET_FUNCTION = "_get_ticker_tz"
    TARGET_CLASS = "TickerBase"

    analyzer = FindUpDownFunc(REPO_PATH, TARGET_FUNCTION, TARGET_CLASS)
    upstream, downstream = analyzer.find()

    logging.info("Upstream Functions:")
    for func in upstream:
        logging.info(func)

    logging.info("\nDownstream Functions:")
    for func in downstream:
        logging.info(func)
