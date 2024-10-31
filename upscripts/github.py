import logging
from datetime import datetime

import requests

from pyscripts import log_config

logger = log_config.setup_logging()


def get_last_update(username):
    logger.info('Starting update github service...')
    url = f'https://api.github.com/users/{username}/events/public'
    headers = {'Accept': 'application/vnd.github.v3+json'}
    response = requests.get(url, headers=headers)

    result = {
        'raw_response': None,
        'raw_datetime': None,
        'formatted_datetime': None,
        'update_desc': None,
        'update_moment': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

    if response.status_code == 200:
        events = response.json()
        result['raw_response'] = events
        logger.debug(f'Fetched {len(events)} events from GitHub for {username}')
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
                    'ForkEvent',
                ]:
                    result['raw_datetime'] = event['created_at']
                    result['formatted_datetime'] = (
                        datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                        .strftime("%Y-%m-%d %H:%M:%S")
                        .lower()
                    )
                    result['update_desc'] = (
                        f"{event['type']} at repo {event['repo']['name']} at {event['repo']['url']}"
                    )
                    break

    elif response.status_code == 404:
        logger.error(f'404 when fetching updates from GitHub for {username}')
    else:
        logger.error(
            f'Error when fetching updates from GitHub for {username}: {response.status_code}'
        )

    logger.info('Finishing update github service...')
    return result
