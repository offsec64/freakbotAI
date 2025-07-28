#!/usr/bin/python3

#Logs a Steam user's hours in their most played game to a MySQL database
#Use cron (unix) or task scheduler (win) to run this script periodically, idealy every 24 hours.

import mysql.connector
import os
import requests
import xmltodict
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")

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

parsed_data = parse_xml_from_url_to_dict(STEAM_URL)

if parsed_data:
    print("Successfully parsed XML into dictionary")
    #print(parsed_data)
else:
    print("Failed to parse XML from URL.")

mydb = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USERNAME,
    password=DB_PASSWORD,
    database="goontech"
)

if mydb.is_connected():
    print("Connected to MySQL database")
    mycursor = mydb.cursor()

    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    steam_id = parsed_data["profile"]["steamID64"]

    #This needs to go into a try/catch block at some point

    for game in parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"]:

        game_name = game["gameName"]
        formatted_name = game_name.replace(" ", "_")
        formatted_name = formatted_name.lower()

        hours = game["hoursOnRecord"]
        hours = hours.replace(",", "")

        create_table = f"CREATE TABLE IF NOT EXISTS {formatted_name} (id INT AUTO_INCREMENT PRIMARY KEY, steam_id VARCHAR(50) NOT NULL, game_name VARCHAR(50), hours VARCHAR(50) NOT NULL, timestamp VARCHAR(100) NOT NULL UNIQUE);"
        mycursor.execute(create_table)

        insert_data = f"INSERT INTO {formatted_name}  " + "(steam_id, game_name, hours, timestamp) VALUES (%s, %s, %s, %s)"
        val = (steam_id, game_name, hours, formatted_time)

       # sql="INSERT INTO steam_data (steamid, game_name, hours, timestamp) VALUES (%s, %s, %s, %s)"
        
        mycursor.execute(insert_data, val)
        mydb.commit()


    #hours = parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][0]["hoursOnRecord"]
    #hours = hours.replace(",", "")

    #game_name = parsed_data["profile"]["mostPlayedGames"]["mostPlayedGame"][0]["gameName"]

    mycursor.execute("SELECT * FROM steam_data ORDER BY timestamp DESC LIMIT 10")

    myresult = mycursor.fetchall()

    for x in myresult:
        print(x)

    mydb.close()
    print("MySQL connection closed")

else:
    print("Failed to connect to MySQL database")
    mydb.close()

