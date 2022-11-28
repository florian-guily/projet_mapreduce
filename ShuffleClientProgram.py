# multiconn-client.py
import numpy as np
import time, threading, logging, os
from obj.MyServer import PrincipalServer
    
if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    main_start = time.time()
    HOSTS = ["tp-3a209-10.enst.fr", "tp-1a201-04.enst.fr", "tp-1a207-23.enst.fr", "tp-1a207-24.enst.fr", "tp-1a207-25.enst.fr", "tp-1a201-14.enst.fr", "tp-1a201-18.enst.fr",  "tp-1a201-22.enst.fr",  "tp-1a201-23.enst.fr",  "tp-1a201-27.enst.fr"]  # The server's hostname or IP address
    PORT = 64998  # The port used by the server
    server = PrincipalServer(None, "localhost", PORT, -1)

    server.establish_connection(HOSTS)
    server.broadcast_msg(HOSTS)
    path = 'samples/CC-MAIN-20220924151538-20220924181538-00000.warc.wet'
    file_size = os.stat(path).st_size
    chunk_size = file_size//len(HOSTS)

    start = time.time()
    logging.info("Sending data to servers...")
    f = open(path, 'r')
    for neighbour in server.neighbours.values():
        id = neighbour.id
        neighbour.send_msg(id)
        data = f.read(chunk_size)
        next = f.read(1)
        while (next != ' ') & (next != '\n') & (next != ''):
            data += next
            next = f.read(1)
        neighbour.send_thread = threading.Thread(target=neighbour.alternative_send_msg, args=(data,))
        neighbour.send_thread.start()
        
    logging.info(f"Started send thread for server {neighbour.id} ")
    server.stop_send_neighbours()
    duration = time.time() - start
    logging.info(f"Finished sending data to servers in {duration} seconds.")
    start_after_send = time.time()

    
    server.start_recv_neighbours()
    server.stop_recv_neighbours()

    f = open('./results.txt', 'w')
    for neighbour in server.neighbours.values():
        for key, val in neighbour.recvd_data.items():
            f.write(f"{key} {val}\n")
    total_duration = time.time() - main_start
    after_send_duration = time.time() - start_after_send
    logging.info(f"Finished total distributed map reduce in {total_duration} seconds.")
    logging.info(f"Finished distributed map reduce after sending data in {after_send_duration} seconds.")
    server.shutdown()



    





