#!/usr/bin/python

import requests
from bs4 import BeautifulSoup
import sys

verbose = sys.argv[1] if len(sys.argv) > 1 else "z"


def get_mulesoft_status_components():
    url = 'https://status.mulesoft.com'

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        components = soup.find_all('div', attrs={'data-component-id': True})

        non_operational_components = []
        all_components = []
        for component in components:
            name_span = component.find('span', class_='name')
            status_span = component.find('span', class_='component-status')
            name = name_span.text.strip() if name_span else 'No Name'
            status = status_span.text.strip() if status_span else 'No Status'
            all_components.append((name, status))
            if status.lower() != "operational":
                non_operational_components.append((name, status))

        if verbose == "-v":
            for name, status in all_components:
                print(f"{name}\n   Status: {status}\n")
        elif non_operational_components:
            for name, status in non_operational_components:
                print(f"Component: {name}, Status: {status}")
        else:
            print("All systems at MuleSoft are Green")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")


if __name__ == "__main__":
    get_mulesoft_status_components()
