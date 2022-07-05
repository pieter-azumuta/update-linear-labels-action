import requests
import sys
import re

linear_token = sys.argv[3]

url = 'https://api.linear.app/graphql'
headers = {'Authorization': linear_token,
           'Content-Type': 'application/json'}


def get_issue(team_key, issue_number):
    query = """
    query Issues($teamKey: String!, $issueNumber: Float) { 
        issues(filter: {team: {key: {eq: $teamKey}}, number: {eq: $issueNumber}}) {
            nodes {
                id,
                branchName,
                parent {
                    id
                },
                team {
                    id
                },
                labels {
                    nodes {
                        id
                    }
                }
            }
        }
    }
    """
    variables = {'teamKey': team_key, 'issueNumber': issue_number}
    payload = {'query': query, 'variables': variables}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    matched_issues = response.json()['data']['issues']['nodes']

    if len(matched_issues) == 0:
        return None
    else:
        return matched_issues[0]


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
        return None
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
    return None


def label_issue(branch_name, label_to_add):
    match = re.search("^(\w+)-(\d+)-.*$", branch_name)
    if match is None:
        print('Unable to infer issue code from branch name', flush=True)
        sys.exit(1)
    team_key = match.group(1).upper()
    issue_number = int(match.group(2))

    print("Inferred issue code='{}-{}' from branch='{}'".format(team_key,
          issue_number, branch_name), flush=True)

    issue = get_issue(team_key, issue_number)
    if issue is None:
        print('No matching issues found!', flush=True)
        sys.exit(1)

    issue_id = issue['id']
    if issue['parent']:
        parent_id = issue['parent']['id']
    else:
        parent_id = None

    team_id = issue['team']['id']
    label_ids = list(map(
        lambda x: x['id'], issue['labels']['nodes']))
    new_label_id = get_label_id(team_id, label_to_add)
    if new_label_id is None:
        print('No matching label found!')
        sys.exit(1)

    label_ids.append(new_label_id)
    label_ids = list(set(label_ids))

    set_labels(issue_id, label_ids)

    # We support only one level of nested issues for now.
    # Anything more would require writing a recursive query which is not worth it
    # unless we have use-cases for it.
    if parent_id:
        set_labels(parent_id, label_ids)


if __name__ == '__main__':
    try:
        label_issue(sys.argv[2], sys.argv[1])
    except requests.HTTPError as e:
        print("API response: {}".format(e.response.text), flush=True)
        raise

    print("All done!")
