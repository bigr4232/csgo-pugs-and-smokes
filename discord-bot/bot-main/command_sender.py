import socket

# Send command to execute certain gamemode
async def gamemodeStart(gamemode, HOST, PORT):
    if gamemode == 'nade-practice':
        await sendCMD('exec nadeprac', HOST, PORT)

# Send changelevel command to server
async def changemap(map, HOST, PORT):
    cmd = (f'changelevel de_{map}')
    await sendCMD(cmd, HOST, PORT)

# Get server password
async def getPassword(HOST, PORT):
    response = await sendCMD('-get-password', HOST, PORT)
    return response

# Get server port
async def getServerPort(HOST, PORT):
    response = await sendCMD('-get-port', HOST, PORT)
    return response

# Send packet to server
async def sendCMD(cmd, HOST, PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        cmd = cmd.encode('utf8')
        s.connect((HOST, PORT))
        s.sendall(cmd)
        returnVal = s.recv(1024)
        return returnVal.decode('utf8')