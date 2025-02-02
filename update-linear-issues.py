from cmath import log
import requests
import sys
import re

linear_token = sys.argv[1]

url = 'https://api.linear.app/graphql'
headers = {'Authorization': linear_token,
           'Content-Type': 'application/json'}

def get_status_id(state_name):
    query = """
    query WorkflowStates($filter: WorkflowStateFilter) {
        workflowStates(filter: $filter) {
            nodes {
                id
            }
        }
    }
    """
    variables = {
        "filter": {
            "name": {
                "eqIgnoreCase": state_name
            }
        }
    }
    payload = {'query': query, 'variables': variables}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    status_id = response.json()['data']['workflowStates']['nodes'][0]['id']
    
    return status_id;


def create_label(team_id, label_name):
    query = """
    mutation IssueLabelCreate($input: IssueLabelCreateInput!) {
        issueLabelCreate(input: $input) {
            success
            issueLabel {
                id
            }
        }
    }
    """
    variables = {'input': {'name': label_name, 'color': '#E2E2E2', 'description': 'Generated by GitHub action', 'teamId': team_id}}
    payload = {'query': query, 'variables': variables}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    success = response.json()['data']['issueLabelCreate']['success']
    id = response.json()['data']['issueLabelCreate']['issueLabel']['id']

    if success:
        print('Created new label "' + label_name + '"')
        return id
    else:
        print('Unable to create new label "' + label_name + '"')
        return None


def get_label_id(team_id, label_name):
    query = """
    query LabelsByTeam ($teamId: ID) {
        issueLabels(filter: {team: {id: {eq: $teamId}}}) {
            nodes {
                id,
                name
            }
        }
    }
    """
    variables = {'teamId': team_id}
    payload = {'query': query, 'variables': variables}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    labels = response.json()['data']['issueLabels']['nodes']
    matched_label = list(filter(lambda x: x['name'] == label_name, labels))

    if len(matched_label) == 0:
        return create_label(team_id, label_name)
    else:
        return matched_label[0]['id']


def set_labels(issue_id, label_ids):
    query = """
    mutation IssueUpdate ($issueId: String!, $labelIds: [String!])  {
        issueUpdate(
            id: $issueId,
            input: {
                labelIds: $labelIds
            }
        ) {
            success
            issue {
                id
            }
        }
    }
    """
    variables = {'labelIds': label_ids, 'issueId': issue_id}
    payload = {'query': query, 'variables': variables}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    success = response.json()['data']['issueUpdate']['success']
    
    return success


def label_issue(issue, label_name):
    issue_id = issue['id']
    team_id = issue['team']['id']

    label_ids = list(map(lambda label: label['id'], issue['labels']['nodes']))
    new_label_id = get_label_id(team_id, label_name)

    if new_label_id is None:
        print('No matching label found!')
        return None

    label_ids.append(new_label_id)
    label_ids = list(set(label_ids))

    success = set_labels(issue_id, label_ids)
    if success:
        print('Added label "' + label_name + '" to issue with title "' + issue['title'] + '"')
    else:
        print('Unable to add label "' + label_name + '" to issue with title "' + issue['title'] + '"')
    
    return success

def batch_move_issues(issue_ids, status_name):
    status_id = get_status_id(status_name);

    query = """
    mutation IssueBatchUpdate($issueBatchUpdateInput: IssueUpdateInput!, $ids: [UUID!]!) {
        issueBatchUpdate(input: $issueBatchUpdateInput, ids: $ids) {
            success
            issues {
                id
            }
        }
    }
    """
    variables = {
        "ids": issue_ids,
        "issueBatchUpdateInput": {
            "stateId": status_id
        }
    }
    payload = {'query': query, 'variables': variables}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    success = response.json()['data']['issueBatchUpdate']['success']
    issueCount = len(response.json()['data']['issueBatchUpdate']['issues'])

    if success:
        print('Moved "' + str(issueCount) + '" issues to  status with name "' + status_name + '"')
    else:
        print('Unable to move "' + str(issueCount) + '" issues to status with name "' + status_name + '"')

    return success


def get_issues(status_name):
    query = """
    query Issues($filter: IssueFilter) {
      issues(filter: $filter) {
        nodes {
          id
          title
          team {
            id
          }
          labels {
            nodes {
              id
              name
            }
          }
        }
      }
    }
    """
    variables = {
        "filter": {
            "state": {
                "name": {
                    "eqIgnoreCase": status_name
                }
            }
        }
    }
    payload = {'query': query, 'variables': variables}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    issues = response.json()['data']['issues']['nodes']
    
    return issues

def label_issues(issues, label_name):
    count = 0
    for issue in issues:
        success = label_issue(issue, label_name)
        if success:
            count = count+1

    print('Added label "' + label_name + '" to ' + str(count) + ' issues')


if __name__ == '__main__':
    try:
        from_status_name = sys.argv[2]
        to_status_name = sys.argv[3]
        label_name = sys.argv[4]

        issues = get_issues(from_status_name)
        issue_ids = list(map(lambda issue: issue['id'], issues))

        if(len(issue_ids) == 0):
            print('No issues found with status "' + from_status_name + '"')

            sys.exit()

        batch_move_issues(issue_ids, to_status_name)
        label_issues(issues, label_name)

    except requests.HTTPError as e:
        print("API response: {}".format(e.response.text), flush=True)
        raise
