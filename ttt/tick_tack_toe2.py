# TO DO
# create config file for save.txt 

import copy
import json 
from datetime import datetime
from pathlib import Path
import re 
from typing import Dict, List, Tuple, Union
import psycopg2
from configparser import ConfigParser #to do with accesing .ini files
import pdb 

EXIT = 'exit'

EMPTY_3X3_BOARD = [['_','_','_'],
                   ['_','_','_'],
                   ['_','_','_']]

EMPTY_4X4_BOARD = [['_','_','_','_'],
                    ['_','_','_','_'],
                    ['_','_','_','_'],
                    ['_','_','_','_']]

class GameState:
    def __init__(self,name, gb,current_player, move_log) -> None:
        self.name = name
        self.gb: List[List] = gb
        self.current_player: str = current_player
        self.move_log: List[tuple] = move_log

def choose_board_size() -> int:
    resp_choice = input('Choose a board size \n a. 3x3 \n b. 4x4\n> ') 
    size = None
    if resp_choice[0].lower() == 'a' or resp_choice[0] == '3':
        size = 3
    elif resp_choice[0].lower() == 'b' or resp_choice[0] == '4':
        size = 4
    else:
        print('Invalid choice. Pick a or b')
        choose_board_size()
    return size 


# returns path to directory where game is/should be saved
def get_appropriate_save_directory(config_file:str,test=False) -> str:    
    config = configparser.ConfigParser()
    config.read(config_file)
    if test == True:
        return config.get('INDEX_ALPHABET_FILES','saved_test_games')
    return config.get('INDEX_ALPHABET_FILES','saved_games_directory')
    # eg "docs/alphebetized"

# Get db connection data from config.ini 
def config(config_file:str='config/config.ini', section:str='postgresql') -> dict:
    # pdb.set_trace()
    parser = ConfigParser()
    parser.read(config_file)
    db_params = {}
    if parser.has_section(section):
        item_tups = parser.items(section)
        for tup in item_tups:
            db_params[tup[0]] = tup[1]
    else:
        raise Exception(f"Section {section} not found in file {config_file}")
    return db_params 

# Create table (if unexistant) in postgres db to store info of saved games 
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

def save_game(game_state:GameState) -> None:
    # pdb.set_trace()
    game_state.name = input('save as: ')
    overwrite = None

    conn = None
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    # check if game already in db
    sql_check_db = "SELECT * FROM saved_games WHERE saved_games.game_name = %s"
    cur.execute(sql_check_db,(game_state.name,))
    db_data = cur.fetchall()
    if len(db_data) > 0: #update entry
        print("\nGame already exists, do you want to overwrite it?")
        overwrite = input("\nY/N: ")
        if overwrite.upper() == 'N':
            cur.close()
            conn.close()
            # pdb.set_trace()
            return save_game(game_state)
        else: 
            sql = """UPDATE saved_games 
                SET gb = %s, current_player = %s, move_log = %s
                WHERE saved_games.game_name = %s"""
            vals = (game_state.gb, game_state.current_player, json.dumps(game_state.move_log), game_state.name)
    else: #add new entry
        sql = """INSERT INTO saved_games(game_name,gb,current_player,move_log)
                    VALUES (%s,%s,%s,%s)"""
        vals = (game_state.name, game_state.gb, game_state.current_player, json.dumps(game_state.move_log))
    
    cur.execute(sql,vals)
    conn.commit() 
    cur.close()
    conn.close()
    return True

def load_saved_board() -> GameState:
    conn = None
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    
    #list games
    sql_list_games = """SELECT game_name FROM saved_games"""
    cur.execute(sql_list_games)
    game_data = cur.fetchall()
    print("\nSAVED GAMES")
    for i in range(len(game_data)):
        print(game_data[i][0])
    
    #choose and load game
    user_choice = input('\nChoose a game to load: ')
    sql_get_game = """SELECT * FROM saved_games WHERE saved_games.game_name = %s """
    vals = (user_choice,)
    cur.execute(sql_get_game,vals)
    game_data = cur.fetchone()
    # restart if user input not in db
    if game_data == None:
        print('Invalid name - must type name exactly')
        cur.close()
        conn.close()
        load_saved_board()
    #close connection, return loaded game
    else:
        cur.close()
        conn.close()  
        return GameState(game_data[1],game_data[2],game_data[3],game_data[4])
    

# VISUAL | Adds row and colum labels - asethetic only
def add_axis_title(gb:List[List]) -> List[List]:
    gb_copy = copy.deepcopy(gb) 
    board_size = len(gb)
    col_head = [" "]
    for i in range(board_size):
        col_head.append(str(i+1))
    gb_copy.insert(0,col_head)

    alphabet = ["A","B","C","D"]
    row_head = [""]
    for i in range(board_size): 
        row_head.append(alphabet[i])
    for i in range(1,(board_size+1)):
        gb_copy[i].insert(0,f'{row_head[i]}')
    return gb_copy

# VISUAL | prints out board nicely
def print_beautiful_board(gb_copy:List[List]) -> str:
    print('\n')
    size = len(gb_copy)
    board_string = str()
    for r in range(size):
        for c in range(size):
            board_string += f"{gb_copy[r][c]}  "
        board_string += "\n"
    print(board_string)
    return board_string
     

def check_hor(gb:List[List]) -> Union[str,bool]:
    board_size = len(gb)
    for r in gb:
        s_check = 0
        target = r[0]
        for c in r:
            if c != '_' and c == target:
                s_check +=1
                if s_check == board_size:
                    return target 
    return False


def check_vert(gb:List[List]) -> Union[str,bool]:
    board_size = len(gb)
    col = 0
    for c in range(board_size):
        s_check = 0
        target = gb[0][c]
        col += 1
        for r in range(board_size):
            if gb[r][c] != '_' and gb[r][c] == target:
                s_check += 1
                if s_check == board_size:
                    return target
    return False 


def check_di(gb:List[List]) -> Union[str,bool]:
    board_size = len(gb)
    
    target = gb[0][0]
    s_check = 0
    for i in range(board_size):
        if gb[i][i] == target and gb[i][i] != '_':
            s_check += 1
        if s_check == board_size:
            return target 
    
    target = gb[0][-1]
    s_check = 0
    for i in range(board_size):
        if gb[i][-(i+1)] == target and gb[i][-(i+1)] != '_':
            s_check += 1
        if s_check == board_size:
            return target 
    return False
            

def check_win(gb:List[List]) -> Union[str,bool]:
    poss = [check_hor(gb),check_vert(gb),check_di(gb)]
    for f in poss:
        if f:
            print(f'{f} Wins, Game Over!\n')
            return f
    else:
        return False


def convert(move:str) -> tuple:
    move = move.upper()
    con_dict = {
        'A1' : [0,0],
        'A2' : [0,1],
        'A3' : [0,2],
        'A4' : [0,3],
        'B1' : [1,0],
        'B2' : [1,1],
        'B3' : [1,2],
        'B4' : [1,3],
        'C1' : [2,0],
        'C2' : [2,1],
        'C3' : [2,2],
        'C4' : [2,3],
        'D1' : [3,0],
        'D2' : [3,1],
        'D3' : [3,2],
        'D4' : [3,3],
         }
    r = con_dict[move][0]
    c = con_dict[move][1]
    return r,c

def check_availability(gb:List[List],r:int,c:int) -> bool:
    if gb[r][c] == '_':
        return True 
    else:
        return False
            
def get_move(game_state: GameState) -> Union[Tuple,str]:
    move = (input(f"\nPlayer {game_state.current_player}: ")).upper()
    if move[0] == 'S':
        return 'save'
    if move == 'UNDO':
        if len(game_state.move_log) == 0:
            print('No move to undo')
            return get_move(game_state)
        return 'undo'
    board_size = len(game_state.gb)
    if board_size == 3:
        valid_moves = re.findall("^(A|B|C).*(1|2|3)$", move)
    if board_size == 4:
        valid_moves = re.findall("^(A|B|C|D).*(1|2|3|4)$", move)
    if valid_moves:
        r,c = convert(move)
        available = check_availability(game_state.gb,r,c)
        if not available:
            print('\nInvalid, spot already taken\n')
            return get_move(game_state)
        else:
            return r,c
    else:
        print('\nInvalid entry, try again\n')
        return get_move(game_state)

def update_board(game_state: GameState, coordinates:tuple) -> List[List]:
    gb_copy = copy.deepcopy(game_state.gb)
    gb_copy[coordinates[0]][coordinates[1]] = game_state.current_player
    print_beautiful_board(add_axis_title(gb_copy))
    return gb_copy


def undo_turn(gb:List[List],last_coordinates:tuple) -> List[List]:
    gb_copy = copy.deepcopy(gb)
    r,c = last_coordinates
    gb_copy[r][c] = '_'
    return gb_copy 


def play() -> str:
    print("\nWelcome to Tick_Tack_Toe\nNote: write 's' on your turn to save the game\n")
    resp_game_type = input("What kind of game do you want? \nA. New Game \nB. Saved Game\n> ")
    # Saved game
    if resp_game_type[0].capitalize() == 'B' or resp_game_type[0].capitalize() == 'S':
        game_state = load_saved_board()
        gb = game_state.gb
        current_player = game_state.current_player
        move_log = game_state.move_log
    #New game
    else:
        chosen_board_size = choose_board_size()
        if chosen_board_size == 4:
            gb = copy.deepcopy(EMPTY_4X4_BOARD)
        elif chosen_board_size == 3: 
            gb = copy.deepcopy(EMPTY_3X3_BOARD)
        game_state = GameState('new',gb,'x',list())
    print_beautiful_board(add_axis_title(game_state.gb))

    winner = False
    while not winner:
        processed_user_input = get_move(game_state)
        # Save game
        if processed_user_input == 'save':
            save_game(game_state)
            print('your game has been saved')
            return EXIT
        # Undo last move
        elif processed_user_input == 'undo':
            last_coordinate = game_state.move_log.pop()
            game_state.gb = undo_turn(game_state.gb,last_coordinate)
            print_beautiful_board(add_axis_title(game_state.gb))
       # update game with new move
        else:
            game_state.gb = update_board(game_state, processed_user_input)
            game_state.move_log.append(processed_user_input)
            winner = check_win(game_state.gb)
            if winner:
                break 
            if len(game_state.move_log) == len(game_state.gb)**2:
                print('STALE MATE, GAME OVER!')
                return EXIT 
        if game_state.current_player == 'x':
            game_state.current_player = 'o'
        elif game_state.current_player == 'o':
            game_state.current_player = 'x'
            
    return EXIT

if __name__ == "__main__":      
    play()









