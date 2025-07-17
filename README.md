# FreakBotAI - Synergizing Marketable B2B Solutions for the Chronically Online

### Usage:  
1. Create/activate a python virtual enviroment in the project root directory (should be Python 3.12 or higher)
2. Create and populate a .env file as described in the *Enviroment Setup* section
3. Run `pip install -r requirements.txt` to install all the necessary project dependencies
4. Run `python3 (insert script name here).py` to start the desired script. Script functionality details listed in the *Files* section.
5. (Optional) Run `crontab -e` and add the line `0 * * * * /path-to-venv/venv/bin/python3 /path/to/script/dblog.py` to the end of the file. This will tell cron to execute the database logging script once per hour.

### Enviroment Setup:
This project requires a .env file in the root directory with the following key/value pairs:  

- API_KEY - Discord API key  
- ABSTRACT_API_KEY - API key for the Abstract API  
- DISCORD_CHANNEL_ID - Channel ID for the bot to post IP messages in  
- OUTSIDE_PORT - Port for the web server (should be 9480 if on prod server)  
- DB_USERNAME - Username to access database  
- DB_PASSWORD - Password to access database  

### Files:  
- **dblog.py** - Database logging tool. Retreives data from Steam and adds it to a mySQL database. Use cron in the prod enviroment to run every hour.
- **iplog.py** - IP Address logging tool. Hosts a Flask web server with IP grabber funtionality and logs to Discord server.
- **main.py** - Contains main bot functionality.
- **templates/index.html** - Webpage hosted by iplog.py

