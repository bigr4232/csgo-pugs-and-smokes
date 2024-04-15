import socket
import config_loader
import asyncio
import subprocess
import os
import logging
import sys
import datetime

# Globals
__version__ = '1.1.0'
content = config_loader.loadYaml()
HOST = '0.0.0.0'
PORT = int(content['PORT'])
csServerPath = content['startCommand'][:content['startCommand'].find('/game')]
if '-port' in content['startCommand']:
    portStr = content['startCommand'][content['startCommand'].find('-port')+6:]
    csServerPort = portStr[0:portStr.find(' ')]
else:
    csServerPort = '27015'

currentMap = content['startCommand'][content['startCommand'].find('+map')+5:]
currentMap = currentMap[:currentMap.find(' ')]

# Get input args
debugMode = False
logger = logging.getLogger('logs')
for arg in sys.argv:
    if arg == '-log':
        debugMode = True
        now = datetime.datetime.now()
        pre = now.strftime("%Y-%m-%d_%H:%M:%S")
        fh = logging.FileHandler(f'controller-{pre}-logs.log')
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

# Logging
logger = logging.getLogger('logs')
if debugMode:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Check if cs server is running
async def serverRunning():
    var = subprocess.check_output(["screen -ls; true"],shell=True)
    if ".csgoServer\t(" in var.decode():
        return True
    else:
        return False
    
# Initalize a command
async def initCommand(inputCommand):
    inputCommand = inputCommand + '^M'
    command = ['screen', '-S', 'csgoServer', '-p0', '-X', 'stuff', inputCommand]
    return command

# Get output of server, finds value of command passed into function
async def getServerOutput(command):
    await asyncio.sleep(.5)
    path = os. getcwd() + '/output.txt'
    subprocess.run(['screen', '-r', 'csgoServer', '-p0', '-X', 'hardcopy', path])
    with open('output.txt') as f:
        lines = f.readlines()
    subprocess.run(['rm', 'output.txt'])
    for line in reversed(lines):
        if command+' = ' in line:
            return line[14:line.find('\n')]
    return ''

# Check if player is a bot
async def isBot(line):
    for char in line:
        if char.isalpha():
            if char == 'B':
                return True
            else:
                return False

# Get number of players in the server
async def getNumPlayers():
    cmd = await initCommand('status')
    subprocess.run(cmd)
    await asyncio.sleep(.5)
    path = os. getcwd() + '/output.txt'
    subprocess.run(['screen', '-r', 'csgoServer', '-p0', '-X', 'hardcopy', path])
    with open('output.txt') as f:
        lines = f.readlines()
    subprocess.run(['rm', 'output.txt'])
    count = False
    numPlayers = 0
    for line in reversed(lines):
        if line == '#end\n':
            count = True
        elif line == '  id     time ping loss      state   rate adr name\n':
            break
        elif count and line[0:5] != '65535' and not await isBot(line):
            numPlayers += 1
    return numPlayers


# Send terminal command to start server
async def startServer(startCommand):
    if not await serverRunning():
        subprocess.run(['screen', '-dmS', 'csgoServer'])
        cmd = await initCommand(startCommand)
        subprocess.run(cmd)
        await asyncio.sleep(6)

# Send terminal command to stop server
async def stopServer():
    if await serverRunning():
        subprocess.run(['screen', '-S', 'csgoServer', '-X', 'quit'])

# Send command to server
async def sendCMD(command):
    cmd = await initCommand(command)
    subprocess.run(cmd)

# Get server password
async def getPassword():
    cmd = initCommand('sv_password')
    subprocess.run(cmd)
    response = await getServerOutput('sv_password')
    return response

# Update server
async def updateServer(csgoServerPath, startCommand):
    await stopServer()
    cmd = f'steamcmd +force_install_dir {csgoServerPath} +login anonymous +app_update 730 +quit'
    subprocess.run(cmd, shell=True)
    await startServer(startCommand)

# Get server password
async def getPassword():
    cmd = await initCommand('sv_password')
    subprocess.run(cmd)
    response = await getServerOutput('sv_password')
    return response

# Reload map on server
async def reloadMap():
    cmd = await initCommand(f'changelevel {currentMap}')
    subprocess.run(cmd)

# Parse command sent
# Returns string or '' for value not needed on return
async def parseCommand(cmd):
    returnVal = '-'
    if cmd[0] == '-':
        if cmd[1:] == 'start-server':
            await startServer(content['startCommand'])
        elif cmd[1:] == 'stop-server':
            await stopServer()
        elif cmd[1:] == 'restart-server':
            await stopServer()
            await asyncio.sleep(1)
            await startServer(content['startCommand'])
        elif cmd[1:] == 'update-server':
            await updateServer(csServerPath, content['startCommand'])
        elif cmd[1:] == 'get-password':
            returnVal = await getPassword()
        elif cmd[1:] == 'get-port':
            returnVal = csServerPort
        elif cmd[1:] == 'server-status':
            returnVal = str(await serverRunning())
        elif cmd[1:] == 'controller-version':
            returnVal = __version__
        elif cmd[1:] == 'reload-map':
            await reloadMap()
    else:
        if 'changelevel' in cmd:
            global currentMap
            currentMap = cmd[cmd.find('de_'):]
        await sendCMD(cmd)
    return returnVal


# Start socket server
async def startTCPServer(s):
    while True:
        conn, addr = s.accept()
        data = conn.recv(1024)
        receivedVal = data.decode('utf8')
        logger.debug(f'Received packet {receivedVal}')
        returnVal = await parseCommand(receivedVal)
        if not data:
            break
        logger.debug(f'Sending packet {returnVal}')
        conn.send(returnVal.encode('utf8'))
        conn.close

# Start server socket. If error, wait 60 seconds and retry
async def main():
    try:
        logger.info(f'Starting cs server controller (v{__version__})')
        logger.info('Attempting server connection')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        logger.info('Successfully connected, Listening')
        await startTCPServer(s)
    except Exception as e:
        logger.info(e)
        logger.info('Server connection failed, retrying in 60 seconds')
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        await asyncio.sleep(10)
        await main()

if __name__ == "__main__":
    asyncio.run(main())
