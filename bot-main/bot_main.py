import discord
from discord import app_commands
import config_loader
import command_sender
import asyncio
from requests import get
import logging

# Intents and tree inits
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
managers = {}
tree = app_commands.CommandTree(client)
config = config_loader.loadYaml()
gamemode = 'nade-practice'
tenManPlayers = dict()
ip = get('https://api.ipify.org').content.decode('utf8')
if '-port' in config['startCommand']:
    portStr = config['startCommand'][config['startCommand'].find('-port')+6:]
    port = portStr[0:portStr.find(' ')]
else:
    port = '27015'
serverPassword = ''

logger = logging.getLogger('logs')
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# TODO discord.py api needs support for steam:// implementation for the button to work
# This will be implemented in the get-server-info commands
# Class for connect to server button
class ButtonForServer(discord.ui.View):
    def __init__(self):
        super().__init__()
        url = f'steam://connect/{ip}:{port}/{serverPassword}'
        self.add_item(discord.ui.Button(label='Connect', url=url))

# Class for 10 mans buttons
class TenMansButton(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Join",style=discord.ButtonStyle.green)
    async def green_button(self, ctx:discord.Interaction, button:discord.ui.Button):
        print('button pressed')
        await ctx.response.edit_message(content = 'kldfjas')

# Checks if user has the role with a role ID as input
async def checkIfUserHasRole(roles, roleID):
    for role in roles:
        if role.id == roleID:
            return True
    return False

# Ten mans discord command
@tree.command(name='ten-mans', description='start 10 mans')
@app_commands.choices(option=[app_commands.Choice(name='start', value='start'),
                              app_commands.Choice(name='cancel', value='cancel'),])
async def tenMans(ctx: discord.Interaction, option:app_commands.Choice[str]):
    if option.name == 'start':
        await ctx.response.send_message('0 players joined', view=TenMansButton())
    elif option.name == 'cancel':
        print()

# Start server command
@tree.command(name='start-server', description='send command to server to start')
async def startServerCommand(ctx: discord.Interaction):
    if not ctx.guild:
        guild = client.get_guild(int(config['discordGuildID']))
        member = await guild.fetch_member(ctx.user.id)
        memberRoles = member.roles
    else:
        memberRoles = ctx.user.roles
    if await checkIfUserHasRole(memberRoles, int(config['discordAdminRole'])):
        await ctx.response.send_message('Starting Counter Strike server.', delete_after=30)
        serverPassword = await command_sender.startServer(config['startCommand'])
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)

# Stop server command
@tree.command(name='stop-server', description='send command to server to stop')
async def startServerCommand(ctx: discord.Interaction):
    if not ctx.guild:
        guild = client.get_guild(int(config['discordGuildID']))
        member = await guild.fetch_member(ctx.user.id)
        memberRoles = member.roles
    else:
        memberRoles = ctx.user.roles
    if await checkIfUserHasRole(memberRoles, int(config['discordAdminRole'])):
        await ctx.response.send_message('Stopping Counter Strike server.', delete_after=30)
        await command_sender.stopServer()
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)
        
# Restart server command
@tree.command(name='restart-server', description='send command to server to restart')
async def startServerCommand(ctx: discord.Interaction):
    if not ctx.guild:
        guild = client.get_guild(int(config['discordGuildID']))
        member = await guild.fetch_member(ctx.user.id)
        memberRoles = member.roles
    else:
        memberRoles = ctx.user.roles
    if await checkIfUserHasRole(memberRoles, int(config['discordAdminRole'])):
        await ctx.response.send_message('Restarting Counter Strike server.', delete_after=30)
        await command_sender.stopServer()
        await command_sender.startServer(config['startCommand'])
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)

# Start gamemode
@tree.command(name='gamemode', description='start gamemode on the server specified by the option')
@app_commands.choices(option=[app_commands.Choice(name='nade-practice', value='nade-practice')])
async def serverGameModeCommand(ctx: discord.Interaction, option:app_commands.Choice[str]):
    if not ctx.guild:
        guild = client.get_guild(int(config['discordGuildID']))
        member = await guild.fetch_member(ctx.user.id)
        memberRoles = member.roles
    else:
        memberRoles = ctx.user.roles
    if await checkIfUserHasRole(memberRoles, int(config['discordAdminRole'])):
        await ctx.response.send_message(f'Switching server to gamemode {option.value}', delete_after=30)
        global gamemode
        gamemode = 'nade-practice'
        await command_sender.gamemodeStart(option.value)
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)

# Change map
@tree.command(name='changemap', description='changemap to specified map')
@app_commands.choices(option=[app_commands.Choice(name='ancient', value='ancient'),
                              app_commands.Choice(name='anubis', value='anubis'),
                              app_commands.Choice(name='dust2', value='dust2'),
                              app_commands.Choice(name='inferno', value='infero'),
                              app_commands.Choice(name='mirage', value='mirage'),
                              app_commands.Choice(name='nuke', value='nuke'),
                              app_commands.Choice(name='overpass', value='overpass'),
                              app_commands.Choice(name='vertigo', value='vertigo')])
async def changeMap(ctx: discord.Interaction, option:app_commands.Choice[str]):
    if not ctx.guild:
        guild = client.get_guild(int(config['discordGuildID']))
        member = await guild.fetch_member(ctx.user.id)
        memberRoles = member.roles
    else:
        memberRoles = ctx.user.roles
    if await checkIfUserHasRole(memberRoles, int(config['discordAdminRole'])):
        await ctx.response.send_message(f'Switching server to the map {option.value}', delete_after=30)
        await command_sender.changemap(option.value)
        await asyncio.sleep(10)
        await command_sender.gamemodeStart(gamemode)
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)

# Send server command
@tree.command(name='send-server-command', description='Send a command to the server')
async def sendServerCommand(ctx: discord.Interaction, command: str):
    if not ctx.guild:
        guild = client.get_guild(int(config['discordGuildID']))
        member = await guild.fetch_member(ctx.user.id)
        memberRoles = member.roles
    else:
        memberRoles = ctx.user.roles
    if await checkIfUserHasRole(memberRoles, int(config['discordAdminRole'])):
        await ctx.response.send_message(f'Sending command to server {command}', delete_after=30)
        resp = await command_sender.sendCMD(command)
        if resp != '':
            await ctx.channel.send(f'Server responded with {resp}')
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)

# Get server info command
@tree.command(name='get-server-info', description='Get info to connect to cs server')
async def getServerInfo(ctx: discord.Interaction):
    serverPassword = await command_sender.getPassword()
    await ctx.response.send_message(f'Server ip: {ip}\nServer port: {port}\nServer password: {serverPassword}\nconnect {ip}:{port}; password Tacos024')

@tree.command(name='update-server', description='Update cs2 server if there is an update available')
async def updateServer(ctx: discord.Interaction):
    if not ctx.guild:
        guild = client.get_guild(int(config['discordGuildID']))
        member = await guild.fetch_member(ctx.user.id)
        memberRoles = member.roles
    else:
        memberRoles = ctx.user.roles
    if await checkIfUserHasRole(memberRoles, int(config['discordAdminRole'])):
        await ctx.response.defer()
        serverPassword = await command_sender.updateServer(config['steamCMDInstallPath'], config['csgoServerInstallPath'], config['startCommand'], config['serverLoginUsername'], config['serverLoginPassword'])
        await ctx.followup.send('Server is updated and running.')
        await ctx.channel.send(f'Server ip: {ip}\nServer port: {port}\nServer password: {serverPassword}\nconnect {ip}:{port}; password Tacos024')
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)

# Initialization
@client.event
async def on_ready():
    #await tree.sync()
    logger.info("connected")

client.run(config['discordBotToken'])
