from utils.create_fragment import create_fragment
from utils.convert_txt import convert_string_to_txt
import utils.constants as c
import math

def send_packet(message, sender, destination_address, origin_adress=None, nickname=None, ServerSide = False):

    # Converte a mensagem em um arquivo txt
    if ServerSide:
        path_file = convert_string_to_txt(message, nickname, True) # SERVER sending
    else:
        path_file = convert_string_to_txt(message, nickname) # CLIENT sending
    # Lendo o conteudo do arquivo
    file = open(path_file,"rb")
    contents = file.read()

    #fragmentando o arquivo em diversas partes
    fragIndex = 0 # Indice do fragmento
    fragSize = c.FRAG_SIZE # Tamanho do fragmento (setado em 8 para facilitar os testes, mas o o correto seria => tamanho do buffer(1024) - tamanho do header(16))
    fragCount = math.ceil(len(contents) / fragSize) # Quantidade total de fragmentos

    # Envia os fragmentos para o servidor
    while contents:
        fragment = create_fragment(contents, fragSize, fragIndex, fragCount)

        if origin_adress:
            sender.sendto(fragment, (origin_adress, destination_address)) # Envia o fragmento (header + data)
        else:
            sender.sendto(fragment, (destination_address)) # Envia o fragmento (header + data)

        contents = contents[fragSize:] # Remove o fragmento enviado do conteúdo
        fragIndex += 1 # Incrementa o índice do fragmento