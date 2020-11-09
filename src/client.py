import settings
import socket
import json
import numpy as np
import sys
import threading as t
import multiprocessing as mp
import time
import subprocess
import io


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


class Client(BaseClient):
    """
    Client used to connect to the tablut server
    """
    CELL_MAPPING = {
        "EMPTY": 0,
        "BLACK": -1,
        "WHITE": 1,
        "KING": 69
    }

    def __init__(self, host: str, port: int, turn: str):
        super().__init__(host, port, turn)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self._host, self._port))

    def send_name(self, name: str):
        encoded = name.encode("UTF-8")
        length = len(encoded).to_bytes(4, 'big')
        self._sock.sendall(length + encoded)

    def send_move(self, move: tuple):
        """
        Sends move to the server.
        Move[0] is the starting position, move[1] the ending position
        """
        move_obj = {
            "from": move[0],
            "to": move[1]
        }

        encoded = json.dumps(move_obj).encode("UTF-8")
        length = len(encoded).to_bytes(4, 'big')
        self._sock.sendall(length+encoded)

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

        # convert cell to own mapping
        state["board"] = [list(map(lambda x: self.CELL_MAPPING[x], row))
                          for row in state["board"]]

        return state["board"], state["turn"].lower()

    def close(self):
        self._sock.close()


class RandomClient(BaseClient):
    """
    Wrapper for java random client
    """
    
    def __init__(self, host: str, port: int, turn: str):
        self._host = host
        self._port = port
        self._turn = turn
    
    def send_name(self, name: str):
        """
        Name is actually sent by the java script, just ignore the param
        The method itself starts a java process with random_player.jar
        """
        self._process = subprocess.Popen([
            "java",
            "-jar",
            settings.TABLUT_RANDOM_PLAYER,
            self._turn,
            str(self._port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        for line in io.TextIOWrapper(self._process.stdout, encoding="utf-8"):
            if "You are player" in line:
                break

        time.sleep(1)

    def send_move(self, move: tuple):
        # Move is automatically sent by the process
        pass

    def receive_state(self):
        # No need to receive state, it's handled by process
        pass

    def close(self):
        self._process.terminate()

if __name__ == "__main__":
    # Test client from command line
    import server_wrapper

    server = server_wrapper.TablutServerWrapper()
    server.start()

    host = "localhost"
    c1 = Client(host, server.black_port, "black")
    c1.send_name("client_1")

    c2 = RandomClient(host, server.white_port, "white")
    c2.send_name("random_client")

    state1 = None
    while state1 is None:
        state1 = c1.receive_state()
    print(state1)

    c1.close()
    c2.close()
    server.stop()
