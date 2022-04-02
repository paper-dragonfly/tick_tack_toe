#Create game that can be saved
import copy
import json 
from datetime import datetime
EXIT = 'exit'

EMPTY_BOARD = [['_','_','_'],
               ['_','_','_'],
               ['_','_','_']]

def save_game(gb:str, file_name:str):
    with open(file_name,'r') as f:
        save_dict = json.loads(f.read())
    save_name = input('save as: ')
    save_name = save_name + " " + str(datetime.now())
    save_dict[save_name] = gb 
    save_str = json.dumps(save_dict) 
    with open(file_name, 'w') as f:
        f.write(save_str)

def load_saved_board(file_name:str):
    with open(file_name) as f:    
        f_info = f.read()
    py_info = json.loads(f_info) 
    key_list = py_info.keys()
    n = 1 
    num_name_dict = {}
    for key in key_list:
        num_name_dict[n] = key
        n += 1
    print(num_name_dict)
    game_choice = int(input('Choose a game to load: ')) 
    return py_info[num_name_dict[game_choice]]
    

# VISUAL | Adds row and colum labels - asethetic only
def display(gb):
    gb_copy = copy.deepcopy(gb) 
    gb_copy.insert(0,[' ','1','2','3'])
    letlist = ["","A","B","C"]
    for i in range(1,4):
        gb_copy[i].insert(0,f'{letlist[i]}')
    return gb_copy

# VISUAL | prints out board nicely
def beautiful_board(display_output):
    string_list = [] #exists for test purposes
    for i in range(4):
        string = (f"""{display_output[i][0]}  {display_output[i][1]}  {display_output[i][2]}  {display_output[i][3]}""")
        print(string)
        string_list.append(string)
    return string_list
     

# Horizontal win?
def check_hor(gb):
    for r in gb:
        if r[0] == r[1] == r[2] != '_':
            print(f"{r[0]} Wins!")
            return True 
    return False

#vertical win?
def check_vert(gb):
    for c in range(3):
        if gb[0][c]== gb[1][c]==gb[2][c] != '_':
            print(f'{gb[0][c]} wins!')
            return True
    return False

# Diagonal win?
def check_di(gb):
    if gb[0][0]==gb[1][1]==gb[2][2] != "_":
        return True
    elif gb[0][2]==gb[1][1]==gb[2][0] != "_":
        return True
    else:
        return False

# Any wins?
def check_win(gb):
    if check_di(gb) or check_hor(gb) or check_vert(gb) == True:
        return True
    else:
        return False

# NEEDED?
def convert(move):
    move = move.upper()
    con_dict = {
        'A1' : [0,0],
        'A2' : [0,1],
        'A3' : [0,2],
        'B1' : [1,0],
        'B2' : [1,1],
        'B3' : [1,2],
        'C1' : [2,0],
        'C2' : [2,1],
        'C3' : [2,2],
         }
    r = con_dict[move][0]
    c = con_dict[move][1]
    return r,c
        

# Player 1 (x) moves: print board, submit choice
def turn(gb, player, symbol):
    beautiful_board(display(gb))
    move = input(f"\nPlayer {player}: ")
    try:
        r,c = convert(move)
        if gb[r][c] == '_':
            gb[r][c] = symbol
            return gb
        else:
            print('\nInvalid move, spot already taken\n')
            return turn(gb,player,symbol)
    except KeyError:
        if move.lower() == 'save':
            save_game(gb,'docs/ttt_game.txt')
            print('your game has been saved')
            return EXIT
        else:
            print("\nInvalid entry, try again\n")
            return turn(gb,player,symbol)


def play():
    print("Welcome to Tick_Tack_Toe")
    # 3x3 or 4x4 - changes gb 
    game = input("Do you want to open a New game or Saved game? ")
    if game[0].capitalize() == 'S':
        gb = load_saved_board('docs/ttt_game.txt')
    else:
        gb = copy.deepcopy(EMPTY_BOARD)

    win = False
    while not win:
        win = check_win(gb)
        x_move = turn(gb,1,'x')
        if x_move == EXIT:
            return EXIT
        win = check_win(gb)
        if win == True:
            print('\nGame Over!')
            return EXIT
        o_move = turn(gb,2,'o')
        if o_move == EXIT:
            return EXIT
        win = check_win(gb) 
    print(beautiful_board(display(gb)))
    print('\nGame Over!')
    return 'End'

if __name__ == "__main__":      
    play()









