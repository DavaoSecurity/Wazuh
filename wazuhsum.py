# 'https://your-wazuh-server.com', 'your-username', and 'your-password' with your actual Wazuh server URL, username, and password.
# Authenticates to the Wazuh API to get a token. Uses the token to get a list of all agents. 
# Saves each Agent summary to a JSON file in the Downloads folder, with a file name based on the agent ID.
# Creates an HTML table with the summary information.
# Saves the HTML table to a file in the Downloads folder, with a file name based on the agent ID
# Note: The verify=False parameter in the requests calls is used to disable SSL verification. This is not recommended for production
# environments due to security risks. IfTrueto ensure the connection is secure.

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
    # Get all agents
    agents_url = f'{wazuh_url}/api/v1/agents'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    response = requests.get(agents_url, headers=headers, verify=False)

    if response.status_code == 200:
        agents = response.json()['data']['affected_items']
        # Get the path to the Downloads folder
        downloads_folder = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads')

        for agent in agents:
            agent_id = agent['id']
            # Get the summary for each agent
            summary_url = f'{wazuh_url}/api/v1/agents/{agent_id}/summary'
            response = requests.get(summary_url, headers=headers, verify=False)

            if response.status_code == 200:
                summary = response.json()['data']['affected_items'][0]
                # Create a file name based on the agent ID
                json_file_name = f'agent_{agent_id}_summary.json'
                html_file_name = f'agent_{agent_id}_summary.html'
                json_file_path = os.path.join(downloads_folder, json_file_name)
                html_file_path = os.path.join(downloads_folder, html_file_name)

                # Save the summary to a JSON file
                with open(json_file_path, 'w') as file:
                    json.dump(summary, file, indent=4)

                # Create the HTML content
                html_content = f"""
                <html>
                <body>
                <h1>Agent {agent_id} Summary</h1>
                <table border="1">
                <tr>
                <th>Name</th>
                <th>Value</th>
                </tr>
                """

                for key, value in summary.items():
                    html_content += f"""
                    <tr>
                    <td>{key}</td>
                    <td>{value}</td>
                    </tr>
                    """

                html_content += """
                </table>
                </body>
                </html>
                """

                # Save the summary to an HTML file
                with open(html_file_path, 'w') as file:
                    file.write(html_content)

                print(f"Summary for agent {agent_id} saved to {json_file_path} and {html_file_path}")
            else:
                print(f"Failed to get summary for agent {agent_id}. Status code: {response.status_code}")
    else:
        print(f"Failed to get agents. Status code: {response.status_code}")
else:
    print(f"Authentication failed. Status code: {response.status_code}")
