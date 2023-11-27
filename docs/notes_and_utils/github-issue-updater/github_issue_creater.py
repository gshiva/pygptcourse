import argparse
import csv
import json

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


def create_issue(title, body, labels, milestone):
    """Create a new issue with the given title, body, labels, and milestone"""
    issue_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"

    data = {"title": title, "body": body, "labels": labels, "milestone": milestone}
    response = requests.post(issue_url, headers=headers, json=data)
    if response.status_code == 201:
        try:
            issue = response.json()
            print(f"Issue created: {issue['html_url']}")
            return issue
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    else:
        print(f"Error creating issue: {response.status_code}")
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
    args = parser.parse_args()

    # Reading the CSV file
    csv_content = read_csv(args.csv_file)

    # Creating GitHub issues from CSV content
    for row in csv_content:
        # Title,Body,Labels,Milestone,Assignee,State
        title, body, labels, milestone, assignee, state = row
        labels = [label.strip() for label in labels.split(",")]
        create_issue(title, body, labels, milestone)


if __name__ == "__main__":
    main()
