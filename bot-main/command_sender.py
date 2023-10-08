import subprocess

# Initalize a command
async def initCommand(inputCommand):
    inputCommand = inputCommand + '^M'
    command = ['screen', '-S', 'csgoServer', '-X', 'stuff', inputCommand]
    return command

# Send terminal command to start server
async def startServer(startCommand):
    subprocess.run(['screen', '-dmS', 'csgoServer'])
    cmd = await initCommand(startCommand)
    subprocess.run(cmd)

# Send terminal command to stop server
async def stopServer():
    subprocess.run(['screen', '-S', 'csgoServer', '-X', 'quit'])

# Send command to execute certain gamemode
async def gamemodeStart(gamemode):
    if gamemode == 'nade-practice':
        cmd = await initCommand('exec nadeprac')
    subprocess.run(cmd)

# Send changelevel command to server
async def changemap(map):
    cmd = await initCommand(f'changelevel de_{map}')
    subprocess.run(cmd)

# Send command to server and return response
async def sendCMD(command):
    cmd = await initCommand(command)
    response = subprocess.run(cmd, capture_output=True)
    return response