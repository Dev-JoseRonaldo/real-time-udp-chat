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

#client.settimeout(2)

# Função para receber mensagens
def receive():
    while True:
        message_received_bytes, _ = client.recvfrom(c.BUFF_SIZE)

        header = message_received_bytes[:16] # Separando o Header
        message_received_bytes = message_received_bytes[16:] # Separando a mensagem
        (fragSize, fragIndex, fragCount, checksum) = struct.unpack('!IIII', header) # Desempacotando o header

        header_no_checksum = struct.pack('!III', fragSize, fragIndex, fragCount) # Criando um header sem o checksum, para fazer a verificação de checksum depois
        fragment_no_checksum = header_no_checksum + message_received_bytes # Criando um fragmento que o header não tem checksum, para comparar com o checksum que foi feito no remetente, pois lá não havia checksum no header quando o checksum foi calculado

        checksum_check = crc32(fragment_no_checksum) # Criando o checksum do lado do receptor(servidor neste caso), usando o CRC

        if checksum != checksum_check: # Fazendo a verificação dos valores dos checksums
            print("Houve corrupção no pacote!")
        else:
            decoded_message = message_received_bytes.decode()
            print(decoded_message)

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

    # Verifica se a mensagem inserida é um o comando para entrar na sala
    if message.startswith("hi, meu nome eh "):
        # Se já estiver conectado, exibe mensagem de que já está conectado
        if is_conected:
            print("Você já está conectado à sala!")

        # Caso não esteja conectado, conecta à sala
        else:
            nickname = message[16:]
            is_conected = True
            
            send_packet(message, client, 9999, client_ip, nickname)

    # Caso seja o comando de sair da sala
    elif message == "bye":
        # Se não estiver conectado exibi mensagem de que não está conectado
        if not is_conected:
            print("Você não está conectado à sala!")

        # Caso esteja conectado, sai da sala
        else:
            send_packet(message, client, 9999, client_ip, nickname)
            is_conected = False

    # Se estiver conectado e a mensagem não for um comando, envia essa mensagem para o servidor
    elif is_conected:
        send_packet(message, client, 9999, client_ip, nickname)

    # Caso não esteja conectado e a mensagem não seja um comando, exibe mensagem de comando inválido
    else:
        print("Comando inválido!")