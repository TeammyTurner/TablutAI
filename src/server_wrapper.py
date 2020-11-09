import settings
import subprocess
import socket
import io
import time

class TablutServerWrapper(object):
    """
    Class wrapping server so multiple instances can be executed in parallel
    """

    def __init__(self):
        self._black_port = None
        self._white_port = None

    @property
    def black_port(self):
        return self._black_port

    @property
    def white_port(self):
        return self._white_port

    def available_ports(self):
        """
        Return the first two available ports over 5800
        https://codereview.stackexchange.com/questions/116450/find-available-ports-on-localhost
        """
        ports = []

        port = 5800
        while len(ports) < 2:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                res = sock.connect_ex(("localhost", port))
                if res > 0:
                    ports.append(port)

            port += 1

        return tuple(ports)

    def start(self):
        """
        Start a tablut server instance
        https://pythonspot.com/python-subprocess/
        """
        self._white_port, self._black_port = self.available_ports()

        self._process = subprocess.Popen([
            "java",
            "-jar",
            settings.TABLUT_SERVER,
            "-wp", str(self._white_port),
            "-bp", str(self._black_port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        
        #self._output = io.TextIOBase(self._process.stdout, encoding="utf-8")
        for line in io.TextIOWrapper(self._process.stdout, encoding="utf-8"):
            if "Waiting for connections..." in line:
                break

        time.sleep(1)

    def stop(self):
        self._process.terminate()
