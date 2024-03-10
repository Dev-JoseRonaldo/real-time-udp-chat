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