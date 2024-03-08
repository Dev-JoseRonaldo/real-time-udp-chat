from utils.create_fragment import create_fragment
from utils.convert_txt import convert_string_to_txt
import utils.constants as c
import math
import time

def send_packet(message, sender, destination_address, origin_adress=None, nickname=None, seq_num=None, ack_num=None):
    fragment_sent = True # Controle do status de envio do fragmento
    
    # Converte a mensagem em um arquivo txt
    if not origin_adress:
        path_file = convert_string_to_txt(message, nickname, True) # SERVER sending
    else:
        path_file = convert_string_to_txt(message, nickname) # CLIENT sending
    # Lendo o conteudo do arquivo
    file = open(path_file,"rb")
    contents = file.read()

    #fragmentando o arquivo em diversas partes
    fragIndex = 0 # Indice do fragmento
    fragSize = c.FRAG_SIZE # Tamanho do fragmento 
    fragCount = math.ceil(len(contents) / fragSize) # Quantidade total de fragmentos

    # Envia os fragmentos
    if contents: # Se pacote enviado for com conteúdo
        while contents: 
            fragment = create_fragment(contents, fragSize, fragIndex, fragCount, seq_num, ack_num)
            try:
                sender.settimeout(c.TIMEOUT)
                if origin_adress:
                    sender.sendto(fragment, (origin_adress, destination_address)) # Envia o fragmento (header + data) para servidor
                else:
                    sender.sendto(fragment, (destination_address)) # Envia o fragmento (header + data) para cliente
            except sender.timeout:
                print("O envio da mensagem excedeu o tempo limite!")
                fragment_sent = False

            if fragment_sent:
                contents = contents[fragSize:] # Remove o fragmento enviado do conteúdo
                fragIndex += 1 # Incrementa o índice do fragmento
            
            fragment_sent = True # Reestabele status 'True' para fazer nova conferência

    else: # Se pacote enviado for de reconhecimento
        fragment = create_fragment(contents, fragSize, fragIndex, fragCount, seq_num, ack_num)
        
        if origin_adress:
            sender.sendto(fragment, (origin_adress, destination_address)) # Envia o fragmento (header + data) para servidor
        else:
            sender.sendto(fragment, (destination_address)) # Envia o fragmento (header + data) para cliente