import psycopg2
import config_loader
from state_to_abbrevation import stateToAbbrev

config = config_loader.loadYaml()
host = config['dbhost']
user = config['dbuser']
password = config['dbpassword']

# Add server to database
async def addServer(ip, location, discordName, port, link):
    with psycopg2.connect(host=host, user=user, password=password, dbname='servers') as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM serverlist;')
            servers = cur.fetchall()
            numServers = 0
            state = location[0].upper()
            state += location[1:].lower()
            for server in servers:
                if server[2] == state and server[3] == discordName:
                    numServers += 1
            serverid = f'{discordName}-{stateToAbbrev[state]}'
            if numServers > 0:
                serverid += f'-{str(numServers)}'
            cur.execute('INSERT INTO serverlist VALUES (%s, %s, %s, %s, %s, %s)', (ip, serverid, state, discordName, port, link))
            conn.commit()

# Get list of servers in database
async def getServers():
    with psycopg2.connect(host=host, user=user, password=password, dbname='servers') as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM serverlist;')
            return cur.fetchall()