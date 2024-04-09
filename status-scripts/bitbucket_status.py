import requests
import sys

if len(sys.argv) > 1:
  verbose = sys.argv[1]
else:
  verbose = "z"

def get_github_status_components():
    url = 'https://bitbucket.status.atlassian.com/api/v2/summary.json'

    try:
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
        else:
          if non_operational_components:
              for component in non_operational_components:
                  name, status = component
                  print(f"Component: {name}, Status: {status}")
          else:
              overall_status_description = data['status']['description']
              print(f"Status: {overall_status_description}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except KeyError:
        print("Error parsing data. API response might have changed.")

if __name__ == "__main__":
    get_github_status_components()
