from nose.tools import assert_equal 
import ttt.tick_tack_toe as tick
import unittest.mock #is this neccessary? 
from unittest.mock import patch
import copy
import os
import json

empty_board= [['_','_','_'],
              ['_','_','_'],
              ['_','_','_']]

mid_game_board=[['o','_','_'],
                ['x','x','_'],
                ['_','_','o']]

di_win_board =[['x','_','o'],
               ['_','x','_'],
               ['_','_','x']]

hor_win_board =[['x','x','x'],
                ['o','o','_'],
                ['o','_','x']]

vert_win_board =[['o','x','x'],
                ['o','o','_'],
                ['o','_','x']]

x_move_board= [['x','_','_'],
                 ['_','_','_'],
                 ['_','_','_']]

o_move_board= [['_','_','_'],
                 ['_','o','_'],
                 ['_','_','_']]

def test_basic():
    print("I RAN!", end='')


# def test_load_saved_board():
#     test_str = json.dumps([['o','_','_'],['x','x','_'],['_','_','o']])
#     with open('docs/test.txt', 'w') as f:
#         f.write(test_str)
#     assert_equal(tick.load_saved_board('docs/test.txt'),mid_game_board) 

def test_display():
    assert_equal(tick.display(empty_board),[[' ', '1', '2', '3'], ['A', '_', '_', '_'], ['B', '_', '_', '_'], ['C', '_', '_', '_']])
    assert_equal(tick.display(mid_game_board),[[' ', '1', '2', '3'], ['A', 'o', '_', '_'], ['B', 'x', 'x', '_'], ['C', '_', '_', 'o']])

def test_beautiful_board():
    assert_equal(tick.beautiful_board(tick.display(empty_board)), ['   1  2  3', 'A  _  _  _', 'B  _  _  _', 'C  _  _  _'])

def test_check_wins():
    assert_equal(tick.check_hor(empty_board),False)
    assert_equal(tick.check_hor(hor_win_board), True)

    assert_equal(tick.check_vert(empty_board),False)
    assert_equal(tick.check_vert(vert_win_board),True)

    assert_equal(tick.check_di(empty_board),False)
    assert_equal(tick.check_di(di_win_board),True)

    assert_equal(tick.check_win(mid_game_board), False)
    assert_equal(tick.check_win(vert_win_board), True)

def test_convert():
    assert_equal(tick.convert('A2'), (0,1))

def test_turn():
    copy_empty_board = copy.deepcopy(empty_board)
    with patch('builtins.input', lambda _: 'a1'):
        assert_equal(tick.turn(copy_empty_board,1,'x'),x_move_board)

    ## how do I test if a function is recursive? 
    # with patch('builtins.input', lambda _:'a1'):
        # assert_equal(move_x(x_move_board), move_x(x_move_board))
    

