import discord
from discord import app_commands
from discord.ext import commands
import config_loader
import command_sender

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
managers = {}
tree = app_commands.CommandTree(client)
config = config_loader.loadYaml()

@client.event
async def on_ready():
    await tree.sync()

client.run(config['discordBotToken'])