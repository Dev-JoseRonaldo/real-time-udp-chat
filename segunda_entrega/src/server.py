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
from utils.checksum import find_checksum
from utils.folder_management import delete_folder

# Inicialia fila para armazenar mensagens a serem processadas
messages = queue.Queue()
# Listas para armazenar endereços IP, nicknames, sequence number e acks dos clientes conectados
clients_ip = []
clients_nickname = []
seq_and_ack_controler = []

# Criação do socket UDP
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Atribuição do endereço do servidor
server.bind(c.SERVER_ADRR)

finalization_ack = False # Avisa se ack de finalização foi recebido

#Função responsável por remover um client de clients_ip e clients_nickname
def remove_client(client): 
    index_client = clients_ip.index(client)
    clients_ip.remove(client)
    clients_nickname.pop(index_client)
    seq_and_ack_controler.pop(index_client)

# Função para receber mensagens dos clientes
def receive():
    global finalization_ack

    # Numero de fragmentos recebidos
    received_chunks = 0
    # Lista de fragmentos recebidos
    rec_list = []

    while True:
        message_received_bytes, address_ip_client = server.recvfrom(c.BUFF_SIZE)

        header = message_received_bytes[:c.HEADER_SIZE] # Separando o Header
        message_received_bytes = message_received_bytes[c.HEADER_SIZE:] # Separando a mensagem

        (fragSize, fragIndex, fragCount, seq_num, ack_num, checksum) = struct.unpack('!IIIIII', header) # Desempacotando o header

        header_no_checksum = struct.pack('!IIIII', fragSize, fragIndex, fragCount, seq_num, ack_num) # Criando um header sem o checksum, para fazer a verificação de checksum depois
        fragment_no_checksum = header_no_checksum + message_received_bytes # Criando um fragmento que o header não tem checksum, para comparar com o checksum que foi feito no remetente, pois lá não havia checksum no header quando o checksum foi calculado

        checksum_check = find_checksum(fragment_no_checksum) # Criando o checksum do lado do receptor(servidor neste caso), usando o CRC
               
        # Normalizando o checksum para comparação
        checksum = bin(checksum)[2:]
        checksum = '0' * (len(checksum_check) - len(checksum)) + checksum

        # Converte a sequência de bytes da mensagem recebida em uma string    
        decoded_message = message_received_bytes.decode(encoding="ISO-8859-1") 

        if decoded_message == "SYN":
            print(f'Enviando SYN-ACK!')
            send_packet("SYN-ACK", server, address_ip_client, None, f"3-way-handshake-{address_ip_client}", seq_num, ack_num)

        # Verificando se o cliente já está na lista de clientes
        else:
            if address_ip_client not in clients_ip:
                nickname = decoded_message.split("eh ")[1]
                clients_ip.append(address_ip_client)
                clients_nickname.append(nickname)
                seq_and_ack_controler.append([0, 0])
                index = clients_ip.index(address_ip_client)

                #deletar 3-way handshake
                delete_folder("./segunda_entrega/data", f"3-way-handshake-{str(address_ip_client)}", True)
            else:
                index = clients_ip.index(address_ip_client)
                nickname = clients_nickname[index]

            if seq_and_ack_controler:
                current_seq_num = seq_and_ack_controler[index][0]
                current_ack_num = seq_and_ack_controler[index][1]
            
                # Fazendo a verificação do checksum, sequence number e ack
                if decoded_message == "ACK": # Remove o cliente das listas clients_ip, clients_nickname e seq_and_ack_controler
                    print(f'Recebeu ACK do FYN-ACK enviado!')
                    finalization_ack = True
                elif decoded_message: # Caso exista mensagem para ser enviada a usuários, irá conferir checksum e sequence number
                    if checksum != checksum_check or seq_num != current_ack_num: 
                        if checksum != checksum_check:
                            print("Houve corrupção no pacote!")

                        print(f'Enviando ACK do último pacote recebido!')
                        if current_ack_num == 0:
                            send_packet('', server, address_ip_client, None, nickname, seq_num, 1)
                        else:
                            send_packet('', server, address_ip_client, None, nickname, seq_num, 0)
                        
                        # resetando a lista de fragmentos
                        received_chunks = 0
                        rec_list = []
                    
                    else: # Enviará mensagem para usuários conectados e ack do pacote recebido para remetente do pacote
                        if decoded_message == "bye":
                            print(f'Enviando FYN-ACK!')
                            send_packet("FYN-ACK", server, address_ip_client, None, nickname, seq_num, current_ack_num)
                        else:
                            print(f'Enviando ACK!')
                            send_packet('', server, address_ip_client, None, nickname, seq_num, current_ack_num)

                        # Atualiza próximo ack a ser enviado
                        if current_ack_num == 0:
                            seq_and_ack_controler[index][1] = 1
                        else:
                            seq_and_ack_controler[index][1] = 0
                        
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
                            #salvando o arquivo
                            content = b''.join(rec_list) # Juntando os fragmentos
                            content = content.decode(encoding = "ISO-8859-1") # Decodificando a mensagem

                            if content.startswith("hi, meu nome eh "):
                                messages.put((decoded_message, address_ip_client, nickname))
                            elif content.startswith("bye"):
                                messages.put((decoded_message, address_ip_client, nickname))
                            else:   
                                message = f"{nickname}: {content}"

                                # Salvando a mensagem na fila
                                messages.put((message, address_ip_client, nickname))

                            # resetando a lista de fragmentos
                            received_chunks = 0
                            rec_list = []

                else: # Caso seja pacote de reconhecimento, irá conferir ack number
                    if checksum != checksum_check or ack_num != current_seq_num: # Reenvia último pacote (DICA: guardar último pacote enviado em uma variável até recber ack do mesmo)
                        if checksum != checksum_check:
                            print(f"Houve corrupção no pacote!")
                    else: # Recebe ack do pacote recebido e atualiza próximo número de sequência a ser enviado
                        c.ACK_RECEIVED = True # Afirma que recebeu ack
                        print(f'Recebeu ACK do pacote!')

                        if current_seq_num == 0:
                            seq_and_ack_controler[index][0] = 1
                        elif current_seq_num == 1:
                            seq_and_ack_controler[index][0] = 0

# Função para transmitir mensagens a todos os clientes
def broadcast():
    global finalization_ack
    
    while True:
        while not messages.empty(): # Caso exista mensagens na fila
            # Pega bytes e endereço IP do cliente da mensagem da fila 
            decoded_message, address_ip_client, nickname = messages.get()

            for client_ip in clients_ip: # Envia a mensagem recebida para todos os clientes conectados

                index = clients_ip.index(client_ip)
                name = clients_nickname[index]
                current_seq_num = seq_and_ack_controler[index][0]
                current_ack_num = seq_and_ack_controler[index][1]

                try:
                    if decoded_message.startswith("hi, meu nome eh "): # Verifica se a mensagem é uma mensagem de inscrição
                        # Envia mensagem de notificação de entrada do novo cliente
                        print(f'Enviando que {nickname} entrou no chat para cliente {name}!')
                        send_packet(f"{nickname} se juntou", server, client_ip, None, name, current_seq_num, current_ack_num)

                        # mensagem chegou, apagar pastas
                        if nickname:
                            delete_folder("./segunda_entrega/data", nickname, True)

                    elif decoded_message == "bye": # Verifica se a mensagem é uma mensagem de saída                 
                        # Envia mensagem de notificação de saída do cliente
                        print(f'Enviando que {nickname} saiu do chat para cliente {name}!')
                        send_packet(f"{nickname} saiu da sala!", server, client_ip, None, name, current_seq_num, current_ack_num)

                        # mensagem chegou, apagar pastas
                        if nickname:
                            delete_folder("./segunda_entrega/data", nickname, True)
                        
                    else:
                        ip = address_ip_client[0]
                        port = address_ip_client[1]
                        # Formatando mensagem para exibição
                        message_output = f'{ip}:{port}/~{decoded_message} {get_current_time_and_date()}'

                        print(f'Enviando mensagem do usuário {nickname} para cliente {name}!')
                        send_packet(message_output, server, client_ip, None, name, current_seq_num, current_ack_num)

                        # mensagem chegou, apagar pastas
                        if nickname:
                            delete_folder("./segunda_entrega/data", nickname, True)

                except Exception as e:
                    print(f"Erro ao enviar mensagem: {e}")

            if decoded_message == "bye":
                while not finalization_ack:
                    pass
                remove_client(address_ip_client)
                print(f'Removeu {nickname} da lista de usuários conectados!')
                finalization_ack = False

# Inicia uma thread para as funções de recebimento e transmissão
receive_tread = threading.Thread(target=receive)
broadcast_tread = threading.Thread(target=broadcast)

receive_tread.start()
broadcast_tread.start()