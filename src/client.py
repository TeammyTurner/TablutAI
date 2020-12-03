import argparse
import socket
import json
import numpy as np
import sys
import threading as t
import multiprocessing as mp
import time
import subprocess
import io
from mcts.mcts import MCTS
from tablut.game import Game, Player
from tablut.rules.ashton import Board
from tablut.player import RandomPlayer
from copy import deepcopy
import pprint


class BaseClient(object):
    """
    Base client class to be subclassed
    """

    def __init__(self, host: str, port: int, turn: str):
        if turn.lower() not in ["white", "black"]:
            raise ValueError("turn can only be 'black' or 'white'")

        self._host = host
        self._port = port
        self._turn = turn

    def send_name(self, name: str, turn: str):
        raise NotImplementedError

    def send_move(self, move: tuple):
        raise NotImplementedError

    def receive_state(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class GameEndedException(Exception):
    """
    Exception that gets thrown when the game is ended
    """
    pass


class Client(BaseClient):
    """
    Client used to connect to the tablut server
    """
    PIECE_MAPPING = {
        "WHITE": 2,
        "BLACK": -2,
        "KING": 1,
        "EMPTY": 0,
        "THRONE": 0  # This should be 0.7 but we're already considering it in the EMPTY_BOARD
    }

    COLUMN_INDICES = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
    EMPTY_BOARD = [[0, 0, 0, -0.5, -0.5, -0.5, 0, 0, 0],
                   [0, 0, 0, 0, -0.5, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [-0.5, 0, 0, 0, 0, 0, 0, 0, -0.5],
                   [-0.5, -0.5, 0, 0, 0.7, 0, 0, -0.5, -0.5],
                   [-0.5, 0, 0, 0, 0, 0, 0, 0, -0.5],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, -0.5, 0, 0, 0, 0],
                   [0, 0, 0, -0.5, -0.5, -0.5, 0, 0, 0]]

    def __init__(self, host: str, port: int, turn: str):
        super().__init__(host, port, turn)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self._host, self._port))

    def send_name(self, name: str):
        encoded = name.encode("UTF-8")
        length = len(encoded).to_bytes(4, 'big')
        self._sock.sendall(length + encoded)

    def send_move(self, start, end):
        """
        Sends move to the server.
        Move[0] is the starting position, move[1] the ending position
        """
        move = self.convert_move(start, end)
        move_obj = {
            "from": move[0],
            "to": move[1]
        }
        print(move)
        encoded = json.dumps(move_obj).encode("UTF-8")
        length = len(encoded).to_bytes(4, 'big')
        self._sock.sendall(length+encoded)

    def convert_board(self, java_board):
        board = np.array(self.EMPTY_BOARD)
        for row_i, row in enumerate(board):
            for column_i, column in enumerate(row):
                board[row_i][column_i] = column + \
                    self.PIECE_MAPPING[java_board[row_i][column_i]]
        return board

    def convert_move(self, start, end):
        return (self.COLUMN_INDICES[start[1]]+str(start[0]+1), self.COLUMN_INDICES[end[1]]+str(end[0]+1))

    def receive_state(self):
        """
        Returns a tuple containing the state received from the server and turn of the next player
        """
        # Wait for useful data
        received_char = self._sock.recv(1)
        while(received_char == b'\x00'):
            received_char = self._sock.recv(1)

        # Decode received data
        length_str = received_char + self._sock.recv(1)
        total = int.from_bytes(length_str, "big")
        state = self._sock.recv(total).decode("UTF-8")

        state = json.loads(state)

        return self.convert_board(state["board"]), state["turn"].lower()

    def close(self):
        self._sock.close()


TURN_MAPPING = {
    "black": Player.BLACK,
    "white": Player.WHITE
}

PORTS = {
    "white": 5800,
    "black": 5801
}

PLAYER_NAMES = {
    "white": "WANDA",
    "black": "COSMO"
}

WHITE_DEFAULT_MAX_DEPTH = 23


def setup_args():
    '''Parse the given arguments'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--player',
                        dest='player', type=str, required=True)
    parser.add_argument('-i', '--ip', dest='ip',
                        type=str, default="localhost")
    parser.add_argument('-t', '--timeout', dest='timeout',
                        type=int, default=50)
    parser.add_argument('-d', '--max-depth', dest='max_depth',
                        type=int, default=WHITE_DEFAULT_MAX_DEPTH)
    parser.add_argument('-c', '--c', dest='C',
                        type=int, default=np.sqrt(2))
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = setup_args()
    player_arg = str(args.player).lower()
    OUR_PLAYER = TURN_MAPPING[player_arg]
    # Fixing the parameters
    if player_arg == "black" and args.max_depth == WHITE_DEFAULT_MAX_DEPTH:
        max_depth = 35  # Default for black
    else:
        max_depth = args.max_depth
    C = args.C
    timeout = int(args.timeout) - 5

    c1 = Client(args.ip, PORTS[player_arg], player_arg)
    c1.send_name(PLAYER_NAMES[player_arg])

    board = Board()
    game = Game(board)
    # Main game loop
    try:
        while not game.ended:
            state = None
            while state is None:
                state, turn = c1.receive_state()
                game.board.board = state
                if turn not in ["black", "white"]:
                    raise GameEndedException
                game.turn = TURN_MAPPING[turn]
                print(state, turn)
            if game.turn == OUR_PLAYER:
                mcts = MCTS(deepcopy(game), OUR_PLAYER,
                            max_depth=max_depth, C=C)
                start, end = mcts.search(timeout)
                print(start, end)
                c1.send_move(start, end)
    except GameEndedException:
        print("Game ended with state {}".format(turn))

    c1.close()
