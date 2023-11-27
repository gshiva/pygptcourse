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


def list_issues():
    """List all issues from the repository with pagination."""
    issues = []
    page = 1
    while True:
        issues_url = (
            f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues?page={page}"
        )
        response = requests.get(issues_url, headers=headers)
        if response.status_code == 200:
            try:
                page_issues = response.json()
                if not page_issues:
                    break  # No more issues, exit the loop
                issues.extend(page_issues)
                page += 1
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return []  # Return an empty list on error
            except Exception as e:
                print(f"An error occurred: {e}")
                return []  # Return an empty list on error
        else:
            print(f"Error fetching issues: {response.status_code}")
            print(response.text)
            return []  # Return an empty list on error

    return issues


def update_issue(issue_number, new_title, new_body):
    """Update the issue with a new body"""
    issue_url = (
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}"
    )
    data = {"title": new_title, "body": new_body}
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
    print("Starting the program")
    issues = list_issues()

    print(f"Number of issues: {len(issues)}")

    for issue in issues:
        title = issue["title"]
        body = issue["body"]

        new_title = title
        new_body = body

        # Check if the title is in the requirements dictionary
        if "missile" in title:
            new_title = title.replace("missile", "T-Shirt")

        if "missile" in body:
            new_body = body.replace("missile", "T-Shirt")

        if title != new_title or body != new_body:
            update_issue(issue["number"], new_title, new_body)


if __name__ == "__main__":
    main()
