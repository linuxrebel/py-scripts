#!/usr/bin/python

import requests
import sys

verbose = sys.argv[1] if len(sys.argv) > 1 else "z"

# GitLab's status page is hosted on status.io (not Atlassian Statuspage).
# The public API endpoint uses the page ID found in the status page source.
PAGE_ID = '5b36dc6502d06804c08349f7'


def get_gitlab_status_components():
    url = f'https://status.io/1.0/status/{PAGE_ID}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        result = data.get('result', {})
        overall = result.get('status_overall', {})
        components = result.get('status', [])

        non_operational_components = []
        for component in components:
            name = component['name']
            status = component['status']
            if status.lower() != "operational":
                non_operational_components.append((name, status))

        if verbose == "-v":
            for component in components:
                name = component['name']
                status = component['status']
                print(f"{name}\n   Status: {status}\n")
        elif non_operational_components:
            for name, status in non_operational_components:
                print(f"Component: {name}, Status: {status}")
        else:
            print(f"Status: {overall.get('status', 'All Systems Operational')}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except KeyError:
        print("Error parsing data. API response might have changed.")


if __name__ == "__main__":
    get_gitlab_status_components()
