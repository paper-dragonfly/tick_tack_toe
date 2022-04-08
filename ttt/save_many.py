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

if __name__ == "__main__":      
    save_many(game_state)
