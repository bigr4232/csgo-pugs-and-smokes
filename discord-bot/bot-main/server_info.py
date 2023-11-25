import databaseServerHandler as dsh
import command_sender
import asyncio

# Class of servers accessible by the bot
# These are stored in serverList dictionary with the key as the serverid
class Server:
    def __init__(self, ip, controllerPort, link, location, serverPassword = '', serverPort = ''):
        self.ip = ip
        self.controllerPort = controllerPort
        self.link = 'https://' + link
        self.location = location
        self.serverPassword = serverPassword
        self.serverPort = serverPort

async def updateServers():
    servers = await dsh.getServers()
    for server in servers:
        newServer = Server(server[0], server[4], server[5], server[2])
        serverList.update({server[1]:newServer})

serverList = dict()    