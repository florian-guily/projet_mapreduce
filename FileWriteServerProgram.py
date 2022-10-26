# echo-server.py

import socket
from collections import Counter
import re

def map_count_word(text):
    words = re.findall(r'[A-Za-z]+', text)
    dico = Counter(words)
    return dict(dico)

HOST = ""  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        print(conn)
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            count_word = map_count_word(data)
            with open("./count_word.txt", 'w') as f:
                f.write(str(count_word))
                msg = f"Wrote data {count_word}".encode()
                conn.sendall(msg)