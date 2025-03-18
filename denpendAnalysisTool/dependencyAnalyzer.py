import torch
import logging
from main import DependencyClassifier  # Assuming the DependencyClassifier is defined in main.py

# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

class DependencyAnalyzer:
    def __init__(self, model_dir="/path/to/your/model", max_input_length=256):
        """
        Initializes the DependencyAnalyzer class and loads the model.
        
        Parameters
        ----------
        model_dir : str
            Directory where the model is stored.
        max_input_length : int, optional
            Maximum length of the input code (default is 256).
        """
        self.model_dir = model_dir
        self.max_input_length = max_input_length
        self.classifier = None
        self._load_model()

    def _load_model(self):
        """
        Loads the dependency classifier model.
        Logs success or failure to load the model.
        """
        try:
            self.classifier = DependencyClassifier(load_dir=self.model_dir)
            logging.info(f"Model loaded successfully from {self.model_dir}")
        except Exception as e:
            logging.error(f"Failed to load the model from {self.model_dir}: {e}")
            self.classifier = None

    def _truncate_code(self, code: str) -> str:
        """
        Truncates the code to ensure it doesn't exceed the maximum length.
        
        Parameters
        ----------
        code : str
            The code string to truncate.
        
        Returns
        -------
        str
            The truncated code string.
        """
        return code[:self.max_input_length]

    def _construct_input_pair(self, code_1: str, code_2: str):
        """
        Constructs the input pair for the model based on two code strings.

        Parameters
        ----------
        code_1 : str
            The first code string.
        code_2 : str
            The second code string.

        Returns
        -------
        tuple
            A tuple containing the two truncated code strings.
        """
        code_1 = self._truncate_code(code_1)
        code_2 = self._truncate_code(code_2)
        return self.classifier.construct_pair(code_1, code_2)

    def get_dependency(self, code_1: str, code_2: str) -> float:
        """
        Analyzes the dependency score between two code strings.

        Parameters
        ----------
        code_1 : str
            The first code string.
        code_2 : str
            The second code string.

        Returns
        -------
        float
            The dependency score (between 0 and 1).
        """
        if not self.classifier:
            logging.error("Model is not loaded. Please load the model first.")
            return 0.0

        try:
            input_pair = self._construct_input_pair(code_1, code_2)
            dependency_score = self.classifier.gen(input_pair)
            logging.info(f"Calculated dependency score: {dependency_score}")
            return dependency_score
        except Exception as e:
            logging.error(f"Error during dependency calculation: {e}")
            return 0.0

    def compare_multiple_codes(self, code_pairs: list) -> list:
        """
        Compares multiple pairs of code and returns their dependency scores.

        Parameters
        ----------
        code_pairs : list
            A list of tuples where each tuple contains two code strings.

        Returns
        -------
        list
            A list of dependency scores corresponding to each code pair.
        """
        scores = []
        for code_1, code_2 in code_pairs:
            score = self.get_dependency(code_1, code_2)
            scores.append(score)
        return scores

    def analyze_and_get_results(self, code_1: str, code_2: str) -> dict:
        """
        Analyzes two pieces of code and returns detailed results in a dictionary.

        Parameters
        ----------
        code_1 : str
            The first code string.
        code_2 : str
            The second code string.

        Returns
        -------
        dict
            A dictionary containing the input code, dependency score, and other relevant details.
        """
        dependency_score = self.get_dependency(code_1, code_2)
        result = {
            "code_1": code_1,
            "code_2": code_2,
            "dependency_score": dependency_score,
            "truncated_code_1": self._truncate_code(code_1),
            "truncated_code_2": self._truncate_code(code_2)
        }
        return result


# ========== Example Usage ==========
if __name__ == "__main__":
    # Example code snippets for analysis
    code_1 = "def foo(): pass"  # Example code 1
    code_2 = "def bar(): pass"  # Example code 2

    # Initialize analyzer
    analyzer = DependencyAnalyzer(model_dir="/path/to/your/model")

    # Get dependency score for two code snippets
    score = analyzer.get_dependency(code_1, code_2)
    logging.info(f"Dependency score between code_1 and code_2: {score}")

    # Compare multiple code pairs
    code_pairs = [("def foo(): pass", "def bar(): pass"), ("def add(a, b): return a + b", "def multiply(a, b): return a * b")]
    scores = analyzer.compare_multiple_codes(code_pairs)
    logging.info(f"Dependency scores for multiple pairs: {scores}")

    # Get detailed analysis results
    result = analyzer.analyze_and_get_results(code_1, code_2)
    logging.info(f"Detailed analysis result: {result}")
