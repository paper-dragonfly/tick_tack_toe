from nose.tools import assert_equal 
import ttt.tick_tack_toe2 as tick
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

EMPTY_4X4_BOARD = [['_','_','_','_'],
                    ['_','_','_','_'],
                    ['_','_','_','_'],
                    ['_','_','_','_']]

X_4X4_BOARD = [['x', 'x', 'x', 'o'], 
                ['x', 'x', 'x', 'o'], 
                ['x', 'x', 'x', 'x'], 
                ['a', 'a', 'a', 'o']]

x_move_gameState = tick.GameState('test_xa1',x_move_board,'o',[(0,0)])
empty_gameState = tick.GameState('test_empty',empty_board,'x',[])

def test_basic():
    print("I RAN!", end='')
 

def test_board_size():
    with patch('builtins.input', lambda _: 'a'):
        assert_equal(tick.choose_board_size(),3)
    with patch('builtins.input', lambda _: 'b'):
        assert_equal(tick.choose_board_size(),4)

def test_save_load_game():
    with patch('builtins.input', lambda _: 'test_save'):
        tick.save_game(x_move_gameState,True)
        assert_equal(tick.load_saved_board(True).gb, x_move_board)

def test_add_axis_title():
    assert_equal(tick.add_axis_title(empty_board),[[' ', '1', '2', '3'], ['A', '_', '_', '_'], ['B', '_', '_', '_'], ['C', '_', '_', '_']])
    assert_equal(tick.add_axis_title(mid_game_board),[[' ', '1', '2', '3'], ['A', 'o', '_', '_'], ['B', 'x', 'x', '_'], ['C', '_', '_', 'o']])
    assert_equal(tick.add_axis_title(EMPTY_4X4_BOARD),[[' ', '1', '2', '3', '4'], ['A', '_', '_', '_', '_'], ['B', '_', '_', '_', '_'], ['C', '_', '_', '_', '_'],['D', '_', '_', '_', '_']])

def test_print_beautiful_board():
    assert_equal(tick.print_beautiful_board(tick.add_axis_title(empty_board)), '   1  2  3  \nA  _  _  _  \nB  _  _  _  \nC  _  _  _  \n')

def test_check_wins():
    assert_equal(tick.check_hor(empty_board),False)
    assert_equal(tick.check_hor(hor_win_board), 'x')

    assert_equal(tick.check_vert(empty_board),False)
    assert_equal(tick.check_vert(vert_win_board),'o')

    assert_equal(tick.check_di(empty_board),False)
    assert_equal(tick.check_di(di_win_board),'x')

    assert_equal(tick.check_win(mid_game_board), False)
    assert_equal(tick.check_win(vert_win_board), 'o')
    assert_equal(tick.check_win(X_4X4_BOARD),'x')


def test_convert():
    assert_equal(tick.convert('A2'), (0,1))


def test_check_availability():
    assert_equal(tick.check_availability(mid_game_board,1,1), False)
    assert_equal(tick.check_availability(mid_game_board,1,2), True)


def test_get_move():
    with patch('builtins.input', lambda _: 'a1'):
        assert_equal(tick.get_move(empty_gameState), (0,0))
    with patch('builtins.input', lambda _: 'save'):
        assert_equal(tick.get_move(empty_gameState), 'save')
    with patch('builtins.input', lambda _: 'undo'):
        assert_equal(tick.get_move(x_move_gameState), 'undo')


def test_update_board():
    assert_equal(tick.update_board(empty_gameState, (0,0)), x_move_board)


def test_undo_turn():
    assert_equal(tick.undo_turn(x_move_board, (0,0)), empty_board)
        
    
