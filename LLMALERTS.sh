#!/bin/bash
# Read Suricata IDS Alerts and use LLM to enrich the infor about the Alert

# Configuration
SURICATA_LOG="/var/log/suricata/eve.json"  # Path to Suricata logs in Ubuntu 24
LLAMA_API_URL="https://api.llama.com/v1/insight"  # Replace with actual Llama API URL ?????
LLAMA_API_KEY="api_key_here"  # 
OUTPUT_JSON_FILE="suricata_insight_results.json"  # Output JSON file
OUTPUT_HTML_FILE="suricata_insight_results.html"  # Output HTML file

# Function to get the latest alert from Suricata logs
get_latest_alert() {
    tail -n 1 "$SURICATA_LOG" | jq -r '. | select(.event_type == "alert") | {alert: .alert, src_ip: .src_ip, dest_ip: .dest_ip, file: .file}'
}

# Function to query Llama LLM for insights
get_insight() {
    local file_info="$1"
    response=$(curl -s -X POST "$LLAMA_API_URL" \
        -H "Authorization: Bearer $LLAMA_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"file_info\": $file_info}")

    echo "$response" | jq -r '.insight'
}

# Main script execution
latest_alert=$(get_latest_alert)

if [ -z "$latest_alert" ]; then
    echo "No new alerts found."
    exit 0
fi

echo "Latest Alert: $latest_alert"

# Get insights from Llama LLM
insight=$(get_insight "$latest_alert")

# Create a JSON object to save results
result_json=$(jq -n --arg alert "$latest_alert" --arg insight "$insight" '{
    latest_alert: $alert | fromjson,
    llama_insight: $insight
}')

# Save the results to a JSON file
echo "$result_json" > "$OUTPUT_JSON_FILE"
echo "Results saved to $OUTPUT_JSON_FILE"

# Create an HTML file to save results
{
    echo "<!DOCTYPE html>"
    echo "<html lang='en'>"
    echo "<head>"
    echo "    <meta charset='UTF-8'>"
    echo "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>"
    echo "    <title>Suricata Insight Results</title>"
    echo "    <style>"
    echo "        body { font-family: Arial, sans-serif; margin: 20px; }"
    echo "        h1 { color: #333; }"
    echo "        pre { background: #f4f4f4; padding: 10px; border-radius: 5px; }"
    echo "    </style>"
    echo "</head>"
    echo "<body>"
    echo "    <h1>Suricata Insight Results</h1>"
    echo "    <h2>Latest Alert</h2>"
    echo "    <pre>$(echo "$latest_alert" | jq .)</pre>"
    echo "    <h2>Llama LLM Insight</h2>"
    echo "    <pre>$insight</pre>"
    echo "</body>"
    echo "</html>"
} > "$OUTPUT_HTML_FILE"

echo "Results saved to $OUTPUT_HTML_FILE"
