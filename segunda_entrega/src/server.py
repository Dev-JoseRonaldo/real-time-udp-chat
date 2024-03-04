# Importando bibliotecas python 
import socket # Cria sockets par comunicação em uma rede
import queue # Fila para armazenar mensagens
import threading # Cria threads, que são úteis para executar operações simultâneas
import struct # Bilioteca que Interpreta bytes como dados binários compactados
from zlib import crc32 # Calcula uma soma de verificação CRC 32 bits

from utils.convert_txt import convert_string_to_txt
from utils.send_packet import send_packet
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

#server.settimeout(2)

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

        message_received_bytes, address_ip_client = server.recvfrom(c.BUFF_SIZE)

        header = message_received_bytes[:16] # Separando o Header
        message_received_bytes = message_received_bytes[16:] # Separando a mensagem

        (fragSize, fragIndex, fragCount, checksum) = struct.unpack('!IIII', header) # Desempacotando o header

        header_no_checksum = struct.pack('!III', fragSize, fragIndex, fragCount) # Criando um header sem o checksum, para fazer a verificação de checksum depois
        fragment_no_checksum = header_no_checksum + message_received_bytes # Criando um fragmento que o header não tem checksum, para comparar com o checksum que foi feito no remetente, pois lá não havia checksum no header quando o checksum foi calculado

        checksum_check = crc32(fragment_no_checksum) # Criando o checksum do lado do receptor(servidor neste caso), usando o CRC

        # Fazendo a verificação dos valores dos checksums
        if checksum != checksum_check: 
            print("Houve corrupção no pacote!")
            # resetando a lista de fragmentos
            received_chunks = 0
            rec_list = []
        else: 
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
                name = 'ServerLogin'
                for ip in clients_ip:
                    if ip == address_ip_client:
                        index = clients_ip.index(ip)
                        name = clients_nickname[index]
                        break

                #salvando o arquivo
                content = b''.join(rec_list) # Juntando os fragmentos
                content = content.decode(encoding = "ISO-8859-1") # Decodificando a mensagem
                path_file = convert_string_to_txt(content, name, True) # Salvando em um arquivo

                # lendo o conteudo do arquivo e preparando a mensagem para envio
                with open(path_file, "r") as arquivo:
                    received_text = arquivo.read()
                    if received_text.startswith("hi, meu nome eh "):
                        messages.put((message_received_bytes, address_ip_client))
                    elif received_text.startswith("bye"):
                        messages.put((message_received_bytes, address_ip_client))
                    else:   
                        message = f"{name}: {received_text}".encode()

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
            decoded_message = message_bytes.decode(encoding="ISO-8859-1") 

             # Verificando se o cliente já está na lista de clientes
            if address_ip_client not in clients_ip:
                name = decoded_message.split("eh ")[1]
                clients_ip.append(address_ip_client)
                clients_nickname.append(name)

            for client_ip in clients_ip: # Envia a mensagem recebida para todos os clientes conectados
                try:
                    if decoded_message.startswith("hi, meu nome eh "): # Verifica se a mensagem é uma mensagem de inscrição
                        # Decodifica mensagem para saber nickname do usuário
                        nickname = decoded_message[decoded_message.index("eh ")+3:]

                        # Envia mensagem de notificação de entrada do novo cliente
                        send_packet(f"{nickname} se juntou", server, client_ip, None, nickname, True)

                    elif decoded_message == "bye": # Verifica se a mensagem é uma mensagem de inscrição

                        # Remove o cliente das listas clients_ip e clients_nickname
                        remove_client(client_ip)
                        
                        # Envia mensagem de notificação de saida do cliente
                        send_packet(f"{nickname} saiu da sala!", server, client_ip, None, nickname, True)
                    else:
                        ip = address_ip_client[0]
                        port = address_ip_client[1]
                        # Formatando mensagem para exibição
                        message_output = f'{ip}:{port}/~{decoded_message} {get_current_time_and_date()}'

                        send_packet(message_output, server, client_ip, None, nickname, True)

                except Exception as e:
                    print(f"Erro ao enviar mensagem: {e}")


# Inicia uma thread para as funções de recebimento e transmissão
receive_tread = threading.Thread(target=receive)
broadcast_tread = threading.Thread(target=broadcast)

receive_tread.start()
broadcast_tread.start()