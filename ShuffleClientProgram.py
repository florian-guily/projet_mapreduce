# multiconn-client.py
import numpy as np
import time, threading, logging
from obj.MyServer import PrincipalServer
    
if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    main_start = time.time()
    # HOSTS = ["tp-3a209-10.enst.fr", "tp-1a201-04.enst.fr", "tp-1a207-23.enst.fr", "tp-1a207-24.enst.fr", "tp-1a207-25.enst.fr"]  # The server's hostname or IP address
    HOSTS = ["tp-3a209-10.enst.fr", "tp-1a201-04.enst.fr", "tp-1a207-23.enst.fr", "tp-1a207-24.enst.fr"]
    PORT = 64998  # The port used by the server
    server = PrincipalServer(None, "localhost", PORT, -1)

    server.establish_connection(HOSTS)
    server.broadcast_msg(HOSTS)

    # with open('sample1.txt', 'r') as f:
    # with open('1', 'r') as f:
    #     lines = f.readlines()

    # chunk_size = len(lines)//len(HOSTS)
    start = time.time()
    logging.info("Sending data to servers...")
    for neighbour in server.neighbours.values():
        id = neighbour.id
        neighbour.send_msg(id)
        neighbour.send_thread = threading.Thread(target=neighbour.send_split)
        neighbour.send_thread.start()
        # if id == len(HOSTS):
        #     neighbour.send_thread = threading.Thread(target=neighbour.alternative_send_msg, args=(lines[(id)*chunk_size:],))
        #     neighbour.send_thread.start()
        # else :
        #     neighbour.send_thread = threading.Thread(target=neighbour.alternative_send_msg, args=(lines[(id)*chunk_size:(id+1)*chunk_size],))
        #     neighbour.send_thread.start()
        logging.info(f"Started send thread for server {neighbour.id} ")
    server.stop_send_neighbours()
    duration = time.time() - start
    logging.info(f"Finished sending data to servers in {duration} seconds.")

    
    server.start_recv_neighbours()
    server.stop_recv_neighbours()

    f = open('./results.txt', 'w')
    for neighbour in server.neighbours.values():
        for key, val in neighbour.recvd_data.items():
            f.write(f"{key} {val}\n")
    total_duration = time.time() - main_start
    logging.info(f"Finished distributed map reduce in {total_duration} seconds.")
    server.shutdown()



    





