import socket
import config_loader
import asyncio
import subprocess
import os
import logging

content = config_loader.loadYaml()
HOST = '0.0.0.0'
PORT = int(content['PORT'])
if '-port' in content['startCommand']:
    portStr = content['startCommand'][content['startCommand'].find('-port')+6:]
    csServerPort = portStr[0:portStr.find(' ')]
else:
    csServerPort = '27015'

# Logging
logger = logging.getLogger('logs')
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Initalize a command
def initCommand(inputCommand):
    inputCommand = inputCommand + '^M'
    command = ['screen', '-S', 'csgoServer', '-p0', '-X', 'stuff', inputCommand]
    return command

# Get output of server, finds value of command passed into function
def getServerOutput(command):
    asyncio.sleep(.5)
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
def isBot(line):
    for char in line:
        if char.isalpha():
            if char == 'B':
                return True
            else:
                return False

# Get number of players in the server
def getNumPlayers():
    cmd = initCommand('status')
    subprocess.run(cmd)
    asyncio.sleep(.5)
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
        elif count and line[0:5] != '65535' and not isBot(line):
            numPlayers += 1
    return numPlayers


# Send terminal command to start server
def startServer(startCommand):
    subprocess.run(['screen', '-dmS', 'csgoServer'])
    cmd = initCommand(startCommand)
    subprocess.run(cmd)
    asyncio.sleep(6)

# Send terminal command to stop server
def stopServer():
    subprocess.run(['screen', '-S', 'csgoServer', '-X', 'quit'])

# Send command to server
def sendCMD(command):
    cmd = initCommand(command)
    subprocess.run(cmd)

# Get server password
def getPassword():
    cmd = initCommand('sv_password')
    subprocess.run(cmd)
    response = getServerOutput('sv_password')
    return response

# Update server
def updateServer(steamCMDpath, csgoServerPath, startCommand, username, password):
    stopServer()
    cmd = f'{steamCMDpath} +force_install_dir {csgoServerPath} +login {username} {password} +app_update 730 +quit'
    subprocess.run(cmd, shell=True)
    startServer(startCommand)

# Get server password
def getPassword():
    cmd = initCommand('sv_password')
    subprocess.run(cmd)
    response = getServerOutput('sv_password')
    return response

# Parse command sent
# Returns string or '' for value not needed on return
def parseCommand(cmd):
    returnVal = ''
    if cmd[0] == '-':
        if cmd[1:] == 'start-server':
            startServer(content['StartCommand'])
        elif cmd[1:] == 'stop-server':
            stopServer()
        elif cmd[1:] == 'restart-server':
            stopServer()
            asyncio.sleep(1)
            startServer(content['StartCommand'])
        elif cmd[1:] == 'update-server':
            updateServer(content['steamCMDInstallPath'], os.getcwd() + 'game/bin/linuxsteamrt64/cs2', content['StartCommand'], content['serverLoginUsername'], content['serverLoginPassword'])
        elif cmd[1:] == 'get-password':
            returnVal = getPassword()
        elif cmd[1:] == 'get-port':
            returnVal = csServerPort
    else:
        sendCMD()
    return returnVal


# Start socket server
def startServer():
    logger.info('Successfully connected')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            data = conn.recv(1024)
            returnVal = parseCommand(data.decode('utf8'))
            if not data:
                break
            conn.sendall(returnVal.encode('utf8'))
            conn.close

# Start server socket. If error, wait 60 seconds and retry
def main():
    try:
        logger.info('Attempting server connection')
        startServer()
    except:
        logger.info('Server connection failed, retrying in 60 seconds')
        asyncio.sleep(60)
        main()

if __name__ == "__main__":
    main()