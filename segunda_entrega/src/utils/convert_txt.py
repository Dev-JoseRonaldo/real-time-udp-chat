from utils.update_dict_file_counter import client_dict_file_counter, server_dict_file_counter, update_dict_file_counter
from utils.folder_management import create_folder
#função responsável por salvar sstring em arquivo .txt
def convert_string_to_txt(string, user, ServerSide = False):
    # Dicionário com contador de arquivos por usuário para salvar mensagens corretamente
    global client_dict_file_counter, server_dict_file_counter
    
    # Atualiza no dicionário o usuário e número de arquivos do mesmo
    if ServerSide:
        dict_file_counter = update_dict_file_counter(server_dict_file_counter, user)
    else:
        dict_file_counter = update_dict_file_counter(client_dict_file_counter, user)

    file_name = f'{user}{dict_file_counter[user]}'

    #flag para modificar o caminho do arquivo caso seja gerado pelo servidor
    #../../data
    path_file = create_folder("./segunda_entrega/data", user, ServerSide) + f"/{file_name}.txt"


    #salvando string em arquivo .txt
    file = open(path_file, "a")
    file.write(string)

    #retornando o caminho do arquivo
    return path_file