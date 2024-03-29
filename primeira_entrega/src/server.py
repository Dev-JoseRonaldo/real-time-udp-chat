# Importando bibliotecas python 
import socket # Cria sockets par comunicação em uma rede
import queue # Fila para armazenar mensagens
import threading # Cria threads, que são úteis para executar operações simultâneas
import struct # Bilioteca que Interpreta bytes como dados binários compactados

from utils.convert_txt import convert_string_to_txt
import utils.constants as c
from utils.get_current_time_and_date import get_current_time_and_date

# Inicialia fila para armazenar mensagens a serem processadas
messages = queue.Queue()
# Listas para armazenar endereços IP e nicknames  dos clientes conectados
clients_ip = []
clients_nickname = []

# Criação do socket UDP
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Atribuição do endereço do servidor
server.bind(c.SERVER_ADRR)

#Função responsável por remover um client de clients_ip e clients_nickname
def remove_client(client): 
    index_client = clients_ip.index(client)
    clients_ip.remove(client)
    clients_nickname.pop(index_client)

# Função para receber mensagens dos clientes
def receive():
    # Numero de fragmentos recebidos
    received_chunks = 0
    # Lista de fragmentos recebidos
    rec_list = []

    while True:
        try:
            # Recebe mensagens em bytes e o endereço IP + porta do cliente do socket do servidor
            message_received_bytes, address_ip_client = server.recvfrom(c.BUFF_SIZE)

            # Coloca a mensagem recebida e o endereço IP do cliente na fila para processamento, 
            # Caso a mensagem tenha a tag de SIGNUP_TAG ou QUIT_TAG
            if (message_received_bytes.decode().startswith("SIGNUP_TAG:") or
                message_received_bytes.decode().startswith("QUIT_TAG:")):
                messages.put((message_received_bytes, address_ip_client))                   
            # Caso contrário, força erro para cair no except
            else:
                raise NameError('MESSAGE_TAG')

        # Se der erro ao tentar decodificar a mensagem foi por que a mensagem não veio com uma tag mapeada a cima
        # ou seja, foi uma mensagem enviada ao chat e deverá seguir os passos abaixo
        except:
            header = message_received_bytes[:16] # Separando o Header
            message_received_bytes = message_received_bytes[16:] # Separando a mensagem
            (fragSize, fragIndex, fragCount, crc) = struct.unpack('!IIII', header) # Desempacotando o header

            # Adiciona fragCount posições vazias na lista de fragmentos recebidos
            # Serve para salvar os fragmentos na ordem correta
            if len(rec_list) < fragCount:
                need_to_add = fragCount - len(rec_list)
                rec_list.extend([''] * need_to_add)

             # Adiciona o fragmento recebido na lista de fragmentos recebidos
            rec_list[fragIndex] = message_received_bytes
            received_chunks += 1

            # Caso já tenha recebido todos os fragmentos
            if received_chunks == fragCount:
                # Achando o nome pelo ip
                for ip in clients_ip:
                    if ip == address_ip_client:
                        index = clients_ip.index(ip)
                        name = clients_nickname[index]
                        break

                #salvando o arquivo
                content = b''.join(rec_list) # Juntando os fragmentos
                content = content.decode(encoding = "ISO-8859-1") # Decodificando a mensagem
                path_file = convert_string_to_txt(name, content, serverSide=True) # Salvando em um arquivo

                # lendo o conteudo do arquivo e preparando a mensagem para envio
                with open(path_file, "r") as arquivo:
                    message = f"{name}: {arquivo.read()}".encode()

                # Salvando a mensagem na fila
                messages.put((message, address_ip_client))

                # resetando a lista de fragmentos
                received_chunks = 0
                rec_list = []

            # Caso haja perda de pacotes, ou seja, não recebeu todos os fragmentos
            elif (received_chunks < fragCount) and (fragIndex == fragCount - 1):
                print("Houve perda de pacote!")
                # resetando a lista de fragmentos
                received_chunks = 0
                rec_list = []

# Função para transmitir mensagens a todos os clientes
def broadcast():
    while True:
        while not messages.empty(): # Caso exista mensagens na fila
            # Pega bytes e endereço IP do cliente da mensagem da fila 
            message_bytes, address_ip_client = messages.get()

            # Converte a sequência de bytes da mensagem recebida em uma string    
            decoded_message = message_bytes.decode(encoding = "ISO-8859-1") 

             #verificando se o cliente já está na lista de clientes
            if address_ip_client not in clients_ip:
                name = decoded_message[decoded_message.index(":")+1:]
                clients_ip.append(address_ip_client)
                clients_nickname.append(name)

            for client_ip in clients_ip: # Envia a mensagem recebida para todos os clientes conectados
                try:
                    if decoded_message.startswith("SIGNUP_TAG:"): # Verifica se a mensagem é uma mensagem de inscrição
                        # Decodifica mensagem para saber nickname do usuário
                        nickname = decoded_message[decoded_message.index(":")+1:]

                        # Envia mensagem de notificação de entrada do novo cliente
                        server.sendto(f"{nickname} se juntou ".encode(), client_ip)

                    elif decoded_message.startswith("QUIT_TAG:"): # Verifica se a mensagem é uma mensagem de inscrição
                        # Decodifica mensagem para saber nickname do usuário
                        nickname = decoded_message[decoded_message.index(":")+1:]

                        # Remove o cliente das listas clients_ip e clients_nickname
                        remove_client(client_ip)
                        
                        # Envia mensagem de notificação de saida do cliente
                        server.sendto(f"{nickname} saiu da sala!".encode(), client_ip)
                    else:
                        ip = address_ip_client[0]
                        port = address_ip_client[1]
                        # Formatando mensagem para exibição
                        message_output = f'{ip}:{port}/~{decoded_message} {get_current_time_and_date()}'

                        # Envia a mensagem para todos os clientes
                        server.sendto(message_output.encode(encoding = 'ISO-8859-1'), client_ip)

                except:
                    # Remove o cliente da lista se ocorrer um erro ao enviar a mensagem
                    remove_client(client_ip)

# Inicia uma thread para as funções de recebimento e transmissão
receive_tread = threading.Thread(target=receive)
broadcast_tread = threading.Thread(target=broadcast)

receive_tread.start()
broadcast_tread.start()