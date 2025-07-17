import json
import os
import discord
import requests
import xmltodict
import datetime
import mysql.connector
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime, timedelta

# -------- Variables --------

#Stores the time when the server first started up. Used in the !about command
aboutTime = datetime.now()

#API key retrevial from enviroment variable. Uses the python-dotenv library
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")

# Get steam info in XML format
STEAM_URL="https://steamcommunity.com/id/Henry1981?xml=1"

# ------- Database Connection --------

result = None

mydb = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USERNAME,
    password=DB_PASSWORD,
    database="goontech"
)

if mydb.is_connected():
    print("Connected to the database successfully!")
    mycursor = mydb.cursor()

    # Selects the most recent entry from the steam_data table
    mycursor.execute("SELECT * FROM `steam_data` ORDER BY `timestamp` DESC LIMIT 1")
    result = mycursor.fetchall()

    if result:
        print("Most recent entry in steam_data:")
        for row in result:
            print(row[3] + " Hours @ " + row[4] + " UTC")  # Assuming the 4th and 5th columns are the relevant data
    else:
        print("No entries found in steam_data table.")

    mycursor.close()
    mydb.close()

else:
    print("Failed to connect to the database.")
    mydb.close()

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
    print("Successfully parsed Steam XML into dictionary!")
    #print(parsed_data)
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

#i want to make this eventually send the parsed data to a local LLM to have it generate a funny message about how much time has been spent on VRChat
@bot.command()
async def vrchathours(ctx):
    channel = bot.get_channel(1393808557257789471)
    for row in result:
        most_played_game = row[2]
        hours = row[3]
        timestamp = row[4]
        msg = f"Most recent {most_played_game} hours: {hours} Logged at {timestamp} UTC"

    # Ollama API endpoint
    url = "http://10.10.10.81:80/api/generate"

    # Request body
    data = {
        "model": "gemma3:12b",  # the model you pulled and want to use
        "prompt": f"You’re a sarcastic AI assistant who just saw this Steam user's playtime in a game: '{msg}'. Make a snarky one-liner about it. Be creative and savage.",
        "temperature": 1.9,        # High creativity
        "repeat_penalty": 1.8,     # Penalize repetition (1.0 = no penalty)
        "top_p": 0.8,           # Top-p sampling (0.0 = no top-p)
        "stream": False  # Set to True if you want streaming responses
    }

    llmResponse = requests.post(url, json=data)

    # Check for success
    if llmResponse.status_code == 200:
        print(llmResponse.json()["response"])
    else:
        print("Error:", llmResponse.status_code, llmResponse.text)

    await channel.send(f"**{msg}**")
    await channel.send(llmResponse.json()["response"])

# -------- Silly commands --------

@bot.command()
async def about(ctx):
    await ctx.send('Synergizing Soy-Based Approaches to Suicide Mitigation Tactics Using Artificial Intelligence Since: ' + str(aboutTime))

@bot.command()
async def goon(ctx):
  await ctx.send('GoonTech(TM) is a leading provider of innovative solutions for the modern world. Our mission is to empower individuals and organizations with cutting-edge technology that enhances productivity, creativity, and connectivity. From AI-driven applications to advanced robotics, GoonTech(TM) is at the forefront of technological advancement, delivering products and services that redefine the boundaries of what is possible. Join us in shaping the future with GoonTech(TM), where innovation meets excellence. (that was what the inline autocomplete gave me in vs code lmao bruh)')

@bot.command()
async def kys(ctx):
    await bot.change_presence(status=discord.Status.offline, activity=discord.Activity(type=discord.ActivityType.listening, name="synergy"))
    await ctx.send('um what the flip man...... if youre happy then im happy i guess :((((((')
    await ctx.send('**you\'re')

@bot.command()
async def ukys(ctx):
    
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.CustomActivity(name=corpobs.json()["phrase"]))
    await ctx.send('screw you then buddy')

# Runs the bot
if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)

#i love freaky bot ai....
#2025 goonsoft.dev
