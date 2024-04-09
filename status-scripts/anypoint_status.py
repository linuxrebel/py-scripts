#!/usr/bin/python

import requests
from bs4 import BeautifulSoup
import sys

# The URL of the site to scrape
url = 'https://status.mulesoft.com'

# find out if a -v argument was given
verbose = sys.argv[1] if len(sys.argv) > 1 else "z"

# Send a GET request to the URL
response = requests.get(url)

# Parse the HTML content of the page with BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Find all div elements with a 'data-component-id' attribute
components = soup.find_all('div', attrs={'data-component-id': True})
all_operational = "True"

# Iterate over each component and print the name and status in a single line
for component in components:
    name_span = component.find('span', class_='name')
    status_span = component.find('span', class_='component-status')
    name = name_span.text.strip() if name_span else 'No Name'
    status = status_span.text.strip() if status_span else 'No Status'
    if status.lower() != "operational" or verbose == "-v" :
        all_operational = "False"
        print(f'{name}: {status}')

if all_operational == "True" :
    print("All systems at Anypoint are Green")

# Add a newline at the end of the printout
print()

