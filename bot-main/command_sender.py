import subprocess

# Initalize a command
async def initCommand(inputCommand):
    inputCommand = '\'' + inputCommand + '^M\''
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