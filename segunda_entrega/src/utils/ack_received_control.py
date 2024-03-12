# ack_manager.py

class AckReceivedControl:
    # Atributos de classe compartilhados entre instâncias
    clients_ack_received = []
    server_ack_received = []

    def __init__(self):
        # Usar os atributos de classe como se fossem atributos de instância
        self.clients_ack_received = AckReceivedControl.clients_ack_received
        self.server_ack_received = AckReceivedControl.server_ack_received

    def update_ack_received(self, origin_address, name, status):
        exist = False

        if origin_address:
            for client in AckReceivedControl.clients_ack_received:
                if client[0] == name:
                    client[1] = status
                    exist = True

            if not exist:
                AckReceivedControl.clients_ack_received.append([name, status])
        else:
            for client in AckReceivedControl.server_ack_received:
                if client[0] == name:
                    client[1] = status
                    exist = True

            if not exist:
                AckReceivedControl.server_ack_received.append([name, status])

        print(AckReceivedControl.server_ack_received)
        print(AckReceivedControl.clients_ack_received)

    def remove_ack_received(self, origin_address, name):

        if origin_address:
            for client in AckReceivedControl.clients_ack_received:
                if client[0] == name:
                    AckReceivedControl.clients_ack_received.remove(client)
        else:
            for client in AckReceivedControl.server_ack_received:
                if client[0] == name:
                    AckReceivedControl.server_ack_received.remove(client)

    def get_ack_received(self, origin_address, name):
        
        if origin_address:
            for client in AckReceivedControl.clients_ack_received:
                if client[0] == name:
                    return client[1]
        else:
            for client in AckReceivedControl.server_ack_received:
                if client[0] == name:
                    return client[1]