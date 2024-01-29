# Importando bibliotecas python 
import socket # Cria sockets par comunicação em uma rede
import queue # Fila para armazenar mensagens
import threading # Cria threads, que são úteis para executar operações simultâneas

# Inicialia fila para armazenar mensagens a serem processadas
messages = queue.Queue()
# Lista para armazenar endereços IP dos clientes conectados
clients = []

# Criação do socket UDP
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Atribuição para porta 9999
server.bind(("localhost", 9999))

# Função para receber mensagens dos clientes
def receive():
    while True:
        try:
            # Recebe mensagens em bytes e o endereço IP do cliente do socket do servidor
            message_received_bytes, address_ip_client = server.recvfrom(1024)
            # Coloca a mensagem recebida e o endereço IP do cliente na fila para processamento
            messages.put((message_received_bytes, address_ip_client))
        except:
            print("Mensagem não recebida")

# Função para transmitir mensagens a todos os clientes
def broadcast():
    while True:
        while not messages.empty(): # Caso exista mensagens na fila
            # Pega bytes e endereço IP do cliente da mensagem da fila 
            message_bytes, address_ip_client = messages.get()

            # Converte a sequência de bytes da mensagem recebida em uma string    
            decoded_message = message_bytes.decode() 

            # Exibe a mensagem decodificada
            print(decoded_message)

            if address_ip_client not in clients: # Adiciona endereço IP da mensagem lida na lista de clientes conectados
                clients.append(address_ip_client)
            for client in clients: # Envia a mensagem recebida para todos os clientes conectados
                try:
                    if decoded_message.startswith("SIGNUP_TAG:"): # Verifica se a mensagem é uma mensagem de inscrição
                        # Decodifica mensagem para saber nickname do usuário
                        nickname = decoded_message[decoded_message.index(":")+1:]

                        # Envia mensagem de notificação de entrada do novo cliente
                        server.sendto(f"{nickname} se juntou ".encode(), client)
                    else:
                        # Envia a mensagem para todos os clientes
                        server.sendto(message_bytes, client)
                except:
                    # Remove o cliente da lista se ocorrer um erro ao enviar a mensagem
                    clients.remove(client)

# Inicia uma thread para as funções de recebimento e transmissão
receive_tread = threading.Thread(target=receive)
broadcast_tread = threading.Thread(target=broadcast)

receive_tread.start()
broadcast_tread.start()