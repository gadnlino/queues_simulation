# Trabalho de simulação - Teoria de Filas

## Introdução

### Visão geral

A implementação foi realizada em Python 3. Para a execução do simulador, ver seção **Instruções para execução do simulador**.

O ponto inicial é o arquivo `main.py`, onde é criado uma instância do o simulador(classe Simulator), com os parametros apropriados. No construtor da classe, são iniciadas as variáveis de controle e parametrizações do simulador(detalhados mais adiante). Em seguida, inicia-se a execução do simulador, chamando o método `run()`.

A execução do simulador é da seguinte forma:

No loop principal, é gerado o evento inicial de chegada do cliente(evento ARRIVAL). Em seguida o programa trata os eventos da lista de eventos e realiza a coleta das estatísticas apropriadas para o cliente associado ao evento. O objetivo é que, a cada partida de um cliente, tenham sido coletadas uma amostra de uma das métricas de seu tempo de atraso e tempo de serviço em cada uma das filas.

Ao final da simulação, há a opção de gerar arquivos com as métricas a cada rodada e gráficos com a evolução desses valores.

Os eventos da simulação podem ser dos seguintes tipos:

- `EventType.ARRIVAL`: é a chegada de um novo cliente ao sistema. Caso o sistema se encontre vazio, o cliente recém chegado inicia imediatamente o serviço. Se o serviço corrente for um cliente oriudo da fila de menor prioridade, o serviço é interrompido e o cliente recém chegado inicia a sua execução. Nos demais casos, o cliente é enfileirado na fila de maior prioridade. É nesse momento que novas chegadas ao sistema são agendadas.

- `EventType.START_SERVICE_1`: início do primeiro serviço do cliente, oriundo da fila de maior prioridade. É obtido o tempo de serviço e agendado um evento de término desse primeiro serviço.

- `EventType.END_SERVICE_1`: término do primeiro serviço do cliente. Se não houverem serviços em execução, o cliente inicia o segundo serviço imediatamente. Caso contrário, é direcionado para a fila de menor prioridade.

- `EventType.START_SERVICE_2`: início do segundo serviço do cliente, oriundo da fila de menor prioridade. É obtido o tempo de serviço e agendado o evento de partida do sistema para o momento do término do serviço.

- `EventType.HALT_SERVICE_2`: interrupção do segundo serviço do cliente. Acontece sempre que um novo cliente chega ao sistema durante um serviço oriundo da fila de menor prioridade. Quando esse evento ocorre, é necessário remover a partida do cliente que teve seu serviço interrompido.

- `EventType.DEPARTURE`: o término do segundo serviço do cliente, e a sua subsequente partida do sistema. Se houverem novos cliente para serem servidos, tem-se o serviço iniciado, seguindo a ordem de prioridade das filas.

Ao final de cada rodada, a média e a variância amostral são obtidas a partir das amostras obtidas durante o tratamento dos eventos.

### Simulador

### Estruturas e variáveis internas

Ao longo do código, são utilizadas diversas variáveis e estruturas de controle. Dentre elas, as mais relevantes são:

- `self.__event_q`: É a lista principal de eventos do simulador. De maneira geral, os eventos são inseridos na lista de maneira que permaneça sempre de maneira crescente pelo `timestamp` dos eventos. A inserção ordenada é feita utilizando o [`insort`](https://docs.python.org/3/library/bisect.html#bisect.insort).

- `self.__waiting_qs`: representação das filas de espera do sistema(como uma lista de listas). É gerida utilizando a estratégia FIFO, suportada pelas APIs padrão de listas do Python.

- `self.__utilization_pct`, `self.__service_rate`, `self.__arrival_rate`: São as indicações das taxas de utilização, de serviço e de chegada ao sistema. As duas primeiras são informadas no momento de instânciação da classe do simulador, e a última é derivada dessas, pela relação $$\rho = {\lambda \over \mu}$$

- `self.__current_timestamp`, `self.__current_service`: usadas para armazenar o tempo corrente de simulação e o serviço corrente em execução. O tempo é avançado à medida em que os eventos são tratados. Quando há o início ou término de um serviço, o valor do serviço corrente é modificado.

- `self.__number_of_rounds`, `self.__samples_per_round`, `self.__current_round`: O número de rodadas da simulação, o número de amostras coletadas a cada rodada, e o contador da rodada corrente.

- `self.__metrics_per_round`: Ao final de cada rodada, o método `self.__generate_round_metrics` é chamado e as métricas para a rodada atual são geradas. O resultado é armazenado como um registro na lista `self.__metrics_per_round`. Essa lista é usada para gerar os gráficos e os arquivos .csv ao final da simulação.

- `self.__event_log_raw`, `self.__event_log_raw_file`: Log de todos os eventos de todas as rodadas de simulação. Ao final, há a opção de salvar esse log no arquivo indicado pela varíavel `self.__event_log_raw_file`. Não interferem nas funções essenciais do simulador, mas foram utilizadas na depuração do simulador nas etapas iniciais de implementação.

Cada evento é representado pela classe `Event`, com as seguintes propriedades:

- `client_id`: Id do cliente associado à esse evento.
- `type`: Tipo do evento.
- `timestamp`: Instante de ocorrência do evento.
- `queue_number`: Número da fila onde o evento irá ocorrer.
- `remaining_service_time`: Tempo restante de serviço do cliente associado ao evento. Será preenchido somente quando type = EventType.START_SERVICE_2.

### Geração de VA's

A geração de variáveis aleatórias é feita usando a função [random](https://docs.python.org/3/library/random.html#random.random), disponível na biblioteca padrão da linguagem. A seed utilizado é a informada na configuração dos parametros do simulador.

Para gerar amostras de variáveis aleatórias exponenciais, é usado o seguinte cálculo(como também indicado nos materiais de aula):

$$x_0 = {\log{u_0} \over -\lambda}$$

### Amostragem

Para as métricas referentes ao número de clientes no sistema e em cada fila de espera, a coleta é realizada a cada tratamento de evento da simulação. Isso permitiu uma maior precisão para a estimativa, em especial para a fila 2, que tem seus eventos associados tratados somente após os eventos da fila 1.

Para a média dos tempos em fila de espera, tempo de serviço e tempo total, é calculado o valor absoluto para cada um dos clientes, e, ao final da rodada, ou seja, após a partida de k clientes, calcula-se o valor médio e a variância para a rodada. Nesse momento, é incrementa-se o estimador para a média do valor médio das rodadas. No gráfico gerado ao final das rodadas, esse valor é apresentado por uma linha tracejada, por ex:

[Médias da simulação tracejado em azul e vermelho](./images/example_mean_values.png)

## Teste de correção dos resultados

Foram realizadas execuções com o processo de chegada e de serviço determinísticos

//TODO: corrigir implementação determinística

## Determinando a fase transiente

Conforme o enunciado da tarefa, a equação de equilibrio para esse sistema é $$2\lambda = {\mu}$$

Então, para $$\rho = 1$$, posso deduzir analiticamente que o sistema permanece em equilíbrio para taxas de chegada até 0.5. Esse valor será mencionado mais adiante na seção **Conclusão**.

Dado isso, analisei o número de serviços executados pelo sistema até que entrasse em equilibrio, para diferentes taxas até essa taxa de serviço crítica, incrementando o número de rodadas e o número de serviços por rodada, e configurando o número de serviços até a fase transiente para 0 nas configurações do simulador.

De maneira geral, observou-se que com 10000 serviços executados(`number_of_rounds`=200, `samples_per_round`=50, `services_until_steady_state`=0), o sistema já se encontrava em equilibrio para as taxas de utilização menores do que 0.5:

[rho = 0.2](./images/wait_time_10000_services_lambda_02.png)

[rho = 0.4](./images/wait_time_10000_services_lambda_04.png)

## Análise dos resultados

//TODO:
### Chegando ao fator mínimo

## Otimizações
//TODO:
## Conclusão

Ao executar a simulação para os diferentes valores da taxa de utilização, fica claro a relação entre essa taxa e a convergência da fila para um estado de equilibrio; Ao executar com taxas maiores do que 0.5, o número de clientes na fila 2 e o tempo de espera médio aumentam indefinidamente!

[Número médio de clientes na fila, lambda=0.49](./images/q_size_lambda_049.png)

[Atraso médio, lambda=0.49](./images/wait_time_lambda_049.png)

[Número médio de clientes na fila, lambda=0.51](./images/q_size_lambda_051.png)

[Atraso médio, lambda=0.51](./images/wait_time_lambda_051.png)

### Dificuldades
- Amostragem de métricas

    Não pude utilizar um sistema de cores a cada **chegada**, como indicado nos materiais de aula. O motivo foi que, na minha implemenmtação, caso considerasse somente as chegadas, as métricas da segunda fila(W2 e X2) poderiam não ser calculadas para o número desejado de clientes. Com isso, determinei que a rodada avançaria sempre que k clientes tivessem a sua **partida** do sistema.

- Cálculo do intervalo de confiança

    Como calculo o número de rodadas previamente, tendo uma precisão alvo para o intervalo de confiança?

## Instruções para execução do simulador

//TODO:

## Integrantes do grupo
- Guilherme Avelino do Nascimento - DRE 117078497