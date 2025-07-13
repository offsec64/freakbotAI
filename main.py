import os
import discord
import requests
import xmltodict
import datetime
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime, timedelta

#Stores the time when the server first started up. Used in the !about command
aboutTime = datetime.now()

#API key retrevial from enviroment variable. Uses the python-dotenv library
load_dotenv()
api_key = os.getenv("API_KEY")

# Get steam info in XML format
STEAM_URL="https://steamcommunity.com/id/Henry1981?xml=1"

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
                    value=f"hoursPlayed: {parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][0]["hoursPlayed"]}\nhoursOnRecord:{parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][0]["hoursOnRecord"]}",
                    inline=False)
    
    embed.add_field(name=parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][1]["gameName"],
                    value=f"hoursPlayed: {parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][1]["hoursPlayed"]}\nhoursOnRecord:{parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][1]["hoursOnRecord"]}",
                    inline=False)
    
    embed.add_field(name=parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][2]["gameName"],
                    value=f"hoursPlayed: {parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][2]["hoursPlayed"]}\nhoursOnRecord:{parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][2]["hoursOnRecord"]}",
                    inline=False)
    
    embed.add_field(name=parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][3]["gameName"],
                    value=f"hoursPlayed: {parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][3]["hoursPlayed"]}\nhoursOnRecord:{parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][3]["hoursOnRecord"]}",
                    inline=False)

    embed.set_image(url=parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][0]["gameLogo"])

    embed.set_thumbnail(url=parsed_data["profile"]["avatarIcon"])

    embed.set_footer(text="FreakBotAI")

    await ctx.send(embed=embed)

@bot.command()
async def goon(ctx):
  await ctx.send('MESSAGE TO SEND')

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
    
    
bot.run(api_key)

#i love freaky bot ai....
