import os

client_dict_file_counter = {}
server_dict_file_counter = {}

def update_dict_file_counter(dict_file_counter, user):
    if dict_file_counter:
        if user in dict_file_counter:
            dict_file_counter[user] += 1
        else:
            dict_file_counter[user] = 1
    else:
        dict_file_counter[user] = 1
    return dict_file_counter

def remove_user_files(dict_file_counter, user, environment):
    file_counter = dict_file_counter[user]
    for count in range(1, file_counter+1):
        file_name = f"{user}{count}"
        os.remove(f"./segunda_entrega/data/{environment}/{file_name}.txt")

    del dict_file_counter[user]