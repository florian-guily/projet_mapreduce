# multiconn-client.py

import sys
import struct, pickle
import socket
from collections import Counter
import re

from obj.MyServer import PrincipalServer


# with open('sample1.txt', 'r') as f:
#             lines = f.readlines() 

# def map_count_word(text):
#     words = re.findall(r'[A-Za-z]+', text)
#     dico = Counter(words)
#     return dict(dico)

    
if __name__ == '__main__':
    HOSTS = ["tp-3a209-10.enst.fr", "tp-1a201-04.enst.fr", "tp-1a201-06.enst.fr"]  # The server's hostname or IP address
    PORT = 65432  # The port used by the server
    server = PrincipalServer(None, "localhost", PORT, -1)

    server.establish_connection(HOSTS)
    server.broadcast_msg(HOSTS)
    for id in range(server.nb_neighbours):
        server.send_msg(id, id)
    





