# Server Controller

This controls the CS2 server and allows command to be sent from the bot to the server.
It requires screen to be installed on the device. It has been tested on Debian with python 3.11
This server receives TCP packets from the bot and responds with '-' if the command
was successful or with the expected response the bot needs.

## Installation

On the first run of using updater.py, it will ask you to fill in yaml options for
config.yaml. These can be adjusted later manually. This cannot run through docker
and can only be used through a standalone python setup.

This file does not need to be in the same directory as your CS server, but the
directory to the CS server must be correct and full in the start command in config.yaml.

Use updater.py to install discord bot files in location of your choosing.
Specify directory on run with -dir flag

Install requirements in virtual environment

run server-controller with python

### Example (Standalone Python)

python updater.py -dir [directory]

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

python controller.py

## config.yaml setup

Updater will ask to set initial config variables. They can be reset later by manually
editing config.yaml.

### Variables

- PORT -> port to run the server-controller on

- startCommand -> command to run CS server with

### config.yaml example

```yaml
PORT: 48482
startCommand: .\cs2.exe -dedicated +map de_dust2

```
