import abc
import struct, pickle
import socket
from collections import Counter
from abc import ABC, abstractmethod

class Server (ABC):   

    def __init__(self, sock : socket.socket, addr, id = None):
        self.id = id
        self.sock = sock
        self.addr = addr
    
    @abstractmethod
    def send_msg(self):
        pass

    @abstractmethod
    def recv_msg(self):
        pass

class NeighbourServer(Server):
    def __init__(self, sock, addr, principal_id, id=None):
        super().__init__(sock, addr, id)
        self.principal_id = principal_id
    
    def set_id(self, id):
        self.id = id

    def send_msg(self, data):
        serialized_data = pickle.dumps(data)
        self.sock.sendall(struct.pack('>I', len(serialized_data)) + serialized_data)

    def recv_msg(self):
        # Read message length and unpack it into an integer
        sock = self.sock
        raw_msglen = sock.recv(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        return self.recvall(msglen)

    def recvall(self, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < n:
            packet = self.sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        msg = pickle.loads(data)
        print(f"[{self.principal_id}] Received msg : {msg}")
        return msg

class PrincipalServer(Server):
    def __init__(self, sock : socket.socket, addr, port, id = None):
        super().__init__(sock, addr, id)
        self.port = port
        self.neighbours : dict[int, NeighbourServer] = {}
        self.nb_neighbours = 0

    def add_neighbour(self, neighbour : NeighbourServer):
        self.neighbours[neighbour.id] = neighbour
        self.nb_neighbours += 1

    def set_client(self, sock : socket.socket, addr):
        self.client = NeighbourServer(sock, addr, self.id, "client")
    
    def set_id(self, id):
        print(f"I am server {id}")
        self.id = id

    def get_neighbour(self, id) -> NeighbourServer:
        return self.neighbours[id]

    def broadcast_msg(self, data):
        for neighbour in self.neighbours.values():
            neighbour.send_msg(data)

    def establish_connection(self, server_list):
        for neighbour_id in range(self.id + 1, len(server_list)):
            addr = server_list[neighbour_id]
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((addr, self.port))
            neighbour = NeighbourServer(s, addr, self.id, neighbour_id)
            self.add_neighbour(neighbour)
            print(f"[{self.id}] Connected to server {neighbour_id} at address {addr}")
            neighbour.send_msg(self.id)
        
    def accept_server(self):
        accepted_server = 0
        while accepted_server < self.id:
            s, addr = self.sock.accept()
            neighbour = NeighbourServer(s, addr, self.id)
            neighbour_id = neighbour.recv_msg()
            neighbour.set_id(neighbour_id)
            self.add_neighbour(neighbour)
            print(f"[{self.id}] Accepted server {neighbour_id} at address {addr}")
            accepted_server += 1
        
    def send_msg(self, id, data):
        self.neighbours[id].send_msg(data)

    def recv_msg(self, id):
        return self.neighbours[id].recv_msg()


