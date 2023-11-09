# This file is used for testing ten mans only

import yaml
import os
import os.path

async def fillTenMan(client, config):
    list = set()
    path = './bot-main/accounts.yaml'
    if os.path.isfile(path):
        with open('bot-main/accounts.yaml', 'r') as c:
            accounts = yaml.safe_load(c)
    guild = client.get_guild(int(config['discordGuildID']))
    for acc in accounts['accounts']:
        member = await guild.fetch_member(int(acc))
        list.add(member)
    return list
    