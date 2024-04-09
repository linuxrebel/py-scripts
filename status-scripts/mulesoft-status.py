import requests
import sys

verbose = sys.argv[1] if len(sys.argv) > 1 else "z"

def get_github_status_components():
    url = 'https://status.mulesoft.com/'

    try:
        _extracted_from_get_github_status_components_5(url)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except KeyError:
        print("Error parsing data. API response might have changed.")


# TODO Rename this here and in `get_github_status_components`
def _extracted_from_get_github_status_components_5(url):
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    components_data = data['components'][:13]  # Get components 0 through 12

    non_operational_components = []
    for component in components_data:
        name = component['name']
        status = component['status']
        if status != "operational":
            non_operational_components.append((name, status))

    if verbose == "-v":
        for component in components_data:
            name = component['name']
            status = component['status']
            print(f"{name}\n   Status: {status}\n")
    elif non_operational_components:
        for component in non_operational_components:
            name, status = component
            print(f"Component: {name}, Status: {status}")
    else:
        overall_status_description = data['status']['description']
        print(f"Status: {overall_status_description}")

if __name__ == "__main__":
    get_github_status_components()
