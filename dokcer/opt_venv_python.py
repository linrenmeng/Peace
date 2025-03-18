import json
import subprocess
import os
import logging

# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def install_packages_in_venv(venv_path, packages, mirror_url="https://mirrors.aliyun.com/pypi/simple"):
    """
    Install specified packages in the given virtual environment.
    
    Parameters
    ----------
    venv_path : str
        Path to the virtual environment.
    packages : list
        List of packages to install.
    mirror_url : str, optional
        The mirror URL to use for package installation (default is aliyun mirror).
        
    Returns
    -------
    bool
        True if installation was successful, False otherwise.
    """
    if not os.path.exists(venv_path):
        logging.error(f"Virtual environment not found at {venv_path}")
        return False

    command = f"{venv_path}/bin/python -m pip install " + " ".join(packages) + f" -i {mirror_url}"
    try:
        logging.info(f"Installing packages: {', '.join(packages)} for virtual environment at {venv_path}...")
        subprocess.run(command, shell=True, check=True)
        logging.info(f"Successfully installed packages for {venv_path}.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install packages for {venv_path}: {e}")
        return False

def process_repositories(json_path):
    """
    Process each project in the JSON file and install required packages for each virtual environment.
    
    Parameters
    ----------
    json_path : str
        Path to the JSON file containing repository and virtual environment data.
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        logging.error(f"JSON file not found: {json_path}")
        return
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON file: {json_path}")
        return

    # Iterate over each repository and project
    for repo_name, projects in data.items():
        for project in projects:
            venv_path = project.get('venv_path')
            if not venv_path:
                logging.warning(f"Missing 'venv_path' for project {repo_name}. Skipping.")
                continue

            packages = ["cirron", "psutil"]
            # Install packages
            success = install_packages_in_venv(venv_path, packages)
            if success:
                logging.info(f"Packages successfully installed for repository: {repo_name}")
            else:
                logging.error(f"Failed to install packages for repository: {repo_name}")

# ========== Example Usage ==========
if __name__ == "__main__":
    json_path = 'data/repoexec_test_python.json'  # JSON file path
    process_repositories(json_path)
