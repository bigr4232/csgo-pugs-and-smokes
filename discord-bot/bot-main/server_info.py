import databaseServerHandler as dsh
import command_sender
import asyncio

# Class of servers accessible by the bot
# These are stored in serverList dictionary with the key as the serverid
class Server:
    def __init__(self, ip, controllerPort, link, serverPassword, serverPort):
        self.ip = ip
        self.controllerPort = controllerPort
        self.link = link
        self.serverPassword = serverPassword
        self.serverPort = serverPort

async def updateServers():
    servers = await dsh.getServers()
    for server in servers:
        password = await command_sender.getPassword(server[0], server[4])
        port = await command_sender.getServerPort(server[0], server[4])
        newServer = Server(server[0], server[4], server[5], password, port)
        serverList.update({server[1]:newServer})

serverList = dict()    