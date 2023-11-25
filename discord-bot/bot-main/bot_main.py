import discord
from discord import app_commands
import config_loader
import command_sender
import asyncio
from requests import get
import logging
import random
import sys
from tenManSim import fillTenMan
from state_to_abbrevation import stateList
import databaseServerHandler as dsh
import server_info

# Intents, tree inits, globals
__version__ = '2.0.0'
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
managers = {}
tree = app_commands.CommandTree(client)
config = config_loader.loadYaml()
gamemode = 'nade-practice'
tenManPlayers = dict()
tenManMessage = dict()
sortedList = dict()
simTenMan = False
serverPassword = ''
asyncio.run(server_info.updateServers())

# get args
for arg in sys.argv:
    if arg == '-sim10man':
        simTenMan = True

# Logging
logger = logging.getLogger('logs')
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Class for connect to server button
class ButtonForServer(discord.ui.View):
    def __init__(self):
        super().__init__()
        url = f'https://cs-pho.bigr.dev'
        self.add_item(discord.ui.Button(label='Connect', url=url, style=discord.ButtonStyle.green))

# Class for 10 mans buttons
class TenMansButton(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)
    @discord.ui.button(label='Join',style=discord.ButtonStyle.green)
    async def green_button(self, ctx:discord.Interaction, button:discord.ui.Button):
        logger.debug(f'green button pressed by {ctx.user.id}')
        checkDup = ctx.user not in tenManPlayers[ctx.guild.id]
        if simTenMan:
            tenManPlayers[ctx.guild.id] = await fillTenMan(client, config)
        if checkDup:
            tenManPlayers[ctx.guild.id].add(ctx.user)
        await ctx.response.edit_message(content = await tenManStatus(ctx), view=self)
        if len(tenManPlayers[ctx.guild.id]) == 10 and checkDup:
            logger.debug('Starting 10 mans')
            if ctx.guild.id in sortedList:
                sortedList[ctx.guild.id].clear()
            sortedList[ctx.guild.id] = await randomizeTeams(tenManPlayers[ctx.guild.id])
            await ctx.channel.send(f'Team 1: {sortedList[ctx.guild.id][0].mention}, {sortedList[ctx.guild.id][1].mention}, {sortedList[ctx.guild.id][2].mention}, {sortedList[ctx.guild.id][3].mention}, {sortedList[ctx.guild.id][4].mention}\nTeam 2: {sortedList[ctx.guild.id][5].mention}, {sortedList[ctx.guild.id][6].mention}, {sortedList[ctx.guild.id][7].mention}, {sortedList[ctx.guild.id][8].mention}, {sortedList[ctx.guild.id][9].mention}')
            await tenManMessage[ctx.guild.id].delete()
            tenManMessage.pop(ctx.guild.id)
    @discord.ui.button(label='leave', style=discord.ButtonStyle.red)
    async def red_button(self, ctx:discord.Interaction, button:discord.ui.Button):
        logger.debug(f'red button pressed by {ctx.user.id}')
        if ctx.user in tenManPlayers[ctx.guild.id]:
            tenManPlayers[ctx.guild.id].remove(ctx.user)
        await ctx.response.edit_message(content = await tenManStatus(ctx), view=self)

# Get IP
async def getIP():
    return get('https://api.ipify.org').content.decode('utf8')

# Make message to send for 10 man status
async def tenManStatus(ctx):
    message = f'{len(tenManPlayers[ctx.guild.id])}/10 players joined:'
    for player in tenManPlayers[ctx.guild.id]:
        if player.display_name is not None:
            message += f"\n{player.display_name}"
        else:
            message += f"\n{player.name}"
    return message

# Randomize teams for 10 mans
async def randomizeTeams(unsortedSet):
    logger.debug('Randomizing teams')
    sortList = list()
    for discordUser in unsortedSet:
        sortList.append(discordUser)
    for i in range(len(sortList)):
        swapidx = random.randint(0,9)
        tempDiscordUser = sortList[swapidx]
        sortList[swapidx] = sortList[i]
        sortList[i] = tempDiscordUser
    return sortList

# Checks if user has the role with a role ID as input
async def checkIfUserHasRole(roles, roleID):
    for role in roles:
        if role.id == roleID:
            return True
    return False

# Re-scramble teams using players who have already readied up.
async def rescrambleTenMans(ctx):
    sortedList[ctx.guild.id] = await randomizeTeams(sortedList[ctx.guild.id])
    await ctx.channel.send(f'New Teams:\nTeam 1: {sortedList[ctx.guild.id][0].mention}, {sortedList[ctx.guild.id][1].mention}, {sortedList[ctx.guild.id][2].mention}, {sortedList[ctx.guild.id][3].mention}, {sortedList[ctx.guild.id][4].mention}\nTeam 2: {sortedList[ctx.guild.id][5].mention}, {sortedList[ctx.guild.id][6].mention}, {sortedList[ctx.guild.id][7].mention}, {sortedList[ctx.guild.id][8].mention}, {sortedList[ctx.guild.id][9].mention}')

# Ten mans discord command
@tree.command(name='ten-mans', description='start 10 mans')
@app_commands.choices(option=[app_commands.Choice(name='start', value='start'),
                      app_commands.Choice(name='cancel', value='cancel'),
                      app_commands.Choice(name='re-scramble', value='re-scramble')])
async def tenMans(ctx: discord.Interaction, option:app_commands.Choice[str]):
    logger.info(f'{ctx.user.name} called ten-mans command with option {option.name}')
    if option.name == 'start':
        if ctx.guild.id not in tenManMessage or tenManMessage[ctx.guild.id] == 0:
            await ctx.response.send_message('Starting 10 mans')
            message = await ctx.channel.send('0/10 players joined', view=TenMansButton())
            tenManMessage.update({ctx.guild.id : message})
            tenManPlayers[ctx.guild.id] = set()
        else:
            await ctx.response.send_message('10 mans already started. Please cancel before starting again')
    elif option.name == 'cancel':
        if ctx.guild.id in tenManMessage:
            await ctx.response.send_message('Ending 10 mans', delete_after=30)
            await tenManMessage[ctx.guild.id].delete()
            tenManMessage.pop(ctx.guild.id)
        else:
            await ctx.response.send_message('No 10 mans running', delete_after=30)
    elif option.name == 're-scramble':
        if ctx.guild.id in sortedList:
            await ctx.response.send_message(f'Re-scrambling Teams')
            await rescrambleTenMans(ctx)
        else:
            await ctx.response.send_message('Teams have not been set in this server') 

# Start server command
@tree.command(name='start-server', description='send command to server to start')
@app_commands.choices(serverchoice=[app_commands.Choice(name=serverID, value=serverID) for serverID in server_info.serverList.keys()])
async def startServerCommand(ctx: discord.Interaction, serverchoice: app_commands.Choice[str]):
    logger.info(f'{ctx.user.name} called server command start-server')
    if not ctx.guild:
        guild = client.get_guild(int(config['discordGuildID']))
        member = await guild.fetch_member(ctx.user.id)
        memberRoles = member.roles
    else:
        memberRoles = ctx.user.roles
    if await checkIfUserHasRole(memberRoles, int(config['discordAdminRole'])):
        await ctx.response.send_message('Starting Counter Strike server.', delete_after=30)
        await command_sender.sendCMD(server_info.serverList[serverchoice.name].ip,
                                     server_info.serverList[serverchoice.name].controllerPort, '-start-server')
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)

# Stop server command
@tree.command(name='stop-server', description='send command to server to stop')
@app_commands.choices(serverchoice=[app_commands.Choice(name=serverID, value=serverID) for serverID in server_info.serverList.keys()])
async def stopServerCommand(ctx: discord.Interaction, serverchoice: app_commands.Choice[str]):
    logger.info(f'{ctx.user.name} called server command stop-server')
    if not ctx.guild:
        guild = client.get_guild(int(config['discordGuildID']))
        member = await guild.fetch_member(ctx.user.id)
        memberRoles = member.roles
    else:
        memberRoles = ctx.user.roles
    if await checkIfUserHasRole(memberRoles, int(config['discordAdminRole'])):
        await ctx.response.send_message('Stopping Counter Strike server.', delete_after=30)
        await command_sender.sendCMD(server_info.serverList[serverchoice.name].ip,
                                     server_info.serverList[serverchoice.name].controllerPort, '-stop-server')
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)
        
# Restart server command
@tree.command(name='restart-server', description='send command to server to restart')
@app_commands.choices(serverchoice=[app_commands.Choice(name=serverID, value=serverID) for serverID in server_info.serverList.keys()])
async def restartServerCommand(ctx: discord.Interaction, serverchoice: app_commands.Choice[str]):
    logger.info(f'{ctx.user.name} called server command restart-server')
    if not ctx.guild:
        guild = client.get_guild(int(config['discordGuildID']))
        member = await guild.fetch_member(ctx.user.id)
        memberRoles = member.roles
    else:
        memberRoles = ctx.user.roles
    if await checkIfUserHasRole(memberRoles, int(config['discordAdminRole'])):
        await ctx.response.send_message('Restarting Counter Strike server.', delete_after=30)
        await command_sender.sendCMD(server_info.serverList[serverchoice.name].ip,
                                     server_info.serverList[serverchoice.name].controllerPort, '-restart-server')
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)

# Start gamemode
@tree.command(name='gamemode', description='start gamemode on the server specified by the option')
@app_commands.choices(serverchoice=[app_commands.Choice(name=serverID, value=serverID) for serverID in server_info.serverList.keys()])
@app_commands.choices(option=[app_commands.Choice(name='nade-practice', value='nade-practice')])
async def serverGameModeCommand(ctx: discord.Interaction, option: app_commands.Choice[str], serverchoice: app_commands.Choice[str]):
    logger.info(f'{ctx.user.name} called server command gamemode with option {option.name}')
    await ctx.response.send_message(f'Switching server to gamemode {option.value}', delete_after=30)
    global gamemode
    gamemode = 'nade-practice'
    await command_sender.gamemodeStart(server_info.serverList[serverchoice.name].ip,
                                     server_info.serverList[serverchoice.name].controllerPort, option.value)

# Change map
@tree.command(name='changemap', description='changemap to specified map')
@app_commands.choices(option=[app_commands.Choice(name='ancient', value='ancient'),
                              app_commands.Choice(name='anubis', value='anubis'),
                              app_commands.Choice(name='dust2', value='dust2'),
                              app_commands.Choice(name='inferno', value='inferno'),
                              app_commands.Choice(name='mirage', value='mirage'),
                              app_commands.Choice(name='nuke', value='nuke'),
                              app_commands.Choice(name='overpass', value='overpass'),
                              app_commands.Choice(name='vertigo', value='vertigo')])
@app_commands.choices(serverchoice=[app_commands.Choice(name=serverID, value=serverID) for serverID in server_info.serverList.keys()])
async def changeMap(ctx: discord.Interaction, option:app_commands.Choice[str], serverchoice: app_commands.Choice[str]):
    logger.info(f'{ctx.user.name} called server command changemap with option {option.name}')
    await ctx.response.send_message(f'Switching server to the map {option.value}', delete_after=30)
    await command_sender.changemap(server_info.serverList[serverchoice.name].ip,
                                     server_info.serverList[serverchoice.name].controllerPort, option.value)
    await asyncio.sleep(10)
    await command_sender.gamemodeStart(server_info.serverList[serverchoice.name].ip,
                                     server_info.serverList[serverchoice.name].controllerPort, gamemode)

# Send server command
@tree.command(name='send-server-command', description='Send a command to the server')
@app_commands.choices(serverchoice=[app_commands.Choice(name=serverID, value=serverID) for serverID in server_info.serverList.keys()])
async def sendServerCommand(ctx: discord.Interaction, command: str, serverchoice: app_commands.Choice[str]):
    logger.info(f'{ctx.user.name} called server command send-server-command with command {command}')
    if not ctx.guild:
        guild = client.get_guild(int(config['discordGuildID']))
        member = await guild.fetch_member(ctx.user.id)
        memberRoles = member.roles
    else:
        memberRoles = ctx.user.roles
    if await checkIfUserHasRole(memberRoles, int(config['discordAdminRole'])):
        await ctx.response.send_message(f'Sending command to server {command}', delete_after=30)
        await command_sender.sendCMD(server_info.serverList[serverchoice.name].ip,
                                     server_info.serverList[serverchoice.name].controllerPort, command)
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)

# Get server info command
@tree.command(name='get-server-info', description='Get info to connect to cs server')
@app_commands.choices(serverchoice=[app_commands.Choice(name=serverID, value=serverID) for serverID in server_info.serverList.keys()])
async def getServerInfo(ctx: discord.Interaction, serverchoice: app_commands.Choice[str]):
    logger.info(f'{ctx.user.name} called server command get-server-info')
    serverPassword = await command_sender.getPassword(server_info.serverList[serverchoice.name].ip,
                                     server_info.serverList[serverchoice.name].controllerPort, )
    port = await command_sender.getServerPort(server_info.serverList[serverchoice.name].ip,
                                     server_info.serverList[serverchoice.name].controllerPort, )
    ip = server_info[serverchoice.name].ip
    await ctx.response.send_message(f'Server ip: {ip}\nServer port: {port}\nServer password: {serverPassword}\nconnect {ip}:{port}; password Tacos024', view=ButtonForServer())

# Command to update server
@tree.command(name='update-server', description='Update cs2 server if there is an update available')
@app_commands.choices(serverchoice=[app_commands.Choice(name=serverID, value=serverID) for serverID in server_info.serverList.keys()])
async def updateServer(ctx: discord.Interaction, serverchoice: app_commands.Choice[str]):
    logger.info(f'{ctx.user.name} called server command update-server')
    if not ctx.guild:
        guild = client.get_guild(int(config['discordGuildID']))
        member = await guild.fetch_member(ctx.user.id)
        memberRoles = member.roles
    else:
        memberRoles = ctx.user.roles
    if await checkIfUserHasRole(memberRoles, int(config['discordAdminRole'])):
        await ctx.response.defer()
        await command_sender.sendCMD(server_info.serverList[serverchoice.name].ip,
                                     server_info.serverList[serverchoice.name].controllerPort, '-update-server')
        await ctx.followup.send('Server is updated and running.')
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)

# Add server to database
@tree.command(name='add-server', description='add server to database')
async def addDatabase(ctx: discord.Interaction, ip: str, controllerport: str, state: str, link: str):
    logger.info(f'{ctx.user.name} called server command update-server')
    if not ctx.guild:
        guild = client.get_guild(int(config['discordGuildID']))
        member = await guild.fetch_member(ctx.user.id)
        memberRoles = member.roles
    else:
        memberRoles = ctx.user.roles
    if await checkIfUserHasRole(memberRoles, int(config['discordAdminRole'])):
        stateExists = False
        lowerState = state.lower()
        for s in stateList:
            if lowerState == s.lower():
                stateExists = True
        if stateExists:
            logger.info('Adding server to database')
            await ctx.response.send_message('Adding server to database', delete_after=30)
            await dsh.addServer(ip, state, ctx.user.display_name, controllerport, link)
            await server_info.updateServers()
            await tree.sync()
            test = tree._get_all_commands()
        else:
            await ctx.response.send_message('State does not exist, please retry with valid state name', delete_after=30)
    else:
        await ctx.response.send_message('This command must be run by a Counter Strike server admin.', delete_after=30)

# Add ! commands for hidden commands
@client.event
async def on_message(ctx):
    if not ctx.guild:
        guild = client.get_guild(int(config['discordGuildID']))
        member = await guild.fetch_member(ctx.user.id)
        memberRoles = member.roles
    else:
        memberRoles = ctx.author.roles
    if await checkIfUserHasRole(memberRoles, int(config['discordAdminRole'])):
        if ctx.content.startswith('!'):
            if ctx.content[1:] == 'version':
                await ctx.channel.send(f'Version: {__version__}')

# Initialization
@client.event
async def on_ready():
    logger.info(f'Starting bot with version {__version__}')
    await tree.sync()
    logger.debug("commands synced")
    test = tree._get_all_commands()
    await command_sender.automatedUpdateServer()

client.run(config['discordBotToken'])
