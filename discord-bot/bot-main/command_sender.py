import socket
from datetime import datetime
import asyncio
import config_loader
import logging

config = config_loader.loadYaml()
HOST = config['HOST']
PORT = config['PORT']

# Logging
logger = logging.getLogger('logs')
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Send command to execute certain gamemode
async def gamemodeStart(gamemode):
    if gamemode == 'nade-practice':
        await sendCMD('exec nadeprac')

# Send changelevel command to server
async def changemap(map):
    cmd = (f'changelevel de_{map}')
    await sendCMD(cmd)

# Get server password
async def getPassword():
    response = await sendCMD('-get-password')
    return response

# Get server port
async def getServerPort():
    response = await sendCMD('-get-port')
    return response

# Send packet to server
async def sendCMD(cmd):
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

        # calculate time till 6am cst
        if actualTime == 43200:
            waitTime = 0
        elif actualTime < 43200:
            waitTime = 43200 - actualTime
        else:
            waitTime = 86400 - actualTime + 43200
        await asyncio.sleep(waitTime)
        logger.info('Auto updating server and restarting...')
        sendCMD('-update-server')