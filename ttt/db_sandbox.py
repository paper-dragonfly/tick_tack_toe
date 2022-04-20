# GOAL: save/retrieve ttt games from database using postgres
# STEPS
# use psycopg2 to connect to postgresql using python: DONE
# create a ttt_db to store games (multiple tables?): DONE
# create table(s) in ttt_db : DONE
# connect to db and add a game : DONE
# connect to db and load game: DONE
# integrate db saving into ttt game: DONE
# save a bunch of games to the db
# be able to load any of those games: DONE
# use indexing to make it easy to search db

import psycopg2
from configparser import ConfigParser #to do with accesing .ini files
import json 
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Union
import pdb


x_move_board= [['x','_','_'],
                 ['_','_','_'],
                 ['_','_','_']]

# define GameState class - object containing info for each game
class GameState:
    def __init__(self,name, gb,current_player, move_log) -> None:
        self.name = name
        self.gb: List[List] = gb
        self.current_player: str = current_player
        self.move_log: List[tuple] = move_log

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

    

# # opens connection to database, executes query, closes connection 
# def execute_query(sql):
#     conn = None
#     params = config()
#     conn = psycopg2.connect(**params)
#     cur = conn.cursor()
#     cur.execute(sql) 
#     conn.commit() 
#     conn.close()


# create postgres table with appropriate columns 
def create_saved_games_table():
    sql_create = """
    CREATE TABLE IF NOT EXISTS saved_games(
        game_id Serial PRIMARY KEY,
        game_name VARCHAR(50) NOT NULL,
        gb TEXT[3][3] NOT NULL,
        current_player VARCHAR(10), 
        move_log JSONB)"""

    conn = None
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    cur.execute(sql_create) 
    conn.commit() 
    conn.close()


def add_row_to_saved_games(game_state:GameState):
    sql= """INSERT INTO saved_games(game_name,gb,current_player,move_log)
            VALUES (%s,%s,%s,%s)"""
    
    conn = None
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    cur.execute(sql,(game_state.name, game_state.gb, game_state.current_player, json.dumps(game_state.move_log))) 
    conn.commit() 
    cur.close()
    conn.close()

def load_game_fm_db(game_state:GameState, game_name:str) -> GameState:
    sql = f"""SELECT * FROM saved_games WHERE saved_games.game_name = '{game_name}' """

    conn = None
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    cur.execute(sql,(game_state.name, game_state.gb, game_state.current_player, json.dumps(game_state.move_log))) 
    data = cur.fetchall()[0] 
    
    conn.commit() 
    cur.close()
    conn.close()  
    return GameState(data[1],data[2],data[3],data[4])

# create instance of GameState for testing purposes
db_test_game = GameState('db_test',x_move_board,'o',[(0,0)])

if __name__ == '__main__':
    # create_saved_games_table()
    # add_row_to_saved_games(db_test_game)
    # (db_test_game.name, db_test_game.gb, db_test_game.current_player, db_test_game.move_log)
    ngs = load_game_fm_db(db_test_game,'db_test')
    print(ngs.gb)
    