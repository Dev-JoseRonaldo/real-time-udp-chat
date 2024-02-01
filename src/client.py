# Importando bibliotecas python 
import socket # Cria sockets par comunicação em uma rede
import random # Possibilita gerar números aleatórios
import threading # Cria threads, que são úteis para executar operações simultâneas
import math # Biblioteca de funções matemáticas
import struct # Bilioteca que Interpreta bytes como dados binários compactados
from zlib import crc32 # Calcula uma soma de verificação CRC 32 bits
from convert_txt import convert_string_to_txt

# Criação do socket UDP
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Atribuição de uma porta aleatória entre 1000 e 9998
client.bind(("localhost", random.randint(1000, 9998)))

# Função responsável por imprimir os comandos disponíveis
def print_commands():
  header = ['Funcionalidade', 'Comando']
  conect_command = ['Conectar à sala', 'hi, meu nome eh <nome_do_usuario>']
  quit_command = ['Sair da sala', 'bye']

  print('---------------------------------------------------------------------')
  print('{:^12} {:>20}'.format(*header))
  print('---------------------------------------------------------------------')
  print('{:^12} {:>45}\n'.format(*conect_command))
  print('{:^12} {:>18}'.format(*quit_command))
  print('---------------------------------------------------------------------\n')

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

print_commands()
is_conected = False

# Loop principal para envio de mensagens
while True:
    # Solicita ao usuário para inserir uma mensagem
    message = input()

    # Verifica se a mensagem inserida é um o comando para entrar na sala
    if message.startswith("hi, meu nome eh "):
        # Se já estiver conectado exibi mensagem de que já está conectado
        if is_conected:
            print("Você já está conectado à sala!")

        # Caso não esteja conectado, conecta à sala
        else:
            nickname = message[16:]
            is_conected = True
            # Envia uma mensagem de inscrição com o nickname escolhido para o servidor
            client.sendto(f"SIGNUP_TAG:{nickname}".encode(), (client.getsockname()[0], 9999))

    # Caso seja o comando de sair da sala
    elif message == "bye":
        # Se não estiver conectado exibi mensagem de que não está conectado
        if not is_conected:
            print("Você não está conectado à sala!")

        # Caso esteja conectado, sai da sala
        else:
            client.sendto(f"QUIT_TAG:{nickname}".encode(), (client.getsockname()[0], 9999))
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
        fragSize = 8 # Tamanaho do fragmento
        fragCount = math.ceil(len(contents) / fragSize) # Quantidade total de fragmentos

        # Envia os fragmentos para o servidor
        while contents:
            data = bytearray() # Estrtura de dados do tipo bytearray
            data.extend(contents[:fragSize]) # Pegando um fragmento de tamanho fragSize
            crc = crc32(data) # gerando uma soma de verificação CRC (pode ser útil para a etapa 2 do projeto)
            header = struct.pack('!IIII', fragSize, fragIndex, fragCount, crc) # Header compactado

            client.sendto(header + bytearray(data), ("localhost", 9999))   # Envia o fragmento (header + data) para o servidor
            contents = contents[fragSize:] # Remove o fragmento enviado do conteúdo
            fragIndex += 1 # Incrementa o índice do fragmento

    # Caso não esteja conectado e a mensagem não seja um comando, exibe mensagem de comando inválido
    else:
        print("Comando inválido!")