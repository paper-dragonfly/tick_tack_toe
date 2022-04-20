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
cur.execute("SELECT * FROM saved_games ")
data = cur.fetchall()
print(data)

# create_sport_table = """CREATE TABLE IF NOT EXISTS sport(
#     id SERIAL PRIMARY KEY, 
#     child_name VARCHAR(50) NOT NULL, 
#     sports VARCHAR(25))"""

# cur.execute(create_sport_table)
# print('successful added sports')
conn.commit()

conn.close() 