# Importando bibliotecas python 
import socket # Cria sockets par comunicação em uma rede
import random # Possibilita gerar números aleatórios
import threading # Cria threads, que são úteis para executar operações simultâneas
import math # Biblioteca de funções matemáticas
import struct # Bilioteca que Interpreta bytes como dados binários compactados
from zlib import crc32 # Calcula uma soma de verificação CRC 32 bits

from utils.send_packet import send_packet
import utils.constants as c
from utils.print_commands import print_commands

# Criação do socket UDP
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Atribuição de uma porta aleatória entre 1000 e 9998
CLIENT_ADRR = random.randint(1000, 9998)
client.bind((c.SERVER_ADRR[0], CLIENT_ADRR))

#fragSize = c.FRAG_SIZE

# Variáveis Globais
seq_num_client = 0 # Número de sequência do pacote enviado pelo cliente
ack_to_send = 0 # Número de reconhecimento do pacote enviado pelo servidor 
client_ip = None 
nickname = None

# Função para receber mensagens
def receive():
    global client, seq_num_client, ack_to_send, client_ip, nickname

    while True:
        message_received_bytes, _ = client.recvfrom(c.BUFF_SIZE)

        header = message_received_bytes[:24] # Separando o Header
        message_received_bytes = message_received_bytes[24:] # Separando a mensagem
        (fragSize, fragIndex, fragCount, seq_num, ack_num, checksum) = struct.unpack('!IIIIII', header) # Desempacotando o header

        header_no_checksum = struct.pack('!IIIII', fragSize, fragIndex, fragCount, seq_num, ack_num) # Criando um header sem o checksum, para fazer a verificação de checksum depois
        fragment_no_checksum = header_no_checksum + message_received_bytes # Criando um fragmento que o header não tem checksum, para comparar com o checksum que foi feito no remetente, pois lá não havia checksum no header quando o checksum foi calculado

        checksum_check = crc32(fragment_no_checksum) # Criando o checksum do lado do receptor(servidor neste caso), usando o CRC

        decoded_message = message_received_bytes.decode()

        # Fazendo a verificação do checksum, sequence number e ack
        if decoded_message: # Caso exista mensagem, irá conferir sequence number
            message = ''

            if checksum != checksum_check or seq_num != ack_to_send: # Reenvia ack do último pacote reconhecido
                print("Houve corrupção no pacote!")
                
                if ack_to_send == 0:
                    send_packet(message, client, 9999, client_ip, nickname, seq_num, 1)
                else:
                    send_packet(message, client, 9999, client_ip, nickname, seq_num, 0)
            else: # Lê mensagem e envia ack do pacote recebido
                print(decoded_message)
                send_packet(message, client, 9999, client_ip, nickname, seq_num, ack_to_send)

                # Atualiza próximo ack a ser enviado
                if ack_to_send == 0:
                    ack_to_send = 1
                else:
                    ack_to_send = 0

        else: # Caso não exista mensagem, irá conferir ack number
            if checksum != checksum_check or ack_num != seq_num_client:  # Reenvia último pacote (DICA: guardar último pacote enviado em uma variável até recber ack do mesmo)
                print("Houve corrupção no pacote!")
            else: # Recebe ack do pacote recebido
                if seq_num_client == 0:
                    seq_num_client = 1
                elif seq_num_client == 1:
                    seq_num_client = 0

            client.settimeout(None)  # Define o timeout de volta para None para desabilitá-lo

# Inicia uma thread para a função receive
receive_thread = threading.Thread(target=receive)
receive_thread.start()

print_commands()
is_conected = False

# Loop principal para envio de mensagens
while True:
    # Solicita ao usuário para inserir uma mensagem
    message = input()
    client_ip = client.getsockname()[0]

    # Se não estiver conectado, exibe mensagem de que não está conectado
    if not is_conected and message == "bye": 
        print("Você não está conectado à sala!")

    # Se já estiver conectado, exibe mensagem de que já está conectado
    elif is_conected and message.startswith("hi, meu nome eh "):
        print("Você já está conectado à sala!")

    # Caso não esteja conectado e a mensagem não seja um comando, exibe mensagem de comando inválido
    elif not is_conected and not message.startswith("hi, meu nome eh "):
        print("Comando inválido!")

    else:
        # Verifica se a mensagem inserida é um o comando para entrar na sala
        if message.startswith("hi, meu nome eh "):
            nickname = message[16:]
            is_conected = True
            
            send_packet(message, client, 9999, client_ip, nickname, seq_num_client, ack_to_send)

        # Caso seja o comando de sair da sala
        elif message == "bye":
            send_packet(message, client, 9999, client_ip, nickname, seq_num_client, ack_to_send)
            is_conected = False #desconecta quando envia ack de reconhecimento de terminar conexão do server 

        # Se estiver conectado e a mensagem não for um comando, envia essa mensagem para o servidor
        else:
            send_packet(message, client, 9999, client_ip, nickname, seq_num_client, ack_to_send)