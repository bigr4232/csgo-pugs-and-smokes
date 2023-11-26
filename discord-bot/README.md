# Discord Bot

Discord bot to control CS server and start 10 mans.

## Installation

On the first run of using updater.py, it will ask you to fill in yaml options for
config.yaml. These can be adjusted later manually.

accounts.yaml only needs to be filled if using -sim10man argument to test 10 mans.
Fill accounts.yaml with 9 user ids for discord.

### Option 1 (Docker)

Use updater.py to install discord bot files in location of your choosing.
Specify directory on run with -dir flag

Run provided docker-compose file.

#### Example (Docker)

python updater.py -dir [directory]

docker compose up -d

### Option 2 (Standalone Python)

Use updater.py to install discord bot files in location of your choosing.
Specify directory on run with -dir flag

Install requirements in virtual environment

run bot-main.py with python

#### Example (Standalone Python)

python updater.py -dir [directory]

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

python bot-man/bot_main.py

## Available Slash Commands

The [server] option is output where the user needs to specify which server to apply the command.

- /gamemode [option] [server] -> Sets server to certain gamemode

  - nade-practice -> executes server nade practice config

- /changemap [option] [server] -> Changes server to specified map

- /update-server [server] -> Updates the CS2 server and restarts it

- /start-server [server] -> Starts the CS2 server

- /stop-server [server] -> Stops the CS2 server

- /restart-server [server] -> Restarts the CS2 server

- /get-server-info [server] -> Get connect info to the CS2 server and display a button to connect directly

- /send-server-command [server] -> Sends a CS command to the CS2 server that you would exectute in console

- /ten-mans [option] -> Used for ten man pugs

  - start -> Starts ten man and sends message to allow people to join

  - stop -> Stops ten mans and deletes message that people join from

  - re-scramble -> Rescrambles teams given by ten mans after teams have been posted

- /addserver [ip] [controllerport] [state] [link]

  - [ip] -> IP address of CS server controller to add as well as CS server

  - [controllerport] -> port that the server controller is running on

  - [state] -> US state that the server is located in

  - [link] -> Link to website that will auto connect user to server

## config.yaml setup

Updater will ask to set initial config variables. They can be reset later by manually
editing config.yaml.

### Variables

- discordBotToken -> api key for discord bot

- discordChannel -> main discord channel for bot, use channel id

- discordAdminRole -> role to give users access to all bot commands, use role id

- discordGuildID -> guild id for main server of the bot

- discordOwnerID -> discord id of main admin of bot

- dbhost -> IP address or hostname of database

- dbuser -> Username to use to connect to database

- dbpassword -> Password to connect to database

### config.yaml example

```yaml
discordBotToken: 'akljkalhtekh98352jkl34h1941904u104n1o4y1945-=41jkl;h4k1j2'
discordChannel: '894713448972934'
discordAdminRole: '57489305729843792'
discordGuildID: '4983217489016438921374'
discordOwnerID: '4890371258937629185741'
dbhost: 489.34.231.53
dbuser: username4131
dbpassword: Password123

```

## accounts.yaml setup

This file is not needed to be setup unless using the simulated 10 mans test. This
test is run by using the input arg -sim10man. To set up, put the discord ids of 9
users to use as test accounts.

### accounts.yaml example

```yaml
accounts:
 - 548907389567984123
 - 8943728947389135748
 - 1981458774328947094
 - 8907598274390782234
 - 4390875982674189024
 - 5890849017498901322
 - 9013580948917498198
 - 4551243241418907970
 - 5123414165162342443
```
