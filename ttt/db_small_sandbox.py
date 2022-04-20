import psycopg2
from configparser import ConfigParser #to do with accesing .ini files


# Get connection data from config.ini 
def config(config_file:str='config/config.ini', section:str='postgresql') -> dict:
    # pdb.set_trace()
    parser = ConfigParser()
    parser.read(config_file)
    db = {}
    if parser.has_section(section):
        item_tups = parser.items(section)
        for tup in item_tups:
            db[tup[0]] = tup[1]
    else:
        raise Exception(f"Section {section} not found in file {config_file}")
    return db 

params = config()
conn = psycopg2.connect(**params)
cur = conn.cursor()

####
name = 'db_tet'
sql = "SELECT * FROM saved_games WHERE saved_games.game_name = %s"
sql2 = "SELECT game_name FROM saved_games"
val = (name,)
# cur.execute(sql,val)
cur.execute(sql2)
data = cur.fetchall()
for i in range(len(data)):
    print(data[i][0])
# print(len(data))
print(data)
#### 

conn.commit()
conn.close() 