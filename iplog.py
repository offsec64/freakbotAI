from flask import Flask, request, jsonify, render_template
import requests
import os
import json
import datetime
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
OUTSIDE_PORT = os.getenv("OUTSIDE_PORT")
ABSTRACT_API_KEY = os.getenv("ABSTRACT_API_KEY")

app = Flask(__name__)

# Replace with your actual Discord bot token and channel ID
DISCORD_BOT_TOKEN = API_KEY
DISCORD_CHANNEL_ID = DISCORD_CHANNEL_ID

def send_ip_to_discord(ip, data):
    url = f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    current_time = datetime.now()

    embed = {
        "title": "New Visitor",
        "description": f"IP Address: `{ip}`",
        "color": 65280,  # green
        "Author": [
            {"name": "Abstract IP Intelligence", "icon_url": "https://cdn.prod.website-files.com/65166126ca18241731aa26b0/65390de624cb65770560dda5_FAV.png"}
        ],
        "fields": [
            {"name": "Approximate Location", "value": f"{data['location']['city']}, {data['location']['region']}, {data['location']['country']} {data['flag']['emoji']}", "inline": False},
            {"name": "Service Provider", "value": f"ISP: {data['company']['name']}\n"f"Domain: {data['company']['domain']}", "inline": False},
            {"name": "Timestamp", "value": current_time.strftime("%Y-%m-%d %H:%M:%S UTC"), "inline": False}
        ]
    }

    json_data = {"embeds": [embed]}

    response = requests.post(url, headers=headers, json=json_data)
    
    if response.status_code != 200 and response.status_code != 204:
        print("Failed to send message to Discord:", response.text)

# ---------- Flask Routes -----------

@app.route("/", methods=["GET"])
def render_page():
    return render_template("index.html")

@app.route("/reveal", methods=["POST"])
def reveal_ip():

    forwarded = request.headers.get('X-Forwarded-For', request.remote_addr)
    ip = forwarded.split(',')[0].strip()

    # Make a request to the Abstract API to get IP intelligence data and parse the response
    response = requests.get(f"https://ip-intelligence.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&ip_address=" + ip)
    data = json.loads(response.text)

    send_ip_to_discord(ip, data)

    #return response.json()  # Return the JSON response directly from the Abstract API
    return jsonify({"ip": ip})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=OUTSIDE_PORT)