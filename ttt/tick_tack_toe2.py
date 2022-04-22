# TODO

import copy
import json 
from datetime import datetime
from pathlib import Path
import re
from sqlite3 import Cursor 
from typing import Dict, List, Tuple, Union
import psycopg2
from configparser import ConfigParser #to do with accesing .ini files
import pdb 

EXIT = 'exit'

INTRO_TEXT ="""
\nWelcome to Tick_Tack_Toe!\n
    What you can do on your turn: 
    Type coordinates to place your marker
    Type 's' or 'save' to save your game
    Type 'undo' to undo the last move
    Type 'end' to cancel the game\n """

EMPTY_3X3_BOARD = [['_','_','_'],
                   ['_','_','_'],
                   ['_','_','_']]

EMPTY_4X4_BOARD = [['_','_','_','_'],
                    ['_','_','_','_'],
                    ['_','_','_','_'],
                    ['_','_','_','_']]

class GameState:
    def __init__(self,name, gb,current_player, move_log, player1, player2) -> None:
        self.name = name
        self.gb: List[List] = gb
        self.current_player: str = current_player
        self.move_log: List[tuple] = move_log
        self.player1: str = player1
        self.player2: str = player2

# Get db connection data from config.ini 
def config(config_file:str='config/config.ini', section:str='postgresql') -> dict:
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


# def update_db(sql:str,str_subs:tuple=None) -> None:
#     conn = None
#     params = config()
#     conn = psycopg2.connect(**params)
#     cur = conn.cursor()
#     if not str_subs:
#         cur.execute(sql)
#     else:
#         cur.execute(sql,str_subs)
#     conn.commit()
#     cur.close()
#     conn.close() 

# def query_db(sql:str, str_subs:tuple=None) -> List[Tuple]:
#     conn = None
#     params = config()
#     conn = psycopg2.connect(**params)
#     cur = conn.cursor()
#     if not str_subs:
#         cur.execute(sql)
#     else:
#         cur.execute(sql,str_subs)
#     db_data = cur.fetchall() 
#     cur.close()
#     conn.close() 
#     return db_data 
        

def select_users(cur) -> tuple: 
    print("Select a user or create a new one:\n\nUSERS ")
    
    #print all user names already in db
    sql = """SELECT user_name FROM ttt_users"""
    cur.execute(sql)
    names : List[Tuple[str]] = cur.fetchall() 
    for i in range(len(names)):
        print(names[i][0])

    #get players' chosen user names
    player1 = input("\nPlayer1 user name: ")
    player2 = input("player2 user name: ")

    # add player to db if they don't already exist and assign them the lowest rank
    for player in (player1,player2):
        # pdb.set_trace()
        sql = """SELECT MAX("rank") FROM ttt_users"""
        cur.execute(sql)
        max_rank : int = cur.fetchall()[0][0]
        new_user_rank = max_rank + 1
        sql = """INSERT INTO ttt_users(user_name,rank) VALUES(%s,%s) ON CONFLICT (user_name) DO NOTHING"""
        str_subs = (player, new_user_rank)
        cur.execute(sql,str_subs)
    return (player1,player2)


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


def save_game(game_state:GameState, cur, conn) -> None:
    game_state.name = input('save as: ')

    # check if game already in db
    sql_check_db = "SELECT * FROM saved_games WHERE saved_games.game_name = %s"
    cur.execute(sql_check_db,(game_state.name,))
    name_match = cur.fetchall()
    if len(name_match) > 0: #update entry
        print("\nGame already exists, do you want to overwrite it?")
        overwrite = input("\nY/N: ")
        if overwrite.upper() == 'N':
            return save_game(game_state, cur)
        else: 
            sql = """UPDATE saved_games 
                SET gb = %s, current_player = %s, move_log = %s
                WHERE saved_games.game_name = %s"""
            str_subs = (game_state.gb, game_state.current_player, json.dumps(game_state.move_log), game_state.name)
    else: #add new entry
        sql = """INSERT INTO saved_games(game_name,gb,current_player,move_log,player1,player2)
                    VALUES (%s,%s,%s,%s,%s,%s)"""
        str_subs = (game_state.name, game_state.gb, game_state.current_player, json.dumps(game_state.move_log), game_state.player1, game_state.player2)
    
    cur.execute(sql,str_subs)
    conn.commit() 
    return True

def load_saved_board(cur) -> GameState:    
    game_names = []
    while len(game_names) == 0: 
        search = input("search for a game or press enter to list all games: ")

        #list games
        # TODO: change formatting to %s -> was getting tuple index out of range when I had %s in there??
        sql_list_games = f"""SELECT game_name FROM saved_games WHERE game_name LIKE '{search}%' """
        cur.execute(sql_list_games)
        game_names : List[str] = [t[0] for t in cur.fetchall()]
        if len(game_names) == 0:
            print("\nNo games found, try again")
        elif len(game_names) == 1:
            # if there is only one result, use that one automatically
            user_choice = game_names[0]
            print(f"\Game Loaded: {user_choice}")
        else: 
            print("\nSAVED GAMES")
            for i in range(len(game_names)):
                print(game_names[i])
            user_choice = input('\nChoose a game to load: ')
    
    #choose and load game
    sql_get_game = """SELECT * FROM saved_games WHERE saved_games.game_name = %s """
    str_subs = (user_choice,)
    cur.execute(sql_get_game,str_subs)
    game_names = cur.fetchone()
    # restart if user input not in db
    if game_names is None:
        print('\nInvalid name - must type name exactly')
        return load_saved_board(cur)
    # return loaded game
    else: 
        return GameState(game_names[1],game_names[2],game_names[3],game_names[4],game_names[5],game_names[6])
    

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
            

def check_win(gb:List[List],player1:str, player2:str) -> Union[str,bool]:
    poss = [check_hor(gb),check_vert(gb),check_di(gb)]
    for f in poss:
        if f:
            player = player1
            if f == 'o':
                player = player2
            print(f'{player} Wins, Game Over!\n')
            return player
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
    user_name = game_state.player1
    if game_state.current_player == "o":
        user_name = game_state.player2
    move = (input(f"\nPlayer {user_name} ({game_state.current_player}): ")).upper()
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

def update_user_stats(winner:str, loser:str):
    # get current user stats - wins, losses
    # TODO:Nico get rid of the for loop
    for player in (winner,loser):
        sql = """SELECT wins,losses FROM ttt_users WHERE ttt_users.user_name = %s"""
        str_subs = (player,)
        player_stats = query_db(sql,str_subs) 
    # change stats and update in db - wins/losses, percent_wins
        if player == winner:
            player_wins = player_stats[0][0] + 1
            player_percent_wins = (player_wins/(player_wins + player_stats[0][1]))*100 
            sql = """UPDATE ttt_users AS u SET wins= %s, percent_wins = %s WHERE u.user_name = %s"""
            str_subs = (player_wins, player_percent_wins, player) 
            update_db(sql,str_subs)
        elif player == loser:
            player_losses = player_stats[0][1] + 1
            player_percent_wins = (player_stats[0][0]/(player_losses + player_stats[0][0]))*100 
            sql = """UPDATE ttt_users AS u SET losses= %s, percent_wins = %s WHERE u.user_name = %s"""
            str_subs = (player_losses,player_percent_wins, player)
            update_db(sql,str_subs)
    # update rank - reranks all users
    sql = """SELECT user_name, percent_wins FROM ttt_users ORDER BY percent_wins DESC"""
    users_by_score = query_db(sql)
    ranks = [(users_by_score[0][0],1)] #[(user_name, rank)]
    for i in range(1,len(users_by_score)):
        # if adj scores are equal
        if users_by_score[i][1] == users_by_score[i-1][1]:
            ranks.append((users_by_score[i][0],ranks[i-1][1]))    
        else:
            ranks.append((users_by_score[i][0],i+1))
    for tup in ranks:
        sql = """UPDATE ttt_users SET rank = %s WHERE user_name = %s"""
        str_subs = (tup[1],tup[0])
        update_db(sql,str_subs)


def play() -> str:
    try:  
        conn = None
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        print(INTRO_TEXT)

        player1, player2 = select_users(cur)

        resp_game_type = input("\nWhat kind of game do you want? \nA. New Game \nB. Saved Game\n> ")
        # Saved game
        if resp_game_type[0].capitalize() == 'B' or resp_game_type[0].capitalize() == 'S':
            game_state = load_saved_board(cur)
            gb = game_state.gb
            
        #New game
        else:
            chosen_board_size = choose_board_size()
            if chosen_board_size == 4:
                gb = copy.deepcopy(EMPTY_4X4_BOARD)
            elif chosen_board_size == 3: 
                gb = copy.deepcopy(EMPTY_3X3_BOARD)
            game_state = GameState('new',gb,'x',list(),player1,player2)
        print_beautiful_board(add_axis_title(game_state.gb))

        winner = False
        while not winner:
            processed_user_input = get_move(game_state)
            # Save game
            if processed_user_input == 'save':
                save_game(game_state,cur, conn)
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
                winner = check_win(game_state.gb, game_state.player1, game_state.player2)
                if winner:
                    loser = game_state.player1
                    if winner == game_state.player1:
                        loser = game_state.player2
                    update_user_stats(winner,loser)  
                    break 
                if len(game_state.move_log) == len(game_state.gb)**2:
                    print('STALE MATE, GAME OVER!')
                    return EXIT 
            if game_state.current_player == 'x':
                game_state.current_player = 'o'
            elif game_state.current_player == 'o':
                game_state.current_player = 'x'
                
        return EXIT
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":      
    play()









