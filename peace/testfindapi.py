import logging
from FindApi import FindApi

# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def run_find_api(repo_path, target_function, target_class=None):
    """
    Runs the FindApi analysis and logs the results.

    Parameters
    ----------
    repo_path : str
        Path to the repository.
    target_function : str
        Name of the function to analyze.
    target_class : str or None, optional
        Name of the class containing the function (if applicable).

    Returns
    -------
    dict
        Dictionary containing "imports" and "api_calls".
    """
    if not repo_path or not target_function:
        logging.error("Repository path and target function must be specified.")
        return {}

    try:
        result = FindApi(repo_path, target_function, target_class)
        logging.info(f"Analysis completed for function: {target_function}")
        logging.info(f"Imports: {result.get('imports', [])}")
        logging.info(f"API Calls: {result.get('api_calls', [])}")
        return result
    except Exception as e:
        logging.error(f"Error during API analysis: {e}")
        return {}

# ========== Example Usage ==========
if __name__ == "__main__":
    REPO_PATH = "/path/to/repository"
    TARGET_FUNCTION = "_get_ticker_tz"
    TARGET_CLASS = "TickerBase"

    results = run_find_api(REPO_PATH, TARGET_FUNCTION, TARGET_CLASS)

    if results:
        print("Imports:", results.get("imports", []))
        print("API Calls:", results.get("api_calls", []))
