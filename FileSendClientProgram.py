# echo-client.py

import socket

HOSTS = ["tp-3a209-10.enst.fr", "tp-1a201-04.enst.fr", "tp-1a201-06.enst.fr"]  # The server's hostname or IP address
PORT = 65432  # The port used by the server
with open('sample1.txt', 'r') as f:
            lines = f.readlines() 

for host, line in zip(HOSTS, lines):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(s)
        s.connect((host, PORT))
        print(s)
        s.sendall(bytes(line, encoding='utf-8'))
        data = s.recv(1024)
    print(f"Received {data!r}")

