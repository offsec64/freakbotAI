# FreakBotAI - Synergizing Marketable B2B Solutions for the Chronically Online
### Prerequisites:
Requires a .env file in the root directory with the following key/value pairs:  

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

