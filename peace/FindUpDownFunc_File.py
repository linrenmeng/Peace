import ast
import os
import logging

# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

class FunctionAnalyzer:
    """
    Analyzes a given function in a Python repository to identify upstream and downstream dependencies.
    """

    def __init__(self, repo_dir, target_function):
        """
        Initializes the Function Analyzer.

        Parameters
        ----------
        repo_dir : str
            The path to the repository.
        target_function : str
            The function name to analyze.
        """
        self.repo_dir = repo_dir
        self.target_function = target_function
        self.target_file = None
        self.target_function_node = None
        self.user_defined_functions = set()

    def find_target_function_file(self):
        """
        Searches for the file containing the target function.

        Returns
        -------
        str or None
            The file path if the function is found, otherwise None.
        """
        for root, _, files in os.walk(self.repo_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    if self._contains_target_function(file_path):
                        return file_path
        return None

    def _contains_target_function(self, file_path):
        """
        Checks if the given file contains the target function.

        Parameters
        ----------
        file_path : str
            Path of the Python file to analyze.

        Returns
        -------
        bool
            True if the function is found, otherwise False.
        """
        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=file_path)
        except (SyntaxError, FileNotFoundError) as e:
            logging.warning(f"Skipping file {file_path} due to error: {e}")
            return False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == self.target_function:
                self.target_file = file_path
                self.target_function_node = node
                self.user_defined_functions = self._get_user_defined_functions(tree)
                logging.info(f"Found target function '{self.target_function}' in {file_path}")
                return True
        return False

    def _get_user_defined_functions(self, tree):
        """
        Extracts all user-defined function names from the AST tree.

        Parameters
        ----------
        tree : ast.AST
            Parsed AST of a Python file.

        Returns
        -------
        set
            Set of function names defined in the file.
        """
        return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}

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

        downstream = set()
        for node in ast.walk(self.target_function_node):
            if isinstance(node, ast.Call):  
                if isinstance(node.func, ast.Name):  # Direct function call
                    downstream.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):  # Method call
                    downstream.add(node.func.attr)

        downstream = {func for func in downstream if func in self.user_defined_functions}
        return [f"{self.target_file}::{func}" for func in downstream]

    def find_upstream_functions(self):
        """
        Identifies functions that call the target function.

        Returns
        -------
        list
            List of upstream function references.
        """
        if not self.target_file:
            return []

        upstream = set()
        try:
            with open(self.target_file, 'r', encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=self.target_file)
        except (SyntaxError, FileNotFoundError) as e:
            logging.warning(f"Skipping file {self.target_file} due to error: {e}")
            return []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for inner_node in ast.walk(node):
                    if isinstance(inner_node, ast.Call):
                        if isinstance(inner_node.func, ast.Name) and inner_node.func.id == self.target_function:
                            upstream.add(node.name)
                        elif isinstance(inner_node.func, ast.Attribute) and inner_node.func.attr == self.target_function:
                            upstream.add(node.name)

        return [f"{self.target_file}::{func}" for func in upstream]

    def analyze(self):
        """
        Performs the function dependency analysis.

        Returns
        -------
        tuple
            (upstream functions, downstream functions).
        """
        if not self.find_target_function_file():
            logging.error(f"Function '{self.target_function}' not found in any file.")
            return [], []

        upstream = self.find_upstream_functions()
        downstream = self.find_downstream_functions()

        return upstream, downstream


# ========== Example Usage ==========
if __name__ == "__main__":
    REPO_DIR = "/path/to/repository"
    TARGET_FUNCTION = "_get_ticker_tz"

    analyzer = FunctionAnalyzer(REPO_DIR, TARGET_FUNCTION)
    upstream, downstream = analyzer.analyze()

    logging.info("Upstream Functions:")
    for func in upstream:
        logging.info(func)

    logging.info("Downstream Functions:")
    for func in downstream:
        logging.info(func)