import subprocess
import os

# ================== Git Repository Management ==================

def mark_repo_as_safe(repo_path):
    """
    Marks a repository as a safe Git directory.

    Args:
        repo_path (str): The absolute path to the repository.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        subprocess.run(
            ["git", "config", "--global", "--add", "safe.directory", repo_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"Repository '{repo_path}' marked as a safe directory.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to mark '{repo_path}' as safe: {e.stderr.decode().strip()}")
        return False

def switch_repo_to_sha(repo_path, sha):
    """
    Switches the Git repository to a specified SHA commit.

    Args:
        repo_path (str): The absolute path to the repository.
        sha (str): The commit SHA to switch to.

    Returns:
        bool: True if the checkout is successful, False otherwise.
    """
    if not os.path.exists(repo_path):
        print(f"Repository path does not exist: {repo_path}")
        return False

    # Mark the repository as safe
    if not mark_repo_as_safe(repo_path):
        return False

    try:
        # Change to the repository directory
        os.chdir(repo_path)

        # Checkout the specified commit
        subprocess.run(
            ["git", "checkout", sha, "-f"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"Repository switched to SHA '{sha}' at '{repo_path}'.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Failed to switch repository '{repo_path}' to SHA '{sha}': {e.stderr.decode().strip()}")
        return False

    except Exception as e:
        print(f"Unexpected error while switching repository '{repo_path}': {str(e)}")
        return False

# ================== Main Execution ==================
if __name__ == "__main__":
    # Example usage (Replace with actual repository path and SHA)
    repo_path = "path/to/repository"  # Anonymous repository path
    commit_sha = "abcdef1234567890abcdef1234567890abcdef12"  # Example commit SHA

    switch_repo_to_sha(repo_path, commit_sha)
