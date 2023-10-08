import discord
from discord import app_commands
import config_loader
import command_sender

# Intents and tree inits
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
managers = {}
tree = app_commands.CommandTree(client)
config = config_loader.loadYaml()

# Checks if user has the role with a role ID as input
async def checkIfUserHasRole(roles, roleID):
    for role in roles:
        if role.id == roleID:
            return True
    return False

# Command to sync new slash commands
@tree.command(name='sync-commands', description='command to sync new slash commands', guild=discord.Object(id=config['discordGuildID']))
async def syncCommands(ctx: discord.Interaction):
    if ctx.user.id == int(config['discordOwnerID']):
        await tree.sync(guild=discord.Object(id=config['discordGuildID']))
        await ctx.response.send_message('Commands synced', delete_after=30)
    else:
        await ctx.response.send_message('This command is only for the server owner.', delete_after=30)

# Start server command
@tree.command(name='start-server', description='send command to server to start', guild=discord.Object(id=config['discordGuildID']))
async def startServerCommand(ctx: discord.Interaction):
    if await checkIfUserHasRole(ctx.user.roles, config['discordAdminRole']):
        await ctx.response.send_message('Starting Counter Strike server.')
        await command_sender.startServer(config['startCommand'])
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.')

# Stop server command
@tree.command(name='stop-server', description='send command to server to stop', guild=discord.Object(id=config['discordGuildID']))
async def startServerCommand(ctx: discord.Interaction):
    if await checkIfUserHasRole(ctx.user.roles, config['discordAdminRole']):
        await ctx.response.send_message('Stopping Counter Strike server.')
        await command_sender.startServer(config['stopCommand'])
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.')
        
# Restart server command
@tree.command(name='restart-server', description='send command to server to restart', guild=discord.Object(id=config['discordGuildID']))
async def startServerCommand(ctx: discord.Interaction):
    if await checkIfUserHasRole(ctx.user.roles, config['discordAdminRole']):
        await ctx.response.send_message('Restarting Counter Strike server.')
        await command_sender.startServer(config['stopCommand'])
        await command_sender.startServer(config['startCommand'])
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.')

# Initialization
@client.event
async def on_ready():
    print("connected")

client.run(config['discordBotToken'])