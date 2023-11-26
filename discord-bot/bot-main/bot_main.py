import discord
from discord import app_commands
import config_loader
import command_sender
import asyncio
import logging
import random
import sys
from tenManSim import fillTenMan
from state_to_abbrevation import stateList
import databaseServerHandler as dsh
import server_info
import datetime

# Intents, tree inits, globals
__version__ = '2.0.0'
__requiredControllerVersion__ = '1.0.1'
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
incompatibleServers = set()
asyncio.run(server_info.updateServers())

# Logging
logger = logging.getLogger('logs')
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# get args
for arg in sys.argv:
    if arg == '-sim10man':
        simTenMan = True
    if arg == '-log':
        logger.setLevel(logging.DEBUG)
        now = datetime.datetime.now()
        pre = now.strftime("%Y-%m-%d_%H:%M:%S")
        fh = logging.FileHandler(f'bot-{pre}-logs.log')
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

# Print output for server status
async def serverInfoOutput(serverID):
    serverStatus = await command_sender.getServerStatus(server_info.serverList[serverID].ip, server_info.serverList[serverID].controllerPort)
    if serverStatus == 'True':
        serverStatus = True
    else:
        serverStatus = False
    ip = server_info.serverList[serverID].ip
    controllerPort = server_info.serverList[serverID].controllerPort
    serverPort = await command_sender.getServerPort(ip, controllerPort)
    serverInfoString = ''
    serverInfoString += 'IP: ' + ip + '\n'
    serverInfoString += 'Port: ' + serverPort + '\n'
    serverInfoString += 'Location: ' + server_info.serverList[serverID].location + '\n'
    if serverStatus:
        password = await command_sender.getPassword(ip, controllerPort)
        serverInfoString += 'Server status: Online\n'
        serverInfoString += 'Server password: ' + password + '\n'
        serverInfoString += 'connect ' + ip + ':' + serverPort + '; password ' + password
    else:
        serverInfoString += 'Server status: Offline'
    return serverInfoString, serverStatus


    
# Class for connect to server button
class ButtonForServer(discord.ui.View):
    def __init__(self, location, url):
        super().__init__()
        self.add_item(discord.ui.Button(label=f'Connect {location}', url=url))

# Selection menu for cs servers
class ServerSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=server, value=server) for server in server_info.serverList.keys()]
        super().__init__(placeholder='Select a server location', max_values=1, min_values=1, options=options)
    async def callback(self, ctx: discord.Interaction):
        serverID = self.values[0]
        location = server_info.serverList[serverID].location
        link = server_info.serverList[serverID].link
        message, serverStatus = await serverInfoOutput(serverID)
        if serverID in incompatibleServers:
            await ctx.response.send_message('Please update the server controller of this server to use it.')
        elif serverStatus:
            await ctx.response.send_message(message, view=ButtonForServer(location, link))
        else:
            await ctx.response.send_message(message)

class ServerSelectView(discord.ui.View):
    def __init__(self, *, timeout = 200):
        super().__init__(timeout=timeout)
        self.add_item(ServerSelect())

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
            await ctx.response.send_message('Starting 10 mans', delete_after=200)
            message = await ctx.channel.send('0/10 players joined', view=TenMansButton())
            tenManMessage.update({ctx.guild.id : message})
            tenManPlayers[ctx.guild.id] = set()
        else:
            await ctx.response.send_message('10 mans already started. Please cancel before starting again', delete_after=30)
    elif option.name == 'cancel':
        if ctx.guild.id in tenManMessage:
            await ctx.response.send_message('Ending 10 mans', delete_after=30)
            await tenManMessage[ctx.guild.id].delete()
            tenManMessage.pop(ctx.guild.id)
        else:
            await ctx.response.send_message('No 10 mans running', delete_after=30)
    elif option.name == 're-scramble':
        if ctx.guild.id in sortedList:
            await ctx.response.send_message(f'Re-scrambling Teams', delete_after=200)
            await rescrambleTenMans(ctx)
        else:
            await ctx.response.send_message('Teams have not been set in this server', delete_after=30) 

# Start server command
@tree.command(name='start-server', description='send command to server to start')
@app_commands.choices(serverchoice=[app_commands.Choice(name=serverID, value=serverID) for serverID in server_info.serverList.keys()])
async def startServerCommand(ctx: discord.Interaction, serverchoice: app_commands.Choice[str]):
    if serverchoice.name not in incompatibleServers:
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
    else:
        await ctx.response.send_message('Please update the server controller of this server to use it.')

# Stop server command
@tree.command(name='stop-server', description='send command to server to stop')
@app_commands.choices(serverchoice=[app_commands.Choice(name=serverID, value=serverID) for serverID in server_info.serverList.keys()])
async def stopServerCommand(ctx: discord.Interaction, serverchoice: app_commands.Choice[str]):
    if serverchoice.name not in incompatibleServers:
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
    else:
        await ctx.response.send_message('Please update the server controller of this server to use it.')
        
# Restart server command
@tree.command(name='restart-server', description='send command to server to restart')
@app_commands.choices(serverchoice=[app_commands.Choice(name=serverID, value=serverID) for serverID in server_info.serverList.keys()])
async def restartServerCommand(ctx: discord.Interaction, serverchoice: app_commands.Choice[str]):
    if serverchoice.name not in incompatibleServers:
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
    else:
        await ctx.response.send_message('Please update the server controller of this server to use it.')

# Start gamemode
@tree.command(name='gamemode', description='start gamemode on the server specified by the option')
@app_commands.choices(serverchoice=[app_commands.Choice(name=serverID, value=serverID) for serverID in server_info.serverList.keys()])
@app_commands.choices(option=[app_commands.Choice(name='nade-practice', value='nade-practice')])
async def serverGameModeCommand(ctx: discord.Interaction, option: app_commands.Choice[str], serverchoice: app_commands.Choice[str]):
    if serverchoice.name not in incompatibleServers:
        logger.info(f'{ctx.user.name} called server command gamemode with option {option.name}')
        await ctx.response.send_message(f'Switching server to gamemode {option.value}', delete_after=30)
        global gamemode
        gamemode = 'nade-practice'
        await command_sender.gamemodeStart(server_info.serverList[serverchoice.name].ip,
                                        server_info.serverList[serverchoice.name].controllerPort, option.value)
    else:
        await ctx.response.send_message('Please update the server controller of this server to use it.')

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
    if serverchoice.name not in incompatibleServers:
        logger.info(f'{ctx.user.name} called server command changemap with option {option.name}')
        await ctx.response.send_message(f'Switching server to the map {option.value}', delete_after=30)
        await command_sender.changemap(server_info.serverList[serverchoice.name].ip,
                                        server_info.serverList[serverchoice.name].controllerPort, option.value)
        await asyncio.sleep(10)
        await command_sender.gamemodeStart(server_info.serverList[serverchoice.name].ip,
                                        server_info.serverList[serverchoice.name].controllerPort, gamemode)
    else:
        await ctx.response.send_message('Please update the server controller of this server to use it.')

# Send server command
@tree.command(name='send-server-command', description='Send a command to the server')
@app_commands.choices(serverchoice=[app_commands.Choice(name=serverID, value=serverID) for serverID in server_info.serverList.keys()])
async def sendServerCommand(ctx: discord.Interaction, command: str, serverchoice: app_commands.Choice[str]):
    if serverchoice.name not in incompatibleServers:
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
    else:
        await ctx.response.send_message('Please update the server controller of this server to use it.')

# Get server info command
@tree.command(name='get-server-info', description='Get info to connect to cs server')
async def getServerInfo(ctx: discord.Interaction):
    logger.info(f'{ctx.user.name} called server command get-server-info')
    await ctx.response.send_message(f'Servers:', view=ServerSelectView())

# Command to update server
@tree.command(name='update-server', description='Update cs2 server if there is an update available')
@app_commands.choices(serverchoice=[app_commands.Choice(name=serverID, value=serverID) for serverID in server_info.serverList.keys()])
async def updateServer(ctx: discord.Interaction, serverchoice: app_commands.Choice[str]):
    if serverchoice.name not in incompatibleServers:
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
    else:
        await ctx.response.send_message('Please update the server controller of this server to use it.')

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

# Check controller versions
async def checkControllerVerion():
    compatibleVersion = __requiredControllerVersion__.split('.')
    for server in server_info.serverList.keys():
        version = await command_sender.getControllerVersion(server_info.serverList[server].ip, server_info.serverList[server].controllerPort)
        if version == '-':
            incompatibleServers.add(server)
        else:
            version = version.split('.')
            if int(version[0]) == int(compatibleVersion[0]):
                if int(version[1]) == int(compatibleVersion[1]):
                    if int(version[2]) < int (compatibleVersion[2]):
                        incompatibleServers.add(server)
                elif int(version[1]) < int(compatibleVersion[1]):
                    incompatibleServers.add(server)
            elif int(version[0]) < int(compatibleVersion[0]):
                incompatibleServers.add(server)
    if len(incompatibleServers) > 0:
        message = 'The following servers have out of date controllers and should be updated before using the bot with them:'
        for server in incompatibleServers:
            message += '\n' + server
        channel = client.get_channel(config['discordChannel'])
        await channel.send(message)
        logger.info(message)

# Initialization
@client.event
async def on_ready():
    logger.info(f'Starting bot v{__version__}')
    await tree.sync()
    logger.debug("commands synced")
    await checkControllerVerion()
    await command_sender.automatedUpdateServer()

client.run(config['discordBotToken'])
