import random

#função responsável por salvar sstring em arquivo .txt
def convert_string_to_txt(user, string, serverSide=False):
    #numero randomico para evitar que o nome do arquivo se repita
    random_number = random.randint(1000, 9998)
    file_name = f'{user}{random_number}'

    #flag para modificar o caminho do arquivo caso seja gerado pelo servidor
    if serverSide:
        path_file = f"./segunda_entrega/data/server/{file_name}.txt"
    else:
        path_file = f"./segunda_entrega/data/client/{file_name}.txt"

    #salvando string em arquivo .txt
    file = open(path_file, "a")
    file.write(string)

    #retornando o caminho do arquivo
    return path_file