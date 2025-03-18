import os
import shutil
import logging

# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def copy_file_to_directories(source_file, target_directory):
    """
    Copies a source file to each directory within the target directory.

    Parameters
    ----------
    source_file : str
        Path to the source file to copy.
    target_directory : str
        Path to the target directory containing subdirectories.

    Returns
    -------
    None
    """
    # Check if source file exists
    if not os.path.isfile(source_file):
        logging.error(f"Source file '{source_file}' does not exist.")
        return

    # Check if target directory exists
    if not os.path.isdir(target_directory):
        logging.error(f"Target directory '{target_directory}' does not exist.")
        return

    # Iterate through the directories in the target directory
    for entry in os.listdir(target_directory):
        target_path = os.path.join(target_directory, entry)
        
        # Check if the entry is a directory
        if os.path.isdir(target_path):
            try:
                # Copy the file to each subdirectory
                shutil.copy(source_file, target_path)
                logging.info(f"Successfully copied {source_file} to {target_path}")
            except PermissionError as e:
                logging.error(f"Permission denied while copying {source_file} to {target_path}: {e}")
            except Exception as e:
                logging.error(f"Error occurred while copying {source_file} to {target_path}: {e}")
        else:
            logging.warning(f"Skipping non-directory entry: {target_path}")

def copy_symlink(source_file, target_directory):
    """
    Creates a symbolic link for the source file in the target directory.

    Parameters
    ----------
    source_file : str
        Path to the source file to link.
    target_directory : str
        Path to the target directory to create the symlink in.

    Returns
    -------
    None
    """
    try:
        symlink_target = os.path.join(target_directory, os.path.basename(source_file))
        os.symlink(source_file, symlink_target)
        logging.info(f"Successfully created symlink for {source_file} at {symlink_target}")
    except FileExistsError:
        logging.warning(f"Symlink for {source_file} already exists in {target_directory}")
    except Exception as e:
        logging.error(f"Error creating symlink for {source_file} in {target_directory}: {e}")

# ========== Example Usage ==========
if __name__ == "__main__":
    # Define the source file and target directory
    source_file = 'data/conftest.py'
    target_directory = 'repo_python'

    # Copy the source file to each directory in the target directory
    copy_file_to_directories(source_file, target_directory)

    # Optionally, create a symlink instead of copying (if needed)
    # copy_symlink(source_file, target_directory)
