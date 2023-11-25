import socket
from datetime import datetime
import asyncio
import logging
import server_info

# Logging
logger = logging.getLogger('logs')
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Send command to execute certain gamemode
async def gamemodeStart(host, port, gamemode):
    if gamemode == 'nade-practice':
        await sendCMD(host, port, 'exec nadeprac')

# Send changelevel command to server
async def changemap(host, port, map):
    cmd = (f'changelevel de_{map}')
    await sendCMD(host, port, cmd)

# Get server password
async def getPassword(host, port):
    response = await sendCMD(host, port, '-get-password')
    return response

# Get server port
async def getServerPort(host, port):
    response = await sendCMD(host, port, '-get-port')
    return response

# Get info on if server is up (True) or down (False)
async def getServerStatus(host, port):
    response = await sendCMD(host, port, '-server-status')
    return response

# Send packet to server
async def sendCMD(HOST, PORT, cmd):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if cmd != '-update-server':
            s.settimeout(20)
        cmd = cmd.encode('utf8')
        s.connect((HOST, int(PORT)))
        s.sendall(cmd)
        returnVal = s.recv(1024)
        return returnVal.decode('utf8')
    
# Send update server command and restart server at 6 am cst
async def automatedUpdateServer():
    while True:
        time = datetime.utcnow()
        actualTime = time.hour*3600 + time.minute*60 + time.second

        # Calculate time till 6am cst
        if actualTime == 43200:
            waitTime = 0
        elif actualTime < 43200:
            waitTime = 43200 - actualTime
        else:
            waitTime = 86400 - actualTime + 43200
        await asyncio.sleep(waitTime)
        logger.info('Auto updating server and restarting...')
        for server in server_info.serverList.keys():
            await sendCMD(server.ip, server.controllerPort, '-update-server')