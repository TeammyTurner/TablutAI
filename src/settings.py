import os

PROJECT_DIR = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-1])

TABLUT_PATH = os.path.join(PROJECT_DIR, "tablut")
TABLUT_SERVER = os.path.join(TABLUT_PATH, "server.jar")
TABLUT_RANDOM_PLAYER = os.path.join(TABLUT_PATH, "random_player.jar")
