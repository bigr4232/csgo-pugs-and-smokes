import yaml

def loadYaml():
    with open('config.yaml', 'r') as config:
        content = yaml.safe_load(config)
    return content

loadYaml()