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
load_dotenv(override=True)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_GENERAL_CHANNEL = int(os.getenv("DISCORD_GENERAL_CHANNEL"))
DISCORD_ROUGEAI_CHANNEL = int(os.getenv("DISCORD_ROUGEAI_CHANNEL"))
DISCORD_STEAMHOURS_CHANNEL = int(os.getenv("DISCORD_STEAMHOURS_CHANNEL"))
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
OLLAMA_API_URL = str(os.getenv("OLLAMA_API_URL"))  # Ollama API endpoint. Replace with an env var at some point

# Get steam info in XML format
STEAM_URL="https://steamcommunity.com/id/Henry1981?xml=1"

# ------- Database Connection --------

databaseResult = None

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
    mycursor.execute("SELECT * FROM `steam_data` ORDER BY `timestamp` DESC LIMIT 2")
    databaseResult = mycursor.fetchall()

    if databaseResult:
        print("Most recent entry in steam_data:")
        for row in databaseResult:
            print(row[3] + " Hours @ " + row[4] + " UTC")
    else:
        print("No entries found in steam_data table.")

    mycursor.close()
    mydb.close()

else:
    print("Failed to connect to the database.")
    mydb.close()

   # -------- LLM Query Functions -------- 

system_prompt = "You are an AI assistant created by GoonSoft Technologies Corporation using their propriatary GoonTech API. " \
"For more background info: GoonSoft Technologies Corporation was founded in 2025 by the visionary Simon Wilch (CFO,CVO) and Jace Deshazer (CEO). " \
"The GoonTech API is the synergy of hardware and sofware powering the next gen AI experience known as the GoonTech Discord server" \
"Your name is FreakBotAI. Your task is to respond to user messages in a discord server named GoonTech. " \
"Do not include any disclaimers or warnings about AI responses. " \
"Just respond as if you were a human and don't be afraid to get a bit creative from time to time."

base_message = [
    {"role": "system", "content": system_prompt},
]   

# Queries the ollama API in chat mode
def llm_query_chat(prompt, model):

    # Ollama API chat query generation
    url = "http://" + OLLAMA_API_URL + "/api/chat"

    messages = base_message + [{"role": "user", "content": prompt}]  # Add user message to the chat history

    data = {
        "model": model,  # model to use 
        "messages": messages,
        "max_tokens": 2000,  # Maximum number of tokens in the response
        "temperature": 1.6,        # High creativity
        "repeat_penalty": 1.4,     # Penalize repetition (1.0 = no penalty)
        "top_p": 0.8,           # Top-p sampling (0.0 = no top-p)
        "stream": False  # Set to True if you want streaming responses
    }

    response = requests.post(url, json=data)

    # Handle the response
    if response.ok:
        print(response.json()["message"]["content"])
        return response.json()["message"]["content"]
    else:
        print("Error:", response.status_code, response.text)
        return "error :( see console for details"

# Queries the ollama API in single query mode
def llm_query_single(prompt, model):

    url = "http://" + OLLAMA_API_URL + "/api/generate"

    # Request body
    data = {
        "model": model,  # model to use 
        "prompt": str(prompt),
        "temperature": 1.9,        # High creativity
        "repeat_penalty": 1.8,     # Penalize repetition (1.0 = no penalty)
        "top_p": 0.8,           # Top-p sampling (0.0 = no top-p)
        "stream": False  # Set to True if you want streaming responses
    }

    llmResponse = requests.post(url, json=data)

    # Check for success
    if llmResponse.status_code == 200:
        print(llmResponse.json()["response"])
       #messages.append({"role": "assistant", "content": llmResponse.json()["response"]})  # Add assistant response to the chat history
    else:
        print("Error:", llmResponse.status_code, llmResponse.text)

    return llmResponse.json()["response"]

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

#Sends the most recent VRChat hours played to a locally hosted LLM API and posts the response to a Discord channel
@bot.command()
async def vrchathours(ctx):

    channel = bot.get_channel(DISCORD_STEAMHOURS_CHANNEL)  # Get the channel to send the message to

    async with ctx.typing():

        """
        for row in result:
            most_played_game = row[2]
            hours = row[3]
            timestamp = row[4]
            msg = f"Most recent {most_played_game} hours: {hours} Logged at {timestamp} UTC"
        """
        gameName = databaseResult[0][2]
        latestHours = int(databaseResult[0][3])
        previousHours = int(databaseResult[1][3])
        delta = latestHours - previousHours
        
        prompt = f"You’re a sarcastic AI assistant who just saw this Steam user's playtime in a game: '{latestHours} Hours in {gameName}'. Make a snarky one-liner about it. Be creative and savage. Please refer to this person as Henry-sama. Do not hold back"
        model = "dolphin3:8b"
        llmResponse = llm_query_single(prompt, model)

        # Send the message to the channel
        await channel.send(f"**Current Hours in '{gameName}': {latestHours}\nChange since yesterday: {delta} Hours**\n{llmResponse}")

@bot.event
async def on_message(message):
   
    if "<@1393782766746865774>" in message.content:

        async with message.channel.typing():
            prompt = message.content.replace("<@1393782766746865774>", "").strip()  # Remove the mention from the prompt
            model = "dolphin3:8b"
        
            llmResponse = llm_query_chat(prompt, model)
            paginator = commands.Paginator()

            
            for line in llmResponse.splitlines():
                paginator.add_line(line)
            
            for page in paginator.pages:
                await message.channel.send(page)
    else:
        # Process other messages normally
        await bot.process_commands(message)

# -------- Silly commands --------

@bot.command()
async def about(ctx):
    await ctx.send('Synergizing Soy-Based Approaches to Suicide Mitigation Tactics Using the Power of Artificial Intelligence Since: ' + str(aboutTime))

@bot.command()
async def goon(ctx):
   
   prompt = "Write a polished, professional company overview for a fictional technology brand called GoonTech™. Use corporate buzzwords and a visionary tone. The company should sound innovative, futuristic, and confident. Focus on areas like AI, robotics, connectivity, and productivity. Make it sound like something you’d read in a press release, investor deck, or tech product website. Keep it under 100 words."
   model = "gemma3:12b"
   llmResponse = llm_query_single(prompt, model)

   # await ctx.send('GoonTech(TM) is a leading provider of innovative solutions for the modern world. Our mission is to empower individuals and organizations with cutting-edge technology that enhances productivity, creativity, and connectivity. From AI-driven applications to advanced robotics, GoonTech(TM) is at the forefront of technological advancement, delivering products and services that redefine the boundaries of what is possible. Join us in shaping the future with GoonTech(TM), where innovation meets excellence. (that was what the inline autocomplete gave me in vs code lmao bruh)')
   await ctx.send(llmResponse)

@bot.command()
async def kys(ctx):

    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.CustomActivity(name="im sorry..."))
    await ctx.send('um what the flip man...... if youre happy then im happy i guess :((((((')
    await ctx.send('**you\'re')

@bot.command()
async def ukys(ctx):
    
    await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name=corpobs.json()["phrase"]))
    await ctx.send('screw you then buddy')

# Run the bot
if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)

#i love freaky bot ai....
#2025 goonsoft.dev
