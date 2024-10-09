import requests
from datetime import datetime


def get_last_update(username):
    url = f'https://api.github.com/users/{username}/events/public'
    headers = {'Accept': 'application/vnd.github.v3+json'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        events = response.json()
        if events:
            # Sort events by created_at in descending order
            sorted_events = sorted(events, key=lambda x: x['created_at'], reverse=True)

            for event in sorted_events:
                # Check if the event type is one that represents a public activity
                if event['type'] in [
                    'PushEvent',
                    'PullRequestEvent',
                    'IssuesEvent',
                    'CreateEvent',
                ]:
                    return event['created_at']

    elif response.status_code == 404:
        print(f"User {username} not found")
    else:
        print(f"Error: {response.status_code}")

    return None
