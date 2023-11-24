import psycopg2
import config_loader
from state_to_abbrevation import stateToAbbrev

config = config_loader.loadYaml()
dbname = config['dbserversname']
host = config['dbhost']
user = config['dbuser']
password = config['dbpassword']

#conn = psycopg2.connect(host=host, user=user, password=password, dbname=dbname)
#cur = conn.cursor()

#cur.execute('INSERT INTO serverlist VALUES (%s, %s, %s, %s)', ('70.190.28.30', 'ryan-IL', 'Illinois', '***REMOVED***'))

#cur.execute("SELECT * FROM serverlist;")
#test = cur.fetchone()

#conn.commit()

#cur.close()
#conn.close()

# Add server to database
async def addServer(ip, location, discordName, port, link):
    with psycopg2.connect(host=host, user=user, password=password, dbname=dbname) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM serverlist;')
            servers = cur.fetchall()
            numServers = 0
            for server in servers:
                if server[2] == location and server[3] == discordName:
                    numServers += 1
            state = stateToAbbrev[0].upper()
            state += stateToAbbrev[1:].lower()
            serverid = f'{discordName}-{stateToAbbrev[location]}'
            if numServers > 0:
                serverid += f'-{str(numServers)}'
            cur.execute('INSERT INTO serverlist VALUES (%s, %s, %s, %s, %s, %s)', (ip, serverid, location, discordName, port, link))
            conn.commit()

# Get list of servers in database
async def getServers():
    with psycopg2.connect(host=host, user=user, password=password, dbname=dbname) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM serverlist;')
            return cur.fetchall()