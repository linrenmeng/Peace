import os
import ast
import logging
from analyze_dependency import DependencyAnalyzer
from FindUpDownFunc_Repo import FindUpDownFunc
from FindFunc import FindFunc

# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

class FunctionDependencyAnalyzer:
    """
    Analyzes a function's upstream and downstream dependencies in a given repository.
    Determines functions that require modifications based on dependency scores.
    """

    def __init__(self, repo_dir, target_function, target_class=None):
        """
        Initializes the function dependency analyzer.

        Parameters
        ----------
        repo_dir : str
            Path to the repository.
        target_function : str
            Name of the target function.
        target_class : str or None, optional
            Name of the class containing the function (if applicable).
        """
        self.repo_dir = repo_dir
        self.target_function = target_function
        self.target_class = target_class
        self.dependency_analyzer = DependencyAnalyzer()

    def _truncate_code(self, code, max_length=500):
        """
        Truncates a given code snippet to a maximum length.

        Parameters
        ----------
        code : str
            Code snippet to truncate.
        max_length : int, optional
            Maximum allowed length (default is 500).

        Returns
        -------
        str
            Truncated code snippet.
        """
        return code[:max_length]

    def _get_function_signature_and_body(self, function_name, class_name=None):
        """
        Retrieves the function signature and body.

        Parameters
        ----------
        function_name : str
            Name of the function.
        class_name : str or None, optional
            Name of the class containing the function (if applicable).

        Returns
        -------
        str or None
            Function signature and body as a string, or None if not found.
        """
        analyzer = FindFunc(self.repo_dir, function_name, class_name)
        signature, body = analyzer.find()
        return f"{signature}\n{body}" if signature and body else None

    def _get_dependent_functions(self, func_list):
        """
        Retrieves functions with their dependency scores.

        Parameters
        ----------
        func_list : list
            List of functions to analyze.

        Returns
        -------
        list
            List of functions that require modification.
        """
        modifications = []
        target_code = self._get_function_signature_and_body(self.target_function, self.target_class)
        
        if target_code is None:
            logging.warning(f"Target function '{self.target_function}' not found. Skipping dependency analysis.")
            return []

        for func in func_list:
            file_path = func["file_path"]
            class_name = func["class_name"]
            function_name = func["function_name"]

            # Ignore test functions
            if function_name.startswith(("test_", "tests_")):
                continue

            # Retrieve function signature and body
            function_code = self._get_function_signature_and_body(function_name, class_name)
            if function_code is None:
                continue

            # Compute dependency score
            score = self.dependency_analyzer.get_dependency(
                self._truncate_code(function_code), 
                self._truncate_code(target_code)
            )

            if score > 0.001:
                modifications.append({
                    "file_path": file_path,
                    "class_name": class_name,
                    "function_name": function_name,
                    "dependency_score": score
                })

        return modifications

    def _get_function_file_path(self, function_name, class_name=None):
        """
        Identifies the file containing the given function.

        Parameters
        ----------
        function_name : str
            Name of the function.
        class_name : str or None, optional
            Name of the class containing the function.

        Returns
        -------
        str or None
            File path of the function, or None if not found.
        """
        for root, _, files in os.walk(self.repo_dir):
            for file in files:
                if file.endswith(".py"):  
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            tree = ast.parse(f.read(), filename=file_path)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                                    if class_name:
                                        for n in ast.walk(tree):
                                            if isinstance(n, ast.ClassDef) and n.name == class_name:
                                                if any(isinstance(x, ast.FunctionDef) and x.name == function_name for x in n.body):
                                                    return file_path
                                    else:
                                        return file_path
                    except (SyntaxError, UnicodeDecodeError):
                        logging.warning(f"Skipping file {file_path} due to parsing errors.")
                        continue
        return None

    def get_modifications(self):
        """
        Determines functions requiring modifications based on dependency scores.

        Returns
        -------
        list
            List of functions that require modification.
        """
        # Identify target function dependencies
        analyzer = FindUpDownFunc(self.repo_dir, self.target_function, self.target_class)
        upstream, downstream = analyzer.find()

        modifications = []

        # Analyze downstream functions
        downstream_modifications = self._get_dependent_functions(downstream)
        modifications.extend(downstream_modifications)

        # Include target function itself
        modifications.append({
            "file_path": self._get_function_file_path(self.target_function, self.target_class),
            "class_name": self.target_class,
            "function_name": self.target_function,
            "dependency_score": 100  # Target function always requires modification
        })

        # Analyze upstream functions
        upstream_modifications = self._get_dependent_functions(upstream)
        modifications.extend(upstream_modifications)

        return modifications


# ========== Example Usage ==========
if __name__ == "__main__":
    REPO_PATH = "/path/to/repository"
    TARGET_FUNCTION = "magphase"
    TARGET_CLASS = None  # Set to None if function is not inside a class

    analyzer = FunctionDependencyAnalyzer(REPO_PATH, TARGET_FUNCTION, TARGET_CLASS)
    modifications = analyzer.get_modifications()

    logging.info("Functions to be modified:")
    for mod in modifications:
        logging.info(mod)

    logging.info(f"Total modifications: {len(modifications)}")
