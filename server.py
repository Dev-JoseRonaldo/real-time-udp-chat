import socket
import queue
import threading

messages = queue.Queue()
clients = []

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("localhost", 9999))

def receive():
    while True:
        try:
            message_received_bytes, address_ip_client = server.recvfrom(1024)
            messages.put((message_received_bytes, address_ip_client))
        except:
            print("Mensagem não recebida")

def broadcast():
    while True:
        while not messages.empty():
            message_bytes, address_ip_client = messages.get()      
            decoded_message = message_bytes.decode() 
            print(decoded_message)
            if address_ip_client not in clients:
                clients.append(address_ip_client)
            for client in clients:
                try:
                    if decoded_message.startswith("SIGNUP_TAG:"):
                        nickname = decoded_message[decoded_message.index(":")+1:]
                        server.sendto(f"{nickname} se juntou ".encode(), client)
                    else:
                        server.sendto(message_bytes, client)
                except:
                    clients.remove(client)

receive_tread = threading.Thread(target=receive)
broadcast_tread = threading.Thread(target=broadcast)

receive_tread.start()
broadcast_tread.start()