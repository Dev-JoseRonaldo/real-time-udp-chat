# Importando bibliotecas python 
import socket # Cria sockets par comunicação em uma rede
import random # Possibilita gerar números aleatórios
import threading # Cria threads, que são úteis para executar operações simultâneas
import math # Biblioteca de funções matemáticas
import struct # Bilioteca que Interpreta bytes como dados binários compactados
from zlib import crc32 # Calcula uma soma de verificação CRC 32 bits

from utils.convert_txt import convert_string_to_txt
import utils.constants as c
from utils.print_commands import print_commands
# Criação do socket UDP
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Atribuição de uma porta aleatória entre 1000 e 9998
CLIENT_ADRR = random.randint(1000, 9998)
client.bind((c.SERVER_ADRR[0], CLIENT_ADRR))

#fragSize = c.FRAG_SIZE

# Função para receber mensagens
def receive():
    while True:
        try:
            # Recebe mensagens do servidor
            message, _ = client.recvfrom(c.BUFF_SIZE)

            # Converte a sequência de bytes da mensagem recebida em uma string
            decoded_message = message.decode() 

            checksum = decoded_message.split(":")[0] # Armazena o checksum criado pelo remetente (servidor neste caso)
            checksum_check = crc32((':'.join(decoded_message.split(":")[1:])).encode()) # Cria um checksum localmente(destinatário) para comparar com o checksum do remetente

            if int(checksum_check) != int(checksum): # Verifica se os checksum são diferentes
                print("Houve corrupção no pacote!")
            else: # Caso os checksums sejam iguais
                print(':'.join(decoded_message.split(":")[1:])) # Exibe a mensagem decodificada
        except:
            pass



# Inicia uma thread para a função receive
receive_thread = threading.Thread(target=receive)
receive_thread.start()

print_commands()
is_conected = False

# Função responsável por criar um fragmento
def create_fragment(contents, fragSize, fragIndex, fragCount):
    data = bytearray() # Estrtura de dados do tipo bytearray
    data.extend(contents[:fragSize]) # Pegando um fragmento de tamanho fragSize
    
    header_checksumless = struct.pack('!III', fragSize, fragIndex, fragCount) # Header compactado sem o checksum
    fragment_checksumless = header_checksumless + bytearray(data) # fragmento sem o checksum

    checksum = crc32(fragment_checksumless) # Gerando uma soma de verificação CRC como checksum
    header = struct.pack('!IIII', fragSize, fragIndex, fragCount, checksum) # Header compactado com checksum
    fragment = header + bytearray(data) # Fragmento completo (com checksum)

    return fragment

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
            # Envia uma mensagem de inscrição com o nickname escolhido para o servidor
            client.sendto(f"SIGNUP_TAG:{nickname}".encode(), (client_ip, 9999))

    # Caso seja o comando de sair da sala
    elif message == "bye":
        # Se não estiver conectado exibi mensagem de que não está conectado
        if not is_conected:
            print("Você não está conectado à sala!")

        # Caso esteja conectado, sai da sala
        else:
            client.sendto(f"QUIT_TAG:{nickname}".encode(), (client_ip, 9999))
            is_conected = False
            print_commands()

    # Se estiver conectado e a mensagem não for um comando, envia essa mensagem para o servidor
    elif is_conected:
        # Converte a mensagem em um arquivo txt
        path_file = convert_string_to_txt(nickname, message)
        # Lendo o conteudo do arquivo
        file = open(path_file,"rb")
        contents = file.read()

        #fragmentando o arquivo em diversas partes
        fragIndex = 0 # Indice do fragmento
        fragSize = 8 # Tamanho do fragmento (setado em 8 para facilitar os testes, mas o o correto seria => tamanho do buffer(1024) - tamanho do header(16))
        fragCount = math.ceil(len(contents) / fragSize) # Quantidade total de fragmentos

        # Envia os fragmentos para o servidor
        while contents:
            fragment = create_fragment(contents, fragSize, fragIndex, fragCount)

            client.sendto(fragment, c.SERVER_ADRR)   # Envia o fragmento (header + data) para o servidor
            contents = contents[fragSize:] # Remove o fragmento enviado do conteúdo
            fragIndex += 1 # Incrementa o índice do fragmento

    # Caso não esteja conectado e a mensagem não seja um comando, exibe mensagem de comando inválido
    else:
        print("Comando inválido!")
