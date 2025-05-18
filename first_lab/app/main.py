import sys, threading
import socket
import json
import time
from game import GameInstance
from P2Pnode import P2Pnode

def main():
    self_port = int(sys.argv[1])
    self_host = sys.argv[2]
    destination_host = sys.argv[3]
    destination_port = int(sys.argv[4])
    starter_server = self_port < destination_port
    game = GameInstance(starter_server)
    p2pnode = P2Pnode(game, self_port, self_host, destination_host, destination_port, starter_server)
    game.run(p2pnode, starter_server)
    
if __name__ == "__main__":
    main()