import yaml

def loadYaml():
    with open('config.yaml', 'r') as config:
        content = yaml.safe_load(config)
    return content

def setYaml(host, port, startcommand, steamcmdinstallpath, serverusername, serverpassword):
    content = loadYaml()
    content['HOST'] = host
    content['PORT'] = port
    content['startCommand'] = startcommand
    content['steamCMDInstallPath'] = steamcmdinstallpath
    content['serverLoginUsername'] = serverusername
    content['serverLoginPassword'] = serverpassword
    with open('config.yaml', 'w') as config:
        yaml.safe_dump(content, config)