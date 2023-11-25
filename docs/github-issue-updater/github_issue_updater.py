
import json
import requests
import pandas as pd

# Set your parameters here
GITHUB_TOKEN = 'token'
REPO_OWNER = 'gshiva'
REPO_NAME = 'pygptcourse'

# Headers for authorization and to ensure the use of the API v3
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}

def list_issues():
    """ List all issues from the repository """
    issues_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'
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
    """ Update the issue with a new body """
    issue_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}'
    data = {
        'body': new_body
    }
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

# Load the updated requirements from the CSV file
csv_file_path = 'github_requirements_updated_specific_req2.csv'
requirements_df = pd.read_csv(csv_file_path)
requirements_dict = requirements_df.set_index('Title')['Body'].to_dict()

print("Starting the program")
issues = list_issues()

for issue in issues:
    title = issue['title']
    body = issue['body']

    # Check if the title is in the requirements dictionary
    if title in requirements_dict:
        new_body = requirements_dict[title]
        update_issue(issue['number'], new_body)
