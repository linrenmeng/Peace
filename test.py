import os
import logging
from dependencyAnalyze import DependencyAnalyzer  # Assuming this is the module where analyze_dependency is defined

# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def analyze_dependency(code_1: str, code_2: str) -> float:
    """
    Analyzes the dependency score between two given code snippets.
    
    Parameters
    ----------
    code_1 : str
        The first code snippet to analyze.
    code_2 : str
        The second code snippet to analyze.
    
    Returns
    -------
    float
        The dependency score (between 0 and 1), where higher means greater dependency.
    """
    try:
        # Initialize the dependency analyzer (this assumes you have loaded the model)
        analyzer = DependencyAnalyzer(model_dir="/path/to/your/model")

        # Call the model to calculate the dependency score
        score = analyzer.get_dependency(code_1, code_2)
        return score
    except Exception as e:
        logging.error(f"Error during dependency analysis: {e}")
        return 0.0

def test_dependency_analysis():
    """
    Tests the dependency analysis functionality with example code snippets.
    """
    # Example code snippets to test the dependency analysis
    code_1 = "def add(a, b): return a + b"
    code_2 = """class DependencyAnalyzer(nn.Module, PyTorchModelHubMixin):
        def __init__(self):
            pass

        def analyze(self, code):
            return add(a, b)  # Using add function inside class
    """

    # Logging the start of the test
    logging.info("Starting the dependency analysis test...")

    # Call the function to get the dependency score
    score = analyze_dependency(code_1, code_2)

    if score:
        logging.info(f"Dependency analysis completed successfully with a score of {score:.4f}")
    else:
        logging.error("Dependency analysis failed or returned no result.")

    return score

def display_result(score):
    """
    Displays the result of the dependency analysis.
    
    Parameters
    ----------
    score : float
        The dependency score to display.
    """
    if score > 0.8:
        print(f"High dependency score: {score}. The two code snippets are highly related!")
    elif score > 0.5:
        print(f"Moderate dependency score: {score}. The code snippets share some relation.")
    else:
        print(f"Low dependency score: {score}. The code snippets appear to be largely independent.")

# ========== Main Execution ==========
if __name__ == "__main__":
    # Run the dependency analysis test
    score = test_dependency_analysis()

    # Display the result
    display_result(score)
