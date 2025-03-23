import json
from code_evaluation_pipeline import evaluate


def load_json_file(file_path):
    """
    Load JSON data from a file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: The loaded JSON data.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {file_path}.")
        return {}


def save_json_file(data, file_path):
    """
    Save data as JSON to a file.

    Args:
        data (dict): The data to be saved.
        file_path (str): Path to the output JSON file.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Evaluation results saved successfully.")
    except Exception as e:
        print(f"Error saving evaluation results to {file_path}: {e}")


def prepare_evaluation_data(modification, repo_info_item, sha, venv_path_prefix):
    """
    Prepare the data for the evaluate function.

    Args:
        modification (dict): A dictionary containing modification details.
        repo_info_item (dict): A dictionary containing repository information.
        sha (str): The SHA of the commit.
        venv_path_prefix (str): The prefix for the virtual environment path.

    Returns:
        dict: The prepared data for evaluation.
    """
    modification["repo_path"] = modification["repo_path"].replace("DOCKER_REPOEXEC_PATH_PLACEHOLDER", "LOCAL_REPOEXEC_PATH_PLACEHOLDER")
    modification["file_path"] = modification["file_path"].replace("DOCKER_REPOEXEC_PATH_PLACEHOLDER", "LOCAL_REPOEXEC_PATH_PLACEHOLDER")
    return {
        "repo_path": modification["repo_path"],
        "venv_path": f"{venv_path_prefix}{repo_info_item['venv_path']}",
        "test_cmd": repo_info_item["test_cmd"],
        "sha": sha,
        "function_name": modification["function_name"],
        "class_name": modification["class_name"],
        "file_path": modification["file_path"],
        "after_code": modification["after"]
    }


def evaluate_modifications(repo_info, modifications_data, venv_path_prefix):
    """
    Evaluate the modifications in each repository.

    Args:
        repo_info (dict): Repository information loaded from JSON.
        modifications_data (dict): Modification data loaded from JSON.
        venv_path_prefix (str): The prefix for the virtual environment path.

    Returns:
        dict: The evaluation results.
    """
    evaluation_results = {}
    for repo_name, sha_results in modifications_data.items():
        repo_eval_results = {}
        repo_info_for_repo = repo_info.get(repo_name, [])
        for sha, modifications in sha_results.items():
            try:
                repo_info_item = next((item for item in repo_info_for_repo if item["sha"] == sha), None)
                if repo_info_item:
                    target_func = repo_info_item["target_func"]
                    for modification in modifications:
                        if modification["function_name"] != target_func:
                            continue
                        evaluation_data = prepare_evaluation_data(modification, repo_info_item, sha, venv_path_prefix)
                        cpu_instr, mem_usage = evaluate(evaluation_data)
                        repo_eval_results[sha] = {
                            "cpu_instr": cpu_instr,
                            "mem_usage": mem_usage
                        }
                        break
            except Exception as e:
                print(f"Error evaluating {repo_name} at SHA {sha}: {e}")
        evaluation_results[repo_name] = repo_eval_results
    return evaluation_results


def main():
    """
    Main function to perform the evaluation process.
    """
    # Load repository information and modification data
    repo_info_file = "REPO_INFO_FILE_PATH_PLACEHOLDER"
    modifications_file = "MODIFICATIONS_FILE_PATH_PLACEHOLDER"
    repo_info = load_json_file(repo_info_file)
    modifications_data = load_json_file(modifications_file)

    # Prefix for virtual environment path
    venv_path_prefix = "VENV_PATH_PREFIX_PLACEHOLDER"

    # Evaluate the modifications
    evaluation_results = evaluate_modifications(repo_info, modifications_data, venv_path_prefix)

    # Save the evaluation results
    output_file = "OUTPUT_FILE_PATH_PLACEHOLDER"
    save_json_file(evaluation_results, output_file)


if __name__ == "__main__":
    main()