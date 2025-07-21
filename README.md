# FreakBotAI - Synergizing Marketable B2B Solutions for the Chronically Online

"GoonSoft - Making technology fun again since 2025!"

## Getting Started:
This project is currently configured to work best on Ubuntu Server 24.04.2 or higher 

**Before running any of these scripts, make sure to complete the following setup procedures:**
1. Ensure your server topology matches what is described in the *Server Topology* section
2. Clone this repository into your server's home directory with `cd ~ && git clone https://github.com/offsec64/freakbotAI.git` (omit the first command if you'd like to install elsewhere)
3. Create/activate a python virtual enviroment in the project root directory with `python3 -m venv venv && source venv/bin/activate` (should be Python 3.12 or higher)
4. Create and populate a .env file as described in the *Enviroment Setup* section
5. Run `pip install -r requirements.txt` to install all the necessary project dependencies into your virtual enviroment
   
### Usage - Bot:  
- Ensure you are using your python virtual enviroment you should have set up earlier
- Make sure all enviroment variables are correctly set up for your specific deployment enviroment.
- Run `python3 main.py` to start the bot.

### Usage - Database Logger:
- Ensure you are using your python virtual enviroment you should have set up earlier
- Make sure all enviroment variables are correctly set up for your specific deployment enviroment.
- (If using Cron) Run `crontab -e` and add the line `0 * * * * /path-to-venv/venv/bin/python3 /path/to/script/dblog.py` to the end of the file. This will tell cron to execute the database logging script once per hour. You can use `crontab -l` to view crontab entries.
- (If running once) Run `python3 dblog.py` 

### Usage - Web Server:

- Ensure you are using your python virtual enviroment you should have set up earlier
- Make sure all enviroment variables are correctly set up for your specific deployment enviroment.
- Clone the website repository into your server's home directory with `cd ~ && git clone https://github.com/offsec64/Goonsoft.dev.git`. Omit the first command if you'd like to install elsewhere. Just make sure you imput the new path to this directory in your .env file

#### Set up nginx:
   - nginx is used as reverse proxy/static content delivery service. Install it with `sudo apt install nginx`
   - Create a config file for the service: `sudo nano /etc/nginx/sites-available/goonsoft`
   - Edit the config file to look like this:
      
      ```
      server {
          listen 80; # the port that nginx will listen on (web facing)
          server_name your-domain.com;  # or use your server's IP
      
          location / {
              proxy_pass http://127.0.0.1:8000; # local port that nginx will proxy
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          }
      }
      ```
      
   - Save the config and enable it with the following commands:
       
      ```
      sudo ln -s /etc/nginx/sites-available/goonsoft /etc/nginx/sites-enabled/
      sudo nginx -t
      sudo systemctl reload nginx
      ```
         
#### Set up Gunicorn:
   - Gunicorn is used as the WSGI server for flask. Install it with: `pip install gunicorn`
   - Run the gunicorn server with run.sh
   - Eventually I will update this guide to show how to make gunicorn run automatically with a system service

  
## Enviroment Setup:
This project requires a .env file in the root directory with the following key/value pairs:  

- DISCORD_BOT_TOKEN - Discord API key  
- ABSTRACT_API_KEY - API key for the Abstract API  
- DISCORD_CHANNEL_ID - Channel ID for the bot to post IP messages in  
- OUTSIDE_PORT - Port for the web server to use 
- DB_USERNAME - Username to access database  
- DB_PASSWORD - Password to access database
- DB_HOST - IP Address of database server  
- PATH_TO_WEBSITE - Path to web files to be served by Flask/nginx

## Recommended Server Topology:

This project can be run off 1 physical server, though it is not recommended. Recommended setup is with 2 seperate servers, both existing inside of a DMZ VLAN for security reasons.

Server 1: 
- Ollama server running on port 11435 proxied to port 80 with nginx

Server 2:
- MySQL server (can be hosted on a third server if you wish)
- Web server to host the bot and webpage. Traffic should br proxied through something like Cloudflare Tunnels

## Files:  
- **dblog.py** - Database logging tool. Retreives data from Steam and adds it to a mySQL database. Use cron in the prod enviroment to run every hour.
- **iplog.py** - Flask web server with IP logging functionality
- **main.py** - Contains main bot functionality.
- **run.sh** - use this to run the gunicorn WSGI server
- **templates/index.html** - Webpage hosted by iplog.py. Now depricated in favor of new Goonsoft webpage!!!


