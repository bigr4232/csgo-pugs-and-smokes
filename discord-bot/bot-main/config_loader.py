import yaml

def loadYaml():
    with open('config.yaml', 'r') as config:
        content = yaml.safe_load(config)
    return content

def setYaml(discordbottoken, discordchannel, discordadminrole, discordguildid, discordowner, dbhost, dbuser, dbpassword):
    content = loadYaml()
    content['discordBotToken'] = discordbottoken
    content['discordChannel'] = discordchannel
    content['discordAdminRole'] = discordadminrole
    content['discordGuildID'] = discordguildid
    content['discordOwnerID'] = discordowner
    content['dbhost'] = dbhost
    content['dbuser'] = dbuser
    content['dbpassword'] = dbpassword
    with open('config.yaml', 'w') as config:
        yaml.safe_dump(content, config)

loadYaml()