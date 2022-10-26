# multiconn-server.py
from ast import main
import sys
import struct, pickle
import socket
from collections import Counter
import re
from obj.MyServer import PrincipalServer

def map_count_word(text):
    words = re.findall(r'[A-Za-z]+', text)
    dico = Counter(words)
    return dict(dico)

# SERVER_LIST = []

# def send_msg(sock, data):
#     serialized_data = pickle.dumps(data)
#     sock.sendall(struct.pack('>I', len(serialized_data)) + serialized_data)


# def recv_msg(sock : socket):
#     # Read message length and unpack it into an integer
#     raw_msglen = sock.recv(4)
#     if not raw_msglen:
#         return None
#     msglen = struct.unpack('>I', raw_msglen)[0]
#     # Read the message data
#     return recvall(sock, msglen)

# def recvall(sock, n):
#     # Helper function to recv n bytes or return None if EOF is hit
#     data = bytearray()
#     while len(data) < n:
#         packet = sock.recv(n - len(data))
#         if not packet:
#             return None
#         data.extend(packet)
#     msg = pickle.loads(data)
#     print(f"Received msg : {msg}")
#     return msg

def init(addr, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((addr, port))
    s.listen()
    server = PrincipalServer(s, addr, port)
    # server_index["server"] = {"sock": s, "addr": 'localhost'}
    client_sock, client_addr = s.accept()
    server.set_client(client_sock, client_addr)
    
    client_id = server.client.recv_msg() # useless as we label client_id as "client"
    
    server_list = server.client.recv_msg()
    id = server.client.recv_msg()
    server.set_id(id)
    return server, server_list

# def establish_connection(id, server_list, server_index):
#     for i, server_addr in enumerate(server_list[id+1:]):
#         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         s.connect((server_addr, PORT))
#         server_index[i+id+1] = {"sock": s, "addr": server_addr}
#         print(f"Connected to server {i+id+1} at address {server_addr}")
#         send_msg(s, id)

# def accept_server(server_index, id):
#     accepted_server = 0
#     while accepted_server < id:
#         s, server_addr = server_index["server"]["sock"].accept()
#         server_id = recv_msg(s)
#         server_index[server_id] = {"sock": s, "addr": server_addr}
#         print(f"Accepted server {server_id} at address {server_addr}")
#         accepted_server += 1
    
if __name__ == '__main__':
    HOST, PORT = "", 65432

    server, server_list = init(HOST, PORT)
    server.establish_connection(server_list)
    server.accept_server()




