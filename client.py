import socket
import random
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(("localhost", random.randint(1000, 9998)))

nickname = input(f"Digite seu nickname: ")

def receive():
    while True:
        try:
            message, _ =client.recvfrom(1024)
            decoded_message = message.decode() 
            print(decoded_message)
        except:
            pass

receive_thread = threading.Thread(target=receive)
receive_thread.start()

client.sendto(f"SIGNUP_TAG:{nickname}".encode(), ("localhost", 9999))

while True:
    message = input()
    if message == "bye":
        exit()
    else:
        client.sendto(f"{nickname}: {message}".encode(), ("localhost", 9999))