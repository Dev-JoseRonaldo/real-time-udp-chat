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