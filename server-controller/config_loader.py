import yaml

def loadYaml():
    with open('config.yaml', 'r') as config:
        content = yaml.safe_load(config)
    return content

def setYaml(port, startcommand):
    content = loadYaml()
    content['PORT'] = port
    content['startCommand'] = startcommand
    with open('config.yaml', 'w') as config:
        yaml.safe_dump(content, config)