import datetime as dt # biblioteca pra manipular datas e horas

# Função responsável por retornar a data e hora atual no formato solicitado
def get_current_time_and_date():
  return dt.datetime.now().strftime("%H:%M:%S %d/%m/%Y ")