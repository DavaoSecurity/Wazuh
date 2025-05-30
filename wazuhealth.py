# replace 'https://your-wazuh-server.com', 'your-username', and 'your-password'with your actual Wazuh server URL, username, and password.
# Authenticates to the Wazuh API to get a token. Uses the token to run the health test on the Wazuh server.
# Saves the health test results to a JSON file in the Downloads folder.
# The verify=False parameter in the requestscalls is used to disable SSL verification. 
# This is not recommended for production environments due to security risks. 
# If your Wazuh server has a valid SSL certificate, you should removeTrueto ensure the connection is secure.
# The health test results Wazuh server status Database connection status File integrity monitoring status Rootcheck status and
# System audit status plus Other system and security

import requests
import json
import os

# Wazuh API credentials and URL
wazuh_url = 'https://your-wazuh-server.com'
wazuh_username = 'your-username'
wazuh_password = 'your-password'

# Authenticate to get the token
auth_url = f'{wazuh_url}/api/v1/authenticate'
headers = {'Content-Type': 'application/json'}
data = {'username': wazuh_username, 'password': wazuh_password}

response = requests.post(auth_url, headers=headers, data=json.dumps(data), verify=False)

if response.status_code == 200:
    token = response.json()['data']['token']
    # Run the health test
    health_test_url = f'{wazuh_url}/api/v1/manager/healthcheck'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    response = requests.get(health_test_url, headers=headers, verify=False)

    if response.status_code == 200:
        health_test_results = response.json()['data']
        # Get the path to the Downloads folder
        downloads_folder = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads')
        file_name = 'wazuh_health_test_results.json'
        file_path = os.path.join(downloads_folder, file_name)

        # Save the health test results to a JSON file
        with open(file_path, 'w') as file:
            json.dump(health_test_results, file, indent=4)

        print(f"Health test results saved to {file_path}")
    else:
        print(f"Failed to run health test. Status code: {response.status_code}")
else:
    print(f"Authentication failed. Status code: {response.status_code}")
