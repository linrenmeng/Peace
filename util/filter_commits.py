import json
import re

# Define list of keywords related to performance optimization
keywords = [
    "performance", "optimize", "efficiency", "speed", "improve", "fast",
    "enhance", "accelerate", "boost", "reduce latency", "reduce time",
    "scale", "scaling"
]

def filter_commits_by_message(input_file, output_file):
    """
    Filters commit messages containing performance-related keywords and saves the results.
    
    Args:
        input_file (str): Path to the input JSON file containing merged commit data
        output_file (str): Path to save the filtered JSON output
    """
    filtered_data = []
    total_commits = 0
    retained_commits = 0
    total_infos = 0
    non_empty_infos = 0
    empty_infos = 0

    # Convert keywords to regular expression patterns
    # Using word boundaries and case-insensitive matching
    keyword_patterns = [re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE) for keyword in keywords]

    # Read merged JSON data
    with open(input_file, 'r') as file:
        merged_data = json.load(file)
    
    # Iterate through each repository's data
    for repo_data in merged_data:
        source_repo = repo_data["source_repo"]
        info_list = repo_data["info"]
        total_commits += len(info_list)
        total_infos += 1

        # Filter commit information that meets the criteria
        # Checks if any keyword pattern matches the commit message
        filtered_info = [
            commit for commit in info_list
            if any(pattern.search(commit.get("commit", {}).get("message", "")) for pattern in keyword_patterns)
        ]

        retained_commits += len(filtered_info)

        # Only keep repository data that contains qualifying commits
        if filtered_info:
            filtered_data.append({"source_repo": source_repo, "info": filtered_info})
            non_empty_infos += 1
        else:
            empty_infos += 1
    
    # Save filtered data to output file
    with open(output_file, 'w') as output:
        json.dump(filtered_data, output, indent=4)

    # Print statistical information
    deleted_commits = total_commits - retained_commits
    print(f"Total commits processed: {total_commits}")
    print(f"Commits retained: {retained_commits}")
    print(f"Commits deleted: {deleted_commits}")
    print(f"Total info entries processed: {total_infos}")
    print(f"Info entries with retained commits: {non_empty_infos}")
    print(f"Info entries with all commits deleted: {empty_infos}")

# Specify input and output files
input_file = 'python_merged_output.json'
output_file = 'python_filtered_commits.json'

# Execute the filtering operation
filter_commits_by_message(input_file, output_file)
