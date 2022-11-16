# multiconn-server.py
from ast import main
import sys
import struct, pickle
import socket
import threading, logging
from collections import Counter
import time
from obj.MyServer import PrincipalServer

def get_data_to_map(server: PrincipalServer):
    data_to_map = server.client.recv_msg()
    logging.info("Preparing data for mapping ...")
    server.set_data_to_map(data_to_map)

def init(addr, port):
    logging.info("Initializing...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((addr, port))
    s.listen()
    server = PrincipalServer(s, addr, port)
    # server_index["server"] = {"sock": s, "addr": 'localhost'}
    client_sock, client_addr = s.accept()
    main_time = time.time()
    server.set_client(client_sock, client_addr)
    
    client_id = server.client.recv_msg() # useless as we label client_id as "client"

    server_list = server.client.recv_msg()
    id = server.client.recv_msg()
    server.set_id(id)
    server.client.principal_id = id
    logging.info(f"[{id}] Server list: {server_list}")
    logging.info(f"[{id}] I am server {id}")
    logging.info(f"[{id}] Receiving data to map from client...")
    thread_data_to_map = threading.Thread(target=get_data_to_map, args=(server,))
    thread_data_to_map.start()
    return server, server_list, thread_data_to_map, main_time
    
if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    HOST, PORT = "", 64998
    server, server_list, thread_data_to_map, main_time = init(HOST, PORT)
    server.establish_connection(server_list)
    server.accept_server()

    thread_data_to_map.join()
    logging.info(f"[{server.id}] Received data to map from client.")

    start = time.time()
    logging.info(f"[{server.id}] Started mapping phase...")
    server.map_data()

    duration = time.time() - start
    logging.info(f"[{server.id}] Finished mapping phase in {duration} seconds.")

    # logging.info(f"[{server.id}] Mapped data : {server.mapped_data}")
    # for key in server.mapped_data:
    #     logging.info(f"[{server.id}] Hash for key {key}: {server.myHash(key)}")
    #     logging.info(f"[{server.id}] Server to send {key}: {server.myHash(key)%len(server_list)}")

    # shuffle_thread = threading.Thread(target=server.shuffle, args=(len(server_list),))

    start = time.time()
    logging.info(f"[{server.id}] Started shuffling phase...")
    # shuffle_thread.start()
    server.local_shuffle(len(server_list))
    server.start_send_neighbours()
    server.start_recv_neighbours()
    server.stop_recv_neighbours()
    server.stop_send_neighbours()

    # shuffle_thread.join()
    duration = time.time() - start
    logging.info(f"[{server.id}] Finished shuffling phase in {duration}.")

    # for id, neighbour in server.neighbours.items():
    #     logging.info(f"[{server.id}] Data shuffled from server {id}: {neighbour.recvd_data}")
    start = time.time()
    logging.info(f"[{server.id}] Started reduce phase...")
    server.reduce()
    duration = time.time() - start
    logging.info(f"[{server.id}] Finished reduce phase in {duration}.")
    start = time.time()
    logging.info(f"[{server.id}] Sending reduced data to client...")
    server.client.send_msg(server.reduced_data)
    server.client.send_msg("OK")
    duration = time.time() - start
    logging.info(f"[{server.id}] Finished sending reduced data to client in {duration}.")
    main_duration = time.time() - main_time
    logging.info(f"[{server.id}] Finished whole map reduce in {main_duration} seconds on this server.")
    server.shutdown()
    


