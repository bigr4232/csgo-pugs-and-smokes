import databaseServerHandler as dsh
import command_sender

# Class of servers accessible by the bot
# These are stored in serverList dictionary with the key as the serverid
class Server:
    def __init__(self, ip, controllerPort, link):
        self.ip = ip
        self.controllerPort = controllerPort
        self.link = link
        self.serverPassword = command_sender.getPassword(ip, controllerPort)
        self.serverPort = command_sender.getServerPort(ip, controllerPort)

async def updateServers():
    servers = await dsh.getServers()
    for server in servers:
        newServer = Server(server[0], server[4], server[5])
        serverList.update({server[1]:newServer})

serverList = dict()    