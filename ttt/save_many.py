import tick_tack_toe2 as tick
from unittest.mock import patch
from tick_tack_toe2 import EMPTY_3X3_BOARD
from string import ascii_letters 
import random
import json 
from pathlib import Path

alphabet = ascii_letters.lower()
game_state = tick.GameState('',EMPTY_3X3_BOARD,'x',[])

def save_many(game_state):
    for i in range(100):
        save_name = ''
        for l in range(6):
            # randomly generate name 10 letters long
            save_name += random.choice(alphabet)
        with patch('builtins.input', lambda _: save_name):
                tick.save_game(game_state)

        # file_name = f'docs/alphabetized/{save_name[0]}.json'
        # Path(file_name).touch(exist_ok=True)
        # with open(file_name,'r') as f:
        #     f_info = f.read()
        # if f_info:
        #     with patch('builtins.input', lambda _: save_name):
        #         tick.save_game(game_state,file_name)
        # else:
        #     with open(file_name,'w') as f:
        #         f.write('{}')
        #     with patch('builtins.input', lambda _: save_name):
        #         tick.save_game(game_state,file_name)

             

# def sort_games():
#     with open('docs/megafile.json','r') as f:
#         py_f_data = json.loads(f.read())
    


if __name__ == "__main__":      
    save_many(game_state)
