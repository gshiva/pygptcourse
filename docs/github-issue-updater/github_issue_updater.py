import requests

# Set your parameters here
GITHUB_TOKEN = 'token'
REPO_OWNER = 'username or organization'
REPO_NAME = 'repo name'

# Headers for authorization and to ensure the use of the API v3
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}

def list_issues():
    """ List all issues from the repository """
    issues_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'
    response = requests.get(issues_url, headers=headers)
    response = requests.get(issues_url, headers=headers)
    if response.status_code == 200:
        try:
            issues = response.json()
            # Debug: print the type and content of the issues variable
            print(f"Received data type: {type(issues)}")
            print(f"Received data: {issues}")
            return issues
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return []
    else:
        print(f"Error fetching issues: {response.status_code}")
        print(response.text)
        return []  # Return an empty list on error

    return response.json()

def update_issue(issue_number, new_title, new_body, labels, milestone):
    """ Update the issue with a new title and body """
    issue_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}'
    data = {
        'title': new_title,
        'body': new_body,
        'labels': labels,
        'milestone': milestone
    }
    response = requests.post(issue_url, headers=headers, json=data)
    print(f"Response: {response}")
    if response.status_code == 200:
        try:
            issues = response.json()
            # Debug: print the type and content of the issues variable
            print(f"Received data type: {type(issues)}")
            print(f"Received data: {issues}")
            return issues
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return []
        return response.json()  # Parse JSON only if the response is OK
    else:
        print(f"Error fetching issues: {response.status_code}")
        print(response.text)
        return []  # Return an empty list on error

    return response.json()

print(f"Starting the program")
issues = list_issues()

for issue in issues:
    title = issue['title']
    body = issue['body']

    # Check if 'missile' is in the title or body
    if 'missile' in title.lower() or 'missile' in body.lower():
        new_title = title.replace('missile', 'T-shirt')
        new_body = body.replace('missile', 'T-shirt')
        update_issue(issue['number'], new_title, new_body, issue['labels'], issue['milestone'] )
