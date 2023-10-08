import discord
from discord import app_commands
import config_loader
import command_sender
import asyncio

# Intents and tree inits
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
managers = {}
tree = app_commands.CommandTree(client)
config = config_loader.loadYaml()
gamemode = 'nade-practice'

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
        await ctx.response.send_message('Starting Counter Strike server.', delete_after=30)
        await command_sender.startServer(config['startCommand'])
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)

# Stop server command
@tree.command(name='stop-server', description='send command to server to stop', guild=discord.Object(id=config['discordGuildID']))
async def startServerCommand(ctx: discord.Interaction):
    if await checkIfUserHasRole(ctx.user.roles, config['discordAdminRole']):
        await ctx.response.send_message('Stopping Counter Strike server.', delete_after=30)
        await command_sender.stopServer()
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)
        
# Restart server command
@tree.command(name='restart-server', description='send command to server to restart', guild=discord.Object(id=config['discordGuildID']))
async def startServerCommand(ctx: discord.Interaction):
    if await checkIfUserHasRole(ctx.user.roles, config['discordAdminRole']):
        await ctx.response.send_message('Restarting Counter Strike server.', delete_after=30)
        await command_sender.stopServer()
        await command_sender.startServer(config['startCommand'])
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)

# Start gamemode
@tree.command(name='gamemode', description='start gamemode on the server specified by the option', guild=discord.Object(id=config['discordGuildID']))
@app_commands.choices(option=[app_commands.Choice(name='nade-practice', value='nade-practice')])
async def serverGameModeCommand(ctx: discord.Interaction, option:app_commands.Choice[str]):
    if await checkIfUserHasRole(ctx.user.roles, config['discordAdminRole']):
        await ctx.response.send_message(f'Switching server to gamemode {option.value}', delete_after=30)
        global gamemode
        gamemode = 'nade-practice'
        await command_sender.gamemodeStart(option.value)
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)

# Change map
@tree.command(name='changemap', description='changemap to specified map', guild=discord.Object(id=config['discordGuildID']))
@app_commands.choices(option=[app_commands.Choice(name='ancient', value='ancient'),
                              app_commands.Choice(name='anubis', value='anubis'),
                              app_commands.Choice(name='dust2', value='dust2'),
                              app_commands.Choice(name='inferno', value='infero'),
                              app_commands.Choice(name='mirage', value='mirage'),
                              app_commands.Choice(name='nuke', value='nuke'),
                              app_commands.Choice(name='overpass', value='overpass'),
                              app_commands.Choice(name='vertigo', value='vertigo')])
async def changeMap(ctx: discord.Interaction, option:app_commands.Choice[str]):
    if await checkIfUserHasRole(ctx.user.roles, config['discordAdminRole']):
        await ctx.response.send_message(f'Switching server to the map {option.value}', delete_after=30)
        await command_sender.changemap(option.value)
        await asyncio.sleep(10)
        await command_sender.gamemodeStart(gamemode)
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)

# Send server command
@tree.command(name='sendServerCommand', description='Send a command to the server', guild=discord.Object(id=config['discordGuildID']))
async def sendServerCommand(ctx: discord.Interaction, command: str):
    if await checkIfUserHasRole(ctx.user.roles, config['discordAdminRole']):
        await ctx.response.send_message(f'Sending command to server {command}', delete_after=30)
        resp = await command_sender.sendCMD(command)
        if resp != '':
            await ctx.channel.send(f'Server responded with {resp}')
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)


# Initialization
@client.event
async def on_ready():
    print("connected")

client.run(config['discordBotToken'])