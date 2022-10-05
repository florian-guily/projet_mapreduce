# echo-client.py

import socket

HOST = "tp-3a209-10.enst.fr"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    with open('SimpleClientProgram.py') as f:
        data = f.read()
    s.connect((HOST, PORT))
    s.sendall(bytes(data, encoding='utf-8'))
    data = s.recv(1024)

print(f"Received {data!r}")