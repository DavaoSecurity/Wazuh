import json
import subprocess
import requests

# Configuration
SURICATA_LOG = "/var/log/suricata/eve.json"  # Path to Suricata logs
LLAMA_API_URL = "https://api.llama.com/v1/insight"  # Replace with actual Llama API URL
LLAMA_API_KEY = "your_api_key_here"  # Replace with your Llama API key
OUTPUT_JSON_FILE = "suricata_insight_results.json"  # Output JSON file
OUTPUT_HTML_FILE = "suricata_insight_results.html"  # Output HTML file

def get_latest_alert():
    """Get the latest alert from Suricata logs."""
    try:
        # Use tail to get the last line of the log file
        result = subprocess.run(['tail', '-n', '1', SURICATA_LOG], capture_output=True, text=True)
        # Parse the JSON output
        alert = json.loads(result.stdout)
        if alert.get("event_type") == "alert":
            return {
                "alert": alert.get("alert"),
                "src_ip": alert.get("src_ip"),
                "dest_ip": alert.get("dest_ip"),
                "file": alert.get("file")
            }
    except Exception as e:
        print(f"Error reading Suricata logs: {e}")
    return None

def get_insight(file_info):
    """Query Llama LLM for insights."""
    headers = {
        "Authorization": f"Bearer {LLAMA_API_KEY}",
        "Content-Type": "application/json"
    }
    data = json.dumps({"file_info": file_info})
    response = requests.post(LLAMA_API_URL, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json().get("insight")
    else:
        print(f"Error querying Llama API: {response.status_code} - {response.text}")
        return None

def save_json(output_file, latest_alert, insight):
    """Save results to a JSON file."""
    result_json = {
        "latest_alert": latest_alert,
        "llama_insight": insight
    }
    with open(output_file, 'w') as json_file:
        json.dump(result_json, json_file, indent=4)
    print(f"Results saved to {output_file}")

def save_html(output_file, latest_alert, insight):
    """Save results to an HTML file."""
    with open(output_file, 'w') as html_file:
        html_content = f"""<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Suricata Insight Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Suricata Insight Results</h1>
    <h2>Latest Alert</h2>
    <pre>{json.dumps(latest_alert, indent=4)}</pre>
    <h2>Llama LLM Insight</h2>
    <pre>{insight}</pre>
</body>
</html>"""
        html_file.write(html_content)
    print(f"Results saved to {output_file}")

def main():
    latest_alert = get_latest_alert()
    
    if latest_alert is None:
        print("No new alerts found.")
        return

    print("Latest Alert:", latest_alert)

    insight = get_insight(latest_alert)

    if insight is None:
        print("No insights received from Llama LLM.")
        return

    save_json(OUTPUT_JSON_FILE, latest_alert, insight)
    save_html(OUTPUT_HTML_FILE, latest_alert, insight)

if __name__ == "__main__":
    main()
