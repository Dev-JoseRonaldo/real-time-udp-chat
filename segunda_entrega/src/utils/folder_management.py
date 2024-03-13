import os
import shutil

# Verifica se uma pasta existe
def is_folder_exists(path, name, server_side=False):
    # Constrói o caminho completo com base nos parâmetros fornecidos
    if server_side:
        path_folder = path + '/server/' + name
    else:
        path_folder = path + '/client/' + name

    return os.path.exists(path_folder)

# Cria uma nova pasta
def create_folder(path, name, server_side=False):
    # Constrói o caminho completo com base nos parâmetros fornecidos
    if server_side:
        path_folder = path + '/server/' + name
    else:
       path_folder = path + '/client/' + name

    # Cria a pasta se ela ainda não existir
    if not os.path.exists(path_folder):
        os.makedirs(path_folder)

    return path_folder

# Exclui uma pasta e seu conteúdo
def delete_folder(path,name, server_side=False):
    # Constrói o caminho completo com base nos parâmetros fornecidos
    if server_side:
        path_folder = f'{path}/server/' + name
    else:
       path_folder = f'{path}/client/' + name

    # Verifica se o caminho da pasta existe e, se sim, exclui a pasta
    if os.path.exists(path_folder):
        shutil.rmtree(path_folder)