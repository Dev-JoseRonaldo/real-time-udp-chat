# Projeto Redes UDP RTC 3.0

## Sobre o Projeto

O projeto em questão consiste na criação de um servidor de chat de sala única, onde os clientes podem se conectar e trocar mensagens, sendo que essas mensagens são representadas por arquivos .txt. O principal objetivo é permitir não apenas a comunicação textual entre os usuários, mas também a transferência de arquivos em formato de texto.

### Especificidades
- Implementação de comunicação UDP utilizando Socket em Python;
- Troca de arquivos .txt em pacotes de até 1024 bytes;
- Exibição das mensagens no formato: `<IP>: <PORTA> /~<nome_usuario>: <mensagem> <hora-data>`;
- Funcionalidades executadas via linhas de comando pelo cliente, conforme tabela:
    ![Alt text](https://res.cloudinary.com/devjoseronaldo/image/upload/v1706836505/udp-chat/tabela_opvyrp.png "tabela")

---

### Como Rodar

1. Primeiro, o usuário deve rodar simultaneamente os dois principais arquivos (nesta ordem) em terminais diferentes:
   - Rodar o arquivo _server.py_
   - Rodar o arquivo _client.py_

2. A partir disso, o primeiro usuário poderá usar o chat.

3. Caso outro usuário deseje usar o chat, é preciso rodar o _client.py_ novamente em outro terminal, de modo que haverá um terminal com _client.py_ para cada pessoa que estiver utilizando o chat.

---

### Desenvolvimento

Ao iniciarmos o desenvolvimento deste projeto, adotamos a metodologia ágil, como Scrum e Kanban, para otimizar a gestão de tarefas e responsabilidades. Utilizamos o Kanban no Notion, estruturando nossas atividades em colunas de "A fazer", "Fazendo" e "Terminado", o que proporcionou uma visão clara do progresso em cada etapa.

#### Divisão de Tarefas e Metodologia Ágil:

1. **Definição de Requisitos Básicos:**
   - Inclusão de elementos essenciais como a MIT License, arquivo gitignore e ReadME, estabelecendo uma base sólida para o projeto.

2. **Comentários no Código:**
   - Iniciamos a documentação do código nos arquivos _client.py_ e _server.py_, visando proporcionar um entendimento claro do funcionamento do programa para todos os membros da equipe.

3. **Conversão de String para Arquivos .txt:**
   - Criamos as estruturas necessárias, incluindo as pastas _data_ e _src_, além do arquivo _convert_txt.py_, para realizar a conversão de strings para arquivos .txt de forma eficiente.

4. **Criação da Saída do Usuário:**
   - Implementamos funções nos arquivos _server.py_ e _client.py_ para gerar a saída desejada, garantindo uma experiência intuitiva para os usuários conectados ao chat.

5. **Refatorização (Ajuste de Outputs):**
   - Realizamos melhorias nas saídas do _client.py_, visando aprimorar a usabilidade do programa e garantir uma interação mais fluida.

#### Progresso e Ferramentas Utilizadas:
O uso do Kanban no Notion nos permitiu acompanhar de perto o progresso de cada tarefa, identificar eventuais gargalos e promover uma comunicação eficaz entre os membros da equipe, junto com o Whatsapp e Discord.
![Alt Text](https://res.cloudinary.com/devjoseronaldo/image/upload/v1706836505/udp-chat/tasks_i6kufa.png "tasks")
    
![Alt Text](https://res.cloudinary.com/devjoseronaldo/image/upload/v1706836505/udp-chat/Calend%C3%A1rio_fzzhdi.png "calendário")

Em cada etapa, buscamos aprimorar a funcionalidade e a eficiência do servidor de chat, garantindo que todas as exigências do projeto fossem atendidas. Comentários detalhados no código e a constante revisão das saídas do cliente foram cruciais para garantir a qualidade do programa desenvolvido.

Esse processo de desenvolvimento, aliado às metodologias ágeis adotadas, proporcionou uma abordagem colaborativa e adaptável, resultando em um projeto bem estruturado e funcional.
