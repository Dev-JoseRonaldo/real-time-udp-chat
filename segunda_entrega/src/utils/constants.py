BUFF_SIZE = 1024
SERVER_ADRR = ("localhost", 9999) # Talvez mudar para só 9999 e usar apenas para endereço do servidor, ou mudar local host para o endereço do cliente
HEADER_SIZE = 24
FRAG_SIZE = BUFF_SIZE - HEADER_SIZE
TIMEOUT = 200 #0.5
ACK_RECEIVED = False