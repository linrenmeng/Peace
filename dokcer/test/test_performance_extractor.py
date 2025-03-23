import subprocess
import os
import re


def extract_cpu_instr(output):
    """
    Extract the CPU instruction count from the pytest output.
    If no match is found, return -1.

    Args:
        output (str): The output from the test command.

    Returns:
        int: The CPU instruction count or -1 if not found.
    """
    match = re.search(r'instruction_count=(\d+)', output)
    return int(match.group(1)) if match else -1


def extract_mem_usage(output):
    """
    Extract the memory usage from the pytest output.
    If no match is found, return -1.

    Args:
        output (str): The output from the test command.

    Returns:
        float: The memory usage in MB or -1 if not found.
    """
    match = re.search(r'Memory usage \(MB\): ([\d.]+)', output)
    return float(match.group(1)) if match else -1


def run_test_after_modification(repo_dir, venv_path, test_cmd):
    """
    Switch the repository to a specified version and run the test command
    to verify if the modified code is valid.

    Args:
        repo_dir (str): The root directory of the repository.
        venv_path (str): The path to the Python virtual environment.
        test_cmd (str): The test command to be executed.

    Returns:
        str or None: The standard output of the test command if successful,
                     None if an error occurs.
    """
    try:
        # Change to the specified repository directory
        os.chdir(repo_dir)

        # Build the full command: activate the virtual environment and run the test command
        full_command = f"export PYTHONPATH=$PYTHONPATH:$(pwd) && bash -c 'source {venv_path}/bin/activate && {test_cmd}'"

        # Run the command and capture the output
        result = subprocess.run(
            full_command,
            shell=True,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10  # Set the timeout to 10 seconds
        )

        # Return the standard output
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error during test execution: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def main():
    """
    Main function to run the test and extract performance metrics.
    """
    # Replace these paths with your actual paths before running
    repo_dir = "your_repo_directory"
    venv_path = "your_venv_path"
    test_cmd = "your_test_command"

    output = run_test_after_modification(repo_dir, venv_path, test_cmd)
    if output:
        print("Code accepted:")
    else:
        print("An error occurred during the test execution.")

    # Extract CPU instructions and memory usage
    cpu_instr = extract_cpu_instr(output)
    mem_usage = extract_mem_usage(output)
    print(f"CPU instructions: {cpu_instr}")
    print(f"Memory usage: {mem_usage} MB")


if __name__ == "__main__":
    main()
