import os
import discord
import requests
import xmltodict
import datetime
import threading
import asyncio
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime, timedelta

# -------- Variables --------

#Stores the time when the server first started up. Used in the !about command
aboutTime = datetime.now()

#API key retrevial from enviroment variable. Uses the python-dotenv library
load_dotenv()
API_KEY = os.getenv("API_KEY")
ABSTRACT_API_KEY = os.getenv("ABSTRACT_API_KEY")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
OUTSIDE_PORT = os.getenv("OUTSIDE_PORT")

# Get steam info in XML format
STEAM_URL="https://steamcommunity.com/id/Henry1981?xml=1"

# -------- IP Grabber --------

# Initialize Flask app
app = Flask(__name__)

def send_ip_to_discord(ip, response):
    
    channel = bot.get_channel(int(DISCORD_CHANNEL_ID))
    if channel:
        # Use the bot's API to send the message
        asyncio.run_coroutine_threadsafe(
            channel.send(f"New visitor IP: `{ip}` \n {response.json()["City"]},{response.json()["Region"]},{response.json()["Country"]}"),
            bot.loop
        )
    else:
        print("Channel not found. Is the bot connected?")

@app.route("/", methods=["GET"])
def get_ip():
    forwarded = request.headers.get('X-Forwarded-For', request.remote_addr)
    ip = forwarded.split(',')[0].strip()
    response = requests.get(f"https://ip-intelligence.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&ip_address=" + ip)
    send_ip_to_discord(ip, response)
    return jsonify({"ip": ip})

def run_flask():
    app.run(host='0.0.0.0', port=OUTSIDE_PORT)

# -------- XML Parsing --------

def parse_xml_from_url_to_dict(STEAM_URL):
    """
    Fetches an XML file from a given URL and parses it into a Python dictionary.

    Args:
        url (str): The URL of the XML file.

    Returns:
        dict: A dictionary representation of the XML file, or None if an error occurs.
    """
    try:
        # Fetch the XML content from the URL
        response = requests.get(STEAM_URL)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        # Get the XML content as bytes or text
        xml_content = response.content # Use .content for bytes, or .text for string if encoding is handled

        # Parse the XML content into a dictionary
        # xmltodict.parse handles the conversion
        my_dict = xmltodict.parse(xml_content)
        return my_dict

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return None

# Example usage:
# Replace with your actual XML file URL
xml_url = STEAM_URL # Example URL

parsed_data = parse_xml_from_url_to_dict(xml_url)

if parsed_data:
    print("Successfully parsed XML into dictionary:")
    print(parsed_data)
else:
    print("Failed to parse XML from URL.")

# -------- Discord Bot --------

intents = discord.Intents.all()

hostname="localhost"
bot = commands.Bot(command_prefix='!',intents=intents)

corpobs = requests.get("https://corporatebs-generator.sameerkumar.website/")

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name=corpobs.json()["phrase"]))

@discord.ext.tasks.loop(minutes=1)
async def statuschange():
    await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name=corpobs.json()["phrase"]))

@bot.command()
async def about(ctx):
    await ctx.send('Synergizing Soy-Based Approaches to Suicide Mitigation Tactics Using Artificial Intelligence Since: ' + str(aboutTime))

@bot.command()
async def ukys(ctx):
    
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.CustomActivity(name=corpobs.json()["phrase"]))
    await ctx.send('fuck you then')

@bot.command()
async def steam(ctx):
    embed = discord.Embed(title="Henry's VRChat Stats",
                      description=f"Status: `{parsed_data["profile"]["stateMessage"]}`",
                      colour=0xf50000)

    embed.set_author(name="SteamAPI")

    embed.add_field(name=parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][0]["gameName"],
                    value=f"Hours Played: {parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][0]["hoursPlayed"]}\nHours on Record: {parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][0]["hoursOnRecord"]}",
                    inline=False)
    
    embed.add_field(name=parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][1]["gameName"],
                    value=f"Hours Played: {parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][1]["hoursPlayed"]}\nHours on Record: {parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][1]["hoursOnRecord"]}",
                    inline=False)
    
    embed.add_field(name=parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][2]["gameName"],
                    value=f"Hours Played: {parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][2]["hoursPlayed"]}\nHours on Record: {parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][2]["hoursOnRecord"]}",
                    inline=False)
    
    embed.add_field(name=parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][3]["gameName"],
                    value=f"Hours Played: {parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][3]["hoursPlayed"]}\nHours on Record: {parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][3]["hoursOnRecord"]}",
                    inline=False)

    embed.set_image(url=parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][0]["gameLogo"])

    embed.set_thumbnail(url=parsed_data["profile"]["avatarIcon"])

    embed.set_footer(text="FreakBotAI")

    await ctx.send(embed=embed)

@bot.command()
async def goon(ctx):
  await ctx.send('GoonTech(TM) is a leading provider of innovative solutions for the modern world. Our mission is to empower individuals and organizations with cutting-edge technology that enhances productivity, creativity, and connectivity. From AI-driven applications to advanced robotics, GoonTech(TM) is at the forefront of technological advancement, delivering products and services that redefine the boundaries of what is possible. Join us in shaping the future with GoonTech(TM), where innovation meets excellence. (that was what the inline autocomplete gave me in vs code lmao bruh)')

@bot.command()
async def vrchathours(ctx):
    channel = bot.get_channel(1393808557257789471)
    s=parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][0]["hoursOnRecord"]
    s = s.replace(",", "")
    await channel.send(s)
    a=datetime.now()
    await channel.send(int(a.strftime('%Y%m%d')))


@bot.command()
async def kys(ctx):
    await bot.change_presence(status=discord.Status.offline, activity=discord.Activity(type=discord.ActivityType.listening, name="synergy"))
    await ctx.send('um what the flip man...... if youre happy then im happy i guess :((((((')
    await ctx.send('**you\'re')


# Run the bot
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run(API_KEY)

#i love freaky bot ai....
