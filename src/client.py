# Importando bibliotecas python 
import socket # Cria sockets par comunicação em uma rede
import random # Possibilita gerar números aleatórios
import threading # Cria threads, que são úteis para executar operações simultâneas

# Criação do socket UDP
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Atribuição de uma porta aleatória entre 1000 e 9998
client.bind(("localhost", random.randint(1000, 9998)))

# Solicita que o usuário informe um nickname
nickname = input(f"Digite seu nickname: ")

# Função para receber mensagens
def receive():
    while True:
        try:
            # Recebe mensagens do servidor
            message, _ = client.recvfrom(1024)

            # Converte a sequência de bytes da mensagem recebida em uma string
            decoded_message = message.decode() 

            # Exibe a mensagem decodificada
            print(decoded_message)
        except:
            pass

# Inicia uma thread para a função receive
receive_thread = threading.Thread(target=receive)
receive_thread.start()

# Envia uma mensagem de inscrição com o nickname escolhido para o servidor
client.sendto(f"SIGNUP_TAG:{nickname}".encode(), ("localhost", 9999))

# Loop principal para envio de mensagens
while True:
    # Solicita ao usuário para inserir uma mensagem
    message = input()

    if message == "bye":
        exit()
    else:
        # Envia a mensagem para o servidor
        client.sendto(f"{nickname}: {message}".encode(), ("localhost", 9999))