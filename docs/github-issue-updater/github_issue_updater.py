import argparse
import json

import pandas as pd
import requests

# Constants for GitHub repository
REPO_OWNER = "gshiva"
REPO_NAME = "pygptcourse"
GITHUB_TOKEN = "PAT token"  # Personal Access Token

# Headers for authorization and to ensure the use of the API v3
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def list_issues():
    """List all issues from the repository"""
    issues_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    response = requests.get(issues_url, headers=headers)
    if response.status_code == 200:
        try:
            issues = response.json()
            return issues
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return []
    else:
        print(f"Error fetching issues: {response.status_code}")
        print(response.text)
        return []  # Return an empty list on error


def update_issue(issue_number, new_body):
    """Update the issue with a new body"""
    issue_url = (
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}"
    )
    data = {"body": new_body}
    response = requests.patch(issue_url, headers=headers, json=data)
    if response.status_code == 200:
        try:
            updated_issue = response.json()
            print(f"Issue updated: {updated_issue.get('title')}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    else:
        print(f"Error updating issue: {response.status_code}")
        print(response.text)


def read_csv(file_path):
    """Reads a CSV file and returns its content."""
    with open(file_path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        return list(reader)


def main():
    # Setting up argument parsing
    parser = argparse.ArgumentParser(
        description="Read a CSV file and create GitHub issues."
    )
    parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    # Parsing arguments
    args = parser.parse_args()  # Load the updated requirements from the CSV file
    # Reading the CSV file
    requirements_df = pd.read_csv(args.csv_file)
    requirements_dict = requirements_df.set_index("Title")["Body"].to_dict()

    print("Starting the program")
    issues = list_issues()

    for issue in issues:
        title = issue["title"]

        # Check if the title is in the requirements dictionary
        if title in requirements_dict:
            new_body = requirements_dict[title]
            update_issue(issue["number"], new_body)


if __name__ == "__main__":
    main()
