import subprocess
import asyncio
import os

# Initalize a command
async def initCommand(inputCommand):
    inputCommand = inputCommand + '^M'
    command = ['screen', '-S', 'csgoServer', '-p0', '-X', 'stuff', inputCommand]
    return command

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

# Send terminal command to start server
async def startServer(startCommand):
    subprocess.run(['screen', '-dmS', 'csgoServer'])
    cmd = await initCommand(startCommand)
    subprocess.run(cmd)
    await asyncio.sleep(6)
    return await getPassword()


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

# Get server password
async def getPassword():
    cmd = await initCommand('sv_password')
    subprocess.run(cmd)
    response = await getServerOutput('sv_password')
    return response

# Update server
async def updateServer(steamCMDpath, csgoServerPath, startCommand):
    await stopServer()
    cmd = f'{steamCMDpath} +force_install_dir {csgoServerPath} +login anonymous +app_update 730 +quit'
    subprocess.run(cmd, shell=True)
    return await startServer(startCommand)

