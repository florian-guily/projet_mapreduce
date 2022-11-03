import logging
import struct, pickle
import socket, threading
from collections import Counter, defaultdict
import re
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
        self.recvd_data = []
        self.data_to_shuffle = []
    
    def set_id(self, id):
        self.id = id

    def send_msg(self, data):
        serialized_data = pickle.dumps(data)
        # logging.info(f"[{self.principal_id}] Sending msg to {self.id}: {type(data)}")
        self.sock.sendall(struct.pack('>I', len(serialized_data)) + serialized_data)
    
    def alternative_send_msg(self, data):
        logging.info(f"[{self.id}] Sending")
        serialized_data = pickle.dumps(data)
        # logging.info(f"[{self.principal_id}] Sending msg to {self.id}: {type(data)}")
        self.sock.sendall(struct.pack('>I', len(serialized_data)) + serialized_data)
        logging.info(f"[{self.id}] Finished sending")

    def recv_msg(self):
        # Read message length and unpack it into an integer
        sock = self.sock
        raw_msglen = sock.recv(4)
        if not raw_msglen:
            return None
        # logging.info(len(raw_msglen))
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
        # logging.info(f"[{self.principal_id}] Received msg from {self.id}: {type(msg)}")
        return msg
    
    def loop_recv(self):
        while True:
            data = self.recv_msg()
            if data == "OK":
                break
            self.recvd_data = data
    
    def send_data_to_shuffle(self):
        self.send_msg(self.data_to_shuffle)
        self.send_msg("OK")
            
    def start_recv(self):
        self.recv_thread = threading.Thread(target=self.loop_recv)
        self.recv_thread.start()

    def start_send_data_to_shuffle(self):
        self.send_thread = threading.Thread(target=self.send_data_to_shuffle)
        self.send_thread.start()
    
    def stop_recv_thread(self):
        self.recv_thread.join()
    
    def stop_send_thread(self):
        self.send_thread.join()


class PrincipalServer(Server):
    def __init__(self, sock : socket.socket, addr, port, id = None):
        super().__init__(sock, addr, id)
        self.port = port
        self.client = None
        self.neighbours : dict[int, NeighbourServer] = {}
        self.nb_neighbours = 0
        self.shuffled_data = []

    def add_neighbour(self, neighbour : NeighbourServer):
        self.neighbours[neighbour.id] = neighbour
        self.nb_neighbours += 1

    def set_client(self, sock : socket.socket, addr):
        self.client = NeighbourServer(sock, addr, self.id, "client")
    
    def set_id(self, id):
        logging.info(f"I am server {id}")
        self.id = id

    def set_data_to_map(self, data):
        data_to_map = ""
        for line in data:
            data_to_map += line
        data_to_map.replace('\n', ' ')
        self.data_to_map = data_to_map

    def map_data(self):
        words = re.findall(r'[A-Za-z]+', self.data_to_map)
        dico = Counter(words)
        self.mapped_data = dict(dico)

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
            logging.info(f"[{self.id}] Connected to server {neighbour_id} at address {addr}")
            neighbour.send_msg(self.id)
        
    def accept_server(self):
        accepted_server = 0
        while accepted_server < self.id:
            s, addr = self.sock.accept()
            neighbour = NeighbourServer(s, addr, self.id)
            neighbour_id = neighbour.recv_msg()
            neighbour.set_id(neighbour_id)
            self.add_neighbour(neighbour)
            logging.info(f"[{self.id}] Accepted server {neighbour_id} at address {addr}")
            accepted_server += 1
        
    def send_msg(self, id, data):
        self.neighbours[id].send_msg(data)

    def recv_msg(self, id):
        return self.neighbours[id].recv_msg()

    def myHash(self, text:str):
        hash=0
        for ch in text:
            hash = ( hash*281  ^ ord(ch)*997) & 0xFFFFFFFF
        return hash

    def local_shuffle(self, n):
        for key in self.mapped_data:
            id = self.myHash(key)%n
            if id == self.id:
                self.shuffled_data.append((key, self.mapped_data[key]))
            else :
                # self.send_msg(id, (key, self.mapped_data[key]))
                self.get_neighbour(id).data_to_shuffle.append((key, self.mapped_data[key]))
        # self.broadcast_msg("OK")

    def start_send_neighbours(self):
        for id, neighbour in self.neighbours.items():
            logging.info(f"[{self.id}] Starting send data to shuffle from server {id} ...")
            neighbour.start_send_data_to_shuffle()
            logging.info(f"[{self.id}] Started send data to shuffle from server {id}")

    def stop_send_neighbours(self):
        for id, neighbour in self.neighbours.items():
            logging.info(f"[{self.id}] Stopping send thread from server {id} ...")
            neighbour.stop_send_thread()
            logging.info(f"[{self.id}] Stopped send thread from server {id}")
        
    def start_recv_neighbours(self):
        for id, neighbour in self.neighbours.items():
            logging.info(f"[{self.id}] Starting recv thread from server {id} ...")
            neighbour.start_recv()
            logging.info(f"[{self.id}] Started recv thread from server {id}")

    def stop_recv_neighbours(self):
        for id, neighbour in self.neighbours.items():
            logging.info(f"[{self.id}] Stopping recv thread from server {id} ...")
            neighbour.stop_recv_thread()
            logging.info(f"[{self.id}] Stopped recv thread from server {id}")
        
    def reduce(self):
        for server in self.neighbours.values():
            self.shuffled_data.extend(server.recvd_data)
        self.reduced_data = defaultdict(int)
        for key, val in self.shuffled_data:
            self.reduced_data[key] += val

    def shutdown(self):
        if self.client != None:
            self.client.sock.close()
        for neighbour in self.neighbours.values():
            neighbour.sock.close()
        if self.sock != None:
            logging.info("Closing socket")
            self.sock.close()
        
        
        



