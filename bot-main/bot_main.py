import discord
from discord import app_commands
import config_loader

# Intents and tree inits
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
managers = {}
tree = app_commands.CommandTree(client)

# Initialization
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=config['discordGuildID']))
    print("connected")

config = config_loader.loadYaml()
client.run(config['discordBotToken'])