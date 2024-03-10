# Importando bibliotecas python 
import socket # Cria sockets par comunicação em uma rede
import random # Possibilita gerar números aleatórios
import threading # Cria threads, que são úteis para executar operações simultâneas
import struct # Bilioteca que Interpreta bytes como dados binários compactados

from utils.send_packet import send_packet
import utils.constants as c
from utils.print_commands import print_commands
from utils.checksum import find_checksum
from utils.folder_management import delete_folder

# Criação do socket UDP
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Atribuição de uma porta aleatória entre 1000 e 9998
CLIENT_ADRR = random.randint(1000, 9998)
client.bind((c.SERVER_ADRR[0], CLIENT_ADRR))

# Variáveis Globais
seq_num_client = 0 # Número de sequência do pacote enviado pelo cliente
ack_to_send = 0 # Número de reconhecimento do pacote enviado pelo servidor 
client_ip = None 
nickname = None
message_buffer = ''

# Função para receber mensagens
def receive():
    global client, seq_num_client, ack_to_send, client_ip, nickname, is_conected

    while True:
        # mensagem chegou, apagar pastas
        if nickname:
            delete_folder("./segunda_entrega/data", nickname)

        message_received_bytes, _ = client.recvfrom(c.BUFF_SIZE)

        header = message_received_bytes[:c.HEADER_SIZE] # Separando o Header
        message_received_bytes = message_received_bytes[c.HEADER_SIZE:] # Separando a mensagem
        (fragSize, fragIndex, fragCount, seq_num, ack_num, checksum) = struct.unpack('!IIIIII', header) # Desempacotando o header

        header_no_checksum = struct.pack('!IIIII', fragSize, fragIndex, fragCount, seq_num, ack_num) # Criando um header sem o checksum, para fazer a verificação de checksum depois
        fragment_no_checksum = header_no_checksum + message_received_bytes # Criando um fragmento que o header não tem checksum, para comparar com o checksum que foi feito no remetente, pois lá não havia checksum no header quando o checksum foi calculado

        checksum_check = find_checksum(fragment_no_checksum) # Criando o checksum do lado do receptor(servidor neste caso)

        # Normalizando o checksum para comparação
        checksum = bin(checksum)[2:]
        checksum = '0' * (len(checksum_check) - len(checksum)) + checksum

        decoded_message = message_received_bytes.decode(encoding="ISO-8859-1")

        # Fazendo a verificação do checksum, sequence number e ack
        if not decoded_message or decoded_message == "FYN-ACK" or decoded_message == "SYN-ACK": # Caso não exista mensagem, seja pacote de finalização ou pacote de inicialização, irá conferir ack number
            if checksum != checksum_check or ack_num != seq_num_client:  # Reenvia último pacote (DICA: guardar último pacote enviado em uma variável até recber ack do mesmo)
                print("Houve corrupção no pacote!")
            else: # Recebe ack do pacote recebido
                c.ACK_RECEIVED = True # Afirma que recebeu ack

                if decoded_message == "FYN-ACK":
                    send_packet("ACK", client, 9999, client_ip, nickname, seq_num, ack_to_send) # Envia reconhecimento de FYN-ACK
                    is_conected = False # Desconecta quando envia ack de reconhecimento de terminar conexão do server
                
                elif decoded_message == "SYN-ACK":
                    send_packet(message_buffer, client, 9999, client_ip, nickname, seq_num_client, ack_to_send)
                    is_conected = True
                else:
                    if seq_num_client == 0:
                        seq_num_client = 1
                    elif seq_num_client == 1:
                        seq_num_client = 0

        elif decoded_message: # Caso exista mensagem, irá conferir sequence number
            if checksum != checksum_check or seq_num != ack_to_send: # Reenvia ack do último pacote reconhecido
                print("Houve corrupção no pacote!")
                
                if ack_to_send == 0:
                    send_packet("", client, 9999, client_ip, nickname, seq_num, 1)
                else:
                    send_packet("", client, 9999, client_ip, nickname, seq_num, 0)
            else: # Lê mensagem e envia ack do pacote recebido
                if(decoded_message.startswith(f"{client_ip}:{CLIENT_ADRR}")):
                    decoded_message = decoded_message[(16 + len(nickname)):]
                    print(f"{client_ip}:{CLIENT_ADRR}/~Você{decoded_message}")
                else:
                    print(decoded_message)
                send_packet("", client, 9999, client_ip, nickname, seq_num, ack_to_send)

                # Atualiza próximo ack a ser enviado
                if ack_to_send == 0:
                    ack_to_send = 1
                else:
                    ack_to_send = 0

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

    if message == "":
            print("Insira sua mensagem!")
    
    # Se não estiver conectado, exibe mensagem de que não está conectado
    elif not is_conected and message == "bye": 
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
            message_buffer = message
            send_packet("SYN", client, 9999, client_ip, nickname, seq_num_client, ack_to_send)

        # Caso seja o comando de sair da sala
        elif message == "bye":
            send_packet(message, client, 9999, client_ip, nickname, seq_num_client, ack_to_send) 

        # Se estiver conectado e a mensagem não for um comando, envia essa mensagem para o servidor
        else:
            send_packet(message, client, 9999, client_ip, nickname, seq_num_client, ack_to_send)