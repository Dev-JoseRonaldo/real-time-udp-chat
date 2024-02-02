# Projeto Redes UDP RTC 3.0

## Sobre

Neste projeto será desenvolvido um servidor de chat de sala única, onde os
clientes se conectam à sala e recebem todas as mensagens dos outros usuários, além de
também poderem enviar mensagens. Entretanto, essas mensagens não são strings como o
convencional, mas, a fim de haver transferência de arquivos e segmentação dos mesmos,
serão arquivos .txt que sendo lidos pelo servidor deverão ser impressos no terminal como
mensagens.
<br>
<br>
O projeto será composto por duas etapas, em que na primeira etapa o grupo deve
desenvolver uma ferramenta de troca de arquivos .txt e reverberar isso em um chat de
mensagens que utilize comunicação com UDP. Na segunda etapa, deverá ser
implementado ao chat básico de troca de mensagens já feito, um protocolo de transferência
confiável, utilizando UDP e o método RDT 3.0.